"""This will handle after the game score screen."""

# coding: utf-8

from curses import window, A_BOLD
from datetime import datetime
from typing import List, Set, Tuple

from tetr_cli.tetr_modules.menu_core.base_mode import BaseModeClass

from tetr_cli.tetr_modules.modules.constants import TARGET_FPS
from tetr_cli.tetr_modules.modules.database import get_scores, get_temp
from tetr_cli.tetr_modules.modules.safe_curses import (
    calculate_centered_menu,
    safe_addstr,
)


class ModeClass(BaseModeClass):
    """This will handle score screen mode."""

    def __init__(self) -> None:
        """This will initialize this class."""
        super().__init__()
        self.user_name: str = "You"
        self.name_input_mode: bool = False
        self.user_place: int = -1

        self.key_cooldown: int = 0
        self.cursor_blink: int = 0
        self.cursor_visible: bool = True

        self.score_temp: str = get_temp("score") or "0"
        self.score: int = int(self.score_temp)
        self.score_type: str = get_temp("score_type") or "Marathon"
        self.score_list: List[Tuple[str, int, str]] = []

    def get_high_score(self) -> None:
        """This will return the high score."""
        high_score_list: List[Tuple[str, int, str, str]] = get_scores(self.score_type)
        if self.score_type != "Sprint":
            high_score_list.sort(key=lambda x: x[1], reverse=True)
        self.score_list = [(player, score, date) for player, score, _, date in high_score_list[:5]]

    def increment_frame(self, stdscr: window, pressed_keys: Set[str]) -> None:
        """This will progress the score screen based on the inputs."""
        if not self.score_list:
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

            if inserted:
                self.name_input_mode = True
                self.score_list.pop()  # Keep only top 5 scores

        display_score_list: List[str] = []
        for list_index, (player, score, date) in enumerate(self.score_list):
            if (
                self.name_input_mode
                and list_index + 1 == self.user_place
                and self.cursor_visible
            ):
                player = player + '|'
            display_score_list.append(
                f"{list_index + 1:>2}. {player:<10} : {score:>10} at {date}"
            )
        start_y, start_x, width = calculate_centered_menu(stdscr, display_score_list)

        # Display score screen
        safe_addstr(
            stdscr,
            start_y - 2,
            (width - len("Score Screen")) // 2,
            "Score Screen",
            A_BOLD,
        )
        for list_index, stats in enumerate(display_score_list):
            safe_addstr(
                stdscr,
                start_y + list_index,
                start_x,
                stats,
            )

        if self.name_input_mode:
            if self.key_cooldown > 0:
                self.key_cooldown -= 1
                return

            if self.cursor_blink == 0:
                self.cursor_visible = not self.cursor_visible
                self.cursor_blink = TARGET_FPS // 2
            else:
                self.cursor_blink -= 1

            for key in pressed_keys:
                if len(key) != 1:
                    continue
                if key == "backspace":
                    self.user_name = self.user_name[:-1]
                    self.score_list[self.user_place - 1] = (
                        self.user_name,
                        self.score,
                        datetime.now().strftime("%Y-%m-%d"),
                    )
                elif len(self.user_name) < 10:
                    self.user_name += key
                    self.score_list[self.user_place - 1] = (
                        self.user_name,
                        self.score,
                        datetime.now().strftime("%Y-%m-%d"),
                    )
                elif key == "enter":
                    self.name_input_mode = False
                    # TODO: Save to database
            return
        confirm_keys: Set[str] = self.get_user_keybind("menu_confirm", menu_mode=True)
        if confirm_keys & pressed_keys:
            self.action["transition"] = ["Main_Menu"]
            self.sound_action["SFX"].append("select_back")


if __name__ == "__main__":
    print("This is a score_screen module, please run starter.py.")
