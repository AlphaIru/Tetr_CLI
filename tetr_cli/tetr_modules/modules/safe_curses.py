"""This module contains the curses definition for safe terminal handling."""

from curses import window
from typing import Optional, List, Tuple


def safe_addstr(
    stdscr: window,
    y: int,
    x: int,
    string: str,
    attr: Optional[int] = None,
) -> None:
    """This will safely add a string to the curses window."""
    max_y, max_x = stdscr.getmaxyx()
    if (
        (0 <= y < max_y)
        and (0 <= x < max_x)
    ):
        try:
            if attr is not None:
                stdscr.addstr(y, x, string, attr)
            else:
                stdscr.addstr(y, x, string)
        except Exception:
            # Ignore any exceptions (like out-of-bounds)
            pass


def calculate_centered_menu(
    stdscr: window,
    options: List[str],
) -> Tuple[int, int, int]:
    """This will calculate the centered position for a menu."""

    height: int = 0
    width: int = 0
    height, width = stdscr.getmaxyx()

    start_y: int = (height // 2) - len(options) // 2
    block_width: int = max(len(option) for option in options) + 2
    start_x: int = (width - block_width) // 2

    return start_y, start_x, width


if __name__ == "__main__":
    print("This is a module, please run starter.py.")
