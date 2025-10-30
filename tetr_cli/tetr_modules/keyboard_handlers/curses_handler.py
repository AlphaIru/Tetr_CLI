"""This is a handler for keyboard input using curses."""
# coding: utf-8

from typing import Dict, Set

from curses import (
    keyname,
    KEY_UP,
    KEY_DOWN,
    KEY_LEFT,
    KEY_RIGHT,
    KEY_BACKSPACE,
    KEY_ENTER,
    KEY_DC,
    KEY_IC,
    KEY_HOME,
    KEY_END,
    KEY_PPAGE,
    KEY_NPAGE,
    KEY_A1,
    KEY_A2,
    KEY_A3,
    KEY_B1,
    KEY_B2,
    KEY_B3,
    KEY_C1,
    KEY_C2,
    KEY_C3,
    KEY_F1,
    KEY_F2,
    KEY_F3,
    KEY_F4,
    KEY_F5,
    KEY_F6,
    KEY_F7,
    KEY_F8,
    KEY_F9,
    KEY_F10,
    KEY_F11,
    KEY_F12,
)


KEY_NAME_CONVERTER: Dict[str, str] = {
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

SPECIAL_KEYS: Dict[int, str] = {
    KEY_UP: "up",
    KEY_DOWN: "down",
    KEY_LEFT: "left",
    KEY_RIGHT: "right",
    KEY_BACKSPACE: "backspace",
    KEY_ENTER: "enter",
    KEY_DC: "delete",
    KEY_IC: "insert",
    KEY_HOME: "home",
    KEY_END: "end",
    KEY_PPAGE: "page_up",
    KEY_NPAGE: "page_down",
    KEY_A1: "<103>",
    KEY_A2: "<104>",
    KEY_A3: "<105>",
    KEY_B1: "<100>",
    KEY_B2: "<101>",
    KEY_B3: "<102>",
    KEY_C1: "<97>",
    KEY_C2: "<98>",
    KEY_C3: "<99>",
    KEY_F1: "f1",
    KEY_F2: "f2",
    KEY_F3: "f3",
    KEY_F4: "f4",
    KEY_F5: "f5",
    KEY_F6: "f6",
    KEY_F7: "f7",
    KEY_F8: "f8",
    KEY_F9: "f9",
    KEY_F10: "f10",
    KEY_F11: "f11",
    KEY_F12: "f12",
}


def curses_key_name(key_code: int) -> Set[str]:
    """Get the name of the key from its code using curses."""

    try:
        if key_code in SPECIAL_KEYS:
            return {SPECIAL_KEYS[key_code]}
        key_name: str = keyname(key_code).decode("utf-8")
        return {KEY_NAME_CONVERTER[key_name]} if key_name in KEY_NAME_CONVERTER else {key_name}
    except (AttributeError, TypeError):
        return {f"unknown_key_{key_code}"}


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
