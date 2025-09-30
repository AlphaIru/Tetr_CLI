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
from pygame.mixer import Sound

from tetr_modules.checker import screen_dimmension_check, screen_dimmension_warning
from tetr_modules.debug import DebugClass
from tetr_modules.mode import GameMode


TARGET_FPS: int = 30
FRAME_DURATION: float = 1 / TARGET_FPS


async def main(pressed_keys: set[str], debug_mode: bool) -> None:
    """The true main code or base of everything."""
    debug_stats: DebugClass = DebugClass()

    mixer.init()
    mixer.music.set_volume(0.25)
    select_move_sound: Sound = mixer.Sound(
        "Tetr_cli/tetr_modules/sounds/sfx/select_move.wav"
    )
    quad_sound: Sound = mixer.Sound("Tetr_cli/tetr_modules/sounds/sfx/quad.wav")

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
    current_bgm: str = ""

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

        sound_action: dict[str, list[str]] = current_mode.get_sound_action()
        if sound_action and "BGM" in sound_action:
            if sound_action["BGM"][0] == "stop":
                mixer.music.stop()
                current_bgm = ""
            elif sound_action["BGM"][0] != current_bgm:
                current_bgm = sound_action["BGM"][0]
                try:
                    mixer.music.load(
                        f"Tetr_cli/tetr_modules/sounds/bgm/{current_bgm}.wav"
                    )
                    mixer.music.play(-1)
                except Exception as err:
                    print(f"Failed to load or play BGM: {err}")
        if sound_action and "SFX" in sound_action:
            for sfx in sound_action["SFX"]:
                try:
                    if sfx == "select_move":
                        select_move_sound.play()
                    elif sfx == "select_confirm" or sfx == "quad":
                        quad_sound.play()
                except Exception as err:
                    print(f"Failed to play SFX: {err}")

        action: str = current_mode.get_mode_action()
        if action == "Quit":  # wait for sound to play
            mixer.music.stop()
            mixer.quit()
            break
        if action == "Solo":
            current_mode.change_mode("solo_menu")
        elif action == "Go_Back":
            current_mode.change_mode("main_menu")
        elif action == "Marathon":
            current_mode.change_mode("marathon")

        if action and pressed_keys is not None:
            pressed_keys.clear()

    endwin()


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
