"""This will handle the solo game mode."""

# coding: utf-8

from copy import deepcopy
from curses import window, A_BOLD, color_pair
from functools import lru_cache
from typing import Optional
from random import shuffle, seed, randint

# from math import floor

# TODO: Flowchart:
# DONE: Generation phase
# Falling phase
# if Hard drop:
#   go to pattern phase.
# Lock phase:
# if moved:
#   if there is space to fall:
#       go to falling phase.
#   else:
#       if lock delay is up:
#           go to lock phase.
#       else:
#           go to pattern phase.
# else:
#   go to pattern phase.
# Pattern phase:
# if pattern:
#   mark for deletion.
# Iterate phase:
# Animation phase:
# Deletion phase:
# Completion phase:
#
# Repeat from Generation phase.

POINTS_TABLE: dict[str, int] = {
    "Single": 100,
    "Double": 300,
    "Triple": 500,
    "Tetris": 800,
    "Mini_Tspin": 100,
    "Mini_Tspin_Single": 200,
    "Tspin": 400,
    "Tspin_Single": 800,
    "Tspin_Double": 1200,
    "Tspin_Triple": 1600,
}

MIN_X: int = 80
MIN_Y: int = 24

BOARD_WIDTH: int = 10
BOARD_HEIGHT: int = 40
DRAW_BOARD_WIDTH: int = BOARD_WIDTH * 2  # Each cell is 2 chars wide
DRAW_BOARD_HEIGHT: int = 20  # Show only 22 rows 20 + 2 for extra
TARGET_FPS: int = 30
MINO_TYPES: set[str] = {"I", "O", "T", "S", "Z", "J", "L"}
MINO_COLOR: dict[str, int] = {"O": 1, "I": 2, "T": 3, "L": 4, "J": 5, "S": 6, "Z": 7}
MINO_ORIENTATIONS: list[str] = ["N", "E", "S", "W"]

# Mino Draw Location: Mino_type -> orientation (in NSEW) ->
# (current_position, 1st_block_position, 2nd_block_position, 3rd_block_position)
#
# Note: (y, x) format
MINO_DRAW_LOCATION: dict[str, dict[str, list[tuple[int, int]]]] = {
    "O": {
        "N": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "S": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "E": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "W": [(0, 0), (0, 1), (1, 0), (1, 1)],
    },
    "I": {
        "N": [(0, 0), (0, -1), (0, 1), (0, 2)],
        "S": [(0, 0), (0, -1), (0, 1), (0, 2)],
        "E": [(0, 0), (-1, 0), (1, 0), (2, 0)],
        "W": [(0, 0), (1, 0), (-1, 0), (-2, 0)],
    },
    "T": {
        "N": [(0, 0), (0, -1), (1, 0), (0, 1)],
        "S": [(0, 0), (0, -1), (-1, 0), (0, 1)],
        "E": [(0, 0), (-1, 0), (0, 1), (1, 0)],
        "W": [(0, 0), (-1, 0), (0, -1), (1, 0)],
    },
    "L": {
        "N": [(0, 0), (0, -1), (0, 1), (1, 1)],
        "S": [(0, 0), (0, -1), (0, 1), (-1, -1)],
        "E": [(0, 0), (-1, 0), (1, 0), (-1, 1)],
        "W": [(0, 0), (-1, 0), (1, 0), (1, -1)],
    },
    "J": {
        "N": [(0, 0), (0, -1), (0, 1), (1, -1)],
        "S": [(0, 0), (0, -1), (0, 1), (-1, 1)],
        "E": [(0, 0), (-1, 0), (1, 0), (1, 1)],
        "W": [(0, 0), (-1, 0), (1, 0), (-1, -1)],
    },
    "S": {
        "N": [(0, 0), (0, -1), (1, 0), (1, 1)],
        "S": [(0, 0), (0, 1), (-1, 0), (-1, -1)],
        "E": [(0, 0), (1, 0), (0, 1), (-1, 1)],
        "W": [(0, 0), (-1, 0), (0, -1), (1, -1)],
    },
    "Z": {
        "N": [(0, 0), (0, 1), (1, 0), (1, -1)],
        "S": [(0, 0), (0, -1), (-1, 0), (-1, 1)],
        "E": [(0, 0), (-1, 0), (0, 1), (1, 1)],
        "W": [(0, 0), (1, 0), (0, -1), (-1, -1)],
    },
}


class Board:
    """This will handle the game board."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.__board: list[list[int]] = [
            ([0] * BOARD_WIDTH) for _ in range(BOARD_HEIGHT)
        ]

    def clear(self) -> None:
        """This will clear the board."""
        self.__board = [([0] * BOARD_WIDTH) for _ in range(BOARD_HEIGHT)]

    def place_mino(
        self, mino: str, orientation: str, position: tuple[int, int]
    ) -> None:
        """This will place the mino on the board."""
        if mino in MINO_DRAW_LOCATION and orientation in MINO_DRAW_LOCATION[mino]:
            for y_offset, x_offset in MINO_DRAW_LOCATION[mino][orientation]:
                y_pos = position[0] + y_offset
                x_pos = position[1] + x_offset
                if 0 <= y_pos < BOARD_HEIGHT and 0 <= x_pos < BOARD_WIDTH:
                    self.__board[y_pos][x_pos] = MINO_COLOR[mino]

    def is_cell_occupied(self, position: tuple[int, int]) -> bool:
        """Check if a cell is occupied."""
        y_pos, x_pos = position
        return (
            0 <= y_pos < BOARD_HEIGHT
            and 0 <= x_pos < BOARD_WIDTH
            and self.__board[y_pos][x_pos] != 0
        )

    def draw_blank_board(
        self,
        stdscr: window,
        offset: tuple[int, int],  # (offset_y, offset_x)
    ) -> window:
        """Draw the Game board centered on the screen."""
        # Draw top border
        stdscr.addstr(
            offset[0] - 1,
            offset[1] - 1,
            "+" + "- " * (DRAW_BOARD_WIDTH // 2) + "+",
        )
        # Draw Side Borders
        middle_line: str = "|" + " " * DRAW_BOARD_WIDTH + "|"
        for row in range(DRAW_BOARD_HEIGHT):
            stdscr.addstr(
                offset[0] + row,
                offset[1] - 1,
                middle_line,
                A_BOLD,
            )
        # Draw bottom border
        stdscr.addstr(
            offset[0] + DRAW_BOARD_HEIGHT,
            offset[1] - 1,
            "+" + "-" * DRAW_BOARD_WIDTH + "+",
            A_BOLD,
        )

        return stdscr

    def draw_minos_on_board(
        self,
        stdscr: window,
        offset: tuple[int, int],  # (offset_y, offset_x)
        max_yx: tuple[int, int],  # (max_y, max_x)
        current_mino: Optional["Mino"] = None,
    ) -> window:
        """Draw the minos on the board."""

        draw_board: list[list[int]] = deepcopy(self.__board)

        # Draw current Mino
        if current_mino:
            if (
                current_mino.type in MINO_DRAW_LOCATION
                and current_mino.orientation in MINO_DRAW_LOCATION[current_mino.type]
            ):
                for y_offset, x_offset in MINO_DRAW_LOCATION[current_mino.type][
                    current_mino.orientation
                ]:
                    y_pos = current_mino.position[0] + y_offset
                    x_pos = current_mino.position[1] + x_offset
                    if 0 <= y_pos < BOARD_HEIGHT and 0 <= x_pos < BOARD_WIDTH:
                        draw_board[y_pos][x_pos] = MINO_COLOR[current_mino.type]

        # Draw cells
        max_rows: int = min(max_yx[0], BOARD_HEIGHT)
        # This is to adjust the drawing height if the terminal is too small
        adjusted_height: int = max_rows - DRAW_BOARD_HEIGHT
        visible_rows: list[list[int]] = draw_board[0:max_rows]
        for y_counter, row in enumerate(visible_rows):
            # y_counter=0 is bottom, y_counter=20 is top of box
            for x_counter, cell in enumerate(row):
                char: str = "  "
                if visible_rows[y_counter][x_counter] > 0:
                    char = "██"
                elif visible_rows[y_counter][x_counter] < 0:
                    char = "▒▒"
                elif y_counter == 20:
                    char = "- "
                # The extra -1 is to adjust for zero indexing
                y: int = offset[0] + (max_rows - 1 - y_counter) - adjusted_height
                # y: int = offset[0] + y_counter - adjusted_height
                x: int = offset[1] + x_counter * 2
                if 0 <= y < max_yx[0] and 0 <= x < max_yx[1] - 1:
                    stdscr.addstr(
                        y,
                        x,
                        char,
                        abs(color_pair(cell)) if cell else A_BOLD,
                    )
        return stdscr

    def draw_queue(
        self,
        stdscr: window,
        offset: tuple[int, int],  # (offset_y, offset_x)
        max_yx: tuple[int, int],  # (max_y, max_x)
        queue_list: list[str],
    ) -> window:
        """Draw the next mino queue."""

        queue_offset: tuple[int, int] = (offset[0], offset[1] + DRAW_BOARD_WIDTH + 1)
        horizontal_length: int = 12
        horizontal_line: str = "-" * horizontal_length + "+"
        vertical_length: int = 17

        # Draw the box and text
        stdscr.addstr(queue_offset[0] - 1, queue_offset[1], horizontal_line, A_BOLD)
        stdscr.addstr(queue_offset[0], queue_offset[1] + 2, "Next", A_BOLD)
        stdscr.addstr(queue_offset[0] + 1, queue_offset[1], horizontal_line, A_BOLD)
        for counter in range(vertical_length):
            stdscr.addstr(
                queue_offset[0] + counter,
                queue_offset[1] + horizontal_length,
                "|",
                A_BOLD,
            )
        stdscr.addstr(
            queue_offset[0] + vertical_length, queue_offset[1], horizontal_line, A_BOLD
        )

        mino_offset: tuple[int, int] = (0, 0)
        pos: tuple[int, int] = (0, 0)

        mino_height: int = 2
        mino_width: int = 4
        queue_length: int = 5

        # Clear the queue area before drawing (prevents leftover blocks)
        for queue_counter in range(queue_length):
            mino_offset = (queue_offset[0] + 2 + queue_counter * 3, queue_offset[1])
            for y_offset in range(mino_height):  # max mino height
                # max mino width (4 blocks * 2 chars + 2 for borders)
                for x_offset in range(mino_width * 2 + 2):
                    pos = (mino_offset[0] + y_offset, mino_offset[1] + x_offset)
                    if 0 <= pos[0] < max_yx[0] and 0 <= pos[1] < max_yx[1] - 1:
                        stdscr.addstr(pos[0], pos[1], "  ", A_BOLD)

        # Draw the next minos using block positions
        for queue_counter in range(queue_length):
            if len(queue_list) > queue_counter:
                mino: str = queue_list[queue_counter]
                orientation: str = "N"
                mino_offset = (
                    queue_offset[0] + 2 + queue_counter * 3,
                    queue_offset[1] + 4,
                )
                if (
                    mino in MINO_DRAW_LOCATION
                    and orientation in MINO_DRAW_LOCATION[mino]
                ):
                    for y_offset, x_offset in MINO_DRAW_LOCATION[mino][orientation]:
                        pos = (
                            mino_offset[0] + (mino_height - 1 - y_offset),
                            mino_offset[1] + x_offset * 2,
                        )
                        if 0 <= pos[0] < max_yx[0] and 0 <= pos[1] < max_yx[1] - 1:
                            stdscr.addstr(
                                pos[0],
                                pos[1],
                                "██",
                                color_pair(MINO_COLOR.get(mino, 0)),
                            )
        return stdscr


class Mino:
    """This will handle the mino."""

    def __init__(self, mino_type: str, level: int) -> None:
        """This will initialize this class."""
        self.__type: str = mino_type
        self.__orientation: str = "N"
        # 21st row at the center column
        self.__position: tuple[int, int] = (21, BOARD_WIDTH // 2 - 1)  # (y, x  )
        self.__soft_drop_counter: int = 0
        self.__fall_delay: int = self.reset_fall_delay(level)
        self.lock_info: dict[str, int] = {
            "lock_delay": int(0.5 * TARGET_FPS),
            "lock_count": 15,
            "lock_height": 21,
        }

    @property
    def type(self) -> str:
        """This will return the mino type."""
        return self.__type

    @property
    def orientation(self) -> str:
        """This will return the mino orientation."""
        return self.__orientation

    @property
    def position(self) -> tuple[int, int]:
        """This will return the mino position."""
        return self.__position

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        """This will set the mino position."""
        self.__position = value

    def get_block_positions(self) -> list[tuple[int, int]]:
        """This will return the block positions of the mino."""
        positions: list[tuple[int, int]] = []
        if (
            self.type in MINO_DRAW_LOCATION
            and self.orientation in MINO_DRAW_LOCATION[self.type]
        ):
            for y_offset, x_offset in MINO_DRAW_LOCATION[self.type][self.orientation]:
                y_pos = self.__position[0] + y_offset
                x_pos = self.__position[1] + x_offset
                positions.append((y_pos, x_pos))
        return positions

    # TODO: Implement SRS wall kick
    def rotate(self, direction: str) -> None:
        """This will rotate the current mino."""
        if direction not in ["left", "right"]:
            return

        current_index: int = MINO_ORIENTATIONS.index(self.orientation)
        new_index: int = 0
        # Note: This does not handle wall kicks
        if direction == "right":
            new_index = (current_index + 1) % len(MINO_ORIENTATIONS)
        elif direction == "left":
            new_index = (current_index - 1) % len(MINO_ORIENTATIONS)
        self.__orientation = MINO_ORIENTATIONS[new_index]

    def move_down(self) -> None:
        """This will move the current mino down."""
        self.__position = (self.__position[0] - 1, self.__position[1])

    @lru_cache(maxsize=4)
    def get_fall_seconds(self, level: int) -> float:
        """This will return the fall seconds for the given level."""
        return pow((0.8 - ((level - 1) * 0.007)), (level - 1))

    @lru_cache(maxsize=4)
    def reset_fall_delay(self, level: int) -> int:
        """This will return the fall delay for the given level."""
        seconds: float = self.get_fall_seconds(level)
        return max(1, int(seconds * TARGET_FPS))

    @property
    def fall_delay(self) -> int:
        """This will return the fall delay."""
        return self.__fall_delay

    @fall_delay.setter
    def fall_delay(self, value: int) -> None:
        """This will set the fall delay."""
        self.__fall_delay = max(0, value)

    @lru_cache(maxsize=4)
    def get_soft_drop_delay(self, level: int) -> int:
        """This will return the soft drop delay for the given level."""
        seconds: float = self.get_fall_seconds(level)
        soft_drop_seconds: float = seconds / 20  # Soft drop is 20 times faster
        return max(1, int(soft_drop_seconds * TARGET_FPS))

    def soft_drop(self, level: int) -> None:
        """This will handle the soft drop."""
        self.__soft_drop_counter += 1
        delay: int = self.get_soft_drop_delay(level)
        if self.__soft_drop_counter >= delay:
            self.move_down()
            self.__soft_drop_counter = 0


class ModeClass:
    """This will handle the solo game mode."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.action: str = ""
        self.countdown: int = TARGET_FPS * 3  # 3 seconds countdown
        self.offset: tuple[int, int] = (0, 0)  # (offset_y, offset_x)
        self.max_yx: tuple[int, int] = (0, 0)  # (max_y, max_x)

        self.seed_value: int = 0
        self.sound_action: dict[str, list[str]] = {"BGM": ["stop"], "SFX": []}
        self.mode: str = "countdown"

        self.board: Board = Board()

        self.current_mino: Optional[Mino] = None
        self.ghost_mino: Optional[Mino] = None
        self.current_hold: str = ""
        self.keyinput_cooldown: set[str] = set()
        # self.lock_info: dict[str, int] = {
        #     "lock_delay": int(0.5 * TARGET_FPS),
        #     "lock_count": 15,
        #     "lock_height": 21,
        # }
        self.level: int = 1

        self.mino_list: list[str] = []
        self.mino_generation(initial=True)

    def pop_action(self) -> str:
        """This will return the action and reset it."""
        action: str = deepcopy(self.action)
        self.action = ""
        return action

    def pop_sound_action(self) -> dict[str, list[str]]:
        """This will return the sound action and reset it."""
        sound_action: dict[str, list[str]] = deepcopy(self.sound_action)
        self.sound_action["SFX"] = []
        return sound_action

    def mino_generation(self, initial: bool = False) -> None:
        """This will handle the mino generation."""
        if initial:
            self.seed_value = randint(1, 1000000000)
            seed(self.seed_value)
            while len(self.mino_list) <= 14:
                new_mino_list = list(MINO_TYPES)
                shuffle(new_mino_list)
                self.mino_list.extend(new_mino_list)
        new_mino_list = list(MINO_TYPES)
        shuffle(new_mino_list)
        self.mino_list.extend(new_mino_list)

    def mino_touching_bottom(
        self,
        mino: Optional[Mino] = None,
    ) -> bool:
        """Return True if the current mino is touching the ground or a placed block below."""
        if mino is None:
            mino = self.current_mino
        for y_pos, x_pos in mino.get_block_positions():  # type: ignore
            if y_pos == 0 or self.board.is_cell_occupied((y_pos - 1, x_pos)):
                return True
        return False

    def calculate_ghost_mino(self) -> Optional[Mino]:
        """Return a ghost mino at the lowest possible position."""
        if self.current_mino is None:
            return None
        ghost: Mino = deepcopy(self.current_mino)
        block_positions = ghost.get_block_positions()

        # For each block, find how far it can drop
        max_drop = BOARD_HEIGHT
        for y, x in block_positions:
            drop = 0
            while y - drop > 0 and not self.board.is_cell_occupied((y - drop - 1, x)):
                drop += 1
            max_drop = min(max_drop, drop)

        # Move ghost down by max_drop
        ghost.position = (ghost.position[0] - max_drop, ghost.position[1])
        return ghost

    def check_keyinput_pressed(self, pressed_keys):
        """This will check the keyinput pressed."""
        if not pressed_keys & {"z", "Z", "ctrl"}:
            self.keyinput_cooldown.discard("left")
        if not pressed_keys & {"x", "X", "up"}:
            self.keyinput_cooldown.discard("right")

    def play_mode(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will play the mode."""
        if len(self.mino_list) <= 14:
            self.mino_generation()
        if self.current_mino is None:
            new_mino_type: str = self.mino_list.pop(0)
            self.current_mino = Mino(mino_type=new_mino_type, level=self.level)

        mino_touching_bottom: bool = self.mino_touching_bottom()

        if self.current_mino.fall_delay > 0:
            self.current_mino.fall_delay -= 1
        else:
            if not mino_touching_bottom:
                self.current_mino.move_down()
            self.current_mino.fall_delay = self.current_mino.reset_fall_delay(
                self.level
            )

        # Checks Pressed Keys
        if pressed_keys & {"z", "Z", "ctrl"} and "left" not in self.keyinput_cooldown:
            self.current_mino.rotate("left")
            self.keyinput_cooldown.add("left")
        elif pressed_keys & {"x", "X", "up"} and "right" not in self.keyinput_cooldown:
            self.current_mino.rotate("right")
            self.keyinput_cooldown.add("right")
        if pressed_keys & {"down"}:
            if not mino_touching_bottom:
                self.current_mino.soft_drop(self.level)

        if mino_touching_bottom:
            # if self.__current_position[0] < self.__lock_info["lock_height"]:
            if self.current_mino.position[0] < self.current_mino.lock_info["lock_height"]:
                self.current_mino.lock_info["lock_height"] = self.current_mino.position[0]
                self.current_mino.lock_info["lock_count"] = 15
            if pressed_keys and not pressed_keys & {"down", "space"}:
                self.current_mino.lock_info["lock_count"] -= 1
                self.current_mino.lock_info["lock_delay"] = int(0.5 * TARGET_FPS)
            else:
                if self.current_mino.lock_info["lock_delay"] > 0:
                    self.current_mino.lock_info["lock_delay"] -= 1
                else:
                    self.board.place_mino(
                        self.current_mino.type,
                        self.current_mino.orientation,
                        self.current_mino.position,
                    )

        self.check_keyinput_pressed(pressed_keys)

        stdscr = self.board.draw_minos_on_board(
            stdscr, self.offset, self.max_yx, self.current_mino
        )

        return stdscr

    def countdown_mode(self, stdscr: window) -> window:
        """This will handle the countdown mode."""
        if self.countdown >= 0:
            stdscr.addstr(
                self.max_yx[0] // 2,
                self.max_yx[1] // 2,
                str((self.countdown // TARGET_FPS) + 1),
                A_BOLD,
            )

        if self.countdown % TARGET_FPS == 0:
            if self.countdown > 0:
                self.sound_action["SFX"].append("3_2_1")

        self.countdown -= 1
        if self.countdown <= 0:
            self.mode = "play_music_wait"
            self.sound_action["SFX"].append("go")
            stdscr.addstr(self.max_yx[0] // 2, self.max_yx[1] // 2, "Go", A_BOLD)
            self.countdown = TARGET_FPS // 2

        return stdscr

    def increment_frame(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will increment the frame."""
        check_max_yx: tuple[int, int] = stdscr.getmaxyx()
        if check_max_yx != self.max_yx:
            self.max_yx = check_max_yx
            self.offset = (
                max(1, (self.max_yx[0] - DRAW_BOARD_HEIGHT) // 2),
                max(1, (self.max_yx[1] - DRAW_BOARD_WIDTH) // 2),
            )

        if check_max_yx[0] < MIN_Y or check_max_yx[1] < MIN_X:
            return stdscr

        stdscr = self.board.draw_blank_board(stdscr, self.offset)
        stdscr = self.board.draw_queue(
            stdscr,
            offset=self.offset,
            max_yx=self.max_yx,
            queue_list=self.mino_list[0:5],
        )

        if "esc" in pressed_keys:
            self.action = "Go_Back"
            return stdscr

        if self.mode == "countdown":
            stdscr = self.countdown_mode(stdscr)
            return stdscr

        stdscr = self.play_mode(stdscr, pressed_keys)

        if self.mode == "play_music_wait":
            self.countdown -= 1
            if self.countdown <= 0:
                self.mode = "play"
                self.sound_action["BGM"] = ["Korobeiniki"]
                return stdscr
            stdscr.addstr(
                self.max_yx[0] // 2,
                self.max_yx[1] // 2,
                "Go",
                A_BOLD,
            )

        return stdscr


if __name__ == "__main__":
    print("This is a module, please run starter.py.")
