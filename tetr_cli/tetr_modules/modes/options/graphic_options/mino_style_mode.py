"""This will handle the Mino Style option mode menu."""

from typing import Dict, Set
from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass

from tetr_cli.tetr_modules.modules.constants import MINO_TO_GHOST
from tetr_cli.tetr_modules.modules.database import set_setting

OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Confirm": {"action": "Gameplay_Options", "sound": "select_confirm"},
    "Go_Back": {"action": "Gameplay_Options", "sound": "select_back"},
}


class ModeClass(VerticalMenuModeClass):
    """This will handle the Mino Style option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(list(MINO_TO_GHOST.keys()), OPTION_TO_ACTION)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Mino Style Options")
        if self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
            selected_option: str = list(MINO_TO_GHOST.keys())[self.selected_option]
            set_setting("mino_style", selected_option)


if __name__ == "__main__":
    print("This is a mino_style_option module, please run starter.py.")
