"""This module contains the SRS rotation system implementation."""

from pprint import pprint

# Dictionary implementation:
# Mino type
# -> situation (Like visual, off the wall, etc.)
#   A: Visual
#   B: Off the Right wall
#   C: Off the Left wall
#   D: Off the Floor
#   E: Out of Right well
#   F: Out of Left well
# -> (Current orientation, New orientation)
# -> List of wall kick data

# O:
#   Is always situation (A), no wall kicks
# I:
#   Point 1 is visual (A)
#   Point 2 is off the right/left wall (B, C)
#   Point 3 is reverse (B, C)
#   Point 4 is off the floor, and to go out the well (D, E, F)
#   Point 5 is reverse, and to go out the well (D, E, F)
# T, L, J, S, Z:
#  Point 1 is visual (A)
#  Point 2 is off the right/left wall (B, C)
#  Point 3 is for off the floor (D)
#  Point 4 is for out of the well (E, F)
#  Point 5 is for reverse, and to go out the well (D, E, F)

O_KICK_LIST: list[tuple[int, int]] = [(0, 0)]
O_ORIENTATION_KEYS: list[tuple[str, str]] = [
    ("N", "W"),
    ("N", "E"),
    ("E", "N"),
    ("E", "S"),
    ("S", "E"),
    ("S", "W"),
    ("W", "S"),
    ("W", "N"),
]

SRS_WALL_KICK_DATA: dict = {
    "O": {
        "A": {key: O_KICK_LIST for key in O_ORIENTATION_KEYS},
        "B": {key: O_KICK_LIST for key in O_ORIENTATION_KEYS},
        "C": {key: O_KICK_LIST for key in O_ORIENTATION_KEYS},
        "D": {key: O_KICK_LIST for key in O_ORIENTATION_KEYS},
        "E": {key: O_KICK_LIST for key in O_ORIENTATION_KEYS},
        "F": {key: O_KICK_LIST for key in O_ORIENTATION_KEYS},
    },
    "I": {
        "A": {
            ("N", "W"): [(0, 0), (0, -2), (0, 1), (-1, -2), (2, 1)],
        },
    }
}

if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
    pprint(SRS_WALL_KICK_DATA)
