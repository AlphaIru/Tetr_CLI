"""This is a main file for Tetr_CLI."""

from asyncio import run
from curses import wrapper, keyname, napms

TARGET_FPS: int = 30
FRAME_DURATION: float = 1 / TARGET_FPS


async def async_main(stdscr) -> None:
    """The true main code or base of everything."""
    # frame_count: int = 0
    # stdscr.addstr(0, 0, "Curses is working!")
    # stdscr.refresh()
    # stdscr.getch()

    stdscr.addstr(0, 0, "Press keys to see them. Press ESC to exit.")

    while True:
        stdscr.addstr(2, 0, "Waiting for key...     ")
        key = stdscr.getch()

        if key != -1:
            stdscr.clear()
            stdscr.addstr(0, 0, "Press keys to see them. Press ESC to exit.")
            stdscr.addstr(2, 0, f"Key code: {key}")
            try:
                key_name = keyname(key).decode()
            except Exception:
                key_name = str(key)
            stdscr.addstr(3, 0, f"Key name: {key_name}")

            if key == 27:  # ESC key
                break

        stdscr.refresh()
        napms(int(FRAME_DURATION))  # Sleep for 50ms (~20 FPS)


def sync_main(stdscr) -> None:
    """This will convert sync to async program."""
    run(async_main(stdscr))


if __name__ == "__main__":
    wrapper(sync_main)
