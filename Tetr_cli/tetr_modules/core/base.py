"""This holds the base attributes and methods for all modes."""

from copy import deepcopy




class BaseMode:
    """This is the base class for all modes."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.board = None
        self.current_mino = None
        self.mino_list = []
        self.current_hold = None
        self.hold_used = False
        self.level = 1
        self.lines_cleared = 0
        self.score = 0
        self.keyinput_cooldown: set[str] = set()
        self.action: str = ""
        self.sound_action: dict[str, list[str]] = {"BGM": ["stop"], "SFX": []}

    def pop_action(self) -> str:
        """This will return the action and reset it."""
        action: str = deepcopy(self.action)
        self.action = ""
        return action

    def pop_sound_action(self) -> dict[str, list[str]]:
        """This will return the sound action and reset it."""
        sound_action: dict[str, list[str]] = deepcopy(self.sound_action)
        self.sound_action["SFX"] = []
        return sound_action


if __name__ == "__main__":
    print("This is a base module for modes. Please run the starter.py.")
