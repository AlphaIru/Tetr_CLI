"""This is the gameplay option mode."""
# coding: utf-8

from typing import Dict, List, Set

from curses import window

from tetr_cli.tetr_modules.menu_core.menu_mode import TwoDimmMenuModeClass


OPTION_LIST: List[str] = [
    "FPS_Limit",
    "Ghost Piece",
    "Go_Back",
]
