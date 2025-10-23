"""This module contains the curses definition for safe terminal handling."""

from curses import window
from typing import Optional


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


if __name__ == "__main__":
    print("This is a module, please run starter.py.")
