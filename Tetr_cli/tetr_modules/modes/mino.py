"""This will handle the mino (tetromino) shapes."""

# coding: utf-8

from functools import lru_cache
from typing import Callable

from tetr_modules.modes.constants import MINO_DRAW_LOCATION

from .constants import (
    BOARD_WIDTH,
    DAS,
    ARR,
    MINO_ORIENTATIONS,
    TARGET_FPS,
)


class Mino:
    """This will handle the mino."""

    def __init__(self, mino_type: str, level: int) -> None:
        """This will initialize this class."""
        self.__type: str = mino_type
        self.__orientation: str = "N"
        # 21st row at the center column
        self.__position: tuple[int, int] = (21, BOARD_WIDTH // 2 - 1)  # (y, x)
        self.__soft_drop_counter: int = 0

        self.__auto_repeat_delay: int = DAS
        self.__last_sideways_direction: str = ""

        self.__fall_delay: int = self.reset_fall_delay(level)
        self.__lock_info: dict[str, int] = {
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

    @orientation.setter
    def orientation(self, value: str) -> None:
        """This will set the mino orientation."""
        if value in MINO_ORIENTATIONS:
            self.__orientation = value

    @property
    def position(self) -> tuple[int, int]:
        """This will return the mino position."""
        return self.__position

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        """This will set the mino position."""
        self.__position = value

    @property
    def lock_info(self) -> dict[str, int]:
        """This will return the lock info."""
        return self.__lock_info

    @lock_info.setter
    def lock_info(self, value: dict[str, int]) -> None:
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

    def move_sideways(self, direction: str) -> None:
        """This will move the current mino sideways."""
        if direction == "left":
            self.__position = (self.__position[0], self.__position[1] - 1)
            return
        elif direction == "right":
            self.__position = (self.__position[0], self.__position[1] + 1)
            return

    def handle_sideways_auto_repeat(
        self,
        pressed_keys: set[str],
        mino_touching_side_func: Callable[[str, 'Mino'], bool]
    ) -> None:
        """Handles auto-repeat for left/right movement."""
        for direction in ["left", "right"]:
            if direction in pressed_keys:
                if self.last_sideways_direction != direction:
                    self.auto_repeat_delay = DAS
                    self.last_sideways_direction = direction
                    if not mino_touching_side_func(direction, self):
                        self.move_sideways(direction)
                else:
                    if self.auto_repeat_delay > 0:
                        self.auto_repeat_delay -= 1
                    else:
                        if not mino_touching_side_func(direction, self):
                            self.move_sideways(direction)
                        self.auto_repeat_delay = ARR
            else:
                if self.last_sideways_direction == direction:
                    self.last_sideways_direction = ""
                    self.auto_repeat_delay = DAS

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

    def hard_drop(
        self,
        mino_touching_bottom_func: Callable[['Mino'], bool],
    ) -> None:
        """This will handle the hard drop."""
        while not mino_touching_bottom_func(self):
            self.move_down()


if __name__ == "__main__":
    print("This is a mino module for modes.")
