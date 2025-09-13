"""The true main program."""

# from asyncio import sleep

from blessed import Terminal

from tetr_modules.checker import screen_dimmension_check, screen_dimmension_warning
from tetr_modules.debug import DebugClass

# from keyboard import


TARGET_FPS: int = 30
FRAME_DURATION: float = 1 / TARGET_FPS

term = Terminal()


async def main(pressed_keys: set, debug_mode: bool) -> None:
    """The true main code or base of everything."""
    debug_stats: DebugClass = DebugClass()

    # with term.cbreak():
    print(term.clear())
    while True:
        height, width = term.height, term.width

        print(term.move_yx(0, 0) + f"Terminal Size: {width} columns, {height} rows")
        print(term.move_yx(2, 0) + "Press 'q' to exit.")

        if "esc" in pressed_keys:
            break


if __name__ == "__main__":
    print("This is a module, please run the starter.py.")
