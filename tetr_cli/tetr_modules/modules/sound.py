"""This will handle all sound related functions."""

# coding: utf-8

from pathlib import Path
from typing import Dict, List
from pygame import mixer
from pygame.mixer import Sound


current_path: Path = Path(__file__).parent.parent.resolve()
sound_path: Path = current_path / "sounds"


async def load_sfx() -> Dict[str, Sound]:
    """Load all sound effects."""

    mixer.init()

    sound_effects = {
        "select_move": mixer.Sound(str(sound_path / "sfx/select_move.wav")),
        "select_confirm": mixer.Sound(str(sound_path / "sfx/select_confirm.wav")),
        "select_back": mixer.Sound(str(sound_path / "sfx/select_back.wav")),
        "single": mixer.Sound(str(sound_path / "sfx/single.wav")),
        "double": mixer.Sound(str(sound_path / "sfx/double.wav")),
        "quad": mixer.Sound(str(sound_path / "sfx/quad.wav")),
        "t_spin_single": mixer.Sound(str(sound_path / "sfx/t_spin_single.wav")),
        "t_spin_double": mixer.Sound(str(sound_path / "sfx/t_spin_double.wav")),
        "t_spin_triple": mixer.Sound(str(sound_path / "sfx/t_spin_triple.wav")),
        "countdown": mixer.Sound(str(sound_path / "sfx/countdown.wav")),
        "go": mixer.Sound(str(sound_path / "sfx/go.wav")),
    }
    return sound_effects


async def play_sounds(
    sound_action: Dict[str, List[str]],
    current_bgm: str,
    sound_effect_dict: Dict[str, Sound],
) -> str:
    """Play sounds."""

    if sound_action and "BGM" in sound_action:
        if not sound_action["BGM"] or sound_action["BGM"][0] == "stop":
            mixer.music.stop()
            current_bgm = ""
        elif sound_action["BGM"][0] != current_bgm:
            current_bgm = sound_action["BGM"][0]
            try:
                mixer.music.load(str(sound_path / f"bgm/{current_bgm}.wav"))
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


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
