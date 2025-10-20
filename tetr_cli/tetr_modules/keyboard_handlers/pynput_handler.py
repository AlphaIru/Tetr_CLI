"""This is the sub-main if pynput is available."""
# coding: utf-8

from threading import Lock
from typing import Set

from pynput import keyboard  # type: ignore


def _name_of_key(key: str) -> str:
    """Get the name of the key and serialize it."""
    if (
        isinstance(key, keyboard.KeyCode)
        and key.char is not None
    ):
        return key.char
    input_key: str = str(key)

    if input_key.startswith("Key."):
        return input_key.split(".", 1)[1]
    return input_key


def setup_pynput_listener(
    pressed_keys: Set[str],
    lock: Lock
) -> keyboard.Listener:
    """Setup the pynput listener for keyboard input."""

    def on_key_press(key) -> None:
        """This is an event catcher when key is pressed"""
        with lock:
            pressed_keys.add(_name_of_key(key))

    def on_key_release(key) -> None:
        """This is an event catcher when key is released"""
        with lock:
            pressed_keys.discard(_name_of_key(key))

    listener: keyboard.Listener = keyboard.Listener(
        on_press=on_key_press,
        on_release=on_key_release
    )

    return listener


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
