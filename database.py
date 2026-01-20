"""
Database utilities for the Health App.
Contains context manager for database access and initialization functions.
"""
import sqlite3
import os
from contextlib import contextmanager
from PyQt6.QtCore import QDate, QTime, QDateTime

# Database path - can be overridden for testing via environment variable
_DB_PATH = os.getenv("HEALTH_APP_DB_PATH", "health_app.db")


def get_db_path():
    """
    Get the current database path.
    
    Returns:
        str: The path to the database file.
    """
    return _DB_PATH


def set_db_path(path: str):
    """
    Set the database path (primarily for testing).
    
    Args:
        path (str): The path to the database file.
    """
    global _DB_PATH
    _DB_PATH = path


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

    conn = sqlite3.connect(_DB_PATH)
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
    
    Also creates the initial meal_plan row if it doesn't exist.
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
            CREATE TABLE IF NOT EXISTS sleep_diary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sleep_date DATE NOT NULL,
                bedtime DATETIME NOT NULL,
                wakeup DATETIME NOT NULL,
                sleep_duration TIME NOT NULL
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
    
    # Create initial meal_plan row if it doesn't exist
    create_meal_plan_row()


# food tracker database operations
#---------------------------------------------------------------------------------
def add_food(food: str, calories: int, entry_date: str):
    """
    Add a food entry to the database.

    Args:
        food (str): The food name.
        calories (int): The calories of the food.
        entry_date (str): The date string in "yyyy-MM-dd" format.
    """
    with use_db("write") as cursor:
        cursor.execute("INSERT INTO foods (food, calories, entry_date) VALUES (?, ?, ?)", (food, calories, entry_date))


def get_food_entries(entry_date: str):
    """
    Get the food entries for a given date.
    
    Args:
        entry_date (str): The date string in "yyyy-MM-dd" format.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT id, food, calories FROM foods WHERE entry_date = ? ORDER BY id DESC", (entry_date,))
        rows = cursor.fetchall()
    return rows


def get_all_distinct_foods():
    """
    Get all distinct foods from the database.
    """

    with use_db("read") as cursor:
        cursor.execute("SELECT DISTINCT food, calories FROM foods")
        rows = cursor.fetchall()
    return rows


def update_food_entry(id: int, food: str, calories: int):
    """
    Update a food entry in the database.
    
    Args:
        id (int): The id of the food entry to update.
        food (str): The food name.
        calories (int): The calories of the food.
    """
    with use_db("write") as cursor:
            cursor.execute(
                "UPDATE foods SET food = ?, calories = ? WHERE id = ?",
                (food, calories, id),
            )


def get_most_common_foods():
    """
    Get the most common foods from the database.
    """
    with use_db("read") as cursor:
        cursor.execute("""
            SELECT MIN(food) as food, AVG(calories) as calories
            FROM foods
            GROUP BY UPPER(food)
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
    return rows


def delete_food_entry(id: int):
    """
    Delete a food entry from the database.
    
    Args:
        id (int): The id of the food entry to delete.
    """
    with use_db("write") as cursor:
        cursor.execute("DELETE FROM foods WHERE id = ?", (id,))

#---------------------------------------------------------------------------------

# exercise tracker database operations
#---------------------------------------------------------------------------------
def add_exercise(activity: str, calories: int, entry_date: str):
    """
    Add an exercise entry to the database.

    Args:
        activity (str): The activity name.
        calories (int): The calories burned during the activity.
        entry_date (str): The date string in "yyyy-MM-dd" format.
    """
    with use_db("write") as cursor:
        cursor.execute("INSERT INTO exercise (activity, calories, entry_date) VALUES (?, ?, ?)", (activity, calories, entry_date))


def get_exercise_entries(entry_date: str):
    """
    Get the exercise entries for a given date.
    
    Args:
        entry_date (str): The date string in "yyyy-MM-dd" format.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT id, activity, calories FROM exercise WHERE entry_date = ? ORDER BY id DESC", (entry_date,))
        rows = cursor.fetchall()
    return rows


def delete_exercise_entry(id: int):
    """
    Delete an exercise entry from the database.
    
    Args:
        id (int): The id of the exercise entry to delete.
    """
    with use_db("write") as cursor:
        cursor.execute("DELETE FROM exercise WHERE id = ?", (id,))

#---------------------------------------------------------------------------------

# goals tracker database operations
#---------------------------------------------------------------------------------
def add_weight(weight: float, entry_date: str, mode: str):
    """
    Add a weight entry to the database.

    Args:
        weight (float): The weight in kg.
        entry_date (str): The date string in "yyyy-MM-dd" format.
        mode (str): The mode to add the weight to. "current" or "target".
    """
    with use_db("write") as cursor:
        if mode == "current":
            cursor.execute("INSERT INTO goals (current_weight, updated_date) VALUES (?, ?)", (weight, entry_date))
        elif mode == "target":
            cursor.execute("INSERT INTO goals (target_weight, updated_date) VALUES (?, ?)", (weight, entry_date))


def get_current_weight():
    """
    Get the current weight from the database.
    
    Returns:
        float or None: The current weight, or None if not set.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT current_weight FROM goals WHERE current_weight IS NOT NULL ORDER BY updated_date DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else None


def get_target_weight():
    """
    Get the target weight from the database.
    
    Returns:
        float or None: The target weight, or None if not set.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT target_weight FROM goals WHERE target_weight IS NOT NULL ORDER BY updated_date DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else None


def check_weekly_weight_entry(week_start_str: str, week_end_str: str):
    """
    Get the current weight for a given week.
    
    Args:
        week_start_str (str): The start date of the week in "yyyy-MM-dd" format.
        week_end_str (str): The end date of the week in "yyyy-MM-dd" format.

    Returns:
        float: The current weight if it exists, otherwise None.
    """
    with use_db("read") as cursor:
            # Check if a current_weight entry exists for this week (Monday to Sunday)
            cursor.execute(
                """
                SELECT current_weight FROM goals 
                WHERE updated_date BETWEEN ? AND ?
                AND current_weight IS NOT NULL
                LIMIT 1
                """,
                (week_start_str, week_end_str),
            )
            result = cursor.fetchone()
            return result[0] if result else None


def delete_weight_entry(id: int):
    """
    Delete a weight entry from the database.
    
    Args:
        id (int): The id of the weight entry to delete.
    """
    with use_db("write") as cursor:
        cursor.execute("DELETE FROM goals WHERE id = ?", (id,))


def get_all_currnet_weight_entries():
    """
    Get all weight entries from the database.
    
    Returns:
        list: A list of tuples containing the weight entries.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT id, current_weight, updated_date FROM goals WHERE current_weight IS NOT NULL ORDER BY updated_date ASC")
        return cursor.fetchall()


def update_weight_entry(id: int, weight: float, entry_date: str):
    """
    Update a weight entry in the database.
    
    Args:
        id (int): The id of the weight entry to update.
        weight (float): The weight value.
        entry_date (str): The date string in "yyyy-MM-dd" format.
    """
    with use_db("write") as cursor:
        cursor.execute("UPDATE goals SET current_weight = ?, updated_date = ? WHERE id = ?", (weight, entry_date, id))


def add_weight_loss_timeframe(timeframe: float, entry_date: str):   
    """
    Add or update a weight loss timeframe entry to the database.
    
    Args:    
        timeframe (float): The timeframe in months.
        entry_date (str): The date string in "yyyy-MM-dd" format.
    """
    with use_db("write") as cursor:
                # First try to update the most recent goals row
                cursor.execute(
                    """
                    UPDATE goals
                    SET weight_loss_timeframe = ?, updated_date = ?
                    WHERE id = (
                        SELECT id FROM goals
                        ORDER BY updated_date DESC, id DESC
                        LIMIT 1
                    )
                    """,
                    (timeframe, entry_date),
                )
                # If no row was updated (fresh DB), insert a new one
                if cursor.rowcount == 0:
                    cursor.execute("INSERT INTO goals (weight_loss_timeframe, updated_date) VALUES (?, ?)", (timeframe, entry_date))


def get_weight_loss_timeframe():
    """
    Get the weight loss timeframe from the database.
    
    Returns:
        float or None: The weight loss timeframe, or None if not set.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT weight_loss_timeframe FROM goals WHERE weight_loss_timeframe IS NOT NULL ORDER BY updated_date DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else None


def add_daily_calorie_goal(calorie_goal: int, entry_date: str):
    """
    Add a daily calorie goal entry to the database.
    
    Args:
        calorie_goal (int): The daily calorie goal.
        entry_date (str): The date string in "yyyy-MM-dd" format.
    """
    with use_db("write") as cursor:
                # First try to update the most recent goals row
                cursor.execute(
                    """
                    UPDATE goals
                    SET daily_calorie_goal = ?, updated_date = ?
                    WHERE id = (
                        SELECT id FROM goals
                        ORDER BY updated_date DESC, id DESC
                        LIMIT 1
                    )
                    """,
                    (calorie_goal, entry_date),
                )
                # If no row was updated (fresh DB), insert a new one
                if cursor.rowcount == 0:
                    cursor.execute("INSERT INTO goals (daily_calorie_goal, updated_date) VALUES (?, ?)", (calorie_goal, entry_date))


def get_daily_calorie_goal():
    """
    Get the most recent daily calorie goal from the database.
    There should only be one but we must handle the use case of one not being set yet
    
    Returns:
        float or None: The daily calorie goal, or None if not set.
    """
    with use_db("read") as cursor:
        cursor.execute(
            """
            SELECT daily_calorie_goal
            FROM goals
            WHERE daily_calorie_goal IS NOT NULL
            LIMIT 1
            """
        )
        result = cursor.fetchone()
        return result[0] if result else None

#---------------------------------------------------------------------------------

#graphs database operations
#---------------------------------------------------------------------------------
def get_earliest_food_date():
    """
    Get the earliest food date from the database.
    
    Returns:
        str or None: The earliest food date, or None if not set.
    """
    with use_db("read") as cursor:
            cursor.execute("SELECT MIN(entry_date) FROM foods")
            result = cursor.fetchone()
            return result[0] if result else None


def get_food_calorie_totals_for_timeframe(start_date: str, end_date: str):
    """
    Get the food calorie totals for a given timeframe.
    
    Args:
        start_date (str): The start date in "yyyy-MM-dd" format.
        end_date (str): The end date in "yyyy-MM-dd" format.

    Returns:
        list: A list of tuples containing the food calorie totals.
    """
    with use_db("read") as cursor:
        cursor.execute(
            """
            SELECT entry_date, SUM(calories) AS total FROM foods WHERE entry_date BETWEEN ? AND ? GROUP BY entry_date ORDER BY entry_date ASC
            """,
            (start_date, end_date)
        )
        return cursor.fetchall()


def get_exercise_calorie_totals_for_timeframe(start_date: str, end_date: str):
    """
    Get the exercise calorie totals for a given timeframe.
    
    Args:
        start_date (str): The start date in "yyyy-MM-dd" format.
        end_date (str): The end date in "yyyy-MM-dd" format.
    """
    with use_db("read") as cursor:
        cursor.execute(
            """
            SELECT entry_date, SUM(calories) AS total FROM exercise WHERE entry_date BETWEEN ? AND ? GROUP BY entry_date ORDER BY entry_date ASC
            """,
            (start_date, end_date)
        )
        return cursor.fetchall()


#---------------------------------------------------------------------------------

# sleep diary database operations
#---------------------------------------------------------------------------------

def add_sleep_diary_entry(sleep_date: QDate, bedtime: QDateTime, wakeup: QDateTime, sleep_duration: QTime):
    """
    Add a sleep diary entry to the database.
    
    Args:
        sleep_date (QDate): The sleep date.
        bedtime (QDateTime): The bedtime.
        wakeup (QDateTime): The wakeup time.
        sleep_duration (QTime): The sleep duration.
    """

    # Convert QDates and QTimes to DATE and TIME strings.
    # Use ISO format for dates so string comparisons and ORDER BY work correctly.
    sleep_date_str = sleep_date.toString("yyyy-MM-dd")
    bedtime_str = bedtime.toString("HH:mm")
    wakeup_str = wakeup.toString("HH:mm")
    sleep_duration_str = sleep_duration.toString("HH:mm")

    with use_db("write") as cursor:
        cursor.execute("INSERT INTO sleep_diary (sleep_date, bedtime, wakeup, sleep_duration) VALUES (?, ?, ?, ?)", (sleep_date_str, bedtime_str, wakeup_str, sleep_duration_str))


def get_sleep_diary_entries(start_qdate: QDate, end_qdate: QDate):
    """
    Get the sleep diary entries for a given timeframe.
    
    Args:
        start_qdate (QDate): The start date.
        end_qdate (QDate): The end date.
    """

    with use_db("read") as cursor:
        cursor.execute(
            """
            SELECT sleep_date, bedtime, wakeup, sleep_duration
            FROM sleep_diary
            WHERE sleep_date BETWEEN ? AND ?
            ORDER BY sleep_date ASC
            """,
            (start_qdate.toString("yyyy-MM-dd"), end_qdate.toString("yyyy-MM-dd")),
        )
        rows = cursor.fetchall()
    return rows


def get_earliest_sleep_diary_date():
    """
    Get the earliest sleep diary date from the database.
    
    Returns:
        QDate or None: The earliest sleep diary date, or None if not set.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT MIN(sleep_date) FROM sleep_diary")
        result = cursor.fetchone()
        if result and result[0]:
            # Stored in ISO format "yyyy-MM-dd"
            return QDate.fromString(result[0], "yyyy-MM-dd")
        return None

#---------------------------------------------------------------------------------

# pantry tracker database operations
#---------------------------------------------------------------------------------
def add_pantry_item(item: str, weight: int):
    """
    Add a pantry item entry to the database.
    
    Args:
        item (str): The item name.
        weight (int): The weight of the item.
    """
    with use_db("write") as cursor:
        cursor.execute("INSERT INTO pantry (item, weight) VALUES (?, ?)", (item, weight))


def get_pantry_items():
    """
    Get all pantry items from the database.
    
    Returns:
        list: A list of tuples containing the pantry items.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT id, item, weight FROM pantry")
        return cursor.fetchall()


def delete_pantry_items(selected_items: list):
    """
    Delete multiple pantry items from the database.
    
    Args:
        selected_items (list): A list of QListWidgetItem objects with IDs stored in UserRole data.
    """
    from PyQt6.QtCore import Qt
    with use_db("write") as cursor:
        for item in selected_items:
            item_id = item.data(Qt.ItemDataRole.UserRole)
            if item_id:
                cursor.execute("DELETE FROM pantry WHERE id = ?", (item_id,))


def clear_pantry():
    """
    Clear all pantry items from the database.
    """
    with use_db("write") as cursor:
        cursor.execute("DELETE FROM pantry")


def add_shopping_list_item(item: str):
    """
    Add a shopping list item entry to the database.
    
    Args:
        item (str): The item name.
    """
    with use_db("write") as cursor:
        cursor.execute("INSERT INTO shopping_list (item) VALUES (?)", (item,))


def get_shopping_list_items():
    """
    Get all shopping list items from the database.
    
    Returns:
        list: A list of tuples containing the shopping list items.
    """
    with use_db("read") as cursor:
        cursor.execute("SELECT id, item FROM shopping_list")
        return cursor.fetchall()


def delete_shopping_list_items(selected_items: list):
    """
    Delete multiple shopping list items from the database.
    
    Args:
        selected_items (list): A list of QListWidgetItem objects with IDs stored in UserRole data.
    """
    from PyQt6.QtCore import Qt
    with use_db("write") as cursor:
        for item in selected_items:
            item_id = item.data(Qt.ItemDataRole.UserRole)
            if item_id:
                cursor.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))


def clear_shopping_list():
    """
    Clear all shopping list items from the database.
    """
    with use_db("write") as cursor:
        cursor.execute("DELETE FROM shopping_list")


def clean_shopping_list_formatting():
    """
    Remove formatting lines (headers, markdown, etc.) from the shopping list.
    Deletes items that are not valid shopping list items and cleans up remaining items.
    """
    def is_valid_item(item: str) -> bool:
        """Check if an item is a valid shopping list item."""
        item = item.strip()
        if not item:
            return False
        if item.startswith("#"):
            return False
        if item in ["**Shopping List:**", "### Shopping List", "Shopping List"]:
            return False
        if item.startswith("---") or item.startswith("==="):
            return False
        if item in ["-", "*", "•"]:
            return False
        if item.lower().startswith("feel free") or item.lower().startswith("note:"):
            return False
        # Remove AI intro text
        if "here's your" in item.lower() or "here is your" in item.lower() or "itemized shopping list" in item.lower():
            return False
        if len(item) < 3:
            return False
        return True
    
    def clean_item_text(item: str) -> str:
        """Clean up item text by removing markdown list markers."""
        item = item.strip()
        # Remove markdown list markers from the start
        if item.startswith("- "):
            item = item[2:].strip()
        elif item.startswith("* "):
            item = item[2:].strip()
        elif item.startswith("• "):
            item = item[2:].strip()
        return item
    
    with use_db("write") as cursor:
        # Get all items
        cursor.execute("SELECT id, item FROM shopping_list")
        all_items = cursor.fetchall()
        
        # Process items: delete invalid ones, update ones that need cleaning
        for item_id, item_text in all_items:
            if not is_valid_item(item_text):
                cursor.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))
            else:
                # Clean up the item text (remove "- " prefix, etc.)
                cleaned = clean_item_text(item_text)
                if cleaned != item_text:
                    cursor.execute("UPDATE shopping_list SET item = ? WHERE id = ?", (cleaned, item_id))

#---------------------------------------------------------------------------------

# meal plan database operations
#---------------------------------------------------------------------------------
def create_meal_plan_row():
    """
    Create the initial meal plan row in the database if it doesn't exist.
    Ensures there is exactly one row (id = 1) to update against.
    """
    with use_db("write") as cursor:
        # Ensure there is exactly one row to update against (id = 1)
        cursor.execute("SELECT COUNT(*) FROM meal_plan")
        count_row = cursor.fetchone()
        existing_count = count_row[0] if count_row else 0
        if existing_count == 0:
            cursor.execute("INSERT INTO meal_plan (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday) VALUES ('', '', '', '', '', '', '')")


def update_meal_plan_for_day(day: str, meal_plan: str):
    """
    Update the meal plan for a given day.
    
    Args:
        day (str): The day of the week.
        meal_plan (str): The meal plan for the given day.
    """
    with use_db("write") as cursor:
        cursor.execute(f"UPDATE meal_plan SET {day} = ?", (meal_plan,))


def get_meal_plan_for_day(day: str):
    """
    Get the meal plan for a given day.
    
    Args:
        day (str): The day of the week.

    Returns:
        str: The meal plan for the given day, or None if not found.
    """
    with use_db("read") as cursor:
        # Note: day is validated against valid_days in day_widget.py, so safe from SQL injection
        cursor.execute(f"SELECT {day} FROM meal_plan")
        row = cursor.fetchone()
        return row[0] if row else None
#---------------------------------------------------------------------------------