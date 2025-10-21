"""This will check if there is problems."""


from curses import window

from tetr_cli.tetr_modules.modules.constants import MIN_X, MIN_Y
from tetr_cli.tetr_modules.modules.safe_curses import safe_addstr


async def screen_dimension_check(stdscr: window) -> bool:
    """This will check the window size."""

    max_y: int = 0
    max_x: int = 0

    max_y, max_x = stdscr.getmaxyx()
    return not (max_y < MIN_Y or max_x < MIN_X)


async def screen_dimension_warning(stdscr: window) -> None:
    """This will display the warning to the user."""

    max_y: int = 0
    max_x: int = 0

    max_y, max_x = stdscr.getmaxyx()

    safe_addstr(
        stdscr,
        0,
        0,
        "Warning! Your screen is too small! Please check the dimmension is large enough!",
    )
    if max_y > 2:
        safe_addstr(
            stdscr,
            1,
            0,
            f"Currently, your screen is {max_x}x{max_y}, please make sure to have 80x24.",
        )


if __name__ == "__main__":
    print("This is a module. Please run main.")
