"""This will handle the Ghost Piece option mode menu."""

from typing import Dict, List, Set
from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass
from tetr_cli.tetr_modules.modules.database import set_setting

OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Visible": {"action": "Gameplay_Options", "sound": "select_confirm"},
    "Hidden": {"action": "Gameplay_Options", "sound": "select_confirm"},
    "Go_Back": {"action": "Gameplay_Options", "sound": "select_back"},
}

OPTION_LIST: List[str] = [
    "Visible",
    "Hidden",
]


class ModeClass(VerticalMenuModeClass):
    """This will handle the Ghost Piece option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(OPTION_LIST, OPTION_TO_ACTION)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Ghost Piece Options")
        if self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
            selected_option: str = OPTION_LIST[self.selected_option]
            ghost_piece_value: str = "true" if selected_option == "Visible" else "false"
            set_setting("ghost_piece", ghost_piece_value)


if __name__ == "__main__":
    print("This is a ghost_piece_option module, please run starter.py.")
