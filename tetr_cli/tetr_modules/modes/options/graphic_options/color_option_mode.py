"""This is the color option mode."""

from typing import Dict, List, Set
from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass

from tetr_cli.tetr_modules.modules.database import set_setting

COLOR_OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "True": {"action": "Graphic_Options", "sound": "select_confirm"},
    "False": {"action": "Graphic_Options", "sound": "select_confirm"},
    "Go_Back": {"action": "Graphic_Options", "sound": "select_back"},
}


OPTION_LIST: List[str] = [
    "True",
    "False",
]


class ModeClass(VerticalMenuModeClass):
    """This will handle the color option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(OPTION_LIST, COLOR_OPTION_TO_ACTION)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Color Options")
        if self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
            selected_option: str = OPTION_LIST[self.selected_option]
            color_value: str = "true" if selected_option == "True" else "false"
            set_setting("color_mode", color_value)


if __name__ == "__main__":
    print("This is a color_option_mode module, please run starter.py.")
