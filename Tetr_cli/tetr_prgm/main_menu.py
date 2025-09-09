"""This will define the main menu."""

from tetr_prgm.checker import checker


class MainMenu():
    """This will define the main menu."""

    def __init__(self) -> None:
        """This will initialize the main menu."""
        self.options: list[str] = [
            "Start Game",
            "Options",
            "Help",
            "Exit"
        ]
        self.current_option: int = 0


if __name__ == "__main__":
    print("This is a module. Please run main.")
