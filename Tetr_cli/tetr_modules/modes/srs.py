"""This module contains the SRS rotation system implementation."""

from pprint import pprint

# Dictionary implementation:
# Mino type
# -> Current orientation
# -> New orientation
# -> Rotation Direction (L or R)
# -> offset list

# WARNING: The endpoint should be moved in NEGATIVE direction.


# Okay long story short: it's not hard.
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


SRS_WALL_KICK_DATA: dict[str, dict[str, dict[str, list[tuple[int, int] | None]]]] = {
    "O": {
        "N": {
            "left": [  # West
                (0, 0),  # 1
                None,  # 2
                None,  # 3
                None,  # 4
                None,  # 5
            ],
            "right": [  # East
                (0, 0),  # 1
                None,  # 2
                None,  # 3
                None,  # 4
                None,  # 5
            ],
        },
        "E": {
            "left": [  # North
                (0, 0),  # 1
                None,  # 2
                None,  # 3
                None,  # 4
                None,  # 5
            ],
            "right": [  # South
                (0, 0),  # 1
                None,  # 2
                None,  # 3
                None,  # 4
                None,  # 5
            ],
        },
        "S": {
            "left": [  # East
                (0, 0),  # 1
                None,  # 2
                None,  # 3
                None,  # 4
                None,  # 5
            ],
            "right": [  # West
                (0, 0),  # 1
                None,  # 2
                None,  # 3
                None,  # 4
                None,  # 5
            ],
        },
        "W": {
            "left": [  # South
                (0, 0),  # 1
                None,  # 2
                None,  # 3
                None,  # 4
                None,  # 5
            ],
            "right": [  # North
                (0, 0),  # 1
                None,  # 2
                None,  # 3
                None,  # 4
                None,  # 5
            ],
        },
    },
    "I": {
        "N": {
            "left": [  # West
                (0, 0),  # 1
                (0, -1),  # 2
                (0, 2),  # 3
                (2, -1),  # 4
                (-1, 2),  # 5
            ],
            "right": [  # East
                (0, 0),  # 1
                (0, -2),  # 2
                (0, 1),  # 3
                (-1, -2),  # 4
                (2, 1),  # 5
            ],
        },
        "E": {
            "left": [  # North
                (0, 0),  # 1
                (0, 2),  # 2
                (0, -1),  # 3
                (1, 2),  # 4
                (-2, -1),  # 5
            ],
            "right": [  # South
                (0, 0),  # 1
                (0, -1),  # 2
                (0, 2),  # 3
                (2, -1),  # 4
                (-1, 2),  # 5
            ],
        },
        "S": {
            "left": [  # East
                (0, 0),  # 1
                (0, 1),  # 2
                (0, -2),  # 3
                (-2, 1),  # 4
                (1, -2),  # 5
            ],
            "right": [  # West
                (0, 0),  # 1
                (0, 2),  # 2
                (0, -1),  # 3
                (1, 2),  # 4
                (-2, -1),  # 5
            ],
        },
        "W": {
            "left": [  # South
                (0, 0),  # 1
                (0, -2),  # 2
                (0, 1),  # 3
                (-1, -2),  # 4
                (2, 1),  # 5
            ],
            "right": [  # North
                (0, 0),  # 1
                (0, 1),  # 2
                (0, -2),  # 3
                (-2, 1),  # 4
                (1, -2),  # 5
            ],
        },
    },
    "T": {
        "N": {
            "left": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                None,  # 4
                (-2, 1),  # 5
            ],
            "right": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                None,  # 4
                (-2, -1),  # 5
            ]
        },
        "E": {
            "left": [  # North
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (0, 2),  # 4
                (1, 2),  # 5
            ],
            "right": [  # South
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (0, 2),  # 4
                (1, 2),  # 5
            ],
        },
        "S": {
            "left": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                None,  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
            "right": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                None,  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
        },
        "W": {
            "left": [  # South
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
            "right": [  # North
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
        },
    },
    "L": {
        "N": {
            "left": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
            "right": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
        },
        "E": {
            "left": [  # North
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (2, 0),  # 4
                (2, 1),  # 5
            ],
            "right": [  # South
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (2, 0),  # 4
                (2, 1),  # 5
            ],
        },
        "S": {
            "left": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
            "right": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
        },
        "W": {
            "left": [  # South
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
            "right": [  # North
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
        },
    },
    "J": {
        "N": {
            "left": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
            "right": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
        },
        "E": {
            "left": [  # North
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (2, 0),  # 4
                (2, 1),  # 5
            ],
            "right": [  # South
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (2, 0),  # 4
                (2, 1),  # 5
            ],
        },
        "S": {
            "left": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
            "right": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
        },
        "W": {
            "left": [  # South
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
            "right": [  # North
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
        }
    },
    "S": {
        "N": {
            "left": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
            "right": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
        },
        "E": {
            "left": [  # North
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (2, 0),  # 4
                (2, 1),  # 5
            ],
            "right": [  # South
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (2, 0),  # 4
                (2, 1),  # 5
            ],
        },
        "S": {
            "left": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
            "right": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
        },
        "W": {
            "left": [  # South
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
            "right": [  # North
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
        },
    },
    "Z": {
        "N": {
            "left": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
            "right": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
        },
        "E": {
            "left": [  # North
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (2, 0),  # 4
                (2, 1),  # 5
            ],
            "right": [  # South
                (0, 0),  # 1
                (0, 1),  # 2
                (-1, 1),  # 3
                (2, 0),  # 4
                (2, 1),  # 5
            ],
        },
        "S": {
            "left": [  # East
                (0, 0),  # 1
                (0, -1),  # 2
                (1, -1),  # 3
                (-2, 0),  # 4
                (-2, -1),  # 5
            ],
            "right": [  # West
                (0, 0),  # 1
                (0, 1),  # 2
                (1, 1),  # 3
                (-2, 0),  # 4
                (-2, 1),  # 5
            ],
        },
        "W": {
            "left": [  # South
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
            "right": [  # North
                (0, 0),  # 1
                (0, -1),  # 2
                (-1, -1),  # 3
                (2, 0),  # 4
                (2, -1),  # 5
            ],
        },
    }
}

if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
    pprint(SRS_WALL_KICK_DATA)
