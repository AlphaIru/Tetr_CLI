"""This is where it stores the current state."""

from typing import Any

from curses import (
    window
)

mode_list: list[str] = [
    "menu"
]


class GameMode():
    """This will take care current game mode."""

    def __init__(self) -> None:
        self.mode: int = 0
        self.mode_name: str = mode_list[0]
        self.mode_data: dict[str, Any] = {}

    def get_current_mode(self) -> int:
        """This will get the current mode."""
        return self.mode

    def get_current_mode_name(self) -> str:
        """This will get the current mode name."""
        return self.mode_name

    def increment_frame(self, stdscr: window) -> window:
        """This will move the game."""
        transition_confirmed: bool = False
        new_mode: int = 0

        if self.mode == 0:
            print(stdscr)

        print(transition_confirmed, new_mode)
        return stdscr

    def change_mode(self, new_mode: int) -> None:
        """This will transition to new mode."""
        self.mode = new_mode
        self.mode_name = mode_list[self.mode]
        self.mode_data = {}


if __name__ == "__main__":
    print("This is a module, please run starter.py.")
