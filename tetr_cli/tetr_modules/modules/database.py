"""This will connect the database and create the tables if they do not exist."""

# coding: utf-8

from pathlib import Path
from sqlite3 import Connection, Cursor


DATABASE_PATH: Path = Path(__file__).parent.parent.resolve()
DB_FILE: str = str(DATABASE_PATH / "data.db")


def reset_database(cursor: Cursor) -> None:
    """Reset the database by dropping existing tables and recreating them."""
    cursor.execute("DROP TABLE IF EXISTS scores")
    cursor.execute("DROP TABLE IF EXISTS keybind")


def insert_default_scores(cursor: Cursor) -> None:
    """Insert default scores into the scores table."""
    cursor.execute(
        """
    INSERT INTO scores (player_name, score, date_played) VALUES
    ('RedWhite', 500000, '2025-10-25'),
    ('Lighting', 400000, '2025-10-25'),
    ('Bunny', 300000, '2025-10-25'),
    ('RagingTree', 200000, '2025-10-25'),
    ('Onkai', 100000, '2025-10-25')
    """
    )


def insert_default_keybinds(cursor: Cursor) -> None:
    """Insert default keybinds into the keybind table."""
    default_keybinds = {
        "move_left": ["left"],
        "move_right": ["right"],
        "rotate_clockwise": ["up", "x"],
        "rotate_counterclockwise": ["z", "ctrl"],
        "soft_drop": ["down"],
        "hard_drop": ["space"],
        "hold_piece": ["c"],
        "restart_game": ["r"],
    }

    for key_name, key_value in default_keybinds.items():
        if len(key_value) == 2:
            cursor.execute(
                """
            INSERT INTO keybind (key_name, key_value1, key_value2) VALUES (?, ?, ?)
            """,
                (key_name, key_value[0], key_value[1]),
            )
        else:
            cursor.execute(
                """
            INSERT INTO keybind (key_name, key_value1) VALUES (?, ?)
            """,
                (key_name, key_value[0]),
            )


def insert_default_settings(cursor: Cursor) -> None:
    """Insert default settings into the settings table."""
    default_settings = [
        ("music_volume", "70"),
        ("sfx_volume", "80"),
    ]

    for setting_name, setting_value in default_settings:
        cursor.execute(
            """
        INSERT INTO settings (setting_name, setting_value) VALUES (?, ?)
        """,
            (setting_name, setting_value),
        )


def initialize_database(reset: bool = False) -> None:
    """This will connect to the database and create the tables if they do not exist."""

    conn: Connection = Connection(DB_FILE)
    cursor: Cursor = conn.cursor()

    if reset:
        reset_database(cursor)

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        date_played TEXT NOT NULL
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS keybind (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_name TEXT NOT NULL,
        key_value1 TEXT NOT NULL,
        key_value2 TEXT DEFAULT NULL
    )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT NOT NULL,
        setting_value TEXT NOT NULL
    )
    """
    )

    cursor.execute("SELECT COUNT(*) FROM scores")
    if cursor.fetchone()[0] == 0:
        insert_default_scores(cursor)

    cursor.execute("SELECT COUNT(*) FROM keybind")
    if cursor.fetchone()[0] == 0:
        insert_default_keybinds(cursor)

    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        insert_default_settings(cursor)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
