"""This is a handler for keyboard input using curses."""
# coding: utf-8

from typing import Set

from curses import keyname


KEY_NAME_CONVERTER: dict[str, str] = {
    " ": "space",
    "KEY_UP": "up",
    "KEY_DOWN": "down",
    "KEY_LEFT": "left",
    "KEY_RIGHT": "right",
    "KEY_END": "end",
    "^[": "esc",
    "^H": "backspace",
    "^I": "tab",
    "^J": "enter",
    "PADENTER": "enter",
    "PADPLUS": "+",
    "PADMINUS": "-",
    "PADSTAR": "*",
    "PADSLASH": "/",
    "PADSTOP": "<110>",
    "PAD0": "<96>",
    "KEY_C1": "<97>",
    "KEY_C2": "<98>",
    "KEY_C3": "<99>",
    "KEY_B1": "<100>",
    "KEY_B2": "<101>",
    "KEY_B3": "<102>",
    "KEY_A1": "<103>",
    "KEY_A2": "<104>",
    "KEY_A3": "<105>"
}


def curses_key_name(key_code: int) -> Set[str]:
    """Get the name of the key from its code using curses."""

    try:
        key_name: str = keyname(key_code).decode("utf-8")
        return {KEY_NAME_CONVERTER[key_name]} if key_name in KEY_NAME_CONVERTER else {key_name}
    except (AttributeError, TypeError):
        return {f"unknown_key_{key_code}"}


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
