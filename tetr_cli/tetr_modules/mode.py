"""This is where it stores the current state."""

# coding: utf-8

from importlib import import_module
from typing import Dict, List, Set

from curses import window


class GameMode:
    """This will take care current game mode."""

    def __init__(self) -> None:
        self.__mode_instance = None
        self.__mode_name: str = "main_menu"

    def get_current_mode_name(self) -> str:
        """This will get the current mode name."""
        return self.__mode_name

    def get_mode_action(self) -> Dict[str, List[str]]:
        """This will return the current mode action."""
        if self.__mode_instance is None:
            raise RuntimeError("Mode not loaded.")
        return self.__mode_instance.pop_action()

    def get_sound_action(self) -> Dict[str, List[str]]:
        """This will return the current mode sound action."""
        if self.__mode_instance is None:
            raise RuntimeError("Mode not loaded.")
        return self.__mode_instance.pop_sound_action()

    def increment_frame(
        self,
        stdscr: window,
        pressed_keys: Set[str]
    ) -> window:
        """This will increment frame based on the current mode."""
        if self.__mode_instance is None:
            raise RuntimeError("Mode not loaded.")
        return self.__mode_instance.increment_frame(stdscr, pressed_keys)

    def change_mode(self, new_mode_name: str) -> None:
        """This will transition to new mode."""
        self.__mode_name = new_mode_name
        try:
            module = import_module(f"tetr_cli.tetr_modules.modes.{self.__mode_name}_mode")
            self.__mode_instance = module.ModeClass()
        except ModuleNotFoundError as exc:
            raise ValueError(f'"{self.__mode_name}" mode is not accessible!') from exc


if __name__ == "__main__":
    print("This is a module, please run starter.py.")
