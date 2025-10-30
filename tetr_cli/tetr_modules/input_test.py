"""This will execute the input_test mode."""

from asyncio import sleep
from curses import (
    cbreak,
    curs_set,
    endwin,
    initscr,
    noecho,
    nocbreak,
    start_color,
    window,
)
from typing import Set

from tetr_cli.tetr_modules.keyboard_handlers.curses_handler import curses_key_name
from tetr_cli.tetr_modules.modules.safe_curses import safe_addstr


async def run_input_test_mode(
    pressed_keys: Set[str],
    ncurses_mode: bool = True,
) -> None:
    """Run the input test mode."""
    stdscr: window = initscr()
    start_color()
    cbreak()
    noecho()
    curs_set(False)
    stdscr.keypad(True)

    stdscr.nodelay(True)

    key: int = 0

    try:
        while True:
            safe_addstr(
                stdscr, 0, 0, "Input Test Mode Activated. Press 'Ctrl+C' to quit."
            )
            if ncurses_mode:
                key = stdscr.getch()
                if key != -1:
                    pressed_keys.clear()
                    pressed_keys.add(f"{key}")
                    pressed_keys.update(curses_key_name(key))
                stdscr.move(1, 0)
                stdscr.clrtoeol()
                stdscr.move(2, 0)
                stdscr.clrtoeol()

                safe_addstr(stdscr, 1, 0, f"Raw Key Code: {key}")
                safe_addstr(
                    stdscr, 2, 0, f"Key Name: {', '.join(curses_key_name(key))}"
                )
                # try:
                #
                # except Exception as e:
                #     safe_addstr(stdscr, 3, 0, f"Error: {e}       ")
                return

            stdscr.move(1, 0)
            stdscr.clrtoeol()

            safe_addstr(
                stdscr,
                1,
                0,
                f"Pressed Keys: {', '.join(sorted(pressed_keys))}",
            )
            stdscr.refresh()
            await sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        nocbreak()
        noecho()
        stdscr.keypad(False)
        curs_set(True)
        endwin()
