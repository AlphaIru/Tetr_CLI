"""This is the control option mode."""

# coding: utf-8

from typing import Dict, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass

from tetr_cli.tetr_modules.modules.constants import CONTROLS_LIST
from tetr_cli.tetr_modules.modules.database import set_temp


OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {}

for control_option in CONTROLS_LIST:
    OPTION_TO_ACTION[control_option] = {
        "action": "Change_Keybind",
        "sound": "select_confirm",
    }

OPTION_TO_ACTION["Go_Back"] = {
    "action": "Option_Menu",
    "sound": "select_back",
}


class ModeClass(VerticalMenuModeClass):
    """This will handle the control option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.control_options = list(OPTION_TO_ACTION.keys())
        super().__init__(self.control_options, OPTION_TO_ACTION)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Control Options")
        if self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
            selected_option: str = self.control_options[self.selected_option]
            set_temp("rebind_control", selected_option)


if __name__ == "__main__":
    print("This is a control_options module, please run starter.py.")
