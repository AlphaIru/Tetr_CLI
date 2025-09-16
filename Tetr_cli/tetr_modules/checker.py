"""This will check if there is problems."""


from curses import window

MIN_X: int = 80
MIN_Y: int = 24


async def screen_dimmension_check(stdscr: window) -> bool:
    """This will check the window size."""

    max_y: int = 0
    max_x: int = 0

    max_y, max_x = stdscr.getmaxyx()
    return False if (max_y < MIN_Y or max_x < MIN_X) else True


async def screen_dimmension_warning(stdscr: window) -> window:
    """This will display the warning to the user."""

    max_y: int = 0
    max_x: int = 0

    max_y, max_x = stdscr.getmaxyx()

    stdscr.addstr(
        0,
        0,
        "Warning! Your screen is too small! Please check the dimmension is large enough!",
    )
    if max_y > 2:
        stdscr.addstr(
            1,
            0,
            f"Currently, your screen is {max_x}x{max_y}, please make sure to have 80x24.",
        )

    return stdscr


if __name__ == "__main__":
    print("This is a module. Please run main.")
