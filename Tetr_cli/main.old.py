"""The true main program."""

# from asyncio import sleep

from curses import window, wrapper

from tetr_modules.checker import screen_dimmension_check, screen_dimmension_warning
from tetr_modules.debug import DebugClass

# from keyboard import


TARGET_FPS: int = 30
FRAME_DURATION: float = 1 / TARGET_FPS


async def signal_handler(signum, frame):
    """
    Signal handler for window resize.
    I asked AI for this one.
    """
    raise Exception("Resize detected")


async def main(pressed_keys: set, debug_mode: bool) -> None:
    """The true main code or base of everything."""
    game_continue: bool = True
    debug_stats: DebugClass = DebugClass()
    while game_continue:
        game_continue = not await run_game(debug_stats, pressed_keys, debug_mode)
    return


async def run_game(debug_stats: DebugClass, pressed_keys: set, debug_mode: bool) -> bool:
    """Recreates the terminal"""

    stdscr = wrapper(lambda stdscr: stdscr)
    stdscr.nodelay(True)

    while True:
        stdscr.clear()

        if await screen_dimmension_check() is False:
            stdscr = await screen_dimmension_warning(stdscr=stdscr)
            stdscr.refresh()
            return False

        stdscr.addstr(0, 0, "Curses is working!")

        # await sleep(FRAME_DURATION)

        if debug_mode:
            stdscr = debug_stats.update_debug(stdscr=stdscr)

        stdscr.refresh()

        if "esc" in pressed_keys:
            break

    return True


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
