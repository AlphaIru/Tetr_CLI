"""This will hold the debug information like FPS."""

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
        self.keypress: set = set()
        return

    def update_debug(
        self, stdscr
    ) -> window:
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
        stdscr.addstr(
            max_y - 4,
            0,
            f"Total frames: {self.total_frame_count}, Frame rate: {self.frame_rate:.2f}",
        )

        return stdscr


if __name__ == "__main__":
    print("This is a module, do not look in here.")
