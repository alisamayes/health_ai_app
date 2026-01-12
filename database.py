"""
Database utilities for the Health App.
Contains context manager for database access and initialization functions.
"""
import sqlite3
from contextlib import contextmanager


@contextmanager
def use_db(mode: str):
    """
    Context manager to standardize database access which is a common occurrence in the app.
    Automatically handles connection, cursor creation, error rollback, and connection closing.
    Commits changes only when mode is "write" and no exceptions occur.

    Parameters
    ----------
    mode : str
        Either "read" or "write". Controls whether a commit is issued
        when the context exits cleanly. "write" mode commits changes, "read" mode does not.

    Yields
    ------
    cursor
        A SQLite cursor object for executing queries.

    Raises
    ------
    ValueError
        If mode is not "read" or "write".
    """
    if mode not in {"read", "write"}:
        raise ValueError(f"Invalid mode: {mode}")

    conn = sqlite3.connect("health_app.db")
    try:
        cursor = conn.cursor()
        try:
            yield cursor
        except Exception:
            conn.rollback()
            raise
        else:
            if mode == "write":
                conn.commit()
    finally:
        conn.close()


def init_db():
    """
    Initialize the database tables for the app if they don't yet exist.
    Creates the following tables:
    - foods: Stores food entries with calories and dates
    - exercise: Stores exercise entries with calories burned and dates
    - goals: Stores weight goals, calorie goals, and timeframes
    - meal_plan: Stores meal plans for each day of the week
    - pantry: Stores pantry items with weights
    - shopping_list: Stores shopping list items
    """
    with use_db("write") as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food TEXT NOT NULL,
                calories INTEGER NOT NULL,
                entry_date TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity TEXT NOT NULL,
                calories INTEGER NOT NULL,
                entry_date TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_weight REAL,
                target_weight REAL,
                daily_calorie_goal REAL,
                weight_loss_timeframe REAL,
                updated_date TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Monday TEXT,
                Tuesday TEXT,
                Wednesday TEXT,
                Thursday TEXT,
                Friday TEXT,
                Saturday TEXT,
                Sunday TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pantry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                weight INTEGER NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL
            )
        """)
