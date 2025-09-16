"""This will handle the menu screen."""

from typing import Any, Set
from curses import (
    A_BOLD,
    A_REVERSE,
    window
)


class ModeClass:
    """This will handle main_menu."""
    def __init__(self) -> None:
        """This will initizalize this class."""
        self.__data: dict[str, Any] = {
            "selected_option": 0,
            "key_cooldown": 0,
            "options": ["Solo", "Multiplayer", "Quit"],
        }

    def increment_frame(
        self,
        stdscr: window,
        pressed_keys: Set[str]
    ) -> window:
        """This will progress the menu based on the inputs."""
        if "up" in pressed_keys:
            self.__data["selected_option"] = max(0, self.__data["selected_option"] - 1)
        elif "down" in pressed_keys:
            self.__data["selected_option"] = min(
                len(self.__data["options"]) - 1, self.__data["selected_option"] + 1
            )

        stdscr.clear()
        stdscr.addstr(0, 0, "Main Menu", A_BOLD)

        for idx, option in enumerate(self.__data["options"]):
            if idx == self.__data["selected_option"]:
                stdscr.addstr(idx + 2, 0, f"> {option}", A_REVERSE)
            else:
                stdscr.addstr(idx + 2, 0, f"  {option}")

        return stdscr


if __name__ == "__main__":
    print("This is a main_menu module, please run starter.py.")
