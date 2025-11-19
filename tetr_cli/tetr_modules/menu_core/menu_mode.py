"""This class holds the basic features for the menu mode."""

# coding: utf-8

from curses import A_BOLD, A_REVERSE
from typing import Dict, List, Set

from tetr_cli.tetr_modules.menu_core.base_mode import BaseModeClass
from tetr_cli.tetr_modules.modules.safe_curses import (
    calculate_centered_menu,
    safe_addstr,
)

from tetr_cli.tetr_modules.modules.database import get_setting, set_setting


class VerticalMenuModeClass(BaseModeClass):
    """This class holds the basic features for the menu mode."""

    def __init__(
        self, option_list: List[str], option_to_action: Dict[str, Dict[str, str]]
    ) -> None:
        """This will initialize this class."""
        super().__init__()
        self.__selected_option: int = 0
        self.__key_cooldown: int = 0
        self.__options: List[str] = option_list
        self.__option_to_action: Dict[str, Dict[str, str]] = option_to_action

    @property
    def selected_option(self) -> int:
        """This will return the selected option."""
        return self.__selected_option

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
            self.action["transition"] = [
                self.__option_to_action[transition_name]["action"]
            ]
            self.sound_action["SFX"].append(
                self.__option_to_action[transition_name]["sound"]
            )
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


class SideMenuToggleClass(BaseModeClass):
    """This class will handle option to increase/decrease values."""

    def __init__(
        self,
        toggle_name: str,
        toggle_to_action: Dict[str, Dict[str, str]],
        lower: int,
        upper: int,
        step: int = 1,
    ) -> None:
        """This will initialize this class."""
        super().__init__()
        self.__key_cooldown: int = 0
        self.__toggle_name: str = toggle_name
        self.__toggle_to_action: Dict[str, Dict[str, str]] = toggle_to_action
        self.__lower: int = lower
        self.__upper: int = upper
        self.__step: int = step
        self.__current_value: int = int(
            get_setting(self.__toggle_name, default_value=str(lower))
        )
        self.__old_value: int = self.__current_value

    @property
    def current_value(self) -> int:
        """This will return the current value."""
        return self.__current_value

    @property
    def old_value(self) -> int:
        """This will return the old value."""
        return self.__old_value

    def menu_control(self, pressed_keys: Set) -> None:
        """This will handle the menu controls."""
        if self.__key_cooldown > 0:
            self.__key_cooldown -= 1
        elif self.get_user_keybind("menu_left", menu_mode=True) & pressed_keys:
            self.sound_action["SFX"].append("select_move")
            self.__current_value = max(self.__lower, self.__current_value - self.__step)
            self.__key_cooldown = 3
        elif self.get_user_keybind("menu_right", menu_mode=True) & pressed_keys:
            self.sound_action["SFX"].append("select_move")
            self.__current_value = min(self.__upper, self.__current_value + self.__step)
            self.__key_cooldown = 3
        elif self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
            self.sound_action["SFX"].append("select_confirm")
            set_setting(self.__toggle_name, str(self.__current_value))
            self.action["transition"] = [self.__toggle_to_action["Confirm"]["action"]]
            self.sound_action["SFX"].append(self.__toggle_to_action["Confirm"]["sound"])
        elif self.get_user_keybind("menu_back", menu_mode=True) & pressed_keys:
            self.action["transition"] = [self.__toggle_to_action["Go_Back"]["action"]]
            self.sound_action["SFX"].append(self.__toggle_to_action["Go_Back"]["sound"])

    def display_toggle(self, stdscr, title: str) -> None:
        """This will display the toggle."""
        start_y, start_x, width = calculate_centered_menu(
            stdscr, [""]
        )

        safe_addstr(stdscr, start_y - 2, (width - len(title)) // 2, title, A_BOLD)

        bar_width: int = 20
        filled_length = int(
            (self.__current_value - self.__lower)
            / (self.__upper - self.__lower)
            * bar_width
        )
        bar: str = (
            self.__toggle_name
            + "["
            + "#" * filled_length
            + "-" * (bar_width - filled_length)
            + "]"
        )
        safe_addstr(
            stdscr,
            start_y,
            start_x - (len(bar) // 2),
            bar,
            A_REVERSE,
        )

        value_str = str(self.__current_value).rjust(3)
        safe_addstr(
            stdscr,
            start_y + 1,
            start_x - len(value_str) // 2,
            value_str,
            A_BOLD,
        )


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
