"""This will handle the solo game mode."""

# coding: utf-8

from copy import deepcopy
from curses import window


# Flowchart:
# Generation 0phase
# Falling phase
# if Hard drop:
#   go to pattern phase.
# Lock phase:
# if moved:
#   if there is space to fall:
#       go to falling phase.
#   else:
#       if lock delay is up:
#           go to lock phase.
#       else:
#           go to pattern phase.
# else:
#   go to pattern phase.
# Pattern phase:
# if pattern:
#   mark for deletion.
# Iterate phase:
# Animation phase:
# Deletion phase:
# Completion phase:
#
# Repeat from Generation phase.


class ModeClass:
    """This will handle the solo game mode."""

    POINTS_TABLE: dict[str, int] = {
        "Single": 100,
        "Double": 300,
        "Triple": 500,
        "Tetris": 800,
        "Mini_Tspin": 100,
        "Mini_Tspin_Single": 200,
        "Tspin": 400,
        "Tspin_Single": 800,
        "Tspin_Double": 1200,
        "Tspin_Triple": 1600,
    }
    BOARD_WIDTH: int = 10
    BOARD_HEIGHT: int = 20

    def __init__(self) -> None:
        """This will initialize this class."""
        self.__countdown: int = 60
        self.__board = self.generate_board()
        self.__action: str = ""
        self.__sound_action: dict[str, list[str]] = {"BGM": ["Korobeiniki"], "SFX": []}

    def pop_action(self) -> str:
        """This will return the action and reset it."""
        action = self.__action
        self.__action = ""
        return action

    def pop_sound_action(self) -> dict[str, list[str]]:
        """This will return the sound action and reset it."""
        sound_action: dict[str, list[str]] = deepcopy(self.__sound_action)
        self.__sound_action["SFX"] = []
        return sound_action

    def generate_board(self) -> list[list[int]]:
        """Generate an empty Tetris board."""
        board: list[list[int]] = []
        for y in range(self.BOARD_HEIGHT):
            if y == self.BOARD_HEIGHT - 1:
                row = [1] * self.BOARD_WIDTH
            elif y % 2 == 0:
                row = [
                    1 if x in (0, self.BOARD_WIDTH - 1) else 0
                    for x in range(self.BOARD_WIDTH)
                ]
            else:
                row = [0] * self.BOARD_WIDTH
            board.append(row)
        return board

    def draw_board(self, stdscr: window) -> window:
        """Draw the Game board centered on the screen."""
        max_y, max_x = stdscr.getmaxyx()
        board_height = self.BOARD_HEIGHT
        board_width = self.BOARD_WIDTH * 2  # Each cell is 2 chars wide

        # Calculate centered offsets if not provided
        offset_y: int = (max_y - board_height) // 2
        offset_x: int = (max_x - board_width) // 2

        # Draw top border
        stdscr.addstr(offset_y - 1, offset_x - 1, "+" + "-" * board_width + "+")

        # Draw side borders and cells
        for column, row in enumerate(self.__board):
            stdscr.addstr(offset_y + column, offset_x - 2, "|")  # Left border
            for x, cell in enumerate(row):
                char = "█" if cell else " "
                stdscr.addstr(offset_y + column, offset_x + x * 2, char * 2)
            stdscr.addstr(
                offset_y + column, offset_x + board_width, "|"
            )  # Right border

        # Draw bottom border
        stdscr.addstr(
            offset_y + board_height,
            offset_x - 1,
            "+" + "-" * board_width + "+",
        )
        return stdscr

    def increment_frame(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will progress the game based on the inputs."""
        stdscr = self.draw_board(stdscr)

        if "esc" in pressed_keys:
            self.__action = "Go_Back"
            return stdscr

        return stdscr


if __name__ == "__main__":
    print("This is a module, please run starter.py.")
