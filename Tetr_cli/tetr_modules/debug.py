"""This will hold the debug information like FPS."""
# coding: utf-8

from time import perf_counter

from curses import window


class DebugClass:
    """The debug class. Holds lots of information related to debug."""

    def __init__(self) -> None:
        """Initializes the variables."""
        self.frame_count: int = 0
        self.total_frame_count: int = 0
        self.frame_rate: float = 0.0
        self.start_time: float = perf_counter()
        self.keypress: set[str] = set()
        self.mode: str = "main_menu"
        return

    def update_keypress(self, keypress: set[str]) -> None:
        """Updates the keypress in the debug class."""
        self.keypress = keypress

    def update_current_mode(self, new_mode: str) -> None:
        """Updates the new mode onto this class."""
        self.mode = new_mode

    def __keypress_set_to_string(self) -> str:
        """Converts keypress set to string."""
        return ", ".join(str(key) for key in self.keypress)

    def update_debug(self, stdscr) -> window:
        """Update debug info on screen and manage frame rate calculation."""
        self.frame_count += 1
        self.total_frame_count += 1
        current_time = perf_counter()
        elapsed = current_time - self.start_time

        if elapsed >= 1.0:
            self.frame_rate = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = current_time

        max_y, _ = stdscr.getmaxyx()
        if max_y > 2:
            stdscr.addstr(
                max_y - 2,
                0,
                (f"Current mode: {self.mode} Total frames: {self.total_frame_count}")
                + (f", Frame rate: {self.frame_rate:.2f}"),
            )

        if max_y > 1:
            stdscr.addstr(
                max_y - 1,
                0,
                f"Current keys: {self.__keypress_set_to_string()}",
            )

        return stdscr


if __name__ == "__main__":
    print("This is a module, do not look in here.")
