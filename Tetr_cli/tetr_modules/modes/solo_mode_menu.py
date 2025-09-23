""""This will handle the solo mode menu."""
# coding: utf-8

# from typing import Set
from curses import A_BOLD, A_REVERSE, window


class SoloModeMenu:
    """This will handle the solo mode menu."""

    def __init__(self, stdscr: window) -> None:
        self.stdscr = stdscr

    def display_menu(self) -> None:
        """Display the solo mode menu."""
        self.stdscr.addstr(0, 0, "Solo Mode Menu", A_BOLD)
        self.stdscr.addstr(1, 0, "1. Start Game", A_REVERSE)
        self.stdscr.addstr(2, 0, "2. Options")
        self.stdscr.addstr(3, 0, "3. Go Back")
        self.stdscr.refresh()


if __name__ == "__main__":
    print("This is a module, not a program.")
