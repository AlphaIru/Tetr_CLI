"""This is the gameplay option mode."""

# coding: utf-8

from typing import Dict, List, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass


GAMEPLAY_OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Delayed Auto Shift (DAS)": {"action": "DAS_Option", "sound": "select_confirm"},
    "Auto Repeat Rate (ARR)": {"action": "ARR_Option", "sound": "select_confirm"},
    "Ghost Piece": {"action": "Ghost_Piece_Option", "sound": "select_confirm"},
    "Go_Back": {"action": "Main_Menu", "sound": "select_back"},
}


GAMEPLAY_OPTION_LIST: List[str] = [
    "Delayed Auto STift (DAS)",
    "Auto Repeat Rate (ARR)",
    "Ghost Piece",
    "Go_Back",
]


class ModeClass(VerticalMenuModeClass):
    """This will handle the gameplay option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(GAMEPLAY_OPTION_LIST, GAMEPLAY_OPTION_TO_ACTION)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Gameplay Options")


if __name__ == "__main__":
    print("This is a gameplay_options module, please run starter.py.")
