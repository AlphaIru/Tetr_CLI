"""This will handle the solo game mode."""

# coding: utf-8

from copy import deepcopy
from curses import window, A_BOLD
from random import shuffle, seed, randint

# from math import floor


# TODO: Flowchart:
# DONE: Generation 0phase
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
DRAW_BOARD_WIDTH: int = BOARD_WIDTH * 2  # Each cell is 2 chars wide
BOARD_HEIGHT: int = 20
TARGET_FPS: int = 30
MINO_TYPES: set[str] = {"I", "O", "T", "S", "Z", "J", "L"}


class ModeClass:
    """This will handle the solo game mode."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.__action: str = ""
        self.__countdown: int = TARGET_FPS * 3  # 3 seconds countdown

        self.__seed_value: int = 0
        self.__sound_action: dict[str, list[str]] = {"BGM": ["stop"], "SFX": []}
        self.__mode: str = "countdown"

        self.__board = [([0] * BOARD_WIDTH) for _ in range(BOARD_HEIGHT)]
        self.__max_y: int = 0
        self.__max_x: int = 0
        self.__offset_x: int = 0
        self.__offset_y: int = 0

        self.__current_mino: str = ""
        self.__current_rotation: str = "0"
        self.__current_position: tuple[int, int] = (0, 0)  # (y, x)
        self.__current_hold: str = ""

        self.__mino_list: list[str] = []
        self.mino_generation(initial=True)

    def pop_action(self) -> str:
        """This will return the action and reset it."""
        action: str = deepcopy(self.__action)
        self.__action = ""
        return action

    def pop_sound_action(self) -> dict[str, list[str]]:
        """This will return the sound action and reset it."""
        sound_action: dict[str, list[str]] = deepcopy(self.__sound_action)
        self.__sound_action["SFX"] = []
        return sound_action

    def draw_hold(self, stdscr: window) -> window:
        """Draw the Hold Box."""
        hold_offset_x: int = self.__offset_x - 12
        horizontal_line: str = "+" + "-" * 9
        stdscr.addstr(
            self.__offset_y - 1,
            hold_offset_x,
            horizontal_line,
            A_BOLD,
        )
        stdscr.addstr(
            self.__offset_y,
            hold_offset_x + 2,
            "Hold",
            A_BOLD,
        )
        stdscr.addstr(
            self.__offset_y + 1,
            hold_offset_x,
            horizontal_line,
            A_BOLD,
        )
        for counter in range(5):
            stdscr.addstr(
                self.__offset_y + counter,
                hold_offset_x,
                "|",
                A_BOLD,
            )
        stdscr.addstr(
            self.__offset_y + 5,
            hold_offset_x,
            horizontal_line,
            A_BOLD,
        )
        return stdscr

    def draw_queue(self, stdscr: window) -> window:
        """Draw the Next Queue Box."""

        queue_offset_x: int = self.__offset_x + DRAW_BOARD_WIDTH + 1
        horizontal_line: str = "-" * 9 + "+"

        stdscr.addstr(
            self.__offset_y - 1,
            queue_offset_x,
            horizontal_line,
            A_BOLD,
        )
        stdscr.addstr(
            self.__offset_y,
            queue_offset_x + 2,
            "Next",
            A_BOLD,
        )
        stdscr.addstr(
            self.__offset_y + 1,
            queue_offset_x,
            horizontal_line,
            A_BOLD,
        )
        for counter in range(15):
            stdscr.addstr(
                self.__offset_y + counter,
                queue_offset_x + 10,
                "|",
                A_BOLD,
            )
        stdscr.addstr(
            self.__offset_y + 15,
            queue_offset_x,
            horizontal_line,
            A_BOLD,
        )
        return stdscr

    def draw_board(self, stdscr: window) -> window:
        """Draw the Game board centered on the screen."""

        # Draw top border
        stdscr.addstr(
            self.__offset_y - 1, self.__offset_x - 1, "+" + "-" * DRAW_BOARD_WIDTH + "+"
        )

        # Draw side borders and cells
        for column, row in enumerate(self.__board):
            stdscr.addstr(
                self.__offset_y + column, self.__offset_x - 2, "|", A_BOLD
            )  # Left border
            for x, cell in enumerate(row):
                char = "█" if cell else " "
                stdscr.addstr(
                    self.__offset_y + column, self.__offset_x + x * 2, char * 2
                )
            stdscr.addstr(
                self.__offset_y + column,
                self.__offset_x + DRAW_BOARD_WIDTH,
                "|",
                A_BOLD,
            )  # Right border

        # Draw bottom border
        stdscr.addstr(
            self.__offset_y + BOARD_HEIGHT,
            self.__offset_x - 1,
            "+" + "-" * DRAW_BOARD_WIDTH + "+",
            A_BOLD,
        )

        return stdscr

    def countdown_mode(self, stdscr: window) -> None:
        """This will handle the countdown mode."""
        if self.__countdown >= 0:
            stdscr.addstr(
                self.__max_y // 2,
                self.__max_x // 2,
                str((self.__countdown // TARGET_FPS) + 1),
                A_BOLD,
            )

        if self.__countdown % TARGET_FPS == 0:
            if self.__countdown > 0:
                self.__sound_action["SFX"].append("3_2_1")

        self.__countdown -= 1
        if self.__countdown <= 0:
            self.__mode = "play"
            self.__sound_action["BGM"] = ["Korobeiniki"]
            self.__sound_action["SFX"].append("go")
            stdscr.addstr(self.__max_y // 2, self.__max_x // 2, "Go", A_BOLD)

    def mino_generation(self, initial: bool = False) -> None:
        """This will handle the mino generation."""
        if initial:
            self.__seed_value = 42  # randint(1, 1000000000)
            seed(self.__seed_value)
            while len(self.__mino_list) <= 14:
                new_mino_list = list(MINO_TYPES)
                shuffle(new_mino_list)
                self.__mino_list.extend(new_mino_list)
        new_mino_list = list(MINO_TYPES)
        shuffle(new_mino_list)
        self.__mino_list.extend(new_mino_list)

    def play_mode(self, stdscr: window) -> None:
        """This will handle the play mode."""
        if len(self.__mino_list) <= 14:
            self.mino_generation()

    def increment_frame(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will progress the game based on the inputs."""

        check_max_y, check_max_x = stdscr.getmaxyx()
        if check_max_y != self.__max_y or check_max_x != self.__max_x:
            self.__max_y = check_max_y
            self.__max_x = check_max_x
            self.__offset_y = (check_max_y - BOARD_HEIGHT) // 2
            self.__offset_x = (check_max_x - DRAW_BOARD_WIDTH) // 2

        stdscr = self.draw_board(stdscr)
        stdscr = self.draw_queue(stdscr)
        stdscr = self.draw_hold(stdscr)

        if "esc" in pressed_keys:
            self.__action = "Go_Back"
            return stdscr

        if self.__mode == "play":
            self.play_mode(stdscr)
        elif self.__mode == "countdown":
            self.countdown_mode(stdscr)

        return stdscr


if __name__ == "__main__":
    print("This is a module, please run starter.py.")
