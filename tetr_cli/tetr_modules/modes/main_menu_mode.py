"""This will handle the menu screen."""
# coding: utf-8

from typing import Dict, List, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass


OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Solo": {"action": "Solo_Menu", "sound": "select_confirm"},
    "Multiplayer": {"action": "Multi_Menu", "sound": "select_confirm"},
    "Options": {"action": "Option_Menu", "sound": "select_confirm"},
    "Quit": {"action": "Quit", "sound": "select_back"},
    "Go_Back": {"action": "Quit", "sound": "select_back"},
}

OPTION_LIST: List[str] = ["Solo", "Multiplayer", "Options", "Quit"]


class ModeClass(VerticalMenuModeClass):
    """This will handle main_menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(OPTION_LIST, OPTION_TO_ACTION)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Main Menu")


if __name__ == "__main__":
    print("This is a main_menu module, please run starter.py.")
