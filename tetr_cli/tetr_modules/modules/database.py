"""This will connect the database and create the tables if they do not exist."""

# coding: utf-8

from typing import Dict, Set, List, Optional, Tuple
from pathlib import Path
from sqlite3 import Connection, Cursor, Error as SQLiteError, connect


DATABASE_PATH: Path = Path(__file__).parent.parent.resolve()
DB_FILE: str = str(DATABASE_PATH / "data.db")


DEFAULT_KEYBINDS: List[Tuple[str, str, Optional[str]]] = [
    ("move_left", "left", None),
    ("move_right", "right", None),
    ("rotate_clockwise", "up", "x"),
    ("rotate_counterclockwise", "z", "ctrl"),
    ("soft_drop", "down", None),
    ("hard_drop", "space", None),
    ("hold_piece", "c", None),
    ("confirm", "enter", None),
    ("back", "backspace", "esc"),
    ("restart", "r", None),
]

DEFAULT_SETTINGS: List[Tuple[str, str]] = [
    ("music_volume", "70"),
    ("sfx_volume", "80"),
    ("FPS_limit", "30"),
]


DEFAULT_SCORES: List[Tuple[str, int, str]] = [
    ("RedWhite", 500000, "2025-10-25"),
    ("Lighting", 400000, "2025-10-25"),
    ("Bunny", 300000, "2025-10-25"),
    ("RagingTree", 200000, "2025-10-25"),
    ("Onkai", 100000, "2025-10-25"),
]


# Scores Table Functions
def drop_scores(cursor: Cursor) -> None:
    """Reset the database by dropping existing tables and recreating them."""
    cursor.execute("DROP TABLE IF EXISTS score")


def create_scores_table(cursor: Cursor) -> None:
    """Create the score table if it does not exist."""
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS score (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        date_played TEXT NOT NULL
    )
    """
    )


def insert_default_scores(cursor: Cursor) -> None:
    """Insert default score into the score table."""
    cursor.executemany(
        """
        INSERT INTO score (player_name, score, date_played) VALUES (?, ?, ?)
        """,
        DEFAULT_SCORES,
    )


# Settings Table Functions
def drop_settings(cursor: Cursor) -> None:
    """Reset the setting table."""
    cursor.execute("DROP TABLE IF EXISTS setting")


def create_settings_table(cursor: Cursor) -> None:
    """Create the setting table if it does not exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS setting (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT NOT NULL,
        setting_value TEXT NOT NULL
    )
    """
    )


def insert_default_settings(cursor: Cursor) -> None:
    """Insert default setting into the setting table."""
    cursor.executemany(
        """
    INSERT INTO setting (setting_name, setting_value) VALUES (?, ?)
    """,
        DEFAULT_SETTINGS,
    )


# Keybinds Table Functions
def drop_keybinds(cursor: Cursor) -> None:
    """Reset the keybind table."""
    cursor.execute("DROP TABLE IF EXISTS keybind")


def create_keybinds_table(cursor: Cursor) -> None:
    """Create the keybind table if it does not exist."""
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


def insert_default_keybinds(cursor: Cursor) -> None:
    """Insert default keybind into the keybind table."""

    cursor.executemany(
        """
    INSERT INTO keybind (key_name, key_value1, key_value2) VALUES (?, ?, ?)
    """,
        DEFAULT_KEYBINDS
    )


def reset_all(cursor: Cursor) -> None:
    """Reset all tables in the database."""
    drop_scores(cursor)
    create_scores_table(cursor)
    insert_default_scores(cursor)

    drop_keybinds(cursor)
    create_keybinds_table(cursor)
    insert_default_keybinds(cursor)

    drop_settings(cursor)
    create_settings_table(cursor)
    insert_default_settings(cursor)


def initialize_database(reset: bool = False) -> None:
    """This will connect to the database and create the tables if they do not exist."""

    try:
        conn: Connection = connect(DB_FILE)
        cursor: Cursor = conn.cursor()

        if reset:
            reset_all(cursor)
            conn.commit()
            return

        create_scores_table(cursor)
        create_keybinds_table(cursor)
        create_settings_table(cursor)

        cursor.execute("SELECT COUNT(*) FROM score")
        if cursor.fetchone()[0] == 0:
            insert_default_scores(cursor)

        cursor.execute("SELECT COUNT(*) FROM keybind")
        if cursor.fetchone()[0] == 0:
            insert_default_keybinds(cursor)

        cursor.execute("SELECT COUNT(*) FROM setting")
        if cursor.fetchone()[0] == 0:
            insert_default_settings(cursor)

        conn.commit()
    except SQLiteError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        conn.close()


def load_keybinds() -> Dict[str, Set[str]]:
    """Load user keybind from the database."""

    rows: List[Tuple[str, str, Optional[str]]] = []
    with connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key_name, key_value1, key_value2 FROM keybind")
        rows = cursor.fetchall()

    user_keybinds: Dict[str, Set[str]] = {}

    for key_name, key_value1, key_value2 in rows:
        if key_name not in user_keybinds:
            user_keybinds[key_name] = set()
        user_keybinds[key_name].add(key_value1)
        if key_value2 is not None:
            user_keybinds[key_name].add(key_value2)

    return user_keybinds


def update_keybind(
    key_name: str, key_value1: str, key_value2: Optional[str] = None
) -> None:
    """Update keybind in the database."""
    conn: Connection = connect(DB_FILE)
    cursor: Cursor = conn.cursor()

    if key_value2 is not None:
        cursor.execute(
            """
        UPDATE keybind SET key_value1 = ?, key_value2 = ? WHERE key_name = ?
        """,
            (key_value1, key_value2, key_name),
        )
    else:
        cursor.execute(
            """
        UPDATE keybind SET key_value1 = ? WHERE key_name = ?
        """,
            (key_value1, key_name),
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
