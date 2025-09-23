"""This is a starter file for Tetr_CLI. This will be sent to main to reduce confusions."""
# coding: utf-8

from asyncio import run, CancelledError
from threading import Lock
from sys import argv

from keyboard import hook, unhook_all  # type: ignore

from main import main


def starter(argv_console: list[str]) -> None:
    """The true starter of the code."""
    pressed_keys: set[str] = set()
    lock: Lock = Lock()

    def on_key_event(event):
        """This is an event catcher when key is pressed"""
        with lock:
            if event.event_type == "down":
                pressed_keys.add(event.name)
            elif event.event_type == "up":
                pressed_keys.discard(event.name)

    hook(on_key_event)
    try:
        run(main(pressed_keys, True if len(argv_console) > 1 else False))
    except (CancelledError, KeyboardInterrupt):
        print("Force quit detected!")
        unhook_all()
        exit(-1)
    unhook_all()


if __name__ == "__main__":
    starter(argv)
