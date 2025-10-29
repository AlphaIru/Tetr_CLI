"""This will handle after the game score screen."""

# coding: utf-8

from curses import window, A_BOLD
from datetime import datetime
from typing import List, Set, Tuple

from tetr_cli.tetr_modules.menu_core.base_mode import BaseModeClass

from tetr_cli.tetr_modules.modules.constants import TARGET_FPS, VALID_CHARS
from tetr_cli.tetr_modules.modules.database import get_scores, set_scores, get_temp
from tetr_cli.tetr_modules.modules.safe_curses import (
    calculate_centered_menu,
    safe_addstr,
)


class ModeClass(BaseModeClass):
    """This will handle score screen mode."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__()
        self.game_over: bool = False

        self.user_name: str = ""
        self.name_input_mode: bool = False
        self.high_score_was_inserted: bool = False
        self.user_place: int = -1

        self.key_cooldown: int = 0
        self.cursor_blink: int = 0
        self.cursor_visible: bool = True

        self.score_temp: str = get_temp("score") or "-1"
        self.score_list: List[Tuple[str, int, str]] = []
        if self.score_temp != "-1":
            self.game_over = True
        self.score: int = int(self.score_temp)
        self.score_type: str = get_temp("score_type") or "Marathon"

    def get_high_score(self) -> None:
        """This will return the high score."""
        high_score_list: List[Tuple[str, int, str, str]] = get_scores(self.score_type)
        if self.score_type != "Sprint":
            high_score_list.sort(key=lambda x: x[1], reverse=True)
        self.score_list = [
            (player, score, date) for player, score, _, date in high_score_list[:5]
        ]

    def initialize_score_list(self) -> bool:
        """This will initialize the mode."""
        self.get_high_score()
        inserted = False
        for list_index, (_, score, _) in enumerate(self.score_list):
            if self.score >= score:
                self.score_list.insert(
                    list_index,
                    (self.user_name, self.score, datetime.now().strftime("%Y-%m-%d")),
                )
                inserted = True
                self.user_place = list_index + 1
                break
        return inserted

    def handle_blink(self) -> None:
        """This will handle the cursor blink for name input."""
        if self.cursor_blink > 0:
            self.cursor_blink -= 1
            return
        self.cursor_visible = not self.cursor_visible
        self.cursor_blink = TARGET_FPS // 2

    def handle_name_input(self, pressed_keys: Set[str]) -> None:
        """This will handle name input for high score."""
        if not pressed_keys:
            return

        input_key: str = pressed_keys.pop()

        if self.key_cooldown > 0:
            self.key_cooldown -= 1
            return

        if input_key == "backspace" and len(self.user_name) > 0:
            self.user_name = self.user_name[:-1]
            self.key_cooldown = 3
            return

        if input_key == "enter":
            self.user_name = self.user_name.strip() or "You"
            self.name_input_mode = False
            self.sound_action["SFX"].append("select_confirm")
            self.action["clear"] = []
            self.key_cooldown = 3
            set_scores(self.score_list, self.score_type)
            return

        if len(self.user_name) < 10:
            if input_key == "space":
                self.user_name += " "
                return
            if input_key in VALID_CHARS:
                self.user_name += input_key

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the score screen based on the inputs."""
        inserted: bool = False
        if not self.score_list:
            inserted = self.initialize_score_list()

        if inserted:
            self.name_input_mode = True
            self.high_score_was_inserted = True
            self.score_list.pop()  # Keep only top 5 scores

        display_score_list: List[str] = []
        for list_index, (player, score, date) in enumerate(self.score_list):
            display_score_list.append(
                f"{list_index + 1:>2}. {player:<12} : {score:>10} at {date}"
            )
        start_y, start_x, width = calculate_centered_menu(stdscr, display_score_list)

        # Display score screen
        title: str = "Game Over" if self.game_over else "Score Screen"
        safe_addstr(
            stdscr,
            start_y - 2,
            (width - len(title)) // 2,
            title,
            A_BOLD,
        )
        for list_index, stats in enumerate(display_score_list):
            safe_addstr(
                stdscr,
                start_y + list_index,
                start_x,
                stats,
            )

        bottom_prompt: str = ""

        if self.name_input_mode:
            temp_user_name: str = self.user_name
            if self.cursor_visible:
                temp_user_name += "|"
            high_score_prompt: str = (
                f"New High Score! Enter your name: {temp_user_name}"
            )
            high_score_prompt += " " * (11 - len(temp_user_name))

            safe_addstr(
                stdscr,
                start_y + len(display_score_list) + 2,
                (width - len(high_score_prompt)) // 2,
                high_score_prompt,
                A_BOLD,
            )
            bottom_prompt = "Press Enter to confirm. Backspace to delete."
            safe_addstr(
                stdscr,
                start_y + len(display_score_list) + 3,
                (width - len(bottom_prompt)) // 2,
                bottom_prompt,
                A_BOLD,
            )

            if self.cursor_blink == 0:
                self.cursor_visible = not self.cursor_visible
                self.cursor_blink = TARGET_FPS // 2
            else:
                self.cursor_blink -= 1

            self.handle_name_input(pressed_keys)
            self.score_list[self.user_place - 1] = (
                self.user_name,
                self.score,
                datetime.now().strftime("%Y-%m-%d"),
            )
            return

        bottom_prompt = "Press Enter to return to Main Menu"
        safe_addstr(
            stdscr,
            start_y + len(display_score_list) + 2,
            (width - len(bottom_prompt)) // 2,
            bottom_prompt,
            A_BOLD,
        )
        if self.score >= 0 and not self.high_score_was_inserted:
            additional_prompt: str = f"Your score is: {self.score}"
            safe_addstr(
                stdscr,
                start_y + len(display_score_list) + 3,
                (width - len(additional_prompt)) // 2,
                additional_prompt,
                A_BOLD,
            )
        if self.key_cooldown > 0:
            self.key_cooldown -= 1
            return
        if "enter" in pressed_keys:
            self.action["transition"] = ["Main_Menu"]
            self.sound_action["SFX"].append("select_back")


if __name__ == "__main__":
    print("This is a score_screen module, please run starter.py.")
