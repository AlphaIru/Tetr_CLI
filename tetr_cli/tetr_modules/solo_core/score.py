"""This will handle score related functions."""
# coding: utf-8

from tetr_cli.tetr_modules.modules.constants import SCORE_TABLE


def calculate_line_score(
    lines_cleared: int,
    level: int,
    t_spin: str = "",
    all_clear: bool = False,
    back_to_back: bool = False,
) -> tuple[int, bool]:
    """This will calculate the score based on the given parameters."""
    base_score: int = 0
    if all_clear:
        if lines_cleared == 4 and back_to_back:
            lines_cleared = 5  # Special case for back-to-back all clear
        base_score = SCORE_TABLE["all_clear"].get(lines_cleared, 0)
    elif t_spin == "T-Spin":
        base_score = SCORE_TABLE["t_spin"].get(lines_cleared, 0)
    elif t_spin == "Mini T-Spin":
        base_score = SCORE_TABLE["mini_t_spin"].get(lines_cleared, 0)
    else:
        base_score = SCORE_TABLE["regular"].get(lines_cleared, 0)

    score = int(base_score * level)
    if back_to_back:
        score = int(score * 1.5)
    if lines_cleared < 4 and not t_spin:
        back_to_back = False
    else:
        back_to_back = True

    return score, back_to_back


def calculate_drop_score(soft_drop_distance: int, hard_drop_distance: int) -> int:
    """This will calculate the drop score based on the given distances."""
    soft_drop_score = soft_drop_distance
    hard_drop_score = hard_drop_distance * 2
    return soft_drop_score + hard_drop_score


if __name__ == "__main__":
    print("This is a score module for solo core.")
