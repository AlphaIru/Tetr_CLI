"""The true main program."""

# coding: utf-8

from asyncio import sleep
from time import perf_counter
from typing import Set, Dict, List

import curses
from curses import (
    cbreak,
    COLOR_CYAN,  # I
    COLOR_GREEN,  # S
    COLOR_MAGENTA,  # T
    COLOR_RED,  # Z
    COLOR_YELLOW,  # O
    COLOR_BLUE,  # J
    COLOR_WHITE,  # Light gray
    COLOR_BLACK,  # Dark gray
    # COLORS,
    curs_set,
    doupdate,
    initscr,
    init_pair,
    endwin,
    nocbreak,
    noecho,
    start_color,
    resize_term,
    use_default_colors,
    window,
    KEY_RESIZE,
)
from pygame import mixer
from pygame.mixer import Sound

from tetr_cli.tetr_modules.keyboard_handlers.curses_handler import curses_key_name

from tetr_cli.tetr_modules.mode import GameMode
from tetr_cli.tetr_modules.modules.checker import (
    screen_dimension_check,
    screen_dimension_warning,
)
from tetr_cli.tetr_modules.modules.constants import TARGET_FPS
from tetr_cli.tetr_modules.modules.debug import DebugClass
from tetr_cli.tetr_modules.modules.sound import load_sfx, play_sounds


FRAME_DURATION: float = 1 / TARGET_FPS

# O, I, T, L, J, S, Z


async def run_transition(transition: str, current_mode: GameMode) -> GameMode:
    """Run the action."""
    if transition == "Solo_Menu":
        current_mode.change_mode("solo_menu")
    elif transition == "Option_Menu":
        current_mode.change_mode("option")
    elif transition == "Main_Menu":
        current_mode.change_mode("main_menu")
    elif transition == "Score_Screen":
        current_mode.change_mode("score_screen")
    elif transition == "Marathon":
        current_mode.change_mode("marathon")
    return current_mode


async def main(
    pressed_keys: Set[str],
    debug_mode: bool,
    ncurses_mode: bool = True,
    no_music_mode: bool = False,
) -> None:
    """The true main code or base of everything."""
    debug_stats: DebugClass = DebugClass()

    audio_check: bool = not no_music_mode
    try:
        mixer.init()
        mixer.music.set_volume(0.25)
        sound_effect_dict: Dict[str, Sound] = await load_sfx()
    except Exception:
        audio_check = False

    stdscr: window = initscr()
    start_color()
    cbreak()
    noecho()
    nocbreak()
    curs_set(False)
    stdscr.keypad(True)

    stdscr.nodelay(True)
    key_input: int = 0
    current_mode: GameMode = GameMode()
    current_mode.change_mode("main_menu")
    current_bgm: str = ""

    use_default_colors()

    if curses.COLORS >= 256:
        init_pair(1, COLOR_YELLOW, -1)  # O
        init_pair(2, COLOR_CYAN, -1)  # I
        init_pair(3, COLOR_MAGENTA, -1)  # T
        init_pair(4, 208, -1)  # L
        init_pair(5, COLOR_BLUE, -1)  # J
        init_pair(6, COLOR_GREEN, -1)  # S
        init_pair(7, COLOR_RED, -1)  # Z
        init_pair(8, 244, -1)  # Garbage
    else:
        init_pair(1, COLOR_YELLOW, -1)  # O
        init_pair(2, COLOR_CYAN, -1)  # I
        init_pair(3, COLOR_MAGENTA, -1)  # T
        init_pair(4, COLOR_YELLOW, COLOR_BLACK)  # L
        init_pair(5, COLOR_BLUE, -1)  # J
        init_pair(6, COLOR_GREEN, -1)  # S
        init_pair(7, COLOR_RED, -1)  # Z
        init_pair(8, COLOR_WHITE, COLOR_BLACK)  # Light gray on black

    start_time: float = 0.0
    elapsed_time: float = 0.0

    try:
        while True:
            if elapsed_time < FRAME_DURATION:
                await sleep(FRAME_DURATION - elapsed_time)
            start_time = perf_counter()

            key_input = stdscr.getch()
            # stdscr.clear()

            if key_input == KEY_RESIZE:
                resize_term(*stdscr.getmaxyx())
                stdscr.clear()
                stdscr.refresh()

            if ncurses_mode:
                if key_input == -1:
                    pressed_keys.clear()
                else:
                    pressed_keys.update(curses_key_name(key_input))

            stdscr.noutrefresh()

            if debug_mode:
                debug_stats.update_keypress(keypress=pressed_keys)
                debug_stats.update_current_mode(
                    new_mode=current_mode.get_current_mode_name()
                )
                debug_stats.update_debug(stdscr=stdscr)

            current_mode.increment_frame(stdscr=stdscr, pressed_keys=pressed_keys)
            doupdate()

            if await screen_dimension_check(stdscr=stdscr) is False:
                stdscr.clear()
                await screen_dimension_warning(stdscr=stdscr)
                if debug_mode:
                    debug_stats.update_debug(stdscr=stdscr)
                doupdate()
                elapsed_time = perf_counter() - start_time
                continue

            if audio_check:
                sound_action: Dict[str, List[str]] = current_mode.get_sound_action()
                current_bgm = await play_sounds(
                    sound_action=sound_action,
                    current_bgm=current_bgm,
                    sound_effect_dict=sound_effect_dict,
                )

            actions: Dict[str, List[str]] = current_mode.get_mode_action()
            if "transition" in actions:
                if "Quit" in actions["transition"]:
                    break
                transition_value: str = actions["transition"][0]
                current_mode = await run_transition(
                    transition=transition_value, current_mode=current_mode
                )
                stdscr.clear()
                if pressed_keys is not None:
                    pressed_keys.clear()

            if "score" in actions and "score_type" in actions:
                pass
                # current_mode.score = int(actions["score"][0])
                # current_mode.score_type = actions["score_type"][0]
            elapsed_time = perf_counter() - start_time
    except KeyboardInterrupt:
        pass

    if mixer and audio_check:
        mixer.music.stop()
        mixer.quit()
    endwin()


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
