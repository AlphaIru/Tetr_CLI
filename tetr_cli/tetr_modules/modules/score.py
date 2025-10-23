"""This will handle score related functions."""
# coding: utf-8

from typing import List
from tetr_cli.tetr_modules.modules.constants import SCORE_TABLE, SCORE_NAME


def calculate_line_score(
    lines_cleared: int,
    level: int,
    t_spin: str = "",
    all_clear: bool = False,
    combo: int = 0,
    back_to_back: bool = False,
) -> tuple[int, bool, List[str]]:
    """This will calculate the score based on the given parameters."""
    base_score: int = 0
    action_text: List[str] = []
    if all_clear:
        if lines_cleared == 4 and back_to_back:
            lines_cleared = 5  # Special case for back-to-back all clear
        base_score = SCORE_TABLE["all_clear"].get(lines_cleared, 0)
        action_text.append("All Clear!")
    elif t_spin == "T-Spin":
        base_score = SCORE_TABLE["t_spin"].get(lines_cleared, 0)
        action_text.append(f"{SCORE_NAME['t_spin'][lines_cleared]}!")
    elif t_spin == "Mini T-Spin":
        base_score = SCORE_TABLE["mini_t_spin"].get(lines_cleared, 0)
        action_text.append(f"{SCORE_NAME['mini_t_spin'][lines_cleared]}!")
    else:
        base_score = SCORE_TABLE["regular"].get(lines_cleared, 0)
        if lines_cleared > 0:
            action_text.append(f"{SCORE_NAME['regular'][lines_cleared]}!")

    score = int(base_score * level)

    if lines_cleared == 0:
        # For T-Spin with 0 lines cleared or no lines cleared
        # Also for Mini T-Spin with 0 lines cleared
        return score, back_to_back, action_text

    if combo > 1:
        score += combo * 50 * level
        action_text.append(f"Combo x{combo}!")
    if lines_cleared < 4 and not t_spin:
        back_to_back = False
    elif not back_to_back:
        back_to_back = True
    else:
        score = int(score * 1.5)
        action_text = ["Back-to-Back!"] + action_text

    return score, back_to_back, action_text


def calculate_drop_score(soft_drop_distance: int, hard_drop_distance: int) -> int:
    """This will calculate the drop score based on the given distances."""
    soft_drop_score = soft_drop_distance
    hard_drop_score = hard_drop_distance * 2
    return soft_drop_score + hard_drop_score


if __name__ == "__main__":
    print("This is a score module for solo core.")
