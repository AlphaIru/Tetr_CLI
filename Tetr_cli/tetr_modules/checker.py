"""This will check if there is problems."""

from os import get_terminal_size

from curses import window

MIN_X: int = 80
MIN_Y: int = 24


async def enhanced_get_t_size() -> tuple[int, int]:
    """Returns the terminal size. YxX"""
    try:
        size = get_terminal_size()
        return size.lines, size.columns
    except OSError:
        return 24, 80


async def screen_dimmension_check() -> bool:
    """This will check the window size."""

    max_y: int = 0
    max_x: int = 0

    max_y, max_x = await enhanced_get_t_size()
    return False if (max_y < MIN_Y or max_x < MIN_X) else True


async def screen_dimmension_warning(stdscr: window) -> window:
    """This will display the warning to the user."""

    max_y: int = 0
    max_x: int = 0

    max_y, max_x = await enhanced_get_t_size()

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
