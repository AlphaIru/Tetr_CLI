"""This holds the base attributes and methods for all modes."""
# coding: utf-8

from copy import copy
from random import shuffle, seed, randint
from typing import Optional, Set, List, Tuple

from tetr_cli.tetr_modules.modules.base_mode import BaseModeClass
from tetr_cli.tetr_modules.modules.constants import (
    BOARD_WIDTH,
    BOARD_HEIGHT,
    MINO_TYPES,
    TARGET_FPS,
)
from tetr_cli.tetr_modules.solo_core.board import Board
from tetr_cli.tetr_modules.solo_core.mino import Mino
from tetr_cli.tetr_modules.modules.score import (
    calculate_drop_score,
    calculate_line_score,
)


class SoloBaseMode(BaseModeClass):
    """This is the base class for all modes."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__()

        # Game stats
        self.level: int = 1
        self.back_to_back: bool = False
        self.combo_count: int = 0
        self.lines_cleared: int = 0
        self.score: int = 0

        # Board
        self.board: Board = Board()

        # Mino
        self.current_mino: Optional[Mino] = None
        self.ghost_mino: Optional[Mino] = None

        # Queue
        self.mino_list: List[str] = []
        self.__seed_value: int = 0

        # Hold
        self.current_hold: Optional[Mino] = None
        self.hold_used: bool = False

        # User inputs
        self.keyinput_cooldown: Set[str] = set()

        # Optimizations for drawing
        self._last_drawn_queue: List[str] = []
        self._last_drawn_hold: Optional[str] = "_init"

        # Optimizations for collision checks
        self._last_bottom_check: Tuple[List[Tuple[int, int]], str, str] = ([], "", "")
        self._last_bottom_result: bool = False
        self._last_side_check: Tuple[Tuple[int, int], str, str, str] = (
            (-1, -1),
            "",
            "",
            "",
        )
        self._last_side_result: bool = False
        self._last_ghost_check: Tuple[Tuple[int, int], str, str] = ((-1, -1), "", "")
        self._last_ghost_result: Tuple[int, int] = (-1, -1)

        # Actions
        self.offset: Tuple[int, int] = (0, 0)  # (offset_y, offset_x)
        self.max_yx: Tuple[int, int] = (0, 0)  # (max_y, max_x)

    def mino_list_generator(self, initial: bool = False, input_seed: int = 0) -> None:
        """This will generate the next mino."""
        new_mino_list: List[str] = []
        if initial:
            if self.__seed_value == 0:
                self.__seed_value = (
                    randint(1, 1000000000) if input_seed == 0 else input_seed
                )
            seed(self.__seed_value)
            while len(self.mino_list) <= 14:
                new_mino_list = list(MINO_TYPES)
                shuffle(new_mino_list)
                self.mino_list.extend(new_mino_list)
        new_mino_list = list(MINO_TYPES)
        shuffle(new_mino_list)
        self.mino_list.extend(new_mino_list)
        self.__seed_value += 17  # Increase seed for next shuffle

    def invalidate_draw_cache(self) -> None:
        """This will invalidate the draw cache."""
        self._last_drawn_queue = []
        self._last_drawn_hold = "_init"

    def reset_mino(
        self, current_mino_check: bool = False, hold_used_check: bool = False
    ) -> None:
        """This will reset the current mino."""
        self.current_mino = None if not current_mino_check else self.current_mino
        if self.current_mino:
            self.current_mino.kick_number = 0
        self.hold_used = hold_used_check
        if not hold_used_check:
            self._last_drawn_hold = "_init"
        self._last_bottom_check = ([], "", "")
        self._last_bottom_result = False
        self._last_side_check = ((-1, -1), "", "", "")
        self._last_side_result = False
        self._last_ghost_check = ((-1, -1), "", "")
        self._last_ghost_result = (-1, -1)

    def mino_touching_bottom(
        self,
        mino: Optional[Mino] = None,
    ) -> bool:
        """This will check if the current mino is touching the bottom."""
        if mino is None:
            return False
        positions: List[Tuple[int, int]] = mino.get_block_positions()
        key: Tuple[List[Tuple[int, int]], str, str] = (
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
        """This will check if the current mino is touching the side."""
        if mino is None:
            return False
        positions: List[Tuple[int, int]] = mino.get_block_positions()
        key: Tuple[Tuple[int, int], str, str, str] = (
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
        block_positions: List[Tuple[int, int]],
    ) -> bool:
        """This will check if the position is valid."""
        if any(
            x_pos < 0
            or x_pos >= BOARD_WIDTH
            or y_pos < 0
            or y_pos >= BOARD_HEIGHT
            or self.board.is_cell_occupied((y_pos, x_pos))
            for y_pos, x_pos in block_positions
        ):
            return False
        return True

    def ghost_mino_position(
        self,
        current_mino: Mino,
    ) -> Tuple[int, int]:
        """This will return the ghost mino position."""
        if current_mino is None:
            return (-1, -1)
        key: Tuple[Tuple[int, int], str, str] = (
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
        result: Tuple[int, int] = ghost_mino.position
        self._last_ghost_check = key
        self._last_ghost_result = result
        return result

    def calculate_score(self, rows_dropped: int = 0) -> None:
        """This will calculate the score from hard drop."""

        self.score += calculate_drop_score(
            soft_drop_distance=0,
            hard_drop_distance=rows_dropped,
        )

        lines_clear_detected: int = self.board.check_line_clear()
        if not self.current_mino:
            return
        all_clear_detected: bool = self.board.detect_all_clear()
        t_spin_detected: str = self.board.detect_t_spin(self.current_mino)
        if lines_clear_detected > 0:
            self.combo_count += 1
        else:
            self.combo_count = 0

        self.board.clear_lines()
        action_text: List[str] = []
        current_score, back_to_back, action_text = calculate_line_score(
            lines_cleared=lines_clear_detected,
            level=self.level,
            t_spin=t_spin_detected,
            all_clear=all_clear_detected,
            combo=self.combo_count,
            back_to_back=self.back_to_back,
        )
        self.score += current_score
        self.back_to_back = back_to_back
        self.lines_cleared += lines_clear_detected
        if action_text:
            self.action["action_text"] = action_text

        if t_spin_detected:
            if lines_clear_detected <= 1:
                self.sound_action["SFX"].append("t_spin_single")
            elif lines_clear_detected == 2:
                self.sound_action["SFX"].append("t_spin_double")
            elif lines_clear_detected == 3:
                self.sound_action["SFX"].append("t_spin_triple")
        else:
            if lines_clear_detected == 1:
                self.sound_action["SFX"].append("single")
            elif lines_clear_detected in (2, 3):
                self.sound_action["SFX"].append("double")
            elif lines_clear_detected == 4:
                self.sound_action["SFX"].append("quad")

        # Level up for every 10 lines cleared
        self.level = max(self.level, (self.lines_cleared // 10) + 1)

    def check_keyinput_pressed(self, pressed_keys: Set[str]) -> None:
        """This will check the keyinput pressed."""

        if not pressed_keys & {"z", "Z", "ctrl"}:
            self.keyinput_cooldown.discard("ccw")
        if not pressed_keys & {"x", "X", "up"}:
            self.keyinput_cooldown.discard("cw")
        if not pressed_keys & {"space"}:
            self.keyinput_cooldown.discard("space")

        if not self.current_mino:
            return

        if pressed_keys & {"z", "Z", "ctrl"} and "ccw" not in self.keyinput_cooldown:
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
                self.current_mino.soft_drop(
                    level=self.level, is_position_valid=self.is_position_valid
                )
                self.current_mino.lock_info["lock_delay"] = int(0.5 * TARGET_FPS)
                self.score += calculate_drop_score(
                    soft_drop_distance=1,
                    hard_drop_distance=0,
                )
        if pressed_keys & {"space"} and "space" not in self.keyinput_cooldown:
            rows_dropped = self.current_mino.hard_drop(
                mino_touching_bottom_func=self.mino_touching_bottom,
                is_position_valid=self.is_position_valid,
            )
            self.board.place_mino(
                self.current_mino.type,
                self.current_mino.orientation,
                self.current_mino.position,
            )

            self.calculate_score(rows_dropped)

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
                    level=self.level
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


if __name__ == "__main__":
    print("This is a base module for modes. Please run the starter.py.")
