"""This is a starter file for tetr_cli. This will be sent to main to reduce confusions."""
# coding: utf-8

from asyncio import run, CancelledError
from threading import Lock
from typing import Set
from sys import argv, exit as sys_exit

from pynput import keyboard  # type: ignore

from tetr_cli.main import main
from tetr_cli.keyboard_handlers.pynput_handler import setup_pynput_listener


def parse_flag(flag_aliases: list[str]) -> bool:
    """Check if any of the given flag aliases are present in the command-line arguments."""
    return any(flag in argv for flag in flag_aliases)


def starter() -> None:
    """The true starter of the code."""

    debug_mode: bool = parse_flag(["--debug", "-d"])
    ncurses_mode: bool = parse_flag(["--curses", "--ncurses", "--c"])

    pressed_keys: Set[str] = set()

    if not ncurses_mode:
        lock: Lock = Lock()
        listener: keyboard.Listener = setup_pynput_listener(pressed_keys, lock)
        listener.start()

    try:
        run(main(pressed_keys, debug_mode=debug_mode, ncurses_mode=ncurses_mode))
        print("\n\n")
        print("Thank you for playing!")
        print("Game made by Airun_Iru")
    except (CancelledError, KeyboardInterrupt):
        print("Force quit detected!")
        if not ncurses_mode:
            listener.stop()
        sys_exit(-1)

    if not ncurses_mode:
        listener.stop()


if __name__ == "__main__":
    starter()
