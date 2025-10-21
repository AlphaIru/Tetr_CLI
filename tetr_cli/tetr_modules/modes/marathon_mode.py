"""This will handle the solo game mode."""

# coding: utf-8

from curses import window, A_BOLD
from typing import Optional, List, Set, Tuple

from tetr_cli.tetr_modules.solo_core.base import SoloBaseMode
from tetr_cli.tetr_modules.solo_core.mino import Mino
from tetr_cli.tetr_modules.modules.constants import (
    MIN_X,
    MIN_Y,
    DRAW_BOARD_HEIGHT,
    DRAW_BOARD_WIDTH,
    TARGET_FPS,
)


class ModeClass(SoloBaseMode):
    """This will handle the solo game mode."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__()
        # For countdown: 3 seconds countdown
        # For animation: 0.5 second animation
        self.mino_list_generator(initial=True)
        self.counter: int = TARGET_FPS * 3  # Formally countdown
        self.mode: str = "countdown"

    def show_stats(self, stdscr: window) -> window:
        """This will show the stats on bottom right."""
        # Note: DRAW_BOARD_HEIGHT is the border height
        # so we minus 2 to get the inner height
        stdscr.addstr(
            self.offset[0] + DRAW_BOARD_HEIGHT - 2,
            self.offset[1] + DRAW_BOARD_WIDTH + 2,
            f"Level: {self.level}",
        )
        stdscr.addstr(
            self.offset[0] + DRAW_BOARD_HEIGHT - 1,
            self.offset[1] + DRAW_BOARD_WIDTH + 2,
            f"Lines: {self.lines_cleared}",
        )
        stdscr.addstr(
            self.offset[0] + DRAW_BOARD_HEIGHT,
            self.offset[1] + DRAW_BOARD_WIDTH + 2,
            f"Score: {self.score}",
        )
        # Debug info
        # stdscr.addstr(
        #     self.offset[0] + DRAW_BOARD_HEIGHT + 1,
        #     self.offset[1] + DRAW_BOARD_WIDTH + 2,
        #     f"Fall delay: {self.current_mino.fall_delay if self.current_mino else '0'}",
        # )
        return stdscr

    def play_mode(self, stdscr: window, pressed_keys: Set[str]) -> window:
        """This will play the mode."""
        if len(self.mino_list) <= 14:
            self.mino_list_generator()
        if not self.current_mino:
            new_mino_type: str = self.mino_list.pop(0)
            self.current_mino = Mino(mino_type=new_mino_type, level=self.level)

        self.check_keyinput_pressed(pressed_keys=pressed_keys)
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
                self.calculate_score()
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
        elif not self.mino_touching_bottom(self.current_mino) and not (
            pressed_keys & {"down", "space"}
        ):
            self.current_mino.move_down(is_position_valid=self.is_position_valid)
            self.current_mino.fall_delay = self.current_mino.reset_fall_delay(
                self.level
            )

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
        if self.counter >= 0:
            stdscr.addstr(
                self.max_yx[0] // 2,
                self.max_yx[1] // 2,
                str((self.counter // TARGET_FPS) + 1),
                A_BOLD,
            )

        if self.counter % TARGET_FPS == 0:
            if self.counter > 0:
                self.sound_action["SFX"].append("countdown")

        self.counter -= 1
        if self.counter <= 0:
            self.mode = "play_music_wait"
            self.sound_action["SFX"].append("go")
            stdscr.addstr(self.max_yx[0] // 2, self.max_yx[1] // 2, "Go", A_BOLD)
            self.counter = TARGET_FPS // 2

        return stdscr

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> window:
        """This will increment the frame."""
        check_max_yx: Tuple[int, int] = stdscr.getmaxyx()
        if check_max_yx != self.max_yx:
            self.max_yx = check_max_yx
            self.offset = (
                max(1, (self.max_yx[0] - DRAW_BOARD_HEIGHT) // 2),
                max(1, (self.max_yx[1] - DRAW_BOARD_WIDTH) // 2),
            )
            self.invalidate_draw_cache()

        if check_max_yx[0] < MIN_Y or check_max_yx[1] < MIN_X:
            return stdscr

        queue_to_draw: List[str] = self.mino_list[0:5]
        hold_to_draw: Optional[str] = (
            self.current_hold.type if self.current_hold else None
        )

        stdscr = self.board.draw_blank_board(stdscr, self.offset)
        stdscr = self.show_stats(stdscr)

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

        if {"r", "R"} & pressed_keys:
            self.action = "Marathon"
            self.sound_action["SFX"].append("select_confirm")
            return stdscr
        if "esc" in pressed_keys:
            self.action = "Solo_Menu"
            self.sound_action["SFX"].append("select_back")
            return stdscr

        if self.mode == "countdown":
            stdscr = self.countdown_mode(stdscr)
            return stdscr

        stdscr = self.play_mode(stdscr, pressed_keys)

        if self.mode == "play_music_wait":
            self.counter -= 1
            if self.counter <= 0:
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
