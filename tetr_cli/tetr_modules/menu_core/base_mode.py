"""This is the whole base module for Tetr CLI modes."""
# coding: utf-8

from copy import deepcopy
from typing import Dict, List, Set

from tetr_cli.tetr_modules.modules.database import load_keybinds


class BaseModeClass:
    """This is the base class for all modes."""

    def __init__(self) -> None:
        """Initialize the base mode class."""
        self.__action: Dict[str, List[str]] = {}
        self.__sound_action: Dict[str, List[str]] = {"BGM": ["stop"], "SFX": []}
        self.__user_keybinds: Dict[str, Dict[str, Set[str]]] = load_keybinds()
        # print(f"Loaded keybinds: {self.__user_keybinds}")

    @property
    def action(self) -> Dict[str, List[str]]:
        """This will return the action dictionary."""
        return self.__action

    @action.setter
    def action(self, value: Dict[str, List[str]]) -> None:
        """This will set the action dictionary."""
        self.__action = value

    @property
    def sound_action(self) -> Dict[str, List[str]]:
        """This will return the sound action dictionary."""
        return self.__sound_action

    @sound_action.setter
    def sound_action(self, value: Dict[str, List[str]]) -> None:
        """This will set the sound action dictionary."""
        self.__sound_action = value

    def get_user_keybind(
        self,
        input_name: str,
        menu_mode: bool = False,
    ) -> Set[str]:
        """This will return the user keybinds dictionary."""
        if menu_mode:
            return self.__user_keybinds["menu_keys"][input_name]
        return self.__user_keybinds["game_keys"][input_name]

    def pop_action(self) -> Dict[str, List[str]]:
        """This will return the action and reset it."""
        actions: Dict[str, List[str]] = deepcopy(self.__action)
        self.__action = {}
        return actions

    def pop_sound_action(self) -> Dict[str, List[str]]:
        """This will return the sound action and reset it."""
        sound_action: Dict[str, List[str]] = deepcopy(self.__sound_action)
        self.__sound_action["SFX"] = []
        return sound_action


if __name__ == "__main__":
    raise Exception("This file is a module and cannot be run directly.")
