"""
ExerciseTracker widget for the Health App.
"""
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QInputDialog,
    QMessageBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QAbstractItemView,
    QLineEdit,
)
from database import add_exercise, delete_exercise_entry, get_exercise_entries, update_exercise_entry

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
        self.date_label = QLabel("Select Date:")
        self.date_label.setFixedSize(75, 25) # Set the size policy to fixed so the label doesnt stretch the layout.
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
        date_layout.addWidget(self.date_label)
        date_layout.addWidget(self.back_day_button)
        date_layout.addWidget(self.date_selector)
        date_layout.addWidget(self.next_day_button)


        # Input buttons for adding, editing and removing exercise entries
        self.add_button = QPushButton("Add Entry")
        self.add_button.clicked.connect(self.add_entry)

        self.edit_button = QPushButton("Edit Entry")
        self.edit_button.clicked.connect(self.edit_entry)

        self.remove_button = QPushButton("Remove Entry")
        self.remove_button.clicked.connect(self.remove_entry)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.edit_button)
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
        Show a dialog to create a new exercise entry.
        Allows the user to enter an activity name and calories burned,
        then saves the entry to the database for the currently selected date.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Exercise Entry")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        message_label = QLabel("What exercise would you like to track and how many calories did it burn?")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        input_layout = QFormLayout()
        activity_input = QLineEdit(dialog)
        activity_input.setPlaceholderText("Enter activity name")
        input_layout.addRow("Activity:", activity_input)

        calorie_input = QLineEdit(dialog)
        calorie_input.setPlaceholderText("Enter calories burned")
        input_layout.addRow("Calories:", calorie_input)
        layout.addLayout(input_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        ok_button.setText("Add")
        cancel_button.setText("Cancel")
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        activity = activity_input.text().strip()
        if not activity:
            return

        try:
            calories = int(calorie_input.text())
        except ValueError:
            QMessageBox.warning(self, "Add Entry", "Calories must be a whole number.")
            return

        date_str = self.date_selector.date().toString("yyyy-MM-dd")
        add_exercise(activity, calories, date_str)
        self.load_entries()

    def edit_entry(self):
        """
        Show a dialog to edit an existing exercise entry.
        Prompts the user to select a row (via selection or row number),
        then shows a dialog with the current activity and calories pre-filled.
        Updates the entry in the database.
        """
        index = -1
        selected_rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)

        # If no rows or more than one row selected, prompt user to select a row to edit.
        if len(selected_rows) != 1:
            row_count = self.table.rowCount()
            if row_count == 0:
                QMessageBox.information(self, "Edit Entry", "There are no entries to edit.")
                return

            row_number, ok = QInputDialog.getInt(
                self,
                "Edit Entry",
                f"Enter row number to edit (1 - {row_count}):",
                1,
                1,
                row_count,
                1,
            )
            if not ok:
                return
            index = row_number - 1
        else:
            index = selected_rows[0]

        # Fetch the row to edit from the database for the current date
        date_str = self.date_selector.date().toString("yyyy-MM-dd")
        entries = get_exercise_entries(date_str)
        if index < 0 or index >= len(entries):
            QMessageBox.warning(self, "Edit Entry", "Invalid row selected.")
            return

        row_to_edit = entries[index]

        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Exercise Entry")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        message_label = QLabel("Edit the activity name and calories burned:")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        input_layout = QFormLayout()

        activity_input = QLineEdit(dialog)
        activity_input.setPlaceholderText("Enter activity name")
        activity_input.setText(row_to_edit[1])
        input_layout.addRow("Activity:", activity_input)

        calorie_input = QLineEdit(dialog)
        calorie_input.setPlaceholderText("Enter calories burned")
        calorie_input.setText(str(row_to_edit[2]))
        input_layout.addRow("Calories:", calorie_input)

        layout.addLayout(input_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        ok_button.setText("Save")
        cancel_button.setText("Cancel")
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        activity = activity_input.text().strip()
        if not activity:
            return

        try:
            calories = int(calorie_input.text())
        except ValueError:
            QMessageBox.warning(self, "Edit Entry", "Calories must be a whole number.")
            return

        # Update the database entry
        update_exercise_entry(row_to_edit[0], activity, calories)
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

