"""This will handle the ARR option mode menu."""

from typing import Dict, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import SideMenuToggleClass
from tetr_cli.tetr_modules.modules.database import set_setting

TOGGLE_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Confirm": {"action": "Gameplay_Options", "sound": "select_confirm"},
    "Go_Back": {"action": "Gameplay_Options", "sound": "select_back"},
}


class ModeClass(SideMenuToggleClass):
    """This will handle the ARR option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(
            toggle_name="arr",
            toggle_to_action=TOGGLE_TO_ACTION,
            lower=0,
            upper=15,
            step=1
        )

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_toggle(stdscr, "ARR Options (Frames)")
        if self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
            set_setting("arr", str(self.current_value))


if __name__ == "__main__":
    print("This is a arr_option module, please run starter.py.")
