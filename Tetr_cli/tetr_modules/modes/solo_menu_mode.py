""""This will handle the solo mode menu."""
# coding: utf-8

from curses import A_BOLD, A_REVERSE, window


class ModeClass:
    """This will handle the solo mode menu."""

    def __init__(self) -> None:
        """This will initialize this class."""
        self.__selected_option: int = 0
        self.__key_cooldown: int = 0
        self.__options: list[str] = ["Marathon", "Sprint", "Ultra", "Go_Back"]
        self.__action: str = ""

    def pop_action(self) -> str:
        """This will return the action and reset it."""
        action = self.__action
        self.__action = ""
        return action

    def increment_frame(self, stdscr: window, pressed_keys: set[str]) -> window:
        """This will progress the menu based on the inputs."""
        if self.__key_cooldown > 0:
            self.__key_cooldown -= 1
        elif "up" in pressed_keys:
            self.__selected_option = max(0, self.__selected_option - 1)
            self.__key_cooldown = 3
        elif "down" in pressed_keys:
            self.__selected_option = min(
                len(self.__options) - 1, self.__selected_option + 1
            )
            self.__key_cooldown = 3
        elif "enter" in pressed_keys:
            self.__action = self.__options[self.__selected_option]
            return stdscr

        height: int = 0
        width: int = 0
        height, width = stdscr.getmaxyx()

        # Those "// 2" just finds the center.
        # +2 in block_width account for "> "

        start_y: int = (height // 2) - len(self.__options) // 2
        block_width: int = max(len(option) for option in self.__options) + 2
        start_x: int = (width - block_width) // 2

        title = "Solo Mode Menu"
        stdscr.addstr(start_y - 2, (width - len(title)) // 2, title, A_BOLD)

        for list_index, option in enumerate(self.__options):
            prefix: str = "  "
            attr: int = 0
            if list_index == self.__selected_option:
                prefix = "> "
                attr = A_REVERSE
            line = f"{prefix}{option}"
            stdscr.addstr(start_y + list_index, start_x, line, attr)
        return stdscr


if __name__ == "__main__":
    print("This is a module, not a program.")
