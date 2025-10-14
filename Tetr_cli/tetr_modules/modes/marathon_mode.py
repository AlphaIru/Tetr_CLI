"""This will handle the solo game mode."""

# coding: utf-8

from copy import copy, deepcopy
from curses import window, A_BOLD
from typing import Optional
from random import shuffle, seed, randint

from tetr_modules.modes.board import Board
from tetr_modules.modes.mino import Mino
from tetr_modules.modes.constants import (
    BOARD_WIDTH,
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

    def reset_mino(self) -> None:
        """This will reset for to spawn the next mino."""
        self.current_mino = None
        self.hold_used = False

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

    def mino_touching_side(
        self,
        direction: str,
        mino: Optional[Mino] = None,
    ) -> bool:
        """Return True if the current mino is touching the side wall or a placed block beside."""
        if mino is None:
            mino = self.current_mino
        if direction == "left":
            for y_pos, x_pos in mino.get_block_positions():  # type: ignore
                if x_pos == 0 or self.board.is_cell_occupied((y_pos, x_pos - 1)):
                    return True
        elif direction == "right":
            for y_pos, x_pos in mino.get_block_positions():  # type: ignore
                if x_pos == BOARD_WIDTH - 1 or self.board.is_cell_occupied(
                    (y_pos, x_pos + 1)
                ):
                    return True
        return False

    def check_keyinput_pressed(
        self,
        pressed_keys,
        mino_touching_bottom: bool,
    ):
        """This will check the keyinput pressed."""

        if self.current_mino:
            if (
                pressed_keys & {"z", "Z", "ctrl"}
                and "ccw" not in self.keyinput_cooldown
            ):
                self.current_mino.rotate("left")
                self.keyinput_cooldown.add("ccw")
            if pressed_keys & {"x", "X", "up"} and "cw" not in self.keyinput_cooldown:
                self.current_mino.rotate("right")
                self.keyinput_cooldown.add("cw")
            if pressed_keys & {"left", "right"}:
                self.current_mino.handle_sideways_auto_repeat(
                    pressed_keys, self.mino_touching_side
                )
            if pressed_keys & {"down"}:
                if not mino_touching_bottom:
                    self.current_mino.soft_drop(self.level)
                    self.current_mino.lock_info["lock_delay"] = int(0.5 * TARGET_FPS)
            if pressed_keys & {"space"} and "space" not in self.keyinput_cooldown:
                self.current_mino.hard_drop(self.mino_touching_bottom)
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
                    temp: Mino = copy(self.current_hold)
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
                    self.hold_used = True
                else:
                    self.current_hold = copy(self.current_mino)
                    self.current_mino = None
                    self.hold_used = True
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

        mino_touching_bottom: bool = self.mino_touching_bottom()

        self.check_keyinput_pressed(pressed_keys, mino_touching_bottom)
        if not self.current_mino:
            stdscr = self.board.draw_minos_on_board(
                stdscr=stdscr,
                offset=self.offset,
                max_yx=self.max_yx,
                current_mino=self.current_mino,
            )
            return stdscr

        if mino_touching_bottom:
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
            )
            return stdscr

        if self.current_mino.fall_delay > 0:
            self.current_mino.fall_delay -= 1
        else:
            if not mino_touching_bottom and (
                not pressed_keys & {"down", "space"}
                or not pressed_keys & {"c", "C", "shift"}
                and self.hold_used
            ):
                self.current_mino.move_down()
            self.current_mino.fall_delay = self.current_mino.reset_fall_delay(
                self.level
            )

        stdscr = self.board.draw_minos_on_board(
            stdscr=stdscr,
            offset=self.offset,
            max_yx=self.max_yx,
            current_mino=self.current_mino,
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
        stdscr = self.board.draw_hold(
            stdscr,
            offset=self.offset,
            max_yx=self.max_yx,
            hold_used=self.hold_used,
            hold_mino=self.current_hold,
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
