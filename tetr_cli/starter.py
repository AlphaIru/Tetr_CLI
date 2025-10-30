"""This is a starter file for tetr_cli. This will be sent to main to reduce confusions."""

# coding: utf-8

from asyncio import run, CancelledError
from curses import endwin, isendwin
from sys import argv, exit as sys_exit
from threading import Lock
from typing import Dict, List, Set

try:
    from pynput import keyboard  # type: ignore

    NO_PYNPUT = False
except ImportError:
    NO_PYNPUT = True

from tetr_cli.main import main
from tetr_cli.tetr_modules.modules.database import initialize_database
from tetr_cli.tetr_modules.input_test import run_input_test_mode

try:
    from tetr_cli.tetr_modules.keyboard_handlers.pynput_handler import (
        setup_pynput_listener,
    )
except ImportError:
    pass

help_dict: Dict[str, str] = {
    "--help, -h": "Display this help information.",
    "--debug, -d": "Enable debug mode with additional logging.",
    "--curses, --ncurses, --c": "Enable ncurses mode for terminal-based UI.",
    "--no-music, --nm": "Disable music playback during the game.",
    "--reset-db, --reset-database, --r": "Reset the game database to default settings.",
}


def parse_flag(flag_aliases: List[str]) -> bool:
    """Check if any of the given flag aliases are present in the command-line arguments."""
    return any(flag in argv for flag in flag_aliases)


def print_help() -> None:
    """Print help information for command-line flags."""
    print("\n\n")
    print("Tetr_CLI Help Information:")
    print("-------------------------\n")
    for flag, description in help_dict.items():
        if flag == "":
            print()
            continue
        print(f"{flag}:")
        print(f"    {description}")
        print()


def starter() -> None:
    """The true starter of the code."""

    debug_mode: bool = parse_flag(["--debug", "-d"])
    ncurses_mode: bool = parse_flag(["--curses", "--ncurses", "-c"])
    no_music_mode: bool = parse_flag(["--no-music", "-nm"])
    reset_database: bool = parse_flag(["--reset-db", "--reset-database", "-r"])
    print_help_call: bool = parse_flag(["--help", "-h"])

    input_test: bool = parse_flag(["--input-test", "-it"])

    if print_help_call:
        print_help()
        return

    if reset_database:
        print("\n\n")
        input_key: str = ""
        while input_key.lower() not in ("y", "n", "yes", "no"):
            input_key = input(
                "Are you sure you want to reset the settings and data?"
                " This action cannot be undone! (y/n): ",
            )
        if input_key.lower() in ("y", "yes"):
            initialize_database(reset=True)
            print("Data has been reset!")
            return
        print("Data reset has been canceled.")
        return

    initialize_database()

    if NO_PYNPUT:
        ncurses_mode = True

    pressed_keys: Set[str] = set()

    if not ncurses_mode:
        lock: Lock = Lock()
        listener: keyboard.Listener = setup_pynput_listener(pressed_keys, lock)
        listener.start()

    if input_test:
        run_input_test_mode(pressed_keys, ncurses_mode)
        return

    try:
        run(
            main(
                pressed_keys,
                debug_mode=debug_mode,
                ncurses_mode=ncurses_mode,
                no_music_mode=no_music_mode,
            )
        )
        print("\n\n")
        print("Thank you for playing!")
        print("Game made by Airun_Iru")
    except (CancelledError, KeyboardInterrupt):
        print("Force quit detected!")
        if not ncurses_mode:
            listener.stop()
        sys_exit(-1)
    finally:
        if not isendwin():
            endwin()
        if not ncurses_mode:
            listener.stop()


if __name__ == "__main__":
    starter()
