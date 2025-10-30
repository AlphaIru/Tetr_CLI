"""This will handle the mino (tetromino) shapes."""

# coding: utf-8

from functools import lru_cache
from typing import Callable, Optional, Set, Dict, List, Tuple

from tetr_cli.tetr_modules.modules.constants import (
    BOARD_WIDTH,
    MINO_DRAW_LOCATION,
    MINO_ORIENTATIONS,
)
from tetr_cli.tetr_modules.solo_core.srs import SRS_WALL_KICK_DATA


class Mino:
    """This will handle the mino."""

    def __init__(self, mino_type: str, level: int, fps_limit: int) -> None:
        """This will initialize this class."""
        self.__type: str = mino_type
        self.__orientation: str = "N"
        self.__kick_number: int = 0

        # 21st row at the center column
        self.__position: Tuple[int, int] = (21, BOARD_WIDTH // 2 - 1)  # (y, x)
        self.__soft_drop_counter: int = 0

        self.__fps_limit: int = fps_limit
        self.__fall_delay: int = self.reset_fall_delay(level)
        self.__lock_info: Dict[str, int] = {
            "lock_delay": int(0.5 * self.__fps_limit),
            "lock_count": 15,
            "lock_height": 21,
        }

        self.__auto_repeat_delay: int = self.calculate_das()
        self.__last_sideways_direction: str = ""

    @property
    def type(self) -> str:
        """This will return the mino type."""
        return self.__type

    @property
    def orientation(self) -> str:
        """This will return the mino orientation."""
        return self.__orientation

    @orientation.setter
    def orientation(self, value: str) -> None:
        """This will set the mino orientation."""
        if value in MINO_ORIENTATIONS:
            self.__orientation = value

    @property
    def position(self) -> Tuple[int, int]:
        """This will return the mino position."""
        return self.__position

    @position.setter
    def position(self, value: Tuple[int, int]) -> None:
        """This will set the mino position."""
        self.__position = value

    @property
    def kick_number(self) -> int:
        """This will return the kick number."""
        return self.__kick_number

    @kick_number.setter
    def kick_number(self, value: int) -> None:
        """This will set the kick number."""
        self.__kick_number = max(0, value)

    @lru_cache(maxsize=4)
    def calculate_das(self) -> int:
        """This will return the delayed auto shift."""
        return int(0.05 * self.__fps_limit)

    @lru_cache(maxsize=4)
    def calculate_arr(self) -> int:
        """This will return the auto repeat rate."""
        return int(0.01 * self.__fps_limit)

    @property
    def lock_info(self) -> Dict[str, int]:
        """This will return the lock info."""
        return self.__lock_info

    @lock_info.setter
    def lock_info(self, value: Dict[str, int]) -> None:
        """This will set the lock info."""
        self.__lock_info = value

    @property
    def auto_repeat_delay(self) -> int:
        """This will return the auto repeat delay."""
        return self.__auto_repeat_delay

    @auto_repeat_delay.setter
    def auto_repeat_delay(self, value: int) -> None:
        """This will set the auto repeat delay."""
        self.__auto_repeat_delay = max(0, value)

    @property
    def last_sideways_direction(self) -> str:
        """This will return the last sideways direction."""
        return self.__last_sideways_direction

    @last_sideways_direction.setter
    def last_sideways_direction(self, value: str) -> None:
        """This will set the last sideways direction."""
        if value in ["left", "right", ""]:
            self.__last_sideways_direction = value

    def get_block_positions(
        self,
        position: Tuple[int, int] = (-1, -1),
        orientation: str = "None",
    ) -> List[Tuple[int, int]]:
        """This will return the block positions of the mino."""
        if position == (-1, -1):
            position = self.__position
        if orientation == "None":
            orientation = self.__orientation
        positions: List[Tuple[int, int]] = []
        mino_shape: List[Tuple[int, int]] = MINO_DRAW_LOCATION[self.type][orientation]
        for y_offset, x_offset in mino_shape:
            y_pos = position[0] + y_offset
            x_pos = position[1] + x_offset
            positions.append((y_pos, x_pos))
        return positions

    def rotate(
        self,
        direction: str,
        is_position_valid: Callable[[List[Tuple[int, int]]], bool],
    ) -> None:
        """This will rotate the current mino."""
        if direction not in ["left", "right"]:
            return

        current_index: int = MINO_ORIENTATIONS.index(self.orientation)
        new_index: int = 0
        if direction == "right":
            new_index = (current_index + 1) % len(MINO_ORIENTATIONS)
        elif direction == "left":
            new_index = (current_index - 1) % len(MINO_ORIENTATIONS)
        temp_orientation: str = MINO_ORIENTATIONS[new_index]

        # kicks: List[Tuple[int, int] | None] = (
        kicks: List[Optional[Tuple[int, int]]] = (
            SRS_WALL_KICK_DATA.get(self.type, {})
            .get(self.orientation, {})
            .get(direction, [(0, 0)])
        )
        for kick_num, off_set in enumerate(kicks, start=1):
            if off_set is None:
                continue
            new_y: int = self.__position[0] + off_set[0]
            new_x: int = self.__position[1] + off_set[1]

            # Debug info
            # print(f"Trying to rotate {self.type} from {self.__orientation},", end=" ")
            # print(f"to {temp_orientation}", end=" ")
            # print(f"Offsets: {off_set[0]}, {off_set[1]}")

            temp_position: Tuple[int, int] = (new_y, new_x)
            block_positions: List[Tuple[int, int]] = self.get_block_positions(
                temp_position, temp_orientation
            )
            if is_position_valid(block_positions):
                self.__kick_number = kick_num
                self.__orientation = temp_orientation
                self.__position = temp_position
                return
        self.__kick_number = 0  # No kick applied if rotation fails

    def move_sideways(self, direction: str) -> None:
        """This will move the current mino sideways."""
        if direction == "left":
            self.__position = (self.__position[0], self.__position[1] - 1)
            return
        if direction == "right":
            self.__position = (self.__position[0], self.__position[1] + 1)
            return

    def handle_sideways_auto_repeat(
        self,
        pressed_keys: Set[str],
        mino_touching_side_func: Callable[[str, "Mino"], bool],
    ) -> None:
        """Handles auto-repeat for left/right movement."""
        direction: str = ""
        if "left" in pressed_keys and "right" not in pressed_keys:
            direction = "left"
        elif "right" in pressed_keys and "left" not in pressed_keys:
            direction = "right"
        if mino_touching_side_func(direction, self):
            direction = ""

        if direction == "":
            self.last_sideways_direction = ""
            self.auto_repeat_delay = self.calculate_das()
            return

        if self.last_sideways_direction != direction:
            self.auto_repeat_delay = self.calculate_das()
            self.last_sideways_direction = direction
            if not mino_touching_side_func(direction, self):
                self.move_sideways(direction)
                self.__kick_number = 0
            else:
                self.auto_repeat_delay = self.calculate_das()
        else:
            if self.auto_repeat_delay > 0:
                self.auto_repeat_delay -= 1
            else:
                if not mino_touching_side_func(direction, self):
                    self.move_sideways(direction)
                    self.__kick_number = 0
                    self.auto_repeat_delay = self.calculate_arr()
                else:
                    self.auto_repeat_delay = self.calculate_das()

    def handle_sideways_curses_input(
        self,
        pressed_keys: Set[str],
        mino_touching_side_func: Callable[[str, "Mino"], bool],
    ) -> None:
        """Handles continuous movement for left/right in curses mode."""
        for direction in ["left", "right"]:
            if direction in pressed_keys:
                if not mino_touching_side_func(direction, self):
                    self.move_sideways(direction)
                    self.__kick_number = 0

    def move_down(
        self,
        is_position_valid: Callable[[List[Tuple[int, int]]], bool]
    ) -> None:
        """This will move the current mino down."""
        new_position = (self.position[0] - 1, self.position[1])
        if is_position_valid(self.get_block_positions(new_position, self.orientation)):
            self.position = new_position
            self.__kick_number = 0

    @lru_cache(maxsize=4)
    def get_fall_seconds(self, level: int) -> float:
        """This will return the fall seconds for the given level."""
        return pow((0.8 - ((level - 1) * 0.007)), (level - 1))

    @lru_cache(maxsize=4)
    def reset_fall_delay(self, level: int) -> int:
        """This will return the fall delay for the given level."""
        seconds: float = self.get_fall_seconds(level)
        return max(0, int(seconds * self.__fps_limit))

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
        return max(0, int(soft_drop_seconds * self.__fps_limit))

    def soft_drop(
        self,
        level: int,
        is_position_valid: Callable[[List[Tuple[int, int]]], bool],
    ) -> None:
        """This will handle the soft drop."""
        self.__soft_drop_counter += 1
        delay: int = self.get_soft_drop_delay(level)
        if self.__soft_drop_counter >= delay:
            new_position = (self.position[0] - 1, self.position[1])
            if is_position_valid(self.get_block_positions(new_position, self.orientation)):
                self.position = new_position
                self.__soft_drop_counter = 0
                self.__kick_number = 0

    def hard_drop(
        self,
        mino_touching_bottom_func: Callable[["Mino"], bool],
        is_position_valid: Callable[[List[Tuple[int, int]]], bool],
    ) -> int:
        """This will handle the hard drop."""
        rows_dropped: int = 0
        previous_position: Tuple[int, int] = self.position
        while not mino_touching_bottom_func(self):
            previous_position = self.position
            self.move_down(is_position_valid)

            if self.position != previous_position:
                rows_dropped += 1
            else:
                break
        if rows_dropped > 0:
            self.__kick_number = 0
        return rows_dropped


if __name__ == "__main__":
    print("This is a mino module for modes.")
