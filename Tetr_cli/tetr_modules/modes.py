"""This is where it stores the current state."""


mode_list: list[str] = [
    "menu"
]


class GameMode():
    """This will take care current game mode."""

    def __init__(self) -> None:
        self.current_mode: int = 0
        self.current: str = mode_list[0]

    def get_current_mode(self) -> int:
        """This will get the current mode."""
        return self.current_mode

    def get_current_mode_name(self) -> str:
        """This will get the current mode name."""
        return self.




if __name__ == "__main__":
    print("This is a module, please run starter.py.")