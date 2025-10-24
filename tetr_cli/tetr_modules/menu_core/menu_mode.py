"""This class holds the basic features for the menu mode."""
# coding: utf-8

from curses import A_BOLD, A_REVERSE
from typing import Dict, List, Set

from tetr_cli.tetr_modules.menu_core.base_mode import BaseModeClass
from tetr_cli.tetr_modules.modules.safe_curses import calculate_centered_menu, safe_addstr


class MenuModeClass(BaseModeClass):
    """This class holds the basic features for the menu mode."""

    def __init__(self, option_list: List[str], option_to_action: Dict[str, Dict[str, str]]) -> None:
        """This will initialize this class."""
        super().__init__()
        self.__selected_option: int = 0
        self.__key_cooldown: int = 0
        self.__options: List[str] = option_list
        self.__option_to_action: Dict[str, Dict[str, str]] = option_to_action

    def menu_control(self, pressed_keys: Set) -> None:
        """This will handle the menu controls."""
        if self.__key_cooldown > 0:
            self.__key_cooldown -= 1
        elif self.get_user_keybind("menu_up", menu_mode=True) & pressed_keys:
            self.__selected_option = max(0, self.__selected_option - 1)
            self.__key_cooldown = 3
            self.sound_action["SFX"].append("select_move")
        elif self.get_user_keybind("menu_down", menu_mode=True) & pressed_keys:
            self.__selected_option = min(
                len(self.__options) - 1, self.__selected_option + 1
            )
            self.__key_cooldown = 3
            self.sound_action["SFX"].append("select_move")
        elif self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
            transition_name: str = self.__options[self.__selected_option]
            self.action["transition"] = [self.__option_to_action[transition_name]["action"]]
            self.sound_action["SFX"].append(self.__option_to_action[transition_name]["sound"])
        elif self.get_user_keybind("menu_back", menu_mode=True) & pressed_keys:
            self.action["transition"] = [self.__option_to_action["Go_Back"]["action"]]
            self.sound_action["SFX"].append(self.__option_to_action["Go_Back"]["sound"])

    def display_menu(self, stdscr, title: str) -> None:
        """This will display the menu."""
        start_y, start_x, width = calculate_centered_menu(stdscr, self.__options)

        safe_addstr(stdscr, start_y - 2, (width - len(title)) // 2, title, A_BOLD)

        for list_index, option in enumerate(self.__options):
            prefix: str = "  "
            attr: int = 0
            if list_index == self.__selected_option:
                prefix = "> "
                attr = A_REVERSE
            safe_addstr(
                stdscr,
                start_y + list_index,
                start_x,
                f"{prefix}{option}",
                attr,
            )


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
