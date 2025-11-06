import sys
import os
import sqlite3
import shutil
import matplotlib.pyplot as plt
import threading
from datetime import datetime, timedelta
from PyQt6.QtCore import QDate, Qt, QTimer, QSettings, QObject, pyqtSignal as Signal
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QInputDialog, QMessageBox, QDateEdit, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QSystemTrayIcon, QCheckBox, QTextEdit, QToolButton, QFileDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from winotify import Notification, audio
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

"""
This is the starter file for an AI-driven self health and tracking app I am working on, using Python for the main part, PyQt for the GUI and SQLite for the database
Plan
Tab 1: Home page → App name, navigation
Tab 2: Calorie Tracker → form to enter meals, calories, macros
Tab 3: Exercise Tracker → log workouts, sets/reps, time
Tab 4: Graphs/Progress → matplotlib charts inside PyQt
Tab 5: Meal Plan & Ideas → static list first, then AI alternative suggestions
Tab 6: Shopping List → add/remove grocery items

core_todo_list = [ "AI suggested meal substitues", "desktop promts"]
extra_todo_list = ["calorie suggestions based on input factors", "goal advice", "sleep diary", "health by day trends", "AI driven improvements", "mobile support", "silent auto open app on bootup"]
completed_todo_list = ["Calorie tracker","exercise tracker", "app styling", "weight goal", "graphs of both over time period", "AI chat bot for health advice", "weekly weigh in reminders", "basic desktop notifcations""meal plan/ ideas",
"""


# Global variables for the colours used in the app to make more human readable than hex codes
white = "#ffffff"
background_dark_gray = "#2b2b2b"
border_gray = "#404040"
button_active_light_gray = "#5a5a5a"
hover_gray = "#4a4a4a"
hover_light_green = "#00a527"
active_dark_green = "#007a1c"
calories_burned_red = "#f01313"
overburn_orange = "#d47a2c"

# --- Database Setup ---
# Initilise the various database tables for the app if they dont yet exist
def init_db():
    """
    This function initializes the database tables for the app if they dont yet exist.
    It creates the tables for the calories, exercise, goals and meal plan.
    """
    conn = sqlite3.connect("health_app.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS calories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food TEXT NOT NULL,
            calories INTEGER NOT NULL,
            entry_date TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS exercise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity TEXT NOT NULL,
            calories INTEGER NOT NULL,
            entry_date TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_weight REAL,
            target_weight REAL,
            updated_date TEXT NOT NULL
        )
    """)
    c.execute("""
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
    conn.commit()
    conn.close()

class HomePage(QWidget):
    """
    This is the home page of the app. It is the first page that the user sees when they open the app.
    It contains the logo, app name, and subtitle.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo label, temp image till i come up with something better
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = QPixmap("assets/legnedary_astrid_boop_upscale.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # App name, temp till i come up with something remotely acceptable
        self.title_label = QLabel("Mindful Mäuschen")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        # Optional subtitle
        self.subtitle_label = QLabel("Mäuschen's personal health app")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        self.subtitle_label.setFont(subtitle_font)
        

        # Add widgets to layout
        self.layout.addWidget(self.logo_label)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)

        self.setLayout(self.layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-scale the pixmap when window size changes
        pixmap = QPixmap("assets/legnedary_astrid_boop_upscale.png")
        if not pixmap.isNull():
            size = int(min(self.width(), self.height()) * 0.5)  # 50% of smaller dimension
            self.logo_label.setPixmap(pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

class CalorieTracker(QWidget):
    """
    This is the calorie tracker page of the app. It is used to track the calories of the food that the user eats.
    It contains a date selector, a table to show the entries for a given date, and a form to add and remove entries.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Date selector section for picking which date to show calorie and food entries for
        self.date_selector = QDateEdit(calendarPopup=True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.setDisplayFormat("dd-MM-yyyy")
        self.date_selector.dateChanged.connect(self.load_entries)
        self.back_day_button = QPushButton("<")
        self.back_day_button.setFixedSize(30, 25)
        self.back_day_button.setObjectName("navigationBtn") # Navigation buttons are smaller than the other buttons in the styling to fit the < and > symbols. Thus needs a special identifier.
        self.back_day_button.clicked.connect(self.back_day)
        self.next_day_button = QPushButton(">")
        self.next_day_button.setFixedSize(30, 25)
        self.next_day_button.setObjectName("navigationBtn")
        self.next_day_button.clicked.connect(self.next_day)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Date:"))
        date_layout.addWidget(self.back_day_button)
        date_layout.addWidget(self.date_selector)
        date_layout.addWidget(self.next_day_button)


        # Input section for adding and removing food and calorie entries
        self.food_input = QLineEdit()
        self.food_input.setPlaceholderText("Enter food name")
        self.calorie_input = QLineEdit()
        self.calorie_input.setPlaceholderText("Enter calories")

        self.add_button = QPushButton("Add Entry")
        self.remove_button = QPushButton("Remove Entry")
        self.add_button.clicked.connect(self.add_entry)
        self.remove_button.clicked.connect(self.remove_entry)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.food_input)
        input_layout.addWidget(self.calorie_input)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.remove_button)

       

        # Table section to show entries for a given date
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Food", "Calories"])
        
        # Enable automatic column resizing to fit content
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.Stretch) 
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().ResizeMode.ResizeToContents) 
        self.table.setWordWrap(True) # Enable word wrapping for long food names
        self.table.setColumnWidth(1, 80) # Set minimum column widths
        
        # Enable keyboard focus and selection
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)

        # Section for showing total daily calorie intake for a given date
        self.calorie_label = QLabel("Daily Calories:")
        self.calorie_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Add to layout
        self.layout.addLayout(date_layout)
        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.calorie_label)
        self.setLayout(self.layout)

        # Load existing data
        self.load_entries()

    def add_entry(self):
        food = self.food_input.text()
        try:
            calories = int(self.calorie_input.text())
        except ValueError:
            return  # Ignore if calories is not a number

        date_str = self.date_selector.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("INSERT INTO calories (food, calories, entry_date) VALUES (?, ?, ?)",
                  (food, calories, date_str))
        conn.commit()
        conn.close()

        self.food_input.clear()
        self.calorie_input.clear()
        self.load_entries()

    def remove_entry(self):
        row_count = self.table.rowCount()
        if row_count == 0:
            QMessageBox.information(self, "Remove Entry", "There are no entries to remove.")
            return

        # Ask user for row number
        row_number, ok = QInputDialog.getInt(
            self,
            "Remove Entry",
            f"Enter row number to remove (1 - {row_count}):",
            1, 1, row_count, 1
        )
        if not ok:
            return

        # Get IDs for this date only
        date_str = self.date_selector.date().toString("yyyy-MM-dd")
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("SELECT id FROM calories WHERE entry_date = ? ORDER BY id DESC", (date_str,))
        ids = [row[0] for row in c.fetchall()]

        index = row_number - 1
        if index < 0 or index >= len(ids):
            conn.close()
            QMessageBox.warning(self, "Remove Entry", "Invalid row number.")
            return

        target_id = ids[index]
        c.execute("DELETE FROM calories WHERE id = ?", (target_id,))
        conn.commit()
        conn.close()

        self.load_entries()

    def back_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.load_entries()
    
    def next_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.load_entries()

    def load_entries(self):
        date_str = self.date_selector.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("SELECT food, calories FROM calories WHERE entry_date = ? ORDER BY id DESC", (date_str,))
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(row[0]))
            self.table.setItem(i, 1, QTableWidgetItem(str(row[1])))

        # Resize columns to fit content after loading data
        self.table.resizeColumnsToContents()

        # Update total calories label
        total_calories = sum(row[1] for row in rows) if rows else 0
        selected_date_display = self.date_selector.date().toString("dd-MM-yyyy")
        self.calorie_label.setText(f"Daily Calories ({selected_date_display}): {total_calories}")

    def keyPressEvent(self, event):
        """Handle keyboard press of the DEL button"""
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_rows()
        else:
            # Pass other key events to the parent class
            super().keyPressEvent(event)

    def delete_selected_rows(self):
        """Deletes the selected row from the database"""
        selected_rows = sorted({index.row() for index in self.table.selectedIndexes()}, reverse=True)
        if not selected_rows:
            return

        reply = QMessageBox.question(
            self,
            "Delete Confirmation",
            f"Delete {len(selected_rows)} record(s) from database?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        date_str = self.date_selector.date().toString("yyyy-MM-dd")
        
        # Get all records for this date with their IDs
        c.execute("SELECT id, food, calories FROM calories WHERE entry_date = ? ORDER BY id DESC", (date_str,))
        rows = c.fetchall()

        # Delete the selected records
        for row_index in selected_rows:
            if row_index < len(rows):
                record_id = rows[row_index][0]  # Get the ID from the database query
                c.execute("DELETE FROM calories WHERE id = ?", (record_id,))

        conn.commit()
        conn.close()

        self.load_entries()

class ExerciseTracker(QWidget):
    """
    This is the exercise tracker page of the app. It is used to track the calories burned by the user through exercise.
    It contains a date selector, a table to show the entries for a given date, and a form to add and remove entries.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
       
        # Date selector section for picking which date to show calorie and food entries for
        self.date_selector = QDateEdit(calendarPopup=True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.setDisplayFormat("dd-MM-yyyy")
        self.date_selector.dateChanged.connect(self.load_entries)
        self.back_day_button = QPushButton("<")
        self.back_day_button.setFixedSize(30, 25)
        self.back_day_button.setObjectName("navigationBtn") # Navigation buttons are smaller than the other buttons in the styling to fit the < and > symbols. Thus needs a special identifier.
        self.back_day_button.clicked.connect(self.back_day)
        self.next_day_button = QPushButton(">")
        self.next_day_button.setFixedSize(30, 25)
        self.next_day_button.setObjectName("navigationBtn")
        self.next_day_button.clicked.connect(self.next_day)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Date:"))
        date_layout.addWidget(self.back_day_button)
        date_layout.addWidget(self.date_selector)
        date_layout.addWidget(self.next_day_button)


        # Input section for adding and removing food and calorie entries
        self.activity_input = QLineEdit()
        self.activity_input.setPlaceholderText("Enter activity name")
        self.calorie_input = QLineEdit()
        self.calorie_input.setPlaceholderText("Enter calories burned")

        self.add_button = QPushButton("Add Entry")
        self.remove_button = QPushButton("Remove Entry")
        self.add_button.clicked.connect(self.add_entry)
        self.remove_button.clicked.connect(self.remove_entry)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.activity_input)
        input_layout.addWidget(self.calorie_input)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.remove_button)

       

        # Table section to show entries for a given date
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Activity", "Calories"])
        
        # Enable automatic column resizing to fit content
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.Stretch) 
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().ResizeMode.ResizeToContents) 
        self.table.setWordWrap(True) # Enable word wrapping for long activity names
        self.table.setColumnWidth(1, 80) # Set minimum column widths
        
        # Enable keyboard focus and selection
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)

        # Section for showing total daily calorie intake for a given date
        self.calorie_label = QLabel("Daily Calories Burned:")
        self.calorie_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Add to layout
        self.layout.addLayout(date_layout)
        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.calorie_label)
        self.setLayout(self.layout)

        # Load existing data
        self.load_entries()

    def add_entry(self):
        activity = self.activity_input.text()
        try:
            calories = int(self.calorie_input.text())
        except ValueError:
            return  # Ignore if calories is not a number

        date_str = self.date_selector.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("INSERT INTO exercise (activity, calories, entry_date) VALUES (?, ?, ?)",
                  (activity, calories, date_str))
        conn.commit()
        conn.close()

        self.activity_input.clear()
        self.calorie_input.clear()
        self.load_entries()

    def remove_entry(self):
        row_count = self.table.rowCount()
        if row_count == 0:
            QMessageBox.information(self, "Remove Entry", "There are no entries to remove.")
            return

        # Ask user for row number
        row_number, ok = QInputDialog.getInt(
            self,
            "Remove Entry",
            f"Enter row number to remove (1 - {row_count}):",
            1, 1, row_count, 1
        )
        if not ok:
            return

        # Get IDs for this date only
        date_str = self.date_selector.date().toString("yyyy-MM-dd")
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("SELECT id FROM exercise WHERE entry_date = ? ORDER BY id DESC", (date_str,))
        ids = [row[0] for row in c.fetchall()]

        index = row_number - 1
        if index < 0 or index >= len(ids):
            conn.close()
            QMessageBox.warning(self, "Remove Entry", "Invalid row number.")
            return

        target_id = ids[index]
        c.execute("DELETE FROM exercise WHERE id = ?", (target_id,))
        conn.commit()
        conn.close()

        self.load_entries()

    def back_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.load_entries()
    
    def next_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.load_entries()

    def load_entries(self):
        date_str = self.date_selector.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("SELECT activity, calories FROM exercise WHERE entry_date = ? ORDER BY id DESC", (date_str,))
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(row[0]))
            self.table.setItem(i, 1, QTableWidgetItem(str(row[1])))

        # Resize columns to fit content after loading data
        self.table.resizeColumnsToContents()

        # Update total calories label
        total_calories = sum(row[1] for row in rows) if rows else 0
        selected_date_display = self.date_selector.date().toString("dd-MM-yyyy")
        self.calorie_label.setText(f"Daily Calories ({selected_date_display}): {total_calories}")

    def keyPressEvent(self, event):
        """Handle keyboard press of the DEL button"""
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_rows()
        else:
            # Pass other key events to the parent class
            super().keyPressEvent(event)

    def delete_selected_rows(self):
        """Deletes the selected row from the database"""
        selected_rows = sorted({index.row() for index in self.table.selectedIndexes()}, reverse=True)
        if not selected_rows:
            return

        reply = QMessageBox.question(
            self,
            "Delete Confirmation",
            f"Delete {len(selected_rows)} record(s) from database?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        date_str = self.date_selector.date().toString("yyyy-MM-dd")
        
        # Get all records for this date with their IDs
        c.execute("SELECT id, activity, calories FROM exercise WHERE entry_date = ? ORDER BY id DESC", (date_str,))
        rows = c.fetchall()

        # Delete the selected records
        for row_index in selected_rows:
            if row_index < len(rows):
                record_id = rows[row_index][0]  # Get the ID from the database query
                c.execute("DELETE FROM exercise WHERE id = ?", (record_id,))

        conn.commit()
        conn.close()

        self.load_entries()

class Graphs(QWidget):
    """
    This is the graphs page of the app. It is used to display the graphs of the calories consumed and burned over time.
    It contains a timeframe selector, a graph to show the data, and navigation buttons to increase or decrease the timeframe.
    TODO: Add in interactivness like that in the goals page.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Timeframe selection
        self.timeframe_selector = QComboBox()
        self.timeframe_selector.addItems(["1 Week", "2 Weeks", "1 Month", "3 Months", "1 Year", "Full History"])
        self.timeframe_selector.currentTextChanged.connect(self.load_graphs)

        # Navigation buttons
        self.back_button = QPushButton("<")
        self.back_button.setFixedSize(30, 25)
        self.back_button.setObjectName("navigationBtn") # Navigation buttons are smaller than the other buttons in the styling to fit the < and > symbols. Thus needs a special identifier.
        self.back_button.clicked.connect(self.back)
        self.next_button = QPushButton(">")
        self.next_button.setFixedSize(30, 25)
        self.next_button.setObjectName("navigationBtn")
        self.next_button.clicked.connect(self.next)
        
        # Layout box for the timeframe naivgation
        timeframe_layout = QHBoxLayout()
        timeframe_layout.addWidget(self.back_button)
        timeframe_layout.addWidget(self.timeframe_selector)
        timeframe_layout.addWidget(self.next_button)
        self.layout.addLayout(timeframe_layout)

        # Matplotlib canvas
        self.canvas = FigureCanvas(Figure(figsize=(6, 3), dpi=100))
        self.graph = self.canvas.figure.add_subplot(111)

        self.layout.addWidget(self.canvas)

        # Ensure canvas/figure/axes respect dark theme colors (Qt stylesheets do not style Matplotlib)
        light_fg = "#ffffff"
        grid_color = "#5a5a5a"
        try:
            self.canvas.setStyleSheet(f"background-color: {background_dark_gray};")
            self.canvas.figure.set_facecolor(background_dark_gray)
            self.graph.set_facecolor(background_dark_gray)
            for spine in self.graph.spines.values():
                spine.set_color(grid_color)
            self.graph.tick_params(colors=light_fg)
            self.graph.title.set_color(light_fg)
            self.graph.xaxis.label.set_color(light_fg)
            self.graph.yaxis.label.set_color(light_fg)
        except Exception:
            pass

        # Initial load
        self.load_graphs()

    def get_date_range(self, timeframe_label: str):
        # Find earliest entry_date in the database. The start date will not be earlier than this.
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("SELECT MIN(entry_date) FROM calories")
        earliest_row = c.fetchone()
        conn.close()
        earliest_qdate = QDate.fromString(earliest_row[0], "yyyy-MM-dd") if earliest_row and earliest_row[0] else None

        end_qdate = QDate.currentDate() # End date is the current date.
        if timeframe_label == "1 Week":
            start_qdate = end_qdate.addDays(-6)
        elif timeframe_label == "2 Weeks":
            start_qdate = end_qdate.addDays(-13)
        elif timeframe_label == "1 Month":
            start_qdate = end_qdate.addMonths(-1).addDays(1)
        elif timeframe_label == "3 Months":
            start_qdate = end_qdate.addMonths(-3).addDays(1)
        elif timeframe_label == "1 Year":
            start_qdate = end_qdate.addYears(-1).addDays(1)
        elif timeframe_label == "Full History": # First entry in the database to the current date.
            return None, end_qdate.toString("yyyy-MM-dd")
        else:
            start_qdate = end_qdate.addDays(-6)

        # If earliest date and start date < earliest date, it means we dont have entries goign that far back and so just keep the range within the bounds of known data.
        if earliest_qdate and start_qdate < earliest_qdate:
            start_qdate = earliest_qdate

        return start_qdate.toString("yyyy-MM-dd"), end_qdate.toString("yyyy-MM-dd")

    def back(self):
        current_index = self.timeframe_selector.currentIndex()
        if current_index > 0:
            self.timeframe_selector.setCurrentIndex(current_index - 1)


    def next(self):
        current_index = self.timeframe_selector.currentIndex()
        last_index = self.timeframe_selector.count() - 1
        if current_index < last_index:
            self.timeframe_selector.setCurrentIndex(current_index + 1)

    def load_graphs(self):
        timeframe = self.timeframe_selector.currentText()
        start_str, end_str = self.get_date_range(timeframe)

        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        
        # Fetch food calorie data
        if start_str is None:
            c.execute(
                """
                SELECT entry_date, SUM(calories) AS total
                FROM calories
                GROUP BY entry_date
                ORDER BY entry_date ASC
                """
            )
        else:
            c.execute(
                """
                SELECT entry_date, SUM(calories) AS total
                FROM calories
                WHERE entry_date BETWEEN ? AND ?
                GROUP BY entry_date
                ORDER BY entry_date ASC
                """,
                (start_str, end_str),
            )
        food_rows = c.fetchall()
        
        # Fetch exercise calorie data
        if start_str is None:
            c.execute(
                """
                SELECT entry_date, SUM(calories) AS total
                FROM exercise
                GROUP BY entry_date
                ORDER BY entry_date ASC
                """
            )
        else:
            c.execute(
                """
                SELECT entry_date, SUM(calories) AS total
                FROM exercise
                WHERE entry_date BETWEEN ? AND ?
                GROUP BY entry_date
                ORDER BY entry_date ASC
                """,
                (start_str, end_str),
            )
        exercise_rows = c.fetchall()
        conn.close()

        # Build a continuous date range and fill missing days with zero
        calorie_date_to_total = {r[0]: r[1] for r in food_rows}
        exercise_date_to_total = {r[0]: r[1] for r in exercise_rows}
        
        if start_str is None:
            if food_rows or exercise_rows:
                all_dates = []
                if food_rows:
                    all_dates.extend([r[0] for r in food_rows])
                if exercise_rows:
                    all_dates.extend([r[0] for r in exercise_rows])
                if all_dates:
                    start_date = min(datetime.strptime(d, "%Y-%m-%d").date() for d in all_dates)
                    end_date = max(datetime.strptime(d, "%Y-%m-%d").date() for d in all_dates)
                else:
                    start_date = datetime.today().date()
                    end_date = start_date
            else:
                start_date = datetime.today().date()
                end_date = start_date
        else:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

        dates = []
        food_totals = []
        exercise_totals = []
        overburn = []
        current = start_date
        index = 0
        while current <= end_date:
            key = current.strftime("%Y-%m-%d")
            dates.append(key)
            food_totals.append(calorie_date_to_total.get(key, 0))
            exercise_totals.append(exercise_date_to_total.get(key, 0) * -1)
            if food_totals[index] + exercise_totals[index] < 0:
                overburn.append(food_totals[index] + exercise_totals[index])
                exercise_totals[index] -= overburn[index]
            else:
                overburn.append(0)
            current += timedelta(days=1)
            index += 1

        # Prepare display labels in dd-MM-yyyy
        display_dates = [datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") for d in dates]

        self.graph.clear()
        if dates:
            # Plot data as bar charts
            self.graph.bar(dates, food_totals, color=active_dark_green, alpha=0.7, label='Calories Intake')
            self.graph.bar(dates, exercise_totals, color=calories_burned_red, alpha=0.7, bottom=food_totals, label='Calorie Burned')
            self.graph.bar(dates, overburn, color=overburn_orange, alpha=0.7, label='Overburn')

            self.graph.set_title("Daily Calories - Consumed vs Burned", color=white)
            self.graph.set_xlabel("Date", color=white)
            self.graph.set_ylabel("Calories", color=white)
            self.graph.grid(True, linestyle='--', alpha=0.3)
            self.graph.legend()
            
            # Label x-axis only when number of points is manageable
            if len(dates) <= 20:
                self.graph.set_xticks(range(len(dates)))
                self.graph.set_xticklabels(display_dates, rotation=45, ha='right')
            else:
                self.graph.set_xticks([])
            self.canvas.figure.tight_layout()
        else:
            self.graph.text(0.5, 0.5, "No data for selected range", ha='center', va='center', color=border_gray, transform=self.graph.transAxes)
            self.graph.set_xticks([])
            self.graph.set_yticks([])
        self.canvas.draw()

class Goals(QWidget):
    """
    This is the goals page of the app. It is used to track the weight goal of the user.
    It contains a current weight button, a target weight button, and a weight loss value label.
    Each point on the graph is interactive and can be expanded for more info and to edit or delete the entry.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
       
        # Following buttons are for inputting and displaying the weight goal values
        self.current_weight = QPushButton("Current Weight: -- kg")
        self.target_weight = QPushButton("Target Weight: -- kg")
        self.weight_loss_value = QLabel("Weight Loss: -- kg")

        self.current_weight.clicked.connect(self.input_current_weight)
        self.target_weight.clicked.connect(self.input_target_weight)

        target_layout = QHBoxLayout()
        target_layout.addWidget(self.current_weight)
        target_layout.addWidget(self.target_weight)
        target_layout.addWidget(self.weight_loss_value)

        self.layout.addLayout(target_layout)

        # Load existing values and update labels
        self.load_info()


        # Matplotlib canvas for displaying the history of weight entries
        self.canvas = FigureCanvas(Figure(figsize=(6, 3), dpi=100))
        self.graph = self.canvas.figure.add_subplot(111)

        self.layout.addWidget(self.canvas)

        # Ensure canvas/figure/axes respect dark theme colors (Qt stylesheets do not style Matplotlib)
        background_dark_gray = "#2b2b2b"
        light_fg = "#ffffff"
        grid_color = "#5a5a5a"
        try:
            self.canvas.setStyleSheet(f"background-color: {background_dark_gray};")
            self.canvas.figure.set_facecolor(background_dark_gray)
            self.graph.set_facecolor(background_dark_gray)
            for spine in self.graph.spines.values():
                spine.set_color(grid_color)
            self.graph.tick_params(colors=light_fg)
            self.graph.title.set_color(light_fg)
            self.graph.xaxis.label.set_color(light_fg)
            self.graph.yaxis.label.set_color(light_fg)
        except Exception:
            pass
        
        # Connect click event to canvas
        self.canvas.mpl_connect('button_press_event', self.on_click)
        
        # Initial load
        target_weight = self.get_target_weight()
        self.load_graphs(target_weight)


    def input_current_weight(self):
        """Make popup appear where user can enter a weight in kg for their current weight. 
        This data is recorded in a database so it's saved for future use.
        Change text of button to match the current weight."""
        weight, ok = QInputDialog.getDouble(
            self,
            "Current Weight",
            "Enter your current weight (kg):",
            value=100.0,
            min=50.0,
            max=300.0,
            decimals=1
        )
        if ok:
            # Save to database
            conn = sqlite3.connect("health_app.db")
            c = conn.cursor()
            c.execute("INSERT INTO goals (current_weight, updated_date) VALUES (?, ?)",
                     (weight, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            
            # Update button text
            self.current_weight.setText(f"Current Weight: {weight} kg")
            # Reload to update weight loss calculation and graph
            self.load_info()
            # Get target weight for graph y-axis limit
            target_weight = self.get_target_weight()
            self.load_graphs(target_weight)

    def input_target_weight(self):
        """Make popup appear where user can enter a weight in kg for their target weight. 
        This data is recorded in a database so it's saved for future use.
        Change text of button to match the target weight."""
        weight, ok = QInputDialog.getDouble(
            self,
            "Target Weight",
            "Enter your target weight (kg):",
            value=100.0,
            min=50.0,
            max=300.0,
            decimals=1
        )
        if ok:
            # Save to database
            conn = sqlite3.connect("health_app.db")
            c = conn.cursor()
            c.execute("INSERT INTO goals (target_weight, updated_date) VALUES (?, ?)",
                     (weight, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            
            # Update button text
            self.target_weight.setText(f"Target Weight: {weight} kg")
            # Reload to update weight loss calculation and graph
            self.load_info()
            # Refresh graph with new target weight as y-axis limit
            self.load_graphs(weight)

    def get_target_weight(self):
        """Get the current target weight from database"""
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("SELECT target_weight FROM goals WHERE target_weight IS NOT NULL ORDER BY updated_date DESC LIMIT 1")
        target_row = c.fetchone()
        conn.close()
        return target_row[0] if target_row else None
    
    def load_info(self):
        """Reload the page so the current and target weight buttons reflect the respective 
        values in the database and the loss value label shows the difference."""
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()       
        # Get latest current weight
        c.execute("SELECT current_weight FROM goals WHERE current_weight IS NOT NULL ORDER BY updated_date DESC LIMIT 1")
        current_row = c.fetchone()
        current_weight = current_row[0] if current_row else None
        
        # Get latest target weight
        c.execute("SELECT target_weight FROM goals WHERE target_weight IS NOT NULL ORDER BY updated_date DESC LIMIT 1")
        target_row = c.fetchone()
        target_weight = target_row[0] if target_row else None
        
        conn.close()
        
        # Update button texts
        if current_weight is not None:
            self.current_weight.setText(f"Current Weight: {current_weight} kg")
        else:
            self.current_weight.setText("Current Weight: -- kg")
            
        if target_weight is not None:
            self.target_weight.setText(f"Target Weight: {target_weight} kg")
        else:
            self.target_weight.setText("Target Weight: -- kg")
        
        # Calculate and display weight loss
        if current_weight is not None and target_weight is not None:
            weight_loss = current_weight - target_weight
            if weight_loss > 0:
                self.weight_loss_value.setText(f"Weight Loss Goal: {weight_loss:.1f} kg")
            elif weight_loss < 0:
                self.weight_loss_value.setText(f"Weight Gain Goal: {abs(weight_loss):.1f} kg")
            else:
                self.weight_loss_value.setText("Goal Achieved! 🎉")
        else:
            self.weight_loss_value.setText("Weight Loss: -- kg")

    def load_graphs(self, target_weight):
        """Load and display weight progress graph from database"""
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        
        # Query for current weight entries with dates and IDs
        c.execute("""
            SELECT id, current_weight, updated_date 
            FROM goals 
            WHERE current_weight IS NOT NULL 
            ORDER BY updated_date ASC
        """)
        rows = c.fetchall()
        conn.close()

        ids = []
        dates = []
        weights = []

        # Extract IDs, dates and weights from database results
        for row in rows:
            entry_id = row[0]  # id
            weight = row[1]  # current_weight
            date_str = row[2]  # updated_date
            
            # Convert date string to datetime for proper sorting and display
            try:
                # Try parsing as date-only format first (YYYY-MM-DD)
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                ids.append(entry_id)
                dates.append(date_obj.strftime("%d-%m-%Y"))  # Format for display
                weights.append(weight)
            except ValueError:
                try:
                    # Fallback to datetime format for old entries (YYYY-MM-DD HH:MM:SS)
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    ids.append(entry_id)
                    dates.append(date_obj.strftime("%d-%m-%Y"))  # Format for display
                    weights.append(weight)
                except ValueError:
                    # Skip entries with invalid date formats
                    continue
        
        # Store data for click events
        self.ids_copy = ids.copy()
        self.dates_copy = dates.copy()
        self.weights_copy = weights.copy()

        self.graph.clear()
        
        if dates and weights:
            # Plot the weight data
            self.graph.plot(dates, weights, marker='o', color= active_dark_green, linewidth=2)
            self.graph.fill_between(range(len(weights)), weights, color= active_dark_green, alpha=0.15)
            self.graph.set_title("Weight Progress", color=white)
            self.graph.set_xlabel("Date", color=white)
            self.graph.set_ylabel("Weight (kg)", color=white)
            self.graph.grid(True, linestyle='--', alpha=0.3)
            
            # Label x-axis only when number of points is manageable
            if len(dates) <= 20:
                self.graph.set_xticks(range(len(dates)))
                self.graph.set_xticklabels(dates, rotation=45, ha='right')
            else:
                self.graph.set_xticks([])
        else:
            # Show message when no data is available
            self.graph.text(0.5, 0.5, "No weight data available", 
                          ha='center', va='center', color=border_gray, 
                          transform=self.graph.transAxes)
            self.graph.set_xticks([])
            self.graph.set_yticks([])
            self.graph.set_title("Weight Progress", color=white)
            self.graph.set_xlabel("Date", color=white)
            self.graph.set_ylabel("Weight (kg)", color=white)
        
        # Set y-axis bottom limit to target weight if provided (apply to both cases)
        if target_weight is not None:
            self.graph.set_ylim(bottom=target_weight)
        else:
            self.graph.set_ylim(bottom=50.0)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def on_click(self, event):
        """Handle click events on the graph to show data point information"""
        
        
        # Check if cursor aligns with a data point
        if event.inaxes != self.graph:
            return
        if not self.dates_copy or not self.weights_copy:
            return
        click_x = event.xdata
        click_y = event.ydata
        if click_x is None or click_y is None:
            return
        
        # Find the closest data point
        min_distance = float('inf')
        closest_index = -1
        
        for i, (date_str, weight) in enumerate(zip(self.dates_copy, self.weights_copy)):
            # Convert date string back to index for distance calculation
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            x_coord = i  # x-axis is indexed by position
            y_coord = weight
            
            # Calculate distance from click to data point
            distance = ((click_x - x_coord) ** 2 + (click_y - y_coord) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_index = i
        
        # Show popup if we found a close enough point (within reasonable distance)
        if closest_index >= 0 and min_distance < 0.5:  # Adjust threshold as needed
            date_str = self.dates_copy[closest_index]
            weight = self.weights_copy[closest_index]
            
            # Create and show popup dialog
            self.show_data_point_popup(date_str, weight, closest_index)
    
    def show_data_point_popup(self, date_str, weight, index):
        """Show popup dialog with data point information"""
        # Calculate days since first entry
        if self.dates_copy:
            first_date = datetime.strptime(self.dates_copy[0], "%d-%m-%Y")
            current_date = datetime.strptime(date_str, "%d-%m-%Y")
            days_since_start = (current_date - first_date).days
            
            # Calculate weight change from previous entry
            weight_change = ""
            if index > 0:
                prev_weight = self.weights_copy[index - 1]
                change = weight - prev_weight
                if change > 0:
                    weight_change = f" (+{change:.1f} kg from previous)"
                elif change < 0:
                    weight_change = f" ({change:.1f} kg from previous)"
                else:
                    weight_change = " (no change from previous)"
            
            # Calculate weight change from first entry
            total_change = ""
            if index > 0:
                first_weight = self.weights_copy[0]
                total_change_val = weight - first_weight
                if total_change_val > 0:
                    total_change = f" (+{total_change_val:.1f} kg from start)"
                elif total_change_val < 0:
                    total_change = f" ({total_change_val:.1f} kg from start)"
                else:
                    total_change = " (no change from start)"
            
            #The following message is indented in the popup but I disliked how it looked code wise if I had no indentation here
            message = f"""Weight Entry Details:
            Date: {date_str}
            Weight: {weight:.1f} kg
            Days since start: {days_since_start}{weight_change}{total_change}

            Entry #{index + 1} of {len(self.dates_copy)} total entries"""
        else:
            message = f"Date: {date_str}\nWeight: {weight:.1f} kg"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Weight Entry Details")
        msg_box.setText(message)

        ok_button = msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        edit_button = msg_box.addButton("Edit", QMessageBox.ButtonRole.ActionRole)
        delete_button = msg_box.addButton("Delete", QMessageBox.ButtonRole.DestructiveRole)
        
        msg_box.exec()

        clicked_button = msg_box.clickedButton()

        if clicked_button == ok_button:
            return
        elif clicked_button == edit_button:
            entry_id = self.ids_copy[index]
            self.edit_weight_entry(date_str, weight, index, entry_id)
            return
        elif clicked_button == delete_button:
            entry_id = self.ids_copy[index]
            self.delete_weight_entry(date_str, weight, index, entry_id)
            return

    def edit_weight_entry(self, current_date_str, current_weight, index, entry_id):
        """Show edit dialog for weight entry"""
        # Parse current date for the dialog
        current_date = datetime.strptime(current_date_str, "%d-%m-%Y")
        
        # Create custom dialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Weight Entry")
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Date input
        date_edit = QDateEdit()
        date_edit.setDate(QDate.fromString(current_date_str, "dd-MM-yyyy"))
        date_edit.setDisplayFormat("dd-MM-yyyy")
        form_layout.addRow("Date:", date_edit)
        
        # Weight input
        weight_input, ok = QInputDialog.getDouble(
            dialog,
            "Edit Weight",
            "Enter new weight (kg):",
            value=current_weight,
            min=50.0,
            max=300.0,
            decimals=1
        )
        
        if not ok:
            return  # User cancelled
            
        # Create button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_date = date_edit.date()
            new_date_str = new_date.toString("yyyy-MM-dd")
            
            # Update database using the entry ID
            self.update_weight_entry(entry_id, new_date_str, weight_input)
            
    def update_weight_entry(self, entry_id, new_date_str, new_weight):
        """Update the weight entry in the database using the entry ID"""
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        
        # Update the entry by ID
        c.execute("""
            UPDATE goals 
            SET current_weight = ?, updated_date = ?
            WHERE id = ?
        """, (new_weight, new_date_str, entry_id))
        
        conn.commit()
        conn.close()
        
        # Reload the graph and refresh all labels
        target_weight = self.get_target_weight()
        self.load_graphs(target_weight)
        
        # Force complete refresh of the canvas and axis labels
        self.canvas.figure.tight_layout()
        self.canvas.flush_events()
        self.canvas.draw()

    def delete_weight_entry(self, current_date_str, current_weight, index, entry_id):
        """Remove weight entry from database and graph"""
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("DELETE FROM goals WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
        
        # Reload the graph and refresh all labels
        target_weight = self.get_target_weight()
        self.load_graphs(target_weight)
        
        # Force complete refresh of the canvas and axis labels
        self.canvas.figure.tight_layout()
        self.canvas.flush_events()
        self.canvas.draw()

class DayWidget(QWidget):
    """
    This class represents a single day widget in the meal plan.
    It contains a header label(button) for the day name and a QTextEdit for the meal list.
    The meal list is automatically saved to the database when changed.
    TODO: Add AI functionality to the day widget to suggest meals for the day.
    """
    def __init__(self, day_name, valid_days):
        super().__init__()
        self.day_name = day_name
        self.valid_days = valid_days
        
        # Create layout for the day widget
        day_layout = QVBoxLayout()
        self.setLayout(day_layout)
        
        # Day header
        self.day_header = QPushButton(day_name)
        self.day_header.clicked.connect(self.show_AI_meal_plan_popup)
        
        # Meal list text editor
        self.meal_list = QTextEdit()
        day_text = self.get_day_text_from_db()
        if day_text is None or day_text == "":
            self.meal_list.setText("• Breakfast\n• Lunch\n• Dinner\n• Snacks")
        else:
            self.meal_list.setText(day_text)
        self.meal_list.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align text to top for better wrapping
        
        # Connect textChanged signal to save to database
        self.meal_list.textChanged.connect(self.on_text_changed)
        
        # Add header and list to day layout with proper stretch
        day_layout.addWidget(self.day_header, 0)  # Header doesn't stretch
        day_layout.addWidget(self.meal_list, 1)   # Meal list stretches to fill remaining space
        day_layout.setContentsMargins(1, 1, 1, 1)  # Minimal margins within each day
        day_layout.setSpacing(2)  # Minimal spacing between header and list
    
    def get_day_text_from_db(self):
        """Load the meal text for this day from the database"""
        # Guard against unexpected column name injection by validating against known days
        if self.day_name not in self.valid_days:
            return None
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        # Select explicit column for the single row (id = 1)
        c.execute(f"SELECT {self.day_name} FROM meal_plan WHERE id = 1")
        row = c.fetchone()
        conn.close()
        if row is None:
            return None
        return row[0]
    
    def on_text_changed(self):
        """Handle text changes and save to database"""
        new_text = self.meal_list.toPlainText()
        self.update_day_text_in_db(new_text)
    
    def update_day_text_in_db(self, new_text):
        """Update the meal text for this day in the database"""
        if self.day_name not in self.valid_days:
            return
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        # Update explicit column for the single row (id = 1)
        c.execute(f"UPDATE meal_plan SET {self.day_name} = ? WHERE id = 1", (new_text,))
        conn.commit()
        conn.close()

    def show_AI_meal_plan_popup(self):
        """
        Show a popup to have AI suggest meals for the day or alternatives to the current meal list for that day. 
        This is disabled if the meal plan AI is disabled in the settings.
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("AI Meal Plan Suggestions")
        msg_box.setText("Would you like to use the OpenAI feature to suggest a meal plan for the day?.")

        Yes_button = msg_box.addButton("Yes", QMessageBox.ButtonRole.AcceptRole)
        No_button = msg_box.addButton("No", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()

        clicked_button = msg_box.clickedButton()

        if clicked_button == Yes_button:     
            self.ai_suggest_day_meal_plan()
        elif clicked_button == No_button:
            return


    def ai_suggest_day_meal_plan(self):
        """Suggest a meal plan for the day using AI with option chips. TODO: Add dietry requirement options for the prompt and cut out AI fluff."""
        current_text = self.meal_list.toPlainText()
        dialog = PlannerOptionsDialog(self, current_text)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # if the user has decided to use the AI feature, form a prompt for it in proper readable english
            AI_promt = "Can you suggest a meal plan for the day by giving me suggestions on what to eat? "
            options = dialog.values() # get the selected options from the popup box and add them to a list
            additional_criteria = []
            for key, value in options.items():
                if value:
                    additional_criteria.append(key)

            # Add the additional criteria to the prompt in proper readable english
            if len(additional_criteria) == 1:
                AI_promt += "I want the meal plan to be " + additional_criteria[0] + ". "
            elif len(additional_criteria) > 1: # add "," between the criteria except for the last one which has "and"
                AI_promt += "I want the meal plan to be " + ", ".join(additional_criteria[:-1]) + " and " + additional_criteria[-1] + ". "
            # Include the current meal plan in the prompt if it exists
            if current_text:
                AI_promt += "The current meal plan is: " + current_text + ". You can use this as a starting point, make changes to it or scrap it entirely if it doesnt fit the criteria."
            
            #debugging print, remove later
            print(AI_promt)

            # Create worker and run in background thread
            worker = AIWorker(AI_promt)
            worker.finished.connect(self.meal_plan_on_ai_response)
            worker.error.connect(self.meal_plan_on_ai_error)
            
            # Store worker reference to prevent garbage collection
            self.current_worker = worker
            self.ai_request_in_progress = True
            
            # Run AI request in background thread
            thread = threading.Thread(target=worker.run)
            thread.daemon = True
            thread.start() 

        else:
            return

    def meal_plan_on_ai_response(self, response):
        """Handle successful AI response"""
        self.meal_list.setPlainText(response)

    def meal_plan_on_ai_error(self, error_message):
        """Handle AI request error"""
        print(error_message)

class PlannerOptionsDialog(QDialog):
    """
    Popup dialog showing chip-style toggle options using checkable QToolButtons.
    Note: This was done as I didnt want to use checkboxes as they are not as visually appealing or consistent with the rest of the app.
    While this is more code and more complex, I belive it is worth it for the better user experience.
    """
    def __init__(self, parent=None, current_text=None):
        super().__init__(parent)
        self.setWindowTitle("AI Meal Planner Options")
        self.current_text = current_text
        main_layout = QVBoxLayout(self)

        label = QLabel("Choose any options you want to include:")
        main_layout.addWidget(label)

        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)

        self.healthy = self._make_chip("Healthy")
        self.cheap = self._make_chip("Cheap")
        self.vegetarian = self._make_chip("Vegetarian")
        self.vegan = self._make_chip("Vegan")
        self.quick = self._make_chip("Quick")

        chips_layout.addWidget(self.healthy)
        chips_layout.addWidget(self.cheap)
        chips_layout.addWidget(self.vegetarian)
        chips_layout.addWidget(self.vegan)
        chips_layout.addWidget(self.quick)

        main_layout.addLayout(chips_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)


    def _make_chip(self, text: str) -> QToolButton:
        btn = QToolButton(self)
        btn.setText(text)
        btn.setCheckable(True)
        btn.setAutoRaise(True)
        return btn

    def values(self) -> dict:
        return {
            "healthy": self.healthy.isChecked(),
            "cheap": self.cheap.isChecked(),
            "vegetarian": self.vegetarian.isChecked(),
            "vegan": self.vegan.isChecked(),
            "quick": self.quick.isChecked(),
        }
        
class MealPlan(QWidget):
    """
    This class creates the meal plan page of the app.
    It contains a layout for the days of the week, and a widget for each day.
    The widget for each day are interactive and allow the user to edit the meal list for the day.
    The meal list is saved to the database when the user edits it.
    """
    def __init__(self):
        super().__init__()
        
        # Initialize QSettings for persistent settings
        self.settings = QSettings("MindfulMauschen", "HealthApp")

        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        # Ensure there is exactly one row to update against (id = 1)
        c.execute("SELECT COUNT(*) FROM meal_plan")
        count_row = c.fetchone()
        existing_count = count_row[0] if count_row else 0
        if existing_count == 0:
            c.execute(
                """
                INSERT INTO meal_plan (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
                VALUES ('', '', '', '', '', '', '')
                """
            )
            conn.commit()
        conn.close()

        self.layout = QVBoxLayout()
        
        # One widget for each day of the week
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Create main horizontal layout for all days
        self.days_layout = QHBoxLayout()
        self.days_layout.setSpacing(2)  # Minimal spacing between columns
        self.days_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create a widget for each day
        self.day_widgets = []
        for day in self.days:
            day_widget = DayWidget(day, self.days)
            self.day_widgets.append(day_widget)
            # Add stretch to make each day widget expand equally
            self.days_layout.addWidget(day_widget, 1)  # Stretch factor of 1 for equal distribution

        
        # Add the days layout to main layout
        self.layout.addLayout(self.days_layout)
        self.setLayout(self.layout)

        # If the meal plan AI is disabled, make the daywidgets headers buttons disabled 
        self.update_header_buttons_state()
    
    def update_header_buttons_state(self):
        """Update the enabled/disabled state of day header buttons based on meal plan AI setting"""
        meal_plan_ai_enabled = self.settings.value("meal_plan_ai_enabled", False, type=bool)
        for day_widget in self.day_widgets:
            day_widget.day_header.setEnabled(meal_plan_ai_enabled)

class AIWorker(QObject):
    """
    This class is a worker class to handle AI requests in a separate thread.
    It is used to handle the AI requests for the meal plan and shopping list.
    It was made asynchronously as intially when a user hit the send button, the app would freeze until the response was ready.
    """
    finished = Signal(str)  # Signal emitted when AI response is ready
    error = Signal(str)  # Signal emitted if there's an error
    
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
    
    def run(self):
        """Execute the AI request"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a health assistant. Provide practical advice and meal suggestions. Be friendly and informative."},
                    {"role": "user", "content": self.prompt}
                ]
            )
            self.finished.emit(response.choices[0].message.content)
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class ChatBot(QWidget):
    """
    This class creates the chat bot page of the app.
    It contains a chat area and an input field for the user to enter their message.
    The requests and responses are displayed in the chat area.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(40)  # Start with single line height
        self.input_field.textChanged.connect(self.adjust_input_height)
        self.send_button = QPushButton("Send")

        self.layout.addWidget(self.chat_area)
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)

        self.send_button.clicked.connect(self.handle_send)
        
        # Track if AI request is in progress
        self.ai_request_in_progress = False
        self.current_worker = None

    def adjust_input_height(self):
        """Adjust the input field height based on content"""
        # Calculate the height needed for the content
        doc = self.input_field.document()
        doc_height = doc.size().height()
        
        # Get the font metrics to calculate proper line height
        font_metrics = self.input_field.fontMetrics()
        line_height = font_metrics.height()
        
        # Set a reasonable minimum and maximum height
        min_height = 40  # Single line
        max_height = 120  # About 4-5 lines max
        
        # Calculate the new height with proper line spacing and padding
        # Add extra padding to ensure the full line is visible
        new_height = max(min_height, min(doc_height + line_height + 10, max_height))
        
        # Update the height
        self.input_field.setMaximumHeight(int(new_height))

    def handle_send(self):
        """Handle send button click - create async AI request"""
        user_message = self.input_field.toPlainText().strip()
        if not user_message:
            return
        
        # Prevent multiple simultaneous requests
        if self.ai_request_in_progress:
            return

        # Display user message
        self.chat_area.append(f"You: {user_message}")
        self.input_field.clear()
        
        # Show "thinking" indicator
        self.chat_area.append("AI: Thinking...")
        
        # Disable send button and input
        self.set_ui_state(False)
        
        # Create worker and run in background thread
        worker = AIWorker(user_message)
        worker.finished.connect(self.chat_bot_on_ai_response)
        worker.error.connect(self.chat_bot_on_ai_error)
        
        # Store worker reference to prevent garbage collection
        self.current_worker = worker
        self.ai_request_in_progress = True
        
        # Run AI request in background thread
        thread = threading.Thread(target=worker.run)
        thread.daemon = True
        thread.start()
    
    def set_ui_state(self, enabled):
        """Enable or disable UI elements during AI request"""
        self.send_button.setEnabled(enabled)
        self.input_field.setEnabled(enabled)
    
    def chat_bot_on_ai_response(self, response):
        """Handle successful AI response"""
        # Remove "Thinking..." and add actual response
        text = self.chat_area.toPlainText()
        if text.endswith("AI: Thinking..."):
            text = text.rsplit("AI: Thinking...", 1)[0]
        self.chat_area.setPlainText(text)
        
        # Add the actual AI response
        self.chat_area.append(f"AI: {response}\n")
        
        # Re-enable UI
        self.set_ui_state(True)
        self.ai_request_in_progress = False
        self.current_worker = None
    
    def chat_bot_on_ai_error(self, error_message):
        """Handle AI request error"""
        # Remove "Thinking..." and add error message
        text = self.chat_area.toPlainText()
        if text.endswith("AI: Thinking..."):
            text = text.rsplit("AI: Thinking...", 1)[0]
        self.chat_area.setPlainText(text)
        
        # Add error message
        self.chat_area.append(f"AI: {error_message}\n")
        
        # Re-enable UI
        self.set_ui_state(True)
        self.ai_request_in_progress = False
        self.current_worker = None

class Settings(QWidget):
    """
    This class creates the settings page of the app.
    It contains a checkbox for each setting and a button to test the desktop notifications.
    The settings are saved to the registry on Windows.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Initialize QSettings for persistent settings
        self.settings = QSettings("MindfulMauschen", "HealthApp")

        
        # Toggle checkboxes section
        self.startup_checkbox = QCheckBox("Enable app auto launch on Windows startup")
        self.food_ai_checkbox = QCheckBox("Enable AI assisted calorie suggestions when inputting food into the tracker")
        self.exercise_ai_checkbox = QCheckBox("Enable AI assisted calorie suggestions when inputting exercise into the tracker")
        self.meal_plan_ai_checkbox = QCheckBox("Enable AI assisted meal plan suggestions")
        self.silent_notif_checkbox = QCheckBox("Make desktop notifications silent")
        
        # Desktop notification test button
        self.desktop_notif = QPushButton("Desktop Notification Test")
        # Button to allow user to import a database to use for the app
        self.import_database_button = QPushButton("Import Database")
        self.import_database_button.clicked.connect(self.import_database)
        
        # Connect checkbox state changes to save settings (except startup which is handled separately)
        self.food_ai_checkbox.stateChanged.connect(self.save_settings)
        self.exercise_ai_checkbox.stateChanged.connect(self.save_settings)
        self.meal_plan_ai_checkbox.stateChanged.connect(self.save_settings)
        self.silent_notif_checkbox.stateChanged.connect(self.save_settings)
        
        # Add widgets to layout
        self.layout.addWidget(self.startup_checkbox)
        self.layout.addWidget(self.food_ai_checkbox)
        self.layout.addWidget(self.exercise_ai_checkbox)
        self.layout.addWidget(self.meal_plan_ai_checkbox)
        self.layout.addWidget(self.silent_notif_checkbox)
        self.layout.addWidget(self.desktop_notif)
        self.layout.addWidget(self.import_database_button)

        # Load saved settings
        self.load_settings()
    
    def get_app_path(self):
        """Get the path to the application executable or script"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as Python script
            return f'"{sys.executable}" "{os.path.abspath(__file__)}"'
    
    def is_startup_enabled(self, startup_settings):
        """Check if the app is set to run on Windows startup"""
        app_name = "MindfulMauschen"
        return startup_settings.contains(app_name)
    
    def toggle_startup(self, state, startup_settings):
        """Enable or disable app launch on Windows startup"""
        app_name = "MindfulMauschen"
        
        if state == Qt.CheckState.Checked.value:
            # Add to startup
            app_path = self.get_app_path()
            startup_settings.setValue(app_name, app_path)
            startup_settings.sync()
        else:
            # Remove from startup
            startup_settings.remove(app_name)
            startup_settings.sync()
    
    def load_settings(self):
        """Load saved settings and apply them to checkboxes"""
        # Originally was having issues where toggling multiple checkboxes at once would only save one of  them
        # As such added in block signals while loading to prevent save_settings from being called and ensuring all checkbox states are saved correctly
        self.startup_checkbox.blockSignals(True)
        self.food_ai_checkbox.blockSignals(True)
        self.exercise_ai_checkbox.blockSignals(True)
        self.silent_notif_checkbox.blockSignals(True)
        self.meal_plan_ai_checkbox.blockSignals(True)
        
        # Load checkbox states (default to False if not found)
        self.startup_checkbox.setChecked(
            self.settings.value("startup_enabled", False, type=bool)
        )
        self.food_ai_checkbox.setChecked(
            self.settings.value("food_ai_enabled", False, type=bool)
        )
        self.exercise_ai_checkbox.setChecked(
            self.settings.value("exercise_ai_enabled", False, type=bool)
        )
        self.silent_notif_checkbox.setChecked(
            self.settings.value("silent_notif_enabled", False, type=bool)
        )
        self.meal_plan_ai_checkbox.setChecked(
            self.settings.value("meal_plan_ai_enabled", False, type=bool)
        )
        
        # Unblock signals after loading
        self.startup_checkbox.blockSignals(False)
        self.food_ai_checkbox.blockSignals(False)
        self.exercise_ai_checkbox.blockSignals(False)
        self.silent_notif_checkbox.blockSignals(False)
        self.meal_plan_ai_checkbox.blockSignals(False)
    
    def save_settings(self):
        """Save current checkbox states to persistent storage"""
        self.settings.setValue("food_ai_enabled", self.food_ai_checkbox.isChecked())
        self.settings.setValue("exercise_ai_enabled", self.exercise_ai_checkbox.isChecked())
        self.settings.setValue("silent_notif_enabled", self.silent_notif_checkbox.isChecked())
        self.settings.setValue("meal_plan_ai_enabled", self.meal_plan_ai_checkbox.isChecked())
        self.settings.sync()
    
    def save_startup_setting(self):
        """Save startup checkbox state separately"""
        self.settings.setValue("startup_enabled", self.startup_checkbox.isChecked())
        self.settings.sync()

    def import_database(self):
        """
        Allow the user to import another instance of the database to use for the app.
        While the databse persists between instances, new versions from the exe produced by pyinstaller will not be able to use the old database.
        This function allows the user to import one from file, useful for dev testing and perhaps other use cases.
        """
        # File explorer for user to find the database file to import (might need to make an export for exe users who dont have the loose source files)
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Database", "", "Database Files (*.db)")
        if file_path:
            try:
                # Backup existing database if it exists
                if os.path.exists("health_app.db"):
                    backup_path = f"health_app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy("health_app.db", backup_path)
                
                # Copy the imported database file to the app's directory
                shutil.copy(file_path, "health_app.db")
                
                QMessageBox.information(
                    self,
                    "Database Imported",
                    "Database imported successfully!\n\nPlease restart the application to see the changes."
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Import Error",
                    f"Failed to import database:\n{str(e)}"
                )

class HealthApp(QMainWindow):
    """
    This class creates the main window of the app.
    It contains the tabs for the different pages of the app.
    It also contains the startup settings for the app.
    """
    def __init__(self):
        super().__init__()
        # Initialize QSettings for app preferences
        self.settings = QSettings("MindfulMauschen", "HealthApp")
        # Windows startup registry settings
        self.startup_settings = QSettings(
            "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            QSettings.Format.NativeFormat
        )
        self.setWindowTitle("Health Tracker App")
        self.setGeometry(300, 300, 800, 400)
        # Prefer an .ico for Windows taskbar; fallback to PNG if .ico not present
        icon_path_ico = os.path.join("assets", "legnedary_astrid_boop_upscale.ico")
        icon_path_png = os.path.join("assets", "legnedary_astrid_boop_upscale.png")
        window_icon = QIcon(icon_path_ico) if os.path.exists(icon_path_ico) else QIcon(icon_path_png)
        self.setWindowIcon(window_icon)
        
        # Apply dark theme styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {background_dark_gray};
                color: {white};
            }}
            QTabWidget::pane {{
                border: 1px solid {border_gray};
                background-color: {background_dark_gray};
                border-radius: 8px;
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
            QTabBar::tab {{
                background-color: {border_gray};
                color: {white};
                padding: 8px 16px;
                margin: 2px;
                border-radius: 6px;
                border: none;
            }}
            QTabBar::tab:selected {{
                background-color: {button_active_light_gray};
            }}
            QTabBar::tab:hover {{
                background-color: {hover_gray};
            }}
            QPushButton {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton#navigationBtn {{
                padding: 2px 6px;
                min-width: 0px; /* smaller padding for  the < and > buttons which were getting cut off due to not enough space */
            }}
            QPushButton:hover {{
                background-color: {hover_light_green};
            }}
            QPushButton:pressed {{
                background-color: {active_dark_green};
            }}
            QLineEdit {{
                background-color: {background_dark_gray};
                color: {white};
                border: 2px solid {border_gray};
                padding: 8px;
                border-radius: 6px;
            }}
            QLineEdit:focus {{
                border-color: {active_dark_green};
            }}
            QDateEdit {{
                background-color: {background_dark_gray};
                color: {white};
                border: 2px solid {border_gray};
                padding: 8px;
                border-radius: 6px;
            }}
            QDateEdit:focus {{
                border-color: {active_dark_green};
            }}
            QTableWidget {{
                background-color: {background_dark_gray};
                color: {white};
                border: 2px solid {border_gray};
                border-radius: 8px;
                gridline-color: {border_gray};
                selection-background-color: {active_dark_green};
                alternate-background-color: {background_dark_gray};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {border_gray};
                background-color: {background_dark_gray};
                color: {white};
            }}
            QTableWidget::item:selected {{
                background-color: {active_dark_green};
                color: {white};
            }}
            QTableWidget::item:alternate {{
                background-color: {background_dark_gray};
            }}
            QHeaderView {{
                background-color: {border_gray};
                color: {white};
            }}
            QHeaderView::section {{
                background-color: {border_gray} !important;
                color: {white} !important;
                padding: 8px;
                border: none;
                font-weight: bold;
                border-radius: 0px;
            }}
            QHeaderView::section:horizontal {{
                border-right: 1px solid {button_active_light_gray};
                background-color: {border_gray} !important;
                color: {white} !important;
            }}
            QHeaderView::section:vertical {{
                border-bottom: 1px solid {button_active_light_gray};
                background-color: {border_gray} !important;
                color: {white} !important;
            }}
            QTableCornerButton::section {{
                background-color: {border_gray} !important;
                border: none;
            }}
            QLabel {{
                color: {white};
            }}
            QComboBox {{
                background-color: {border_gray};
                color: {white};
                border: 2px solid transparent;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QComboBox:hover {{ 
                background-color: {border_gray};
                border-color: {hover_light_green};
            }}
            Figure {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QInputDialog {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QMessageBox {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QCheckBox {{
                color: {white};
                background-color: {background_dark_gray};
            }}
            QcheckBox:indicator:checked {{
                color: {white};
                background-color: {background_dark_gray};
            }}
            QLabel#headerLabel, QPushButton#headerLabel {{
                color: {white};
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                background-color: {border_gray};
                border-radius: 6px;
                margin-bottom: 4px;
                max-height: 20px;
                text-align: center;
            }}
            QTextEdit {{
                color: {white};
                background-color: {background_dark_gray};
                border: 1px solid {border_gray};
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }}
            QToolButton {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QToolButton:checked {{
                background: {active_dark_green};
                border-color: {border_gray};
            }}
            QToolButton:hover {{
                background-color: {hover_light_green};
                border-color: {border_gray};
            }}
            QDialog {{
                background-color: {background_dark_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }}
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.home_page = HomePage()
        self.Settings = Settings()
        self.MealPlan = MealPlan()
        self.tabs.addTab(self.home_page, "Home")
        self.tabs.addTab(CalorieTracker(), "Calorie Tracker")
        self.tabs.addTab(ExerciseTracker(), "Exercise Tracker")
        self.tabs.addTab(Graphs(), "Graphs")
        self.tabs.addTab(Goals(), "Goals")
        self.tabs.addTab(self.MealPlan, "Meal Plans")
        self.tabs.addTab(ChatBot(), "Chat Bot")
        self.tabs.addTab(self.Settings, "Settings")
        
        # Connect meal plan AI checkbox to update MealPlan button states
        self.Settings.meal_plan_ai_checkbox.stateChanged.connect(self.MealPlan.update_header_buttons_state)

        # Setup system tray icon for desktop notifications
        icon_path_ico = os.path.join("assets", "legnedary_astrid_boop_upscale.ico")
        icon_path_png = os.path.join("assets", "legnedary_astrid_boop_upscale.png")
        tray_icon = QIcon(icon_path_ico) if os.path.exists(icon_path_ico) else QIcon(icon_path_png)
        self.tray = QSystemTrayIcon(tray_icon, self)
        self.tray.setVisible(True)
        self.tray.setToolTip("Mindful Mäuschen")
        
        # Connect the notification button from HomePage
        self.Settings.desktop_notif.clicked.connect(self.send_desktop_notif)
        
        # Connect startup checkbox from Settings
        self.Settings.startup_checkbox.stateChanged.connect(
            lambda state: self.handle_startup_toggle(state)
        )
        # Update Windows startup registry based on persistent setting
        self.update_windows_startup()
        
        # Check immediately on startup if there is a weight input for this week
        self.check_weekly_weight_reminder()
        
        # Set up a timer to check every 2 hours throughout the day
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_weekly_weight_reminder)
        self.reminder_timer.start(2 * 60 * 60 * 1000)  # 2 hours in milliseconds

    def handle_startup_toggle(self, state):
        """Handle startup checkbox state change"""
        # Update Windows startup registry based on checkbox state
        self.Settings.toggle_startup(state, self.startup_settings)
        # Save the startup setting to persistent storage
        self.Settings.save_startup_setting()
    
    def update_windows_startup(self):
        """Update Windows startup registry based on persistent setting"""
        startup_enabled = self.Settings.startup_checkbox.isChecked()
        if startup_enabled:
            app_path = self.Settings.get_app_path()
            self.startup_settings.setValue("MindfulMauschen", app_path)
        else:
            self.startup_settings.remove("MindfulMauschen")
        self.startup_settings.sync()

    def check_weekly_weight_reminder(self):
        """Check if a weight has already been entered for this week"""
        now = datetime.now()
        # Calculate the start of the current week (Monday)
        days_since_monday = now.weekday()  # Monday is 0, Sunday is 6
        week_start = now - timedelta(days=days_since_monday)
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        # Calculate the end of the current week (Sunday)
        week_end = week_start + timedelta(days=6)
        week_end_str = week_end.strftime("%Y-%m-%d")
        
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        
        # Check if a current_weight entry exists for this week (Monday to Sunday)
        c.execute("""
            SELECT * FROM goals 
            WHERE updated_date BETWEEN ? AND ?
            AND current_weight IS NOT NULL
        """, (week_start_str, week_end_str))
        
        result = c.fetchone()
        conn.close()
        
        # If no weight entry exists for this week, send notification
        if not result:
            self.send_desktop_notif()

    def send_desktop_notif(self):
        """Send a native Windows desktop notification"""    
            # Create native Windows toast notification
        toast = Notification(
            app_id="Mindful Mäuschen",
            title="Boop! 🐭",
            msg="Beep Boop!Don't forget to log your weight for this week!",
            icon=os.path.abspath("assets/legnedary_astrid_boop_upscale.png") if os.path.exists("assets/legnedary_astrid_boop_upscale.png") else "",
            duration="long"  # Can be "short" or "long"
        )

        # If the silent notifications are disabled, set the audio to the default beep
        if not self.Settings.silent_notif_checkbox.isChecked():
            toast.set_audio(audio.Default, loop=False)            
        toast.add_actions(label="Open App", launch="") 
        toast.add_actions(label="Dismiss", launch="")
        toast.show()




# --- Run App ---
if __name__ == "__main__":
    init_db()
    # Ensure proper taskbar icon on Windows by setting AppUserModelID before creating windows
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MindfulMauschen.HealthApp.1.0")
        except Exception:
            pass
    app = QApplication(sys.argv)
    icon_path_ico = os.path.join("assets", "legnedary_astrid_boop_upscale.ico")
    icon_path_png = os.path.join("assets", "legnedary_astrid_boop_upscale.png")
    app_icon = QIcon(icon_path_ico) if os.path.exists(icon_path_ico) else QIcon(icon_path_png)
    app.setWindowIcon(app_icon)
    window = HealthApp()
    window.show()
    sys.exit(app.exec())
