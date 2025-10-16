"""This is a starter file for tetr_cli. This will be sent to main to reduce confusions."""
# coding: utf-8

from asyncio import run, CancelledError
from threading import Lock
from typing import Set
from sys import argv

from keyboard import hook, unhook_all  # type: ignore

from tetr_cli.main import main


def starter() -> None:
    """The true starter of the code."""
    pressed_keys: Set[str] = set()
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
        run(main(pressed_keys, True if len(argv) > 1 else False))
        print("\n\n")
        print("Thank you for playing!")
        print("Game made by Airun_Iru")
    except (CancelledError, KeyboardInterrupt):
        print("Force quit detected!")
        unhook_all()
        exit(-1)
    unhook_all()


if __name__ == "__main__":
    starter()
