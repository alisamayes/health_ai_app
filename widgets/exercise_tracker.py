"""
ExerciseTracker widget for the Health App.
"""
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QInputDialog, QMessageBox, QDateEdit,
    QAbstractItemView
)
from database import use_db, add_exercise, delete_exercise_entry, get_exercise_entries

class ExerciseTracker(QWidget):
    """
    This is the exercise tracker page of the app. It is used to track the calories burned by the user through exercise.
    It contains a date selector, a table to show the entries for a given date, and a form to add and remove entries.
    """
    def __init__(self):
        """Initialize the ExerciseTracker widget with date selector, input fields, and table."""
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

        # Keyboard shortcuts for navigation: < and , for previous day, > and . for next day
        QShortcut(QKeySequence("Shift+,"), self).activated.connect(self.back_day)  # < key
        QShortcut(QKeySequence(","), self).activated.connect(self.back_day)
        QShortcut(QKeySequence("Shift+."), self).activated.connect(self.next_day)  # > key
        QShortcut(QKeySequence("."), self).activated.connect(self.next_day)

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
        # Disable editing cells by double-clicking as found a user could edit the info locally. While it isnt saved to database its undesirable behaviour.
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
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
        """
        Add a new exercise entry to the database.
        Reads activity name and calories from input fields, validates the calories,
        and saves the entry for the currently selected date.
        """
        activity = self.activity_input.text()
        try:
            calories = int(self.calorie_input.text())
        except ValueError:
            return  # Ignore if calories is not a number

        date_str = self.date_selector.date().toString("yyyy-MM-dd")

        add_exercise(activity, calories, date_str)

        self.activity_input.clear()
        self.calorie_input.clear()
        self.load_entries()

    def remove_entry(self):
        """
        Remove an exercise entry from the database.
        Prompts the user to enter a row number (1-indexed) and deletes
        the corresponding entry for the currently selected date.
        """
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
        ids = [row[0] for row in get_exercise_entries(date_str)]

        index = row_number - 1
        if index < 0 or index >= len(ids):
            QMessageBox.warning(self, "Remove Entry", "Invalid row number.")
            return
        delete_exercise_entry(ids[index])

        self.load_entries()

    def back_day(self):
        """
        Go back to the previous day on the date selector.
        """
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.load_entries()
    
    def next_day(self):
        """
        Go to the next day on the date selector.
        """
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.load_entries()

    def load_entries(self):
        """
        Load the exercise entries for the currently selected date.
        Populates the table with activity names and calories, and updates
        the total daily calories burned label.
        """
        date_str = self.date_selector.date().toString("yyyy-MM-dd")

        rows = get_exercise_entries(date_str)

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(row[1]))
            self.table.setItem(i, 1, QTableWidgetItem(str(row[2])))

        # Resize columns to fit content after loading data
        self.table.resizeColumnsToContents()

        # Update total calories label
        total_calories = sum(row[2] for row in rows) if rows else 0
        selected_date_display = self.date_selector.date().toString("dd-MM-yyyy")
        self.calorie_label.setText(f"Daily Calories ({selected_date_display}): {total_calories}")

    def keyPressEvent(self, event):
        """
        Handle keyboard press events.
        If the Delete key is pressed, deletes the selected rows from the table.
        Otherwise, passes the event to the parent class.
        """
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_rows()
        else:
            # Pass other key events to the parent class
            super().keyPressEvent(event)

    def delete_selected_rows(self):
        """
        Delete the selected rows from the database.
        Shows a confirmation dialog before deleting. Only deletes entries
        for the currently selected date.
        """
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

        date_str = self.date_selector.date().toString("yyyy-MM-dd")
        
        # Get all records for this date with their IDs
        rows = get_exercise_entries(date_str)

        # Delete the selected records
        for row_index in selected_rows:
            if row_index < len(rows):
                delete_exercise_entry(rows[row_index][0])

        self.load_entries()

