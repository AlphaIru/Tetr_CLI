"""This will handle the BGM option menu."""

from typing import Dict, Set
from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import SideMenuToggleClass
from tetr_cli.tetr_modules.modules.database import set_setting

TOGGLE_TO_ACTION: Dict[str, Dict[str, str]] = {
    "Confirm": {"action": "Audio_Options", "sound": "select_confirm"},
    "Go_Back": {"action": "Audio_Options", "sound": "select_back"},
}


class ModeClass(SideMenuToggleClass):
    """This will handle the option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(
            toggle_name="music_volume",
            toggle_to_action=TOGGLE_TO_ACTION,
            lower=0,
            upper=100,
            step=5
        )
        self.sound_action["BGM"] = ["korobeiniki"]

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_toggle(stdscr, "BGM Volume")
        if (
            self.get_user_keybind("menu_left", menu_mode=True) & pressed_keys
            or self.get_user_keybind("menu_right", menu_mode=True) & pressed_keys
            or self.get_user_keybind("menu_confirm", menu_mode=True) & pressed_keys
            or self.get_user_keybind("menu_back", menu_mode=True) & pressed_keys
        ):
            self.action["update_volume"] = []
            if self.get_user_keybind("menu_back", menu_mode=True) & pressed_keys:
                set_setting("music_volume", str(self.old_value))
                return
            set_setting("music_volume", str(self.current_value))


if __name__ == "__main__":
    print("This is a bgm_option module, please run starter.py.")
