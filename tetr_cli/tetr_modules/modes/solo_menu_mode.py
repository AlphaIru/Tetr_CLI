""" "This will handle the solo mode menu."""
# coding: utf-8

from typing import Dict, List, Set

from curses import A_BOLD, A_REVERSE, window

from tetr_cli.tetr_modules.modules.base_mode import BaseModeClass
from tetr_cli.tetr_modules.modules.safe_curses import calculate_centered_menu

OPTION_TO_ACTION: Dict[str, str] = {
    "Marathon": "Marathon",
    "Sprint": "Sprint",
    "Ultra": "Ultra",
    "Go_Back": "Main_Menu",
}


class ModeClass(BaseModeClass):
    """This will handle the solo mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__()
        self.__selected_option: int = 0
        self.__key_cooldown: int = 0
        self.__options: List[str] = ["Marathon", "Sprint", "Ultra", "Go_Back"]

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> window:
        """This will progress the menu based on the inputs."""
        if self.__key_cooldown > 0:
            self.__key_cooldown -= 1
        elif pressed_keys is None:
            self.__key_cooldown = 0
        elif "up" in pressed_keys:
            self.__selected_option = max(0, self.__selected_option - 1)
            self.__key_cooldown = 3
            self.sound_action["SFX"].append("select_move")
        elif "down" in pressed_keys:
            self.__selected_option = min(
                len(self.__options) - 1, self.__selected_option + 1
            )
            self.__key_cooldown = 3
            self.sound_action["SFX"].append("select_move")
        elif "enter" in pressed_keys:
            transition_name: str = self.__options[self.__selected_option]
            self.action["transition"] = [OPTION_TO_ACTION.get(transition_name, "")]
            if transition_name == "Go_Back":
                self.sound_action["SFX"].append("select_back")
            else:
                self.sound_action["SFX"].append("select_confirm")
            return stdscr

        start_y, start_x, width = calculate_centered_menu(stdscr, self.__options)

        title = "Solo Mode Menu"
        stdscr.addstr(start_y - 2, (width - len(title)) // 2, title, A_BOLD)

        for list_index, option in enumerate(self.__options):
            prefix: str = "  "
            attr: int = 0
            if list_index == self.__selected_option:
                prefix = "> "
                attr = A_REVERSE
            line = f"{prefix}{option}"
            stdscr.addstr(start_y + list_index, start_x, line, attr)
        return stdscr


if __name__ == "__main__":
    print("This is a module, not a program.")
