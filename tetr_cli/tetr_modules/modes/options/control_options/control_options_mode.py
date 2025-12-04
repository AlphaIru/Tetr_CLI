"""This is the control option mode."""

# coding: utf-8

from typing import Dict, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass

from tetr_cli.tetr_modules.modules.constants import CONTROLS_LIST
from tetr_cli.tetr_modules.modules.database import set_temp, load_keybinds


class ModeClass(VerticalMenuModeClass):
    """This will handle the control option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.__option_to_action: Dict[str, Dict[str, str]] = {}
        self.__user_keybinds: Dict[str, Set[str]] = load_keybinds()
        for control_option in CONTROLS_LIST:
            control_key: str = ""
            if len(self.__user_keybinds[control_option]) == 1:
                control_key = self.__user_keybinds[control_option].pop()
            else:
                control_key = ", ".join(
                    sorted(self.__user_keybinds[control_option])
                )
            space: str = " " * (15 - len(control_option))
            list_option = f"{control_option}:{space}{control_key}"
            self.__option_to_action[list_option] = {
                "action": "Change_Keybind",
                "sound": "select_confirm",
                "keybind": control_option
            }
        self.__option_to_action["Go_Back"] = {
            "action": "Option_Menu",
            "sound": "select_back",
            "keybind": ""
        }
        self.control_options = list(self.__option_to_action.keys())
        super().__init__(self.control_options, self.__option_to_action)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Control Options")
        if "enter" in pressed_keys:
            selected_option: str = self.control_options[self.selected_option]
            set_temp("rebind_control", self.__option_to_action[selected_option]["keybind"])


if __name__ == "__main__":
    print("This is a control_options module, please run starter.py.")
