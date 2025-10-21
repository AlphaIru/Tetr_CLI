"""This will handle score related functions."""
# coding: utf-8


def calculate_line_score(
    lines_cleared: int,
    level: int,
    t_spin: str = "",
    back_to_back: bool = False,
) -> tuple[int, bool]:
    """This will calculate the score based on the given parameters."""
    if t_spin == "T-Spin":
        if lines_cleared == 1:
            base_score = 800
        elif lines_cleared == 2:
            base_score = 1200
        elif lines_cleared == 3:
            base_score = 1600
        else:
            base_score = 400
    elif t_spin == "Mini T-Spin":
        if lines_cleared == 1:
            base_score = 200
        else:
            base_score = 100
    else:
        if lines_cleared == 1:
            base_score = 100
        elif lines_cleared == 2:
            base_score = 300
        elif lines_cleared == 3:
            base_score = 500
        elif lines_cleared == 4:
            base_score = 800
        else:
            base_score = 0

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
