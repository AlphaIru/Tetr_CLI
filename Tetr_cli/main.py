"""The true main program."""

# coding: utf-8

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
from pygame import mixer

from tetr_modules.checker import screen_dimmension_check, screen_dimmension_warning
from tetr_modules.debug import DebugClass
from tetr_modules.mode import GameMode


TARGET_FPS: int = 30
FRAME_DURATION: float = 1 / TARGET_FPS


async def main(pressed_keys: set[str], debug_mode: bool) -> None:
    """The true main code or base of everything."""
    debug_stats: DebugClass = DebugClass()

    mixer.init()

    stdscr = initscr()
    start_color()
    cbreak()
    noecho()
    curs_set(False)
    stdscr.keypad(True)

    stdscr.nodelay(True)
    key: int = 0
    current_mode: GameMode = GameMode()
    current_mode.change_mode("main_menu")

    while True:
        await sleep(FRAME_DURATION)
        key = stdscr.getch()
        stdscr.clear()

        if key == KEY_RESIZE:
            resize_term(*stdscr.getmaxyx())
            stdscr.clear()
            stdscr.refresh()

        current_mode.increment_frame(stdscr=stdscr, pressed_keys=pressed_keys)

        if debug_mode:
            debug_stats.update_keypress(keypress=pressed_keys)
            debug_stats.update_current_mode(
                new_mode=current_mode.get_current_mode_name()
            )
            stdscr = debug_stats.update_debug(stdscr=stdscr)

        if await screen_dimmension_check(stdscr=stdscr) is False:
            stdscr.clear()
            stdscr = await screen_dimmension_warning(stdscr=stdscr)
            stdscr = debug_stats.update_debug(stdscr=stdscr)
            stdscr.refresh()
            continue

        stdscr.refresh()

        action: str = current_mode.get_mode_action()
        if action == "Quit":
            break
        if action == "Solo":
            current_mode.change_mode("solo_menu")
        elif action == "Go_Back":
            current_mode.change_mode("main_menu")
        elif action == "Marathon":
            current_mode.change_mode("marathon")

        sound_action: dict[str, str | list[str]] = current_mode.get_sound_action()
        if sound_action and "BGM" in sound_action:
            if sound_action["BGM"] == "stop":
                mixer.music.stop()
            else:
                try:
                    mixer.music.load(
                        f"Tetr_cli/tetr_modules/sounds/bgm/{sound_action['BGM']}.wav"
                    )
                    mixer.music.play(-1)
                except Exception as err:
                    print(f"Failed to load or play BGM: {err}")
        if sound_action and "SFX" in sound_action:
            sfx_list: list[str] = sound_action["SFX"]  # type: ignore
            for sfx in sfx_list:
                try:
                    sound = mixer.Sound(f"Tetr_cli/tetr_modules/sounds/sfx/{sfx}.wav")
                    sound.play()
                except Exception as err:
                    print(f"Failed to load or play SFX: {err}")

        if action and pressed_keys is not None:
            pressed_keys.clear()

    endwin()


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
