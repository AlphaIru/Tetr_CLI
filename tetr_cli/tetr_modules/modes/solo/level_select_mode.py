"""This will handle the level select screen."""

from typing import Dict, Set
from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import SideMenuToggleClass
from tetr_cli.tetr_modules.modules.database import set_temp

TOGGLE_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Confirm": {"action": "Marathon", "sound": "select_confirm"},
    "Go_Back": {"action": "Solo_Menu", "sound": "select_back"},
}


class ModeClass(SideMenuToggleClass):
    """This will handle the option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(
            toggle_name="level",
            toggle_to_action=TOGGLE_TO_ACTION,
            lower=0,
            upper=25,
            step=5,
        )
        self.current_value = 1

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_toggle(stdscr, "Marathon Level")
        if self.current_value == 0:
            self.current_value = 1
        elif self.current_value == 6:
            self.current_value = 5
        if "enter" in pressed_keys:
            set_temp("level", str(self.current_value))


if __name__ == "__main__":
    print("This is a bgm_option module, please run starter.py.")
