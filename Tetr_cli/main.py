"""The true main program."""

# coding: utf-8

from asyncio import sleep
from pathlib import Path

from curses import (
    cbreak,
    COLOR_CYAN,  # I
    COLOR_GREEN,  # S
    COLOR_MAGENTA,  # T
    COLOR_RED,  # Z
    COLOR_YELLOW,  # O
    COLOR_BLUE,  # J
    curs_set,
    doupdate,
    initscr,
    init_pair,
    endwin,
    noecho,
    start_color,
    resize_term,
    use_default_colors,
    window,
    KEY_RESIZE,
)
from pygame import mixer
from pygame.mixer import Sound

from tetr_modules.checker import screen_dimension_check, screen_dimension_warning
from tetr_modules.debug import DebugClass
from tetr_modules.mode import GameMode


TARGET_FPS: int = 30
FRAME_DURATION: float = 1 / TARGET_FPS


current_path: Path = Path(__file__).parent.parent.resolve()

# O, I, T, L, J, S, Z


async def load_sfx() -> dict[str, Sound]:
    """Load all sound effects."""

    mixer.init()

    sound_effects = {
        "select_move": mixer.Sound(
            str(current_path / "Tetr_cli/tetr_modules/sounds/sfx/select_move.wav")
        ),
        "select_confirm": mixer.Sound(
            str(current_path / "Tetr_cli/tetr_modules/sounds/sfx/quad.wav")
        ),
        "quad": mixer.Sound(
            str(current_path / "Tetr_cli/tetr_modules/sounds/sfx/quad.wav")
        ),
        "3_2_1": mixer.Sound(
            str(current_path / "Tetr_cli/tetr_modules/sounds/sfx/3_2_1.wav")
        ),
        "go": mixer.Sound(
            str(current_path / "Tetr_cli/tetr_modules/sounds/sfx/go.wav")
        )
    }
    return sound_effects


async def play_sounds(
    sound_action: dict[str, list[str]],
    current_bgm: str,
    sound_effect_dict: dict[str, Sound],
) -> str:
    """Play sounds."""

    if sound_action and "BGM" in sound_action:
        if not sound_action["BGM"] or sound_action["BGM"][0] == "stop":
            mixer.music.stop()
            current_bgm = ""
        elif sound_action["BGM"][0] != current_bgm:
            current_bgm = sound_action["BGM"][0]
            try:
                mixer.music.load(
                    str(current_path / f"Tetr_cli/tetr_modules/sounds/bgm/{current_bgm}.wav")
                )
                mixer.music.play(-1)
            except Exception as err:
                print(f"Failed to load or play BGM: {err}")

    if sound_action and "SFX" in sound_action:
        for sfx in sound_action["SFX"]:
            try:
                sound_effect_dict[sfx].play()
            except Exception as err:
                print(f"Failed to play SFX: {err}")
    return current_bgm


async def run_action(action: str, current_mode: GameMode) -> GameMode:
    """Run the action."""
    if action == "Solo":
        current_mode.change_mode("solo_menu")
    elif action == "Go_Back":
        current_mode.change_mode("main_menu")
    elif action == "Marathon":
        current_mode.change_mode("marathon")
    return current_mode


async def main(pressed_keys: set[str], debug_mode: bool) -> None:
    """The true main code or base of everything."""
    debug_stats: DebugClass = DebugClass()

    mixer.init()
    mixer.music.set_volume(0.25)

    sound_effect_dict: dict[str, Sound] = await load_sfx()

    stdscr: window = initscr()
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

    use_default_colors()
    init_pair(1, COLOR_YELLOW, -1)  # O
    init_pair(2, COLOR_CYAN, -1)    # I
    init_pair(3, COLOR_MAGENTA, -1)  # T
    init_pair(4, 208, -1)  # L
    init_pair(5, COLOR_BLUE, -1)     # J
    init_pair(6, COLOR_GREEN, -1)    # S
    init_pair(7, COLOR_RED, -1)      # Z

    while True:
        await sleep(FRAME_DURATION)
        key = stdscr.getch()
        # stdscr.clear()

        if key == KEY_RESIZE:
            resize_term(*stdscr.getmaxyx())
            stdscr.clear()
            stdscr.refresh()

        stdscr.noutrefresh()

        if debug_mode:
            debug_stats.update_keypress(keypress=pressed_keys)
            debug_stats.update_current_mode(
                new_mode=current_mode.get_current_mode_name()
            )
            stdscr = debug_stats.update_debug(stdscr=stdscr)

        current_mode.increment_frame(stdscr=stdscr, pressed_keys=pressed_keys)
        doupdate()

        if await screen_dimension_check(stdscr=stdscr) is False:
            stdscr.clear()
            stdscr = await screen_dimension_warning(stdscr=stdscr)
            stdscr = debug_stats.update_debug(stdscr=stdscr)
            doupdate()
            continue

        # stdscr.refresh()

        sound_action: dict[str, list[str]] = current_mode.get_sound_action()
        current_bgm = await play_sounds(
            sound_action=sound_action,
            current_bgm=current_bgm,
            sound_effect_dict=sound_effect_dict,
        )

        action: str = current_mode.get_mode_action()
        if action == "Quit":
            mixer.music.stop()
            mixer.quit()
            break
        if action:
            stdscr.clear()
            current_mode = await run_action(action=action, current_mode=current_mode)

        if action and pressed_keys is not None:
            pressed_keys.clear()

    endwin()


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
