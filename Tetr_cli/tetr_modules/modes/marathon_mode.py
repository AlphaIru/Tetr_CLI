"""This will handle the solo game mode."""

# coding: utf-8

from copy import copy, deepcopy
from curses import window, A_BOLD
from typing import Optional
from random import shuffle, seed, randint

from Tetr_cli.tetr_modules.modes.common.board import Board
from Tetr_cli.tetr_modules.modes.common.mino import Mino
from Tetr_cli.tetr_modules.modes.common.constants import (
    BOARD_WIDTH,
    BOARD_HEIGHT,
    DRAW_BOARD_WIDTH,
    DRAW_BOARD_HEIGHT,
    MINO_TYPES,
    MIN_X,
    MIN_Y,
    TARGET_FPS,
)

# Flowchart:
# DONE: Generation phase
# Falling phase
# DONE: if Hard drop:
#   go to pattern phase.
# DONE: Lock phase:
# DONE: if moved:
#   DONE: if there is space to fall:
#       go to falling phase.
#   DONE: else:
#       DONE: if lock delay is up:
#       DONE:    go to lock phase.
#       DONE: else:
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

        self.current_hold: Optional[Mino] = None
        self.hold_used: bool = False

        self.keyinput_cooldown: set[str] = set()
        self.lines_cleared: int = 0
        self.score: int = 0
        self.level: int = 1

        self.mino_list: list[str] = []
        self.mino_generation(initial=True)

        # Optimization for drawing
        self._last_drawn_queue: list[str] = []
        self._last_drawn_hold: Optional[str] = "_init"  # Force initial draw

        # Optimization for collision detection
        self._last_bottom_check: tuple[list[tuple[int, int]], str, str] = ([], "", "")
        self._last_bottom_result: bool = False
        self._last_side_check: tuple[tuple[int, int], str, str, str] = (
            (-1, -1),
            "",
            "",
            "",
        )
        self._last_side_result: bool = False
        self._last_ghost_check: tuple[tuple[int, int], str, str] = ((-1, -1), "", "")
        self._last_ghost_result: tuple[int, int] = (-1, -1)

    def pop_action(self) -> str:
        """This will return the action and reset it."""
        action: str = copy(self.action)
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

    def reset_mino(
        self, current_mino_check: bool = False, hold_used_check: bool = False
    ) -> None:
        """This will reset for to spawn the next mino."""
        self.current_mino = None if not current_mino_check else self.current_mino
        self.hold_used = hold_used_check
        self._last_bottom_check = ([], "", "")
        self._last_bottom_result = False
        self._last_side_check = ((-1, -1), "", "", "")
        self._last_side_result = False
        self._last_ghost_check = ((-1, -1), "", "")
        self._last_ghost_result = (-1, -1)

    def mino_touching_bottom(
        self,
        mino: Optional[Mino],
    ) -> bool:
        """Return True if the current mino is touching the ground or a placed block below."""
        if mino is None:
            return False
        positions: list[tuple[int, int]] = mino.get_block_positions()
        key: tuple[list[tuple[int, int]], str, str] = (
            positions,
            mino.orientation,
            mino.type,
        )
        if key == self._last_bottom_check:
            return self._last_bottom_result
        for y_pos, x_pos in positions:
            if y_pos == 0 or self.board.is_cell_occupied((y_pos - 1, x_pos)):
                self._last_bottom_check = key
                self._last_bottom_result = True
                return True
        self._last_bottom_check = key
        self._last_bottom_result = False
        return False

    def mino_touching_side(
        self,
        direction: str,
        mino: Optional[Mino] = None,
    ) -> bool:
        """Return True if the current mino is touching the side wall or a placed block beside."""
        if mino is None:
            return False
        positions: list[tuple[int, int]] = mino.get_block_positions()
        key: tuple[tuple[int, int], str, str, str] = (
            mino.position,
            mino.orientation,
            mino.type,
            direction,
        )
        if key == self._last_side_check:
            return self._last_side_result
        if direction == "left":
            for y_pos, x_pos in positions:
                if x_pos == 0 or self.board.is_cell_occupied((y_pos, x_pos - 1)):
                    self._last_side_check = key
                    self._last_side_result = True
                    return True
        elif direction == "right":
            for y_pos, x_pos in positions:
                if x_pos == BOARD_WIDTH - 1 or self.board.is_cell_occupied(
                    (y_pos, x_pos + 1)
                ):
                    self._last_side_check = key
                    self._last_side_result = True
                    return True
        return False

    def is_position_valid(
        self,
        block_positions: list[tuple[int, int]],
    ) -> bool:
        """This will check if the position is valid."""
        if any(
            x_pos < 0 or x_pos >= BOARD_WIDTH or
            y_pos < 0 or y_pos >= BOARD_HEIGHT or
            self.board.is_cell_occupied((y_pos, x_pos))
            for y_pos, x_pos in block_positions
        ):
            return False
        return True

    def ghost_mino_position(
        self,
        current_mino: Mino,
    ) -> tuple[int, int]:
        """This will return the ghost mino position."""
        key: tuple[tuple[int, int], str, str] = (
            current_mino.position,
            current_mino.orientation,
            current_mino.type,
        )
        if key == self._last_ghost_check and self._last_ghost_result is not None:
            return self._last_ghost_result
        # Otherwise, calculate as usual
        ghost_mino: Mino = copy(current_mino)
        while not self.mino_touching_bottom(ghost_mino):
            ghost_mino.position = (ghost_mino.position[0] - 1, ghost_mino.position[1])
        result: tuple[int, int] = ghost_mino.position
        self._last_ghost_check = key
        self._last_ghost_result = result
        return result

    def check_keyinput_pressed(self, pressed_keys):
        """This will check the keyinput pressed."""

        if self.current_mino:
            if (
                pressed_keys & {"z", "Z", "ctrl"}
                and "ccw" not in self.keyinput_cooldown
            ):
                self.current_mino.rotate("left", self.is_position_valid)
                self.keyinput_cooldown.add("ccw")
            if pressed_keys & {"x", "X", "up"} and "cw" not in self.keyinput_cooldown:
                self.current_mino.rotate("right", self.is_position_valid)
                self.keyinput_cooldown.add("cw")
            if pressed_keys & {"left", "right"}:
                self.current_mino.handle_sideways_auto_repeat(
                    pressed_keys, self.mino_touching_side
                )
            if pressed_keys & {"down"}:
                if not self.mino_touching_bottom(self.current_mino):
                    self.current_mino.soft_drop(self.level, self.is_position_valid)
                    self.current_mino.lock_info["lock_delay"] = int(0.5 * TARGET_FPS)
            if pressed_keys & {"space"} and "space" not in self.keyinput_cooldown:
                self.current_mino.hard_drop(
                    mino_touching_bottom_func=self.mino_touching_bottom,
                    is_position_valid=self.is_position_valid
                )
                self.board.place_mino(
                    self.current_mino.type,
                    self.current_mino.orientation,
                    self.current_mino.position,
                )
                self.reset_mino()
                self.keyinput_cooldown.add("space")
            if (
                pressed_keys & {"c", "C", "shift"}
                and {"space"} not in pressed_keys
                and not self.hold_used
            ):
                if self.current_hold:
                    temp: Mino = copy(self.current_hold)  # type: ignore
                    self.current_hold = copy(self.current_mino)
                    self.current_mino = temp
                    self.current_mino.position = (21, BOARD_WIDTH // 2 - 1)
                    self.current_mino.orientation = "N"
                    self.current_mino.fall_delay = self.current_mino.reset_fall_delay(
                        self.level
                    )
                    self.current_mino.lock_info = {
                        "lock_delay": int(0.5 * TARGET_FPS),
                        "lock_count": 15,
                        "lock_height": 21,
                    }
                    self.reset_mino(current_mino_check=True, hold_used_check=True)
                else:
                    self.current_hold = copy(self.current_mino)
                    self.reset_mino(hold_used_check=True)
                    self.keyinput_cooldown.add("hold")
        if not pressed_keys & {"z", "Z", "ctrl"}:
            self.keyinput_cooldown.discard("ccw")
        if not pressed_keys & {"x", "X", "up"}:
            self.keyinput_cooldown.discard("cw")
        if not pressed_keys & {"space"}:
            self.keyinput_cooldown.discard("space")

    def play_mode(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will play the mode."""
        if len(self.mino_list) <= 14:
            self.mino_generation()
        if not self.current_mino:
            new_mino_type: str = self.mino_list.pop(0)
            self.current_mino = Mino(mino_type=new_mino_type, level=self.level)

        self.check_keyinput_pressed(pressed_keys)
        if not self.current_mino:
            stdscr = self.board.draw_minos_on_board(
                stdscr=stdscr,
                offset=self.offset,
                max_yx=self.max_yx,
                current_mino=self.current_mino,
                ghost_position=(-1, -1),  # Placeholder value
            )
            return stdscr

        if self.mino_touching_bottom(self.current_mino):
            # print(self.current_mino.type, self.current_mino.lock_info)
            if (
                self.current_mino.position[0]
                < self.current_mino.lock_info["lock_height"]
            ):
                self.current_mino.lock_info["lock_height"] = self.current_mino.position[
                    0
                ]
                self.current_mino.lock_info["lock_count"] = 15
            elif (
                pressed_keys
                and not pressed_keys & {"down", "space"}
                and self.current_mino.lock_info["lock_count"] > 0
            ):
                self.current_mino.lock_info["lock_count"] -= 1
                self.current_mino.lock_info["lock_delay"] = int(0.5 * TARGET_FPS)
            elif self.current_mino.lock_info["lock_delay"] > 0:
                self.current_mino.lock_info["lock_delay"] -= 1
            else:
                self.board.place_mino(
                    self.current_mino.type,
                    self.current_mino.orientation,
                    self.current_mino.position,
                )
                self.reset_mino()

        if not self.current_mino:
            stdscr = self.board.draw_minos_on_board(
                stdscr=stdscr,
                offset=self.offset,
                max_yx=self.max_yx,
                current_mino=self.current_mino,
                ghost_position=(-1, -1),  # Placeholder value
            )
            return stdscr

        if self.current_mino.fall_delay > 0:
            self.current_mino.fall_delay -= 1
        elif (
            not self.mino_touching_bottom(self.current_mino)
            and not pressed_keys
        ):
            self.current_mino.move_down(is_position_valid=self.is_position_valid)
            self.current_mino.fall_delay = self.current_mino.reset_fall_delay(
                self.level
            )

        lines_cleared = self.board.check_line_filled()
        if lines_cleared > 0:
            self.score +=

        self.board.clear_lines()

        stdscr = self.board.draw_minos_on_board(
            stdscr=stdscr,
            offset=self.offset,
            max_yx=self.max_yx,
            current_mino=self.current_mino,
            ghost_position=self.ghost_mino_position(self.current_mino),
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

        queue_to_draw: list[str] = self.mino_list[0:5]
        hold_to_draw: Optional[str] = (
            self.current_hold.type if self.current_hold else None
        )

        stdscr = self.board.draw_blank_board(stdscr, self.offset)
        if queue_to_draw != self._last_drawn_queue:
            stdscr = self.board.draw_queue(
                stdscr,
                offset=self.offset,
                max_yx=self.max_yx,
                queue_list=self.mino_list[0:5],
            )
            self._last_drawn_queue = queue_to_draw.copy()

        if hold_to_draw != self._last_drawn_hold:
            stdscr = self.board.draw_hold(
                stdscr,
                offset=self.offset,
                max_yx=self.max_yx,
                hold_used=self.hold_used,
                hold_mino=self.current_hold,
            )
            self._last_drawn_hold = hold_to_draw

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
