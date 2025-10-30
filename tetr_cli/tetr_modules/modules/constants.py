"""This will hold constants for different game modes."""

# coding: utf-8

from typing import Set, Dict, List, Tuple


MIN_X: int = 80
MIN_Y: int = 24

BOARD_WIDTH: int = 10
BOARD_HEIGHT: int = 40


# (y, x), A B C D
T_SPIN_CORNER_CHECKS: Dict[str, List[Tuple[int, int]]] = {
    "N": [(1, -1), (1, 1), (-1, -1), (-1, 1)],
    "E": [(1, 1), (-1, 1), (1, -1), (-1, -1)],
    "S": [(-1, 1), (-1, -1), (1, 1), (1, -1)],
    "W": [(-1, -1), (1, -1), (-1, 1), (1, 1)],
}

DRAW_BOARD_WIDTH: int = BOARD_WIDTH * 2  # Each cell is 2 chars wide
DRAW_BOARD_HEIGHT: int = 20  # Show only 22 rows 20 + 2 for extra

MINO_TYPES: Set[str] = {"O", "I", "T", "L", "J", "S", "Z"}
MINO_COLOR: Dict[str, int] = {"O": 1, "I": 2, "T": 3, "L": 4, "J": 5, "S": 6, "Z": 7}
MINO_ORIENTATIONS: List[str] = ["N", "E", "S", "W"]

# Mino Draw Location: Mino_type -> orientation (in NSEW) ->
# (current_position, 1st_block_position, 2nd_block_position, 3rd_block_position)
#
# Note: (y, x) format
MINO_DRAW_LOCATION: Dict[str, Dict[str, List[Tuple[int, int]]]] = {
    "O": {
        "N": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "S": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "E": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "W": [(0, 0), (0, 1), (1, 0), (1, 1)],
    },
    "I": {
        "N": [(0, 0), (0, -1), (0, 1), (0, 2)],
        "S": [(-1, 0), (-1, -1), (-1, 1), (-1, 2)],
        "E": [(1, 1), (0, 1), (-1, 1), (-2, 1)],
        "W": [(0, 0), (1, 0), (-1, 0), (-2, 0)],
    },
    "T": {
        "N": [(0, 0), (0, -1), (1, 0), (0, 1)],
        "S": [(0, 0), (0, -1), (-1, 0), (0, 1)],
        "E": [(0, 0), (-1, 0), (0, 1), (1, 0)],
        "W": [(0, 0), (-1, 0), (0, -1), (1, 0)],
    },
    "L": {
        "N": [(0, 0), (0, -1), (0, 1), (1, 1)],
        "S": [(0, 0), (0, -1), (0, 1), (-1, -1)],
        "E": [(0, 0), (-1, 0), (1, 0), (-1, 1)],
        "W": [(0, 0), (-1, 0), (1, 0), (1, -1)],
    },
    "J": {
        "N": [(0, 0), (0, -1), (0, 1), (1, -1)],
        "S": [(0, 0), (0, -1), (0, 1), (-1, 1)],
        "E": [(0, 0), (-1, 0), (1, 0), (1, 1)],
        "W": [(0, 0), (-1, 0), (1, 0), (-1, -1)],
    },
    "S": {
        "N": [(0, 0), (0, -1), (1, 0), (1, 1)],
        "S": [(0, 0), (0, 1), (-1, 0), (-1, -1)],
        "E": [(0, 0), (1, 0), (0, 1), (-1, 1)],
        "W": [(0, 0), (-1, 0), (0, -1), (1, -1)],
    },
    "Z": {
        "N": [(0, 0), (0, 1), (1, 0), (1, -1)],
        "S": [(0, 0), (0, -1), (-1, 0), (-1, 1)],
        "E": [(0, 0), (-1, 0), (0, 1), (1, 1)],
        "W": [(0, 0), (1, 0), (0, -1), (-1, -1)],
    },
}

SCORE_TABLE: Dict[str, Dict[int, int]] = {
    "regular": {
        1: 100,
        2: 300,
        3: 500,
        4: 800,
    },
    "t_spin": {
        0: 400,
        1: 800,
        2: 1200,
        3: 1600,
    },
    "mini_t_spin": {
        0: 100,
        1: 200,
    },
    "all_clear": {
        1: 800,
        2: 1200,
        3: 1600,
        4: 2000,
        5: 3200,  # Back-to-back all clear
    },
}

SCORE_NAME: Dict[str, Dict[int, str]] = {
    "regular": {
        1: "Single",
        2: "Double",
        3: "Triple",
        4: "Quad",
    },
    "t_spin": {
        0: "Tspin",
        1: "Tspin Single",
        2: "Tspin Double",
        3: "Tspin Triple",
    },
    "mini_t_spin": {
        0: "Mini Tspin",
        1: "Mini Tspin Single",
    },
}

VALID_CHARS: frozenset[str] = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _-"
)

if __name__ == "__main__":
    print("This is a constants module for modes.")
