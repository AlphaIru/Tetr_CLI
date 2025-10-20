"""This will handle the game board."""

# coding: utf-8

from copy import deepcopy
from typing import Optional, List, Tuple
from curses import (
    A_BOLD,
    color_pair,
    window,
)

from tetr_cli.tetr_modules.modules.constants import (
    BOARD_HEIGHT,
    BOARD_WIDTH,
    DRAW_BOARD_HEIGHT,
    DRAW_BOARD_WIDTH,
    MINO_COLOR,
    MINO_DRAW_LOCATION,
)

from tetr_cli.tetr_modules.solo_core.mino import Mino


class Board:
    """This will handle the game board."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.__line_clear_queue: List[int] = []
        self.__board: List[List[int]] = [
            ([0] * BOARD_WIDTH) for _ in range(BOARD_HEIGHT)
        ]

    def clear(self) -> None:
        """This will clear the board."""
        self.__board = [([0] * BOARD_WIDTH) for _ in range(BOARD_HEIGHT)]

    def place_mino(
        self, mino: str, orientation: str, position: Tuple[int, int]
    ) -> None:
        """This will place the mino on the board."""
        mino_shape: List[Tuple[int, int]] = MINO_DRAW_LOCATION[mino][orientation]
        for y_offset, x_offset in mino_shape:
            y_pos = position[0] + y_offset
            x_pos = position[1] + x_offset
            if 0 <= y_pos < BOARD_HEIGHT and 0 <= x_pos < BOARD_WIDTH:
                self.__board[y_pos][x_pos] = MINO_COLOR[mino]

    def is_cell_occupied(self, position: Tuple[int, int]) -> bool:
        """Check if a cell is occupied."""
        y_pos, x_pos = position
        return (
            0 <= y_pos < BOARD_HEIGHT
            and 0 <= x_pos < BOARD_WIDTH
            and self.__board[y_pos][x_pos] != 0
        )

    def check_line_filled(self) -> int:
        """This will check if any lines are filled and queue them to be cleared."""
        line_cleared: int = 0
        self.__line_clear_queue.clear()
        for row in range(BOARD_HEIGHT):
            if all(cell != 0 for cell in self.__board[row]):
                self.__line_clear_queue.append(row)
                line_cleared += 1
        return line_cleared

    def clear_lines(self) -> None:
        """This will clear the lines and return the number of lines cleared."""
        # Reverse sort to do it in ascending order
        for row in sorted(self.__line_clear_queue, reverse=True):
            del self.__board[row]
            self.__board.append([0] * BOARD_WIDTH)
        self.__line_clear_queue.clear()

    # Drawing functions

    def draw_blank_board(
        self,
        stdscr: window,
        offset: Tuple[int, int],  # (offset_y, offset_x)
    ) -> window:
        """Draw the Game board centered on the screen."""
        # Draw top border
        stdscr.addstr(
            offset[0] - 1,
            offset[1] - 1,
            "+" + "- " * (DRAW_BOARD_WIDTH // 2) + "+",
        )
        # Draw Side Borders
        middle_line: str = "|" + " " * DRAW_BOARD_WIDTH + "|"
        for row in range(DRAW_BOARD_HEIGHT):
            stdscr.addstr(
                offset[0] + row,
                offset[1] - 1,
                middle_line,
                A_BOLD,
            )
        # Draw bottom border
        stdscr.addstr(
            offset[0] + DRAW_BOARD_HEIGHT,
            offset[1] - 1,
            "+" + "-" * DRAW_BOARD_WIDTH + "+",
            A_BOLD,
        )

        return stdscr

    def draw_minos_on_board(
        self,
        stdscr: window,
        offset: Tuple[int, int],  # (offset_y, offset_x)
        max_yx: Tuple[int, int],  # (max_y, max_x)
        current_mino: Optional["Mino"] = None,  # type: ignore
        ghost_position: Tuple[int, int] = (-1, -1),
    ) -> window:
        """Draw the minos on the board."""

        draw_board: List[List[int]] = deepcopy(self.__board)
        mino_shape: List[Tuple[int, int]] = []

        if current_mino:
            mino_shape = MINO_DRAW_LOCATION[current_mino.type][
                current_mino.orientation
            ]

            # Draw ghost Mino
            for y_offset, x_offset in mino_shape:
                y_pos = ghost_position[0] + y_offset
                x_pos = ghost_position[1] + x_offset
                if 0 <= y_pos < BOARD_HEIGHT and 0 <= x_pos < BOARD_WIDTH:
                    if draw_board[y_pos][x_pos] == 0:
                        draw_board[y_pos][x_pos] = -MINO_COLOR[
                            current_mino.type
                        ]  # Ghost block

            # Draw current Mino
            mino_position: Tuple[int, int] = current_mino.position
            for y_offset, x_offset in mino_shape:
                y_pos = mino_position[0] + y_offset
                x_pos = mino_position[1] + x_offset
                if 0 <= y_pos < BOARD_HEIGHT and 0 <= x_pos < BOARD_WIDTH:
                    draw_board[y_pos][x_pos] = MINO_COLOR[current_mino.type]
            # Debug: Mark the pivot
            # draw_board[current_mino.position[0]][current_mino.position[1]] = (
            #     MINO_COLOR[current_mino.type] * 10
            # )

        # Draw cells
        max_rows: int = min(max_yx[0], BOARD_HEIGHT)
        # This is to adjust the drawing height if the terminal is too small
        adjusted_height: int = max_rows - DRAW_BOARD_HEIGHT
        visible_rows: List[List[int]] = draw_board[0:max_rows]
        for y_counter, row in enumerate(visible_rows):
            # y_counter=0 is bottom, y_counter=20 is top of box
            for x_counter, cell in enumerate(row):
                char: str = "  "
                if visible_rows[y_counter][x_counter] > 0:
                    char = "██"
                    # Debug for marking pivot
                    # char = "██" if visible_rows[y_counter][x_counter] < 10 else "●●"
                elif visible_rows[y_counter][x_counter] < 0:
                    char = "▒▒"
                elif y_counter == 20:
                    char = "- "
                # The extra -1 is to adjust for zero indexing
                y: int = offset[0] + ((max_rows - 1) - y_counter) - adjusted_height
                x: int = offset[1] + x_counter * 2
                color: int = abs(cell)
                if 0 <= y < max_yx[0] and 0 <= x < max_yx[1] - 1:
                    stdscr.addstr(
                        y,
                        x,
                        char,
                        color_pair(color) if cell else A_BOLD,
                    )
        return stdscr

    def draw_queue(
        self,
        stdscr: window,
        offset: Tuple[int, int],  # (offset_y, offset_x)
        max_yx: Tuple[int, int],  # (max_y, max_x)
        queue_list: List[str],
    ) -> window:
        """Draw the next mino queue."""

        queue_offset: Tuple[int, int] = (offset[0], offset[1] + DRAW_BOARD_WIDTH + 1)
        horizontal_length: int = 12
        horizontal_line: str = "-" * horizontal_length + "+"
        vertical_length: int = 17

        # Draw the box and text
        stdscr.addstr(queue_offset[0] - 1, queue_offset[1], horizontal_line, A_BOLD)
        stdscr.addstr(queue_offset[0], queue_offset[1] + 2, "Next", A_BOLD)
        stdscr.addstr(queue_offset[0] + 1, queue_offset[1], horizontal_line, A_BOLD)
        for counter in range(vertical_length):
            stdscr.addstr(
                queue_offset[0] + counter,
                queue_offset[1] + horizontal_length,
                "|",
                A_BOLD,
            )
        stdscr.addstr(
            queue_offset[0] + vertical_length, queue_offset[1], horizontal_line, A_BOLD
        )

        mino_offset: Tuple[int, int] = (0, 0)
        pos: Tuple[int, int] = (0, 0)

        mino_height: int = 2
        mino_width: int = 4
        queue_length: int = 5

        # Clear the queue area before drawing (prevents leftover blocks)
        for queue_counter in range(queue_length):
            mino_offset = (queue_offset[0] + 2 + queue_counter * 3, queue_offset[1])
            for y_offset in range(mino_height):  # max mino height
                # max mino width (4 blocks * 2 chars + 2 for borders)
                for x_offset in range(mino_width * 2 + 2):
                    pos = (mino_offset[0] + y_offset, mino_offset[1] + x_offset)
                    if 0 <= pos[0] < max_yx[0] and 0 <= pos[1] < max_yx[1] - 1:
                        stdscr.addstr(pos[0], pos[1], "  ", A_BOLD)

        # Draw the next minos using block positions
        for queue_counter in range(queue_length):
            if len(queue_list) > queue_counter:
                mino: str = queue_list[queue_counter]
                orientation: str = "N"
                mino_offset = (
                    queue_offset[0] + 2 + queue_counter * 3,
                    queue_offset[1] + 4,
                )
                mino_shape: List[Tuple[int, int]] = MINO_DRAW_LOCATION[mino][orientation]
                for y_offset, x_offset in mino_shape:
                    pos = (
                        mino_offset[0] + (mino_height - 1 - y_offset),
                        mino_offset[1] + x_offset * 2,
                    )
                    if 0 <= pos[0] < max_yx[0] and 0 <= pos[1] < max_yx[1] - 1:
                        stdscr.addstr(
                            pos[0],
                            pos[1],
                            "██",
                            color_pair(MINO_COLOR.get(mino, 0)),
                        )
        return stdscr

    def draw_hold(
        self,
        stdscr: window,
        offset: Tuple[int, int],  # (offset_y, offset_x)
        max_yx: Tuple[int, int],  # (max_y, max_x)
        hold_used: bool,
        hold_mino: Optional["Mino"] = None,  # type: ignore
    ) -> window:
        """Draw the hold mino box."""

        horizontal_length: int = 12
        vertical_length: int = 6
        hold_offset: Tuple[int, int] = (offset[0], offset[1] - horizontal_length - 3)
        horizontal_line: str = "+" + "-" * horizontal_length

        # Draw top
        stdscr.addstr(
            hold_offset[0] - 1,
            hold_offset[1],
            horizontal_line,
            A_BOLD,
        )
        stdscr.addstr(
            hold_offset[0],
            hold_offset[1] + 2,
            "Hold",
            A_BOLD,
        )
        stdscr.addstr(
            hold_offset[0] + 1,
            hold_offset[1],
            horizontal_line,
            A_BOLD,
        )
        # Draw side
        for counter in range(vertical_length):
            stdscr.addstr(
                hold_offset[0] + counter,
                hold_offset[1],
                "|",
                A_BOLD,
            )
        # Draw bottom
        stdscr.addstr(
            hold_offset[0] + vertical_length,
            hold_offset[1],
            horizontal_line,
            A_BOLD,
        )

        if not hold_mino:
            return stdscr

        mino_type: str = hold_mino.type
        if mino_type not in MINO_DRAW_LOCATION:
            return stdscr
        mino_char: str = "██"
        if hold_used:
            mino_char = "▒▒"

        mino_height: int = 2
        mino_width: int = 4
        mino_offset: Tuple[int, int] = (hold_offset[0] + 3, hold_offset[1] + 5)
        orientation: str = "N"

        for y in range(mino_height):
            for x in range(-2, mino_width * 2):
                clear_y = mino_offset[0] + y
                clear_x = mino_offset[1] + x
                if 0 <= clear_y < max_yx[0] and 0 <= clear_x < max_yx[1] - 1:
                    stdscr.addstr(clear_y, clear_x, " ", A_BOLD)

        # Draw the hold mino using block positions
        mino_shape: List[Tuple[int, int]] = MINO_DRAW_LOCATION[mino_type][
            orientation
        ]
        for y_offset, x_offset in mino_shape:
            pos = (
                mino_offset[0] + (mino_height - 1 - y_offset),
                mino_offset[1] + x_offset * 2,
            )
            if 0 <= pos[0] < max_yx[0] and 0 <= pos[1] < max_yx[1] - 1:
                stdscr.addstr(
                    pos[0],
                    pos[1],
                    mino_char,
                    color_pair(MINO_COLOR.get(mino_type, 0)),
                )

        return stdscr


if __name__ == "__main__":
    print("This is a module, not a standalone program.")
