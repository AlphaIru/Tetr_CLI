"""This will handle the host room mode."""
# coding: utf-8


from typing import Set

from curses import window, A_BOLD, A_REVERSE

from tetr_cli.tetr_modules.menu_core.base_mode import BaseModeClass

from tetr_cli.tetr_modules.modules.constants import MAX_NAME_LENGTH, NUMBER_SET, VALID_CHARS
from tetr_cli.tetr_modules.modules.safe_curses import (
    calculate_centered_menu,
    safe_addstr,
)


class ModeClass(BaseModeClass):
    """This is the host room mode class."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__()
        self.__selected_option: int = 0
        self.__key_cooldown: int = 0
        # note selected_option:
        # 0: roomname
        # 1: username

        self.__roomname: str = "Your_Room"
        self.__username: str = "Noob_Player1"
        self.__port: str = "5000"

    def menu_control(self, pressed_keys: Set) -> None:
        """This will handle the menu controls."""
        if self.__key_cooldown > 0:
            self.__key_cooldown -= 1
        elif self.get_user_keybind("menu_up", menu_mode=True) & pressed_keys:
            self.__selected_option = max(0, self.__selected_option - 1)
            self.__key_cooldown = 3
            self.sound_action["SFX"].append("select_move")
        elif self.get_user_keybind("menu_down", menu_mode=True) & pressed_keys:
            self.__selected_option = min(2, self.__selected_option + 1)
            self.__key_cooldown = 3
            self.sound_action["SFX"].append("select_move")
        elif self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
            self.action["transition"] = ["Join_Room"]  # Placeholder
            self.sound_action["SFX"].append("select_confirm")
            if self.__username == "":
                self.__username = "Noob_Player1"
            if self.__roomname == "":
                self.__roomname = "Your_Room"
            if self.__port == "0":
                self.__port = "5000"
        elif self.get_user_keybind("menu_back", menu_mode=True) & pressed_keys:
            self.action["transition"] = ["Multi_Menu"]
            self.sound_action["SFX"].append("select_back")

    def display_menu(self, stdscr: window) -> None:
        """This will display the wait room menu."""
        start_y, start_x, _ = calculate_centered_menu(stdscr, [""])

        title: str = "Multiplayer Wait Room"
        safe_addstr(stdscr, start_y - 2, start_x - len(title) // 2, title, A_BOLD)

        safe_addstr(
            stdscr,
            start_y,
            start_x - 12,
            "Username:",
            A_REVERSE if self.__selected_option == 0 else 0,
        )
        safe_addstr(
            stdscr,
            start_y + 4,
            start_x - 2,
            self.__username,
            A_REVERSE if self.__selected_option == 0 else 0,
        )

        safe_addstr(
            stdscr,
            start_y + 2,
            start_x - 12,
            "Room Name:",
            A_REVERSE if self.__selected_option == 1 else 0,
        )
        safe_addstr(
            stdscr,
            start_y + 2,
            start_x - 2,
            self.__roomname,
            A_REVERSE if self.__selected_option == 1 else 0,
        )

        safe_addstr(
            stdscr,
            start_y + 2,
            start_x - 12,
            "Port:",
            A_REVERSE if self.__selected_option == 2 else 0,
        )
        safe_addstr(
            stdscr,
            start_y + 2,
            start_x - 4,
            f"{int(self.__port):>5d}",
            A_REVERSE if self.__selected_option == 2 else 0,
        )

        statement: str = "Enter the Username, Room Name, and Port to connect."
        safe_addstr(
            stdscr,
            start_y + 6,
            start_x - len(statement) // 2,
            statement,
        )
        statement = "Press Enter to Connect or Backspace to Return"
        safe_addstr(
            stdscr,
            start_y + 7,
            start_x - len(statement) // 2,
            statement,
        )

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will run the host room mode."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr)

        if self.__key_cooldown > 0:
            self.__key_cooldown -= 1
            return

        if "backspace" in pressed_keys:
            self.__key_cooldown = 3
            self.sound_action["SFX"].append("select_move")
            self.action["clear"] = []
            if self.__selected_option == 0 and len(self.__username) > 1:
                self.__username = self.__username[:-1]
                return
            elif self.__selected_option == 1 and len(self.__roomname) > 1:
                self.__roomname = self.__roomname[:-1]
                return
            elif len(self.__port) > 1:
                self.__port = self.__port[:-1]
                return
            self.__port = "0"
            return

        if not pressed_keys:
            return

        self.__key_cooldown = 3
        input_key: str = pressed_keys.pop()

        if self.__selected_option == 2:
            number_pressed: str = input_key if input_key in NUMBER_SET else ""
            if number_pressed == "":
                return
            self.action["clear"] = []
            self.sound_action["SFX"].append("select_move")
            self.__port += number_pressed
            if self.__port.startswith("0"):
                self.__port = self.__port[1:]
            if int(self.__port) > 65535:
                self.__port = "65535"
            return

        input_char: str = (
            input_key if input_key in VALID_CHARS else ""
        )
        if input_char == "":
            return

        self.action["clear"] = []
        self.sound_action["SFX"].append("select_move")

        if self.__selected_option == 0:
            if len(self.__username) < MAX_NAME_LENGTH:
                self.__username += input_char
        elif self.__selected_option == 1:
            if len(self.__roomname) < MAX_NAME_LENGTH:
                self.__roomname += input_char


if __name__ == "__main__":
    print("This is a module, not a program.")
