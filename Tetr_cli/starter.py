"""This is a starter file for Tetr_CLI. This will be sent to main to reduce confusions."""

from asyncio import run, Lock
from curses import wrapper, window
from keyboard import hook, unhook_all  # type: ignore

TARGET_FPS: int = 30
FRAME_DURATION: float = 1 / TARGET_FPS


async def async_main(stdscr: window, pressed_keys: set) -> None:
    """The true main code or base of everything."""
    stdscr.addstr(0, 0, "Curses is working!")
    stdscr.refresh()
    stdscr.getch()


def sync_to_async(stdscr: window, pressed_keys: set) -> None:
    """
    This will convert sync to async program.
        Also this wrapper is used to not screwing with the terminal
        after use.
    """
    run(async_main(stdscr, pressed_keys))


def starter() -> None:
    """The true starter of the code."""
    pressed_keys: set = set()
    lock: Lock = Lock()

    def on_key_event(event):
        """This is an event catcher when key is pressed"""
        with lock:
            if event.event_type == "down":
                pressed_keys.add(event.name)
            elif event.event_type == "up":
                pressed_keys.discard(event.name)

    hook(on_key_event)
    wrapper(sync_to_async, pressed_keys)
    unhook_all()


if __name__ == "__main__":
    starter()
