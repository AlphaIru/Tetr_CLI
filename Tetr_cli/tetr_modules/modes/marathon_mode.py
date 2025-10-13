"""This will handle the solo game mode."""

# coding: utf-8

from copy import deepcopy
from curses import window, A_BOLD, color_pair
from math import pow
from random import shuffle, seed, randint

# from math import floor

# TODO: Flowchart:
# DONE: Generation 0phase
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
MINO_ROTATIONS: list[str] = ["N", "E", "S", "W"]
MINO_DRAW_DATA: dict[str, tuple[list[str], int]] = {
    "O": (["████    ", "████    "], 1),
    "I": (["████████", "        "], 2),
    "T": (["██████  ", "  ██    "], 3),
    "L": (["    ██  ", "██████  "], 4),
    "J": (["██      ", "██████  "], 5),
    "S": (["  ████  ", "████    "], 6),
    "Z": (["████    ", "  ████  "], 7),
}

# Mino Draw Location: Mino_type -> Rotation (in NSEW) ->
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


class ModeClass:
    """This will handle the solo game mode."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.__action: str = ""
        self.__countdown: int = TARGET_FPS * 3  # 3 seconds countdown

        self.__seed_value: int = 0
        self.__sound_action: dict[str, list[str]] = {"BGM": ["stop"], "SFX": []}
        self.__mode: str = "countdown"

        # self.__board: list[list[int]] = self.generate_test_board()
        self.__board: list[list[int]] = [
            ([0] * BOARD_WIDTH) for _ in range(BOARD_HEIGHT)
        ]
        self.__max_y: int = 0
        self.__max_x: int = 0
        self.__offset_x: int = 0
        self.__offset_y: int = 0

        self.__current_mino: str = ""
        self.__current_rotation: str = "N"
        self.__current_position: tuple[int, int] = (0, 0)  # (y, x)
        self.__current_hold: str = ""
        self.__keyinput_cooldown: set[str] = set()
        self.__lock_delay: int = 0
        self.__fall_delay: int = self.get_fall_delay(1)
        self.__level: int = 1

        self.__mino_list: list[str] = []
        self.mino_generation(initial=True)

    def generate_test_board(self) -> list[list[int]]:
        """This will generate a test board."""
        test_board: list[list[int]] = [([0] * BOARD_WIDTH) for _ in range(BOARD_HEIGHT)]
        for row in range(BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                if row < 5 and col % 2 == 0:
                    test_board[row][col] = 8
        return test_board

    def pop_action(self) -> str:
        """This will return the action and reset it."""
        action: str = deepcopy(self.__action)
        self.__action = ""
        return action

    def pop_sound_action(self) -> dict[str, list[str]]:
        """This will return the sound action and reset it."""
        sound_action: dict[str, list[str]] = deepcopy(self.__sound_action)
        self.__sound_action["SFX"] = []
        return sound_action

    def draw_mino(self, stdscr: window, mino: str, y_loc: int, x_loc: int) -> None:
        """Draw a mino at the given position."""
        if mino in MINO_DRAW_DATA:
            lines, color = MINO_DRAW_DATA[mino]
            for line_num, line in enumerate(lines):
                stdscr.addstr(y_loc + line_num, x_loc, line, color_pair(color))

    def draw_hold(self, stdscr: window) -> window:
        """Draw the Hold Box."""
        horizontal_length: int = 12
        vertical_length: int = 4
        hold_offset_x: int = self.__offset_x - horizontal_length - 3
        horizontal_line: str = "+" + "-" * horizontal_length

        stdscr.addstr(
            self.__offset_y - 1,
            hold_offset_x,
            horizontal_line,
            A_BOLD,
        )
        stdscr.addstr(
            self.__offset_y,
            hold_offset_x + 2,
            "Hold",
            A_BOLD,
        )
        stdscr.addstr(
            self.__offset_y + 1,
            hold_offset_x,
            horizontal_line,
            A_BOLD,
        )
        for counter in range(4):
            stdscr.addstr(
                self.__offset_y + counter,
                hold_offset_x,
                "|",
                A_BOLD,
            )
        stdscr.addstr(
            self.__offset_y + vertical_length,
            hold_offset_x,
            horizontal_line,
            A_BOLD,
        )

        if self.__current_hold:
            self.draw_mino(
                stdscr, self.__current_hold, self.__offset_y + 2, hold_offset_x + 2
            )
        return stdscr

    def draw_queue(self, stdscr: window) -> window:
        """Draw the Next Queue Box."""

        queue_offset_x: int = self.__offset_x + DRAW_BOARD_WIDTH + 1
        horizontal_length: int = 12
        horizontal_line: str = "-" * horizontal_length + "+"
        vertical_length: int = 17

        # Draw the box and text
        stdscr.addstr(
            self.__offset_y - 1,
            queue_offset_x,
            horizontal_line,
            A_BOLD,
        )
        stdscr.addstr(
            self.__offset_y,
            queue_offset_x + 2,
            "Next",
            A_BOLD,
        )
        stdscr.addstr(
            self.__offset_y + 1,
            queue_offset_x,
            horizontal_line,
            A_BOLD,
        )
        for counter in range(vertical_length):
            stdscr.addstr(
                self.__offset_y + counter,
                queue_offset_x + horizontal_length,
                "|",
                A_BOLD,
            )
        stdscr.addstr(
            self.__offset_y + vertical_length,
            queue_offset_x,
            horizontal_line,
            A_BOLD,
        )

        # Draw the next minos
        # O, I, T, L, J, S, Z
        for queue_counter in range(5):
            if len(self.__mino_list) > queue_counter:
                self.draw_mino(
                    stdscr,
                    self.__mino_list[queue_counter],
                    self.__offset_y + 2 + queue_counter * 3,
                    queue_offset_x + 2,
                )
        return stdscr

    def draw_board(self, stdscr: window) -> window:
        """Draw the Game board centered on the screen."""

        # Draw top border
        stdscr.addstr(
            self.__offset_y - 1,
            self.__offset_x - 1,
            "+" + "- " * (DRAW_BOARD_WIDTH // 2) + "+",
        )

        middle_line: str = "|" + " " * DRAW_BOARD_WIDTH + "|"
        for row in range(DRAW_BOARD_HEIGHT):
            stdscr.addstr(
                self.__offset_y + row,
                self.__offset_x - 1,
                middle_line,
                A_BOLD,
            )

        # Draw bottom border
        stdscr.addstr(
            self.__offset_y + DRAW_BOARD_HEIGHT,
            self.__offset_x - 1,
            "+" + "-" * DRAW_BOARD_WIDTH + "+",
            A_BOLD,
        )

        return stdscr

    def get_fall_delay(self, level: int) -> int:
        """This will return the fall delay in frame per second based on the level."""
        seconds: float = pow((0.8 - ((level - 1) * 0.007)), (level - 1))
        return max(0, int(seconds * TARGET_FPS))

    def rotate_mino(self, direction: str) -> None:
        """This will rotate the current mino."""
        if direction not in ["left", "right"]:
            return
        if not self.__current_mino:
            return

        current_index: int = MINO_ROTATIONS.index(self.__current_rotation)
        new_index: int = 0
        if direction == "right":
            new_index = (current_index + 1) % len(MINO_ROTATIONS)
        elif direction == "left":
            new_index = (current_index - 1) % len(MINO_ROTATIONS)
        self.__current_rotation = MINO_ROTATIONS[new_index]

    def is_mino_touching_bottom(self) -> bool:
        """Return True if the current mino is touching the ground or a placed block below."""
        if (
            self.__current_mino in MINO_DRAW_LOCATION
            and self.__current_rotation in MINO_DRAW_LOCATION[self.__current_mino]
        ):
            for y_offset, x_offset in MINO_DRAW_LOCATION[self.__current_mino][self.__current_rotation]:
                y_pos = self.__current_position[0] + y_offset
                x_pos = self.__current_position[1] + x_offset
                if (
                    y_pos == 0
                    or self.__board[y_pos - 1][x_pos] != 0
                ):
                    return True
        return False

    def draw_mino_on_board(self, stdscr: window) -> window:
        """This will draw the current mino on the board."""

        # 1: DONE: calculate the current mino's blocks positions
        # 2: DONE: calculate the offset and rotation
        # 3: calculate its ghost position
        # 4: DONE: add that to the list of blocks to draw
        # 5: DONE: draw the blocks

        draw_board: list[list[int]] = deepcopy(self.__board)

        if (
            self.__current_mino in MINO_DRAW_LOCATION
            and self.__current_rotation in MINO_DRAW_LOCATION[self.__current_mino]
        ):
            for y_offset, x_offset in MINO_DRAW_LOCATION[self.__current_mino][
                self.__current_rotation
            ]:
                y_pos: int = self.__current_position[0] + y_offset
                x_pos: int = self.__current_position[1] + x_offset
                if 0 <= y_pos < BOARD_HEIGHT and 0 <= x_pos < BOARD_WIDTH:
                    draw_board[y_pos][x_pos] = MINO_COLOR[self.__current_mino]

        max_rows: int = min(self.__max_y, BOARD_HEIGHT)
        adjusted_height: int = max_rows - DRAW_BOARD_HEIGHT
        visible_rows = draw_board[0:max_rows]

        for y_counter, row in enumerate(visible_rows):
            # y_counter=0 is bottom, y_counter=20 is top of box
            for x_counter, cell in enumerate(row):
                char: str = "██" if cell else ("  " if y_counter != 20 else "- ")
                y: int = self.__offset_y + (max_rows - 1 - y_counter) - adjusted_height
                x: int = self.__offset_x + x_counter * 2
                if 0 <= y < self.__max_y and 0 <= x < self.__max_x - 1:
                    stdscr.addstr(
                        y,
                        x,
                        char,
                        color_pair(cell) if cell else A_BOLD,
                    )

        return stdscr

    def countdown_mode(self, stdscr: window) -> None:
        """This will handle the countdown mode."""
        if self.__countdown >= 0:
            stdscr.addstr(
                self.__max_y // 2,
                self.__max_x // 2,
                str((self.__countdown // TARGET_FPS) + 1),
                A_BOLD,
            )

        if self.__countdown % TARGET_FPS == 0:
            if self.__countdown > 0:
                self.__sound_action["SFX"].append("3_2_1")

        self.__countdown -= 1
        if self.__countdown <= 0:
            self.__mode = "play_music_wait"
            self.__sound_action["SFX"].append("go")
            stdscr.addstr(self.__max_y // 2, self.__max_x // 2, "Go", A_BOLD)
            self.__countdown = TARGET_FPS // 2

    def mino_generation(self, initial: bool = False) -> None:
        """This will handle the mino generation."""
        if initial:
            self.__seed_value = 42  # randint(1, 1000000000)
            seed(self.__seed_value)
            while len(self.__mino_list) <= 14:
                new_mino_list = list(MINO_TYPES)
                shuffle(new_mino_list)
                self.__mino_list.extend(new_mino_list)
        new_mino_list = list(MINO_TYPES)
        shuffle(new_mino_list)
        self.__mino_list.extend(new_mino_list)

    def check_keyinput_pressed(self, pressed_keys: set[str]) -> None:
        """This will reset the keyinput cooldown."""
        if not pressed_keys & {"z", "Z", "ctrl"}:
            self.__keyinput_cooldown.discard("left")
        if not pressed_keys & {"x", "X", "up"}:
            self.__keyinput_cooldown.discard("right")

    def play_mode(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will handle the play mode."""
        if len(self.__mino_list) <= 14:
            self.mino_generation()
        if not self.__current_mino:
            self.__current_mino = self.__mino_list.pop(0)
            self.__current_rotation = "N"
            self.__current_position = (21, BOARD_WIDTH // 2 - 1)  # 21 is 20 + 1
            self.__fall_delay = self.get_fall_delay(self.__level)

        if self.__fall_delay > 0:
            self.__fall_delay -= 1
        else:
            if self.__current_position[0] < (BOARD_HEIGHT - 1):
                self.__current_position = (
                    self.__current_position[0] - 1,
                    self.__current_position[1],
                )
            self.__fall_delay = self.get_fall_delay(self.__level)

        if (
            pressed_keys & {"z", "Z", "ctrl"}
            and "left" not in self.__keyinput_cooldown
        ):
            self.rotate_mino("left")
            self.__keyinput_cooldown.add("left")
        elif (
            pressed_keys & {"x", "X", "up"}
            and "right" not in self.__keyinput_cooldown
        ):
            self.rotate_mino("right")
            self.__keyinput_cooldown.add("right")

        self.check_keyinput_pressed(pressed_keys)

        # Check if the mino is touching at the bottom or another block
        if self.__current_position:

        stdscr = self.draw_mino_on_board(stdscr)
        return stdscr

    def increment_frame(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will progress the game based on the inputs."""

        check_max_y, check_max_x = stdscr.getmaxyx()

        if check_max_y != self.__max_y or check_max_x != self.__max_x:
            self.__max_y = check_max_y
            self.__max_x = check_max_x
            self.__offset_y = (check_max_y - DRAW_BOARD_HEIGHT) // 2
            self.__offset_x = (check_max_x - DRAW_BOARD_WIDTH) // 2

        if check_max_x < MIN_X or check_max_y < MIN_Y:
            return stdscr

        stdscr = self.draw_board(stdscr)
        stdscr = self.draw_queue(stdscr)
        stdscr = self.draw_hold(stdscr)

        if "esc" in pressed_keys:
            self.__action = "Go_Back"
            return stdscr

        if self.__mode == "countdown":
            self.countdown_mode(stdscr)
            return stdscr

        stdscr = self.play_mode(stdscr, pressed_keys)

        if self.__mode == "play_music_wait":
            self.__countdown -= 1
            if self.__countdown <= 0:
                self.__mode = "play"
                self.__sound_action["BGM"] = ["Korobeiniki"]
                return stdscr
            stdscr.addstr(
                self.__max_y // 2,
                self.__max_x // 2,
                "Go",
                A_BOLD,
            )

        return stdscr


if __name__ == "__main__":
    print("This is a module, please run starter.py.")
