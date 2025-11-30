"""This will handle the frame option mode menu."""

from typing import Dict, Set
from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import SideMenuToggleClass
from tetr_cli.tetr_modules.modules.database import set_setting


TOGGLE_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Confirm": {"action": "Graphic_Options", "sound": "select_confirm"},
    "Go_Back": {"action": "Graphic_Options", "sound": "select_back"},
}


class ModeClass(SideMenuToggleClass):
    """This will handle the fps option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(
            toggle_name="frame_rate",
            toggle_to_action=TOGGLE_TO_ACTION,
            lower=15,
            upper=60,
            step=15
        )

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_toggle(stdscr, "Frame Rate Limit")
        if (
            self.get_user_keybind("menu_left", menu_mode=True) & pressed_keys
            or self.get_user_keybind("menu_right", menu_mode=True) & pressed_keys
            or self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys
            or self.get_user_keybind("menu_back", menu_mode=True) & pressed_keys
        ):
            if self.get_user_keybind("menu_back", menu_mode=True) & pressed_keys:
                set_setting("fps_limit", str(self.old_value))
                return
            if self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys:
                set_setting("fps_limit", str(self.current_value))
                self.action["update_fps"] = []


if __name__ == "__main__":
    print("This is a fps_option module, please run starter.py.")
