import sys
import sqlite3
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QInputDialog, QMessageBox, QDateEdit
)

"""
This is the starter file for an AI-driven self health and tracking app I am working on, using Python for the main part, PyQt for the GUI and SQLite for the database
Plan
Tab 1: Home page → App name, navigation
Tab 2: Calorie Tracker → form to enter meals, calories, macros
Tab 3: Exercise Tracker → log workouts, sets/reps, time
Tab 4: Graphs/Progress → matplotlib charts inside PyQt
Tab 5: Meal Plan & Ideas → static list first, then AI alternative suggestions
Tab 6: Shopping List → add/remove grocery items

core_todo_list = ["Calorie tracker", "exercise tracker", "graphs of both over time period", "weight goal", "meal plan/ ideas", "AI suggested meal substitues", "desktop promts/ reminders"]
extra_todo_list = ["exercise calorie calculator based on input factors", "goal advice", "sleep diary", "AI chat bot for health advice", "health by day trends", "AI driven improvements", "mobile support"]
completed_todo_list = [""]
"""


# --- Database Setup ---
def init_db():
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
    conn.commit()
    conn.close()

# --- Home Page Widget ---
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo label, temp image till i come up with something better
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = QPixmap("assets/legendary_boop.png")
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

# --- Calorie Tracker Widget ---
class CalorieTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Date selector section for picking which date to show calorie and food entries for
        self.date_selector = QDateEdit(calendarPopup=True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.load_entries)
        self.back_day_button = QPushButton("<")
        self.back_day_button.setFixedSize(30, 25)
        self.back_day_button.clicked.connect(self.back_day)
        self.next_day_button = QPushButton(">")
        self.next_day_button.setFixedSize(30, 25)
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
        self.calorie_label.setText(f"Daily Calories: {total_calories}")


# --- Main Window with Tabs ---
class HealthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Health Tracker App")
        self.setGeometry(300, 300, 750, 400)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(HomePage(), "Home")
        self.tabs.addTab(CalorieTracker(), "Calorie Tracker")
        self.tabs.addTab(QWidget(), "Exercise Tracker (todo)")
        self.tabs.addTab(QWidget(), "Graphs (todo)")
        self.tabs.addTab(QWidget(), "Goal (todo)")
        self.tabs.addTab(QWidget(), "Meal Plans (todo)")
        self.tabs.addTab(QWidget(), "Chat Bot (todo)")


# --- Run App ---
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/legendary_boop.png"))
    window = HealthApp()
    window.show()
    sys.exit(app.exec())
