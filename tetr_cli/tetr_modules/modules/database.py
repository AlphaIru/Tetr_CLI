"""This will connect the database and create the tables if they do not exist."""

# coding: utf-8

from typing import Dict, Set, List, Optional, Tuple
from pathlib import Path
from sqlite3 import Cursor, Error as SQLiteError, connect


DATABASE_PATH: Path = Path(__file__).parent.parent.resolve()
DB_FILE: str = str(DATABASE_PATH / "data.db")


DEFAULT_KEYBINDS: List[Tuple[str, str, Optional[str]]] = [
    ("move_left", "left", None),
    ("move_right", "right", None),
    ("rotate_cw", "up", "x"),
    ("rotate_ccw", "z", "ctrl"),
    ("soft_drop", "down", None),
    ("hard_drop", "space", None),
    ("hold_piece", "c", None),
    ("restart", "r", None)
]


DEFAULT_SETTINGS: List[Tuple[str, str]] = [
    ("music_volume", "20"),
    ("sfx_volume", "70"),
    ("fps_limit", "30"),
    ("mino_style", "[]"),
    ("color_mode", "true"),
    ("ghost_piece", "true"),
    ("das", "10"),
    ("arr", "2"),
]


DEFAULT_SCORES: List[Tuple[str, int, str, str]] = [
    ("RedWhite", 500000, "Marathon", "2025-10-25"),
    ("Lighting", 400000, "Marathon", "2025-10-25"),
    ("Bunny", 300000, "Marathon", "2025-10-25"),
    ("RagingTree", 200000, "Marathon", "2025-10-25"),
    ("Onkai", 100000, "Marathon", "2025-10-25"),
    ("RedWhite", 5000, "Sprint", "2025-10-25"),
    ("Lighting", 6000, "Sprint", "2025-10-25"),
    ("Bunny", 7000, "Sprint", "2025-10-25"),
    ("RagingTree", 8000, "Sprint", "2025-10-25"),
    ("Onkai", 9000, "Sprint", "2025-10-25"),
    ("RedWhite", 100000, "Ultra", "2025-10-25"),
    ("Lighting", 90000, "Ultra", "2025-10-25"),
    ("Bunny", 80000, "Ultra", "2025-10-25"),
    ("RagingTree", 70000, "Ultra", "2025-10-25"),
    ("Onkai", 60000, "Ultra", "2025-10-25"),
]


# Scores Table Functions
def drop_scores(cursor: Cursor) -> None:
    """Reset the database by dropping existing tables and recreating them."""
    cursor.execute("DROP TABLE IF EXISTS scores")


def create_scores_table(cursor: Cursor) -> None:
    """Create the score table if it does not exist."""
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        score_type TEXT DEFAULT 'Marathon',
        date_played TEXT NOT NULL
    )
    """
    )


def insert_default_scores(cursor: Cursor) -> None:
    """Insert default score into the score table."""
    cursor.executemany(
        """
        INSERT INTO scores (player_name, score, score_type, date_played) VALUES (?, ?, ?, ?)
        """,
        DEFAULT_SCORES,
    )


# Settings Table Functions
def drop_settings(cursor: Cursor) -> None:
    """Reset the setting table."""
    cursor.execute("DROP TABLE IF EXISTS settings")


def create_settings_table(cursor: Cursor) -> None:
    """Create the setting table if it does not exist."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
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
    INSERT INTO settings (setting_name, setting_value) VALUES (?, ?)
    """,
        DEFAULT_SETTINGS,
    )


# Keybinds Table Functions
def drop_keybinds(cursor: Cursor) -> None:
    """Reset the keybind table."""
    cursor.execute("DROP TABLE IF EXISTS keybinds")


def create_keybinds_table(cursor: Cursor) -> None:
    """Create the keybind table if it does not exist."""
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS keybinds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_name TEXT NOT NULL,
        key_name1 TEXT NOT NULL,
        key_name2 TEXT DEFAULT NULL
    )
    """
    )


def insert_default_keybinds(cursor: Cursor) -> None:
    """Insert default keybind into the keybind table."""

    cursor.executemany(
        """
    INSERT INTO keybinds (input_name, key_name1, key_name2) VALUES (?, ?, ?)
    """,
        DEFAULT_KEYBINDS,
    )


# Temporary Table Functions
def drop_temp_table(cursor: Cursor) -> None:
    """Drop the temporary table if it exists."""
    cursor.execute("DROP TABLE IF EXISTS temps")


def create_temp_table(cursor: Cursor) -> None:
    """Create the temporary table."""
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS temps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temp_name TEXT NOT NULL,
        temp_value TEXT NOT NULL
    )
    """
    )


# Reset All Tables


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

    drop_temp_table(cursor)
    create_temp_table(cursor)


def initialize_database(reset: bool = False) -> None:
    """This will connect to the database and create the tables if they do not exist."""

    try:
        with connect(DB_FILE) as conn:
            cursor: Cursor = conn.cursor()

            if reset:
                reset_all(cursor)
                conn.commit()
                return

            create_scores_table(cursor)
            create_keybinds_table(cursor)
            create_settings_table(cursor)
            create_temp_table(cursor)

            cursor.execute("SELECT COUNT(*) FROM scores")
            if cursor.fetchone()[0] == 0:
                insert_default_scores(cursor)

            cursor.execute("SELECT COUNT(*) FROM keybinds")
            if cursor.fetchone()[0] == 0:
                insert_default_keybinds(cursor)

            cursor.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                insert_default_settings(cursor)
            conn.commit()

    except SQLiteError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def validate_keybinds(
    given_keybinds: Dict[str, Set[str]],
) -> bool:
    """Validate that there are no conflicting keybinds in given keybinds."""
    binded_keys: Set[str] = set()
    for user_keys in given_keybinds.values():
        for key in user_keys:
            if key in binded_keys:
                return False
            binded_keys.add(key)
    return True


def load_keybinds() -> Dict[str, Set[str]]:
    """Load user keybind from the database."""

    rows: List[Tuple[str, str, Optional[str]]] = []
    with connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT input_name, key_name1, key_name2 FROM keybinds"
        )
        rows = cursor.fetchall()

    game_keybinds: Dict[str, Set[str]] = {}

    for input_name, key_name1, key_name2 in rows:
        if input_name not in game_keybinds:
            game_keybinds[input_name] = set()
        game_keybinds[input_name].add(key_name1)
        if key_name2 is not None:
            game_keybinds[input_name].add(key_name2)

    if not validate_keybinds(game_keybinds):
        with connect(DB_FILE) as conn:
            cursor = conn.cursor()
            drop_keybinds(cursor)
            create_keybinds_table(cursor)
            insert_default_keybinds(cursor)
        return load_keybinds()

    return game_keybinds


def update_keybind(
    key_name: str, key_value1: str, key_value2: Optional[str] = None
) -> bool:
    """Update keybind in the database."""

    default_key_value1: str = ""
    default_key_value2: Optional[str] = None

    success: bool = True

    with connect(DB_FILE) as conn:
        cursor: Cursor = conn.cursor()

        # Get current keybinds for rollback.
        cursor.execute(
            """
            SELECT key_name1, key_name2 FROM keybinds WHERE input_name = ?
            """,
            (key_name,),
        )
        result = cursor.fetchone()
        if result:
            default_key_value1, default_key_value2 = result

        # Update keybinds
        if key_value2 is not None:
            cursor.execute(
                """
            UPDATE keybinds SET key_name1 = ?, key_name2 = ? WHERE input_name = ?
            """,
                (key_value1, key_value2, key_name),
            )
        else:
            cursor.execute(
                """
            UPDATE keybinds SET key_name1 = ?, key_name2 = ? WHERE input_name = ?
            """,
                (key_value1, None, key_name),
            )

        # Validate keybinds
        rows: List[Tuple[str, str, Optional[str]]] = []
        cursor = conn.cursor()
        cursor.execute(
            "SELECT input_name, key_name1, key_name2 FROM keybinds"
        )
        rows = cursor.fetchall()
        game_keybinds: Dict[str, Set[str]] = {}

        for input_name, key_name1, key_name2 in rows:
            if input_name not in game_keybinds:
                game_keybinds[input_name] = set()
            game_keybinds[input_name].add(key_name1)
            if key_name2 is not None:
                game_keybinds[input_name].add(key_name2)

        if not validate_keybinds(game_keybinds):
            # Rollback keybinds
            cursor.execute(
                """
            UPDATE keybinds SET key_name1 = ?, key_name2 = ? WHERE input_name = ?
            """,
                (default_key_value1, default_key_value2, key_name),
            )
            success = False

        conn.commit()
    return success


def get_scores(score_type: str) -> List[Tuple[str, int, str, str]]:
    """Retrieve scores from the database based on score type."""
    with connect(DB_FILE) as conn:
        cursor: Cursor = conn.cursor()

        cursor.execute(
            """
            SELECT player_name, score, score_type, date_played
            FROM scores
            WHERE score_type = ?
            ORDER BY score DESC
            """,
            (score_type,),
        )

        scores: List[Tuple[str, int, str, str]] = cursor.fetchall()
    return scores


def set_scores(
    score_list: List[Tuple[str, int, str]],
    game_type: str,
):
    """Set a score in the scores table."""
    with connect(DB_FILE) as conn:
        cursor: Cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM scores WHERE score_type = ?
            """,
            (game_type,),
        )

        for score in score_list:
            player_name, score_value, date_played = score
            cursor.execute(
                """
                INSERT INTO scores (player_name, score, score_type, date_played)
                VALUES (?, ?, ?, ?)
                """,
                (player_name, score_value, game_type, date_played),
            )

        conn.commit()


def get_setting(setting_name: str, default_value: str) -> str:
    """Get a setting value from the settings table."""
    with connect(DB_FILE) as conn:
        cursor: Cursor = conn.cursor()

        cursor.execute(
            """
            SELECT setting_value FROM settings WHERE setting_name = ?
            """,
            (setting_name,),
        )
        result = cursor.fetchone()

    return result[0] if result else default_value


def set_setting(setting_name: str, setting_value: str) -> None:
    """Set a setting value in the settings table."""
    with connect(DB_FILE) as conn:
        cursor: Cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE settings SET setting_value = ? WHERE setting_name = ?
            """,
            (setting_value, setting_name),
        )

        conn.commit()


def set_temp(key: str, value: str) -> None:
    """Set a temporary value in the temps table."""
    with connect(DB_FILE) as conn:
        cursor: Cursor = conn.cursor()

        check_query = "SELECT COUNT(*) FROM temps WHERE temp_name = ?"
        cursor.execute(check_query, (key,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO temps (temp_name, temp_value) VALUES (?, ?)
                """,
                (key, value),
            )
        else:
            cursor.execute(
                """
                UPDATE temps SET temp_value = ? WHERE temp_name = ?
                """,
                (value, key),
            )

        conn.commit()


def get_temp(key: str) -> str:
    """Get a temporary value from the temps table."""
    with connect(DB_FILE) as conn:
        cursor: Cursor = conn.cursor()

        cursor.execute(
            """
            SELECT temp_value FROM temps WHERE temp_name = ?
            """,
            (key,),
        )
        result = cursor.fetchone()

        cursor.execute("DELETE FROM temps WHERE temp_name = ?", (key,))

    return result[0] if result else ""


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
