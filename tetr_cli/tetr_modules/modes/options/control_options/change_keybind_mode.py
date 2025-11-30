"""This will handle the Keybind Change mode."""

from typing import Dict, Set, List, Optional
from curses import window

from tetr_cli.tetr_modules.menu_core.base_mode import BaseModeClass
from tetr_cli.tetr_modules.modules.safe_curses import (
    calculate_centered_menu,
    safe_addstr,
)

from tetr_cli.tetr_modules.modules.database import get_temp, update_keybind


OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Go_Back": {"action": "Control_Options", "sound": "select_back"},
    "select_confirm": {"action": "Control_Options", "sound": "select_confirm"},
}


class ModeClass(BaseModeClass):
    """This will handle the Keybind Change mode."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__()
        self.keybind_name: str = get_temp("rebind_control")
        self.key_counter: int = 0
        self.new_keybinds: List[Optional[str]] = []

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        start_y, start_x, width = calculate_centered_menu(stdscr, ["temp"])
        statement: str = ""
        statement2: str = ""
        if self.key_counter == 0:
            statement = (
                f"Press a key to bind to '{self.keybind_name}' or 'Esc' to cancel."
            )
        elif self.key_counter == 1:
            statement = (
                f"Press a second key to bind to '{self.keybind_name}' or 'Esc' to pass."
            )
            statement2 = (
                f"First Key: '{self.new_keybinds[0]}'."
            )
        else:
            success: bool = update_keybind(
                self.keybind_name,
                self.new_keybinds[0],  # type: ignore
                self.new_keybinds[1] if len(self.new_keybinds) > 1 else None,
            )
            keys: str = f"{self.new_keybinds[0]}"
            if len(self.new_keybinds) == 2 and self.new_keybinds[1] is not None:
                keys = f"{self.new_keybinds[0]}' and '{self.new_keybinds[1]}"
            if not success:
                statement = (
                    f"Failed to bind '{self.keybind_name}' "
                    + f"to '{keys}'."
                )
            else:
                statement = (
                    f"Successfully bound '{self.keybind_name}' "
                    + f"to '{keys}'."
                )
            statement2 = "Press any to go back."
        safe_addstr(
            stdscr,
            start_y,
            (width - len(statement)) // 2,
            statement,
        )
        if statement2:
            safe_addstr(
                stdscr,
                start_y + 1,
                (width - len(statement2)) // 2,
                statement2,
            )
        if not pressed_keys:
            return
        self.action["clear"] = []
        new_key: str = pressed_keys.pop()
        if new_key == "esc":
            if self.key_counter == 0:
                self.action["transition"] = [OPTION_TO_ACTION["Go_Back"]["action"]]
                self.sound_action["SFX"].append(OPTION_TO_ACTION["Go_Back"]["sound"])
                return
            if self.key_counter == 2:
                self.action["transition"] = [
                    OPTION_TO_ACTION["select_confirm"]["action"]
                ]
                self.sound_action["SFX"].append(
                    OPTION_TO_ACTION["select_confirm"]["sound"]
                )
                return
            self.new_keybinds.append(None)
            self.key_counter += 1
            self.sound_action["SFX"].append(OPTION_TO_ACTION["select_confirm"]["sound"])
            return
        elif self.key_counter < 2:
            self.new_keybinds.append(new_key)
            self.key_counter += 1
            self.sound_action["SFX"].append(OPTION_TO_ACTION["select_confirm"]["sound"])
            return
        if self.key_counter >= 2:
            self.action["transition"] = [
                OPTION_TO_ACTION["select_confirm"]["action"]
            ]
            self.sound_action["SFX"].append(OPTION_TO_ACTION["select_confirm"]["sound"])
            return


if __name__ == "__main__":
    print("This is a change_keybind_mode module, please run starter.py.")
