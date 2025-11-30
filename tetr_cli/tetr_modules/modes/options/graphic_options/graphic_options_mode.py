"""This is the gameplay option mode."""

# coding: utf-8

from typing import Dict, List, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass


GAMEPLAY_OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Color Option": {"action": "Color_Option", "sound": "select_confirm"},
    "Mino Design": {"action": "Mino_Style_Option", "sound": "select_confirm"},
    "Frame Rate": {"action": "FPS_Option", "sound": "select_confirm"},
    "Go_Back": {"action": "Main_Menu", "sound": "select_back"},
}


GAMEPLAY_OPTION_LIST: List[str] = [
    "Color Option",
    "Mino Design",
    "Frame Rate",
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
