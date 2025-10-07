from cProfile import label
import sys
import os
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QInputDialog, QMessageBox, QDateEdit, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

"""
This is the starter file for an AI-driven self health and tracking app I am working on, using Python for the main part, PyQt for the GUI and SQLite for the database
Plan
Tab 1: Home page → App name, navigation
Tab 2: Calorie Tracker → form to enter meals, calories, macros
Tab 3: Exercise Tracker → log workouts, sets/reps, time
Tab 4: Graphs/Progress → matplotlib charts inside PyQt
Tab 5: Meal Plan & Ideas → static list first, then AI alternative suggestions
Tab 6: Shopping List → add/remove grocery items

core_todo_list = ["exercise tracker", "graphs of both over time period", "weight goal", "meal plan/ ideas", "AI suggested meal substitues", "desktop promts/ reminders"]
extra_todo_list = ["exercise calorie calculator based on input factors", "goal advice", "sleep diary", "AI chat bot for health advice", "health by day trends", "AI driven improvements", "mobile support", "weekly weigh in reminders"]
completed_todo_list = ["Calorie tracker", "app styling"]
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

class Graphs(QWidget):
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
        dark_bg = "#2b2b2b"
        light_fg = "#ffffff"
        grid_color = "#5a5a5a"
        try:
            self.canvas.setStyleSheet(f"background-color: {dark_bg};")
            self.canvas.figure.set_facecolor(dark_bg)
            self.graph.set_facecolor(dark_bg)
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
        rows = c.fetchall()
        conn.close()

        # Build a continuous date range and fill missing days with zero
        date_to_total = {r[0]: r[1] for r in rows}
        if start_str is None:
            if rows:
                start_date = datetime.strptime(rows[0][0], "%Y-%m-%d").date()
                end_date = datetime.strptime(rows[-1][0], "%Y-%m-%d").date()
            else:
                start_date = datetime.today().date()
                end_date = start_date
        else:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

        dates = []
        totals = []
        current = start_date
        while current <= end_date:
            key = current.strftime("%Y-%m-%d")
            dates.append(key)
            totals.append(date_to_total.get(key, 0))
            current += timedelta(days=1)

        # Prepare display labels in dd-MM-yyyy
        display_dates = [datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") for d in dates]

        self.graph.clear()
        if dates:
            self.graph.plot(dates, totals, marker='o', color='#009423', linewidth=2)
            self.graph.fill_between(range(len(totals)), totals, color='#009423', alpha=0.15)
            self.graph.set_title("Daily Calories", color="#ffffff")
            self.graph.set_xlabel("Date", color="#ffffff")
            self.graph.set_ylabel("Calories", color="#ffffff")
            self.graph.grid(True, linestyle='--', alpha=0.3)
            # Label x-axis only when number of points is manageable
            if len(dates) <= 20:
                self.graph.set_xticks(range(len(dates)))
                self.graph.set_xticklabels(display_dates, rotation=45, ha='right')
            else:
                self.graph.set_xticks([])
            self.canvas.figure.tight_layout()
        else:
            self.graph.text(0.5, 0.5, "No data for selected range", ha='center', va='center', color='#cccccc', transform=self.graph.transAxes)
            self.graph.set_xticks([])
            self.graph.set_yticks([])
        self.canvas.draw()

class Goals(QWidget):
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
        dark_bg = "#2b2b2b"
        light_fg = "#ffffff"
        grid_color = "#5a5a5a"
        try:
            self.canvas.setStyleSheet(f"background-color: {dark_bg};")
            self.canvas.figure.set_facecolor(dark_bg)
            self.graph.set_facecolor(dark_bg)
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
            c.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    current_weight REAL,
                    target_weight REAL,
                    updated_date TEXT NOT NULL
                )
            """)
            c.execute("INSERT INTO goals (current_weight, updated_date) VALUES (?, ?)",
                     (weight, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
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
            c.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    current_weight REAL,
                    target_weight REAL,
                    updated_date TEXT NOT NULL
                )
            """)
            c.execute("INSERT INTO goals (target_weight, updated_date) VALUES (?, ?)",
                     (weight, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            
            # Update button text
            self.target_weight.setText(f"Target Weight: {weight} kg")
            # Reload to update weight loss calculation and graph
            self.load_info()
            # Refresh graph with new target weight as y-axis limit
            self.load_graphs(weight)

    def load_info(self):
        """Reload the page so the current and target weight buttons reflect the respective 
        values in the database and the loss value label shows the difference."""
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_weight REAL,
                target_weight REAL,
                updated_date TEXT NOT NULL
            )
        """)
        
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
        
        # Query for current weight entries with dates
        c.execute("""
            SELECT current_weight, updated_date 
            FROM goals 
            WHERE current_weight IS NOT NULL 
            ORDER BY updated_date ASC
        """)
        rows = c.fetchall()
        conn.close()

        dates = []
        weights = []

        # Extract dates and weights from database results
        for row in rows:
            weight = row[0]  # current_weight
            date_str = row[1]  # updated_date
            
            # Convert date string to datetime for proper sorting and display
            try:
                # Parse the datetime string (format: "YYYY-MM-DD HH:MM:SS")
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                dates.append(date_obj.strftime("%d-%m-%Y"))  # Format for display
                weights.append(weight)
            except ValueError:
                # Handle different date formats if needed
                continue
        
        # Store data for click events
        self.dates_copy = dates.copy()
        self.weights_copy = weights.copy()

        self.graph.clear()
        
        if dates and weights:
            # Plot the weight data
            self.graph.plot(dates, weights, marker='o', color='#009423', linewidth=2)
            self.graph.fill_between(range(len(weights)), weights, color='#009423', alpha=0.15)
            self.graph.set_title("Weight Progress", color="#ffffff")
            self.graph.set_xlabel("Date", color="#ffffff")
            self.graph.set_ylabel("Weight (kg)", color="#ffffff")
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
                          ha='center', va='center', color='#cccccc', 
                          transform=self.graph.transAxes)
            self.graph.set_xticks([])
            self.graph.set_yticks([])
            self.graph.set_title("Weight Progress", color="#ffffff")
            self.graph.set_xlabel("Date", color="#ffffff")
            self.graph.set_ylabel("Weight (kg)", color="#ffffff")
        
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
            print("OK pressed")
            return
        elif clicked_button == edit_button:
            print("Edit pressed")
            return
        elif clicked_button == delete_button:
            print("Delete pressed")
            return

    def get_target_weight(self):
        """Get the current target weight from database"""
        conn = sqlite3.connect("health_app.db")
        c = conn.cursor()
        c.execute("SELECT target_weight FROM goals WHERE target_weight IS NOT NULL ORDER BY updated_date DESC LIMIT 1")
        target_row = c.fetchone()
        conn.close()
        return target_row[0] if target_row else None



# --- Main Window with Tabs ---
class HealthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Health Tracker App")
        self.setGeometry(300, 300, 800, 400)
        # Prefer an .ico for Windows taskbar; fallback to PNG if .ico not present
        icon_path_ico = os.path.join("assets", "legendary_boop.ico")
        icon_path_png = os.path.join("assets", "legendary_boop.png")
        window_icon = QIcon(icon_path_ico) if os.path.exists(icon_path_ico) else QIcon(icon_path_png)
        self.setWindowIcon(window_icon)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
                border-radius: 8px;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 6px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #5a5a5a;
            }
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton#navigationBtn {
                padding: 2px 6px;
                min-width: 0px; /* smaller padding for  the < and > buttons which were getting cut off due to not enough space */
            }
            QPushButton:hover {
                background-color: #00a527;
            }
            QPushButton:pressed {
                background-color: #007a1c;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 2px solid #404040;
                padding: 8px;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #009423;
            }
            QDateEdit {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 2px solid #404040;
                padding: 8px;
                border-radius: 6px;
            }
            QDateEdit:focus {
                border-color: #009423;
            }
            QTableWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #404040;
                border-radius: 8px;
                gridline-color: #404040;
                selection-background-color: #009423;
                alternate-background-color: #3a3a3a;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTableWidget::item:selected {
                background-color: #009423;
                color: #ffffff;
            }
            QTableWidget::item:alternate {
                background-color: #3a3a3a;
            }
            QHeaderView {
                background-color: #404040;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #404040 !important;
                color: #ffffff !important;
                padding: 8px;
                border: none;
                font-weight: bold;
                border-radius: 0px;
            }
            QHeaderView::section:horizontal {
                border-right: 1px solid #5a5a5a;
                background-color: #404040 !important;
                color: #ffffff !important;
            }
            QHeaderView::section:vertical {
                border-bottom: 1px solid #5a5a5a;
                background-color: #404040 !important;
                color: #ffffff !important;
            }
            QTableCornerButton::section {
                background-color: #404040 !important;
                border: none;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background-color: #404040;
                color: #ffffff;
                border: 2px solid transparent;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QComboBox:hover { 
                background-color: #404040;
                border-color: #00a527;
            }
            Figure {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QInputDialog {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QMessageBox {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(HomePage(), "Home")
        self.tabs.addTab(CalorieTracker(), "Calorie Tracker")
        self.tabs.addTab(QWidget(), "Exercise Tracker (todo)")
        self.tabs.addTab(Graphs(), "Graphs")
        self.tabs.addTab(Goals(), "Goals")
        self.tabs.addTab(QWidget(), "Meal Plans (todo)")
        self.tabs.addTab(QWidget(), "Chat Bot (todo)")


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
    icon_path_ico = os.path.join("assets", "legendary_boop.ico")
    icon_path_png = os.path.join("assets", "legendary_boop.png")
    app_icon = QIcon(icon_path_ico) if os.path.exists(icon_path_ico) else QIcon(icon_path_png)
    app.setWindowIcon(app_icon)
    window = HealthApp()
    window.show()
    sys.exit(app.exec())
