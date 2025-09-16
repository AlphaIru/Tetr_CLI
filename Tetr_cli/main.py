"""The true main program."""

from asyncio import sleep

from curses import (
    cbreak,
    curs_set,
    initscr,
    endwin,
    noecho,
    start_color,
    resize_term,
    KEY_RESIZE,
)

from tetr_modules.checker import screen_dimmension_check, screen_dimmension_warning
from tetr_modules.debug import DebugClass
from tetr_modules.modes import GameMode

# from keyboard import


TARGET_FPS: int = 30
FRAME_DURATION: float = 1 / TARGET_FPS


async def main(pressed_keys: set, debug_mode: bool) -> None:
    """The true main code or base of everything."""
    debug_stats: DebugClass = DebugClass()

    stdscr = initscr()
    start_color()
    cbreak()
    noecho()
    curs_set(False)
    stdscr.keypad(True)

    stdscr.nodelay(True)
    key: int = 0
    current_mode: GameMode = GameMode()

    while True:
        await sleep(FRAME_DURATION)
        key = stdscr.getch()
        stdscr.clear()

        if key == KEY_RESIZE:
            resize_term(*stdscr.getmaxyx())
            stdscr.clear()
            stdscr.refresh()

        current_mode.increment_frame(stdscr=stdscr)

        if debug_mode:
            debug_stats.update_keypress(keypress=pressed_keys)
            stdscr = debug_stats.update_debug(stdscr=stdscr)

        if await screen_dimmension_check(stdscr=stdscr) is False:
            stdscr = await screen_dimmension_warning(stdscr=stdscr)
            stdscr.refresh()
            continue

        stdscr.addstr(0, 0, "Curses is working!")

        # await sleep(FRAME_DURATION)

        stdscr.refresh()

        if "esc" in pressed_keys:
            break

    endwin()


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
