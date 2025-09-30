"""This will handle the menu screen."""
# coding: utf-8

from copy import deepcopy
from curses import A_BOLD, A_REVERSE, window


class ModeClass:
    """This will handle main_menu."""

    def __init__(self) -> None:
        """This will initizalize this class."""
        self.__selected_option: int = 0
        self.__key_cooldown: int = 0
        self.__options: list[str] = ["Solo", "Multiplayer", "Quit"]
        self.__action: str = ""
        self.__sound_action: dict[str, list[str]] = {"BGM": ["stop"], "SFX": []}

    def pop_action(self) -> str:
        """This will return the action and reset it."""
        action = self.__action
        self.__action = ""
        return action

    def pop_sound_action(self) -> dict[str, list[str]]:
        """This will return the sound action and reset it."""
        sound_action: dict[str, list[str]] = deepcopy(self.__sound_action)
        self.__sound_action["SFX"] = []
        return sound_action

    def increment_frame(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will progress the menu based on the inputs."""
        if self.__key_cooldown > 0:
            self.__key_cooldown -= 1
        elif "up" in pressed_keys:
            self.__selected_option = max(0, self.__selected_option - 1)
            self.__key_cooldown = 3
            self.__sound_action["SFX"].append("select_move")
        elif "down" in pressed_keys:
            self.__selected_option = min(
                len(self.__options) - 1, self.__selected_option + 1
            )
            self.__key_cooldown = 3
            self.__sound_action["SFX"].append("select_move")
        elif "enter" in pressed_keys:
            self.__action = self.__options[self.__selected_option]
            self.__sound_action["SFX"].append("select_confirm")  # sound for confirming selection
            return stdscr

        height: int = 0
        width: int = 0
        height, width = stdscr.getmaxyx()

        # Those "// 2" just finds the center.
        # +2 in block_width account for "> "

        start_y: int = (height // 2) - len(self.__options) // 2
        block_width: int = max(len(option) for option in self.__options) + 2
        start_x: int = (width - block_width) // 2

        title = "Main Menu"
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
    print("This is a main_menu module, please run starter.py.")
