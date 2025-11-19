"""This will handle the audio options menu."""
# coding: utf-8

from typing import Dict, List, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import VerticalMenuModeClass

AUDIO_OPTION_TO_ACTION: Dict[str, Dict[str, str]] = {
    "BGM": {"action": "BGM_Option", "sound": "select_confirm"},
    "SFX": {"action": "SFX_Option", "sound": "select_confirm"},
    "Go_Back": {"action": "Main_Menu", "sound": "select_back"},
}

AUDIO_OPTION_LIST: List[str] = [
    "BGM",
    "SFX",
    "Go_Back",
]


class ModeClass(VerticalMenuModeClass):
    """This will handle the option mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__(AUDIO_OPTION_LIST, AUDIO_OPTION_TO_ACTION)

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the menu based on the inputs."""
        self.menu_control(pressed_keys)
        self.display_menu(stdscr, "Audio Options")


if __name__ == "__main__":
    print("This is a audio_options module, please run starter.py.")
