""" "This will handle the solo mode menu."""
# coding: utf-8

from typing import Dict, List, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass


OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Marathon": {"action": "Marathon", "sound": "select_confirm"},
    "Sprint": {"action": "Sprint", "sound": "select_confirm"},
    "Ultra": {"action": "Ultra", "sound": "select_confirm"},
    "Go_Back": {"action": "Main_Menu", "sound": "select_back"},
}

OPTION_LIST: List[str] = ["Marathon", "Sprint", "Ultra", "Go_Back"]


class ModeClass(VerticalMenuModeClass):
    """This will handle the solo mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(OPTION_LIST, OPTION_TO_ACTION)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Solo Mode Menu")


if __name__ == "__main__":
    print("This is a module, not a program.")
