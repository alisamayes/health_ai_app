"""
FoodTracker widget for the Health App.
"""
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QInputDialog, QMessageBox, QDateEdit,
    QDialog, QDialogButtonBox, QFormLayout, QAbstractItemView
)
import os
import requests
from difflib import get_close_matches
from database import use_db, add_food, get_food_entries, update_food_entry, delete_food_entry, get_daily_calorie_goal, get_all_distinct_foods, get_most_common_foods
from config import calories_burned_red, hover_light_green

class FoodTracker(QWidget):
    """
    This is the food tracker page of the app. It is used to track the calories of the food that the user eats.
    It contains a date selector, a table to show the entries for a given date, and a form to add and remove entries.
    """
    def __init__(self):
        """
        Initialize the FoodTracker widget.
        Sets up the date selector, input buttons, table for displaying entries,
        and calorie labels. Loads existing entries for the current date.
        """
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


        # Input buttons for adding and removing food and calorie entries
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
        self.table.setHorizontalHeaderLabels(["Food", "Calories"])
        # Disable editing cells by double-clicking as found a user could edit the info locally. While it isnt saved to database its undesirable behaviour.
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
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
        calorie_layout = QHBoxLayout()
        self.calorie_label = QLabel("Daily Calories Intake:")
        self.daily_calorie_goal_label = QLabel("Daily Calorie Goal:")
        self.calorie_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        self.daily_calorie_goal_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        calorie_layout.addWidget(self.calorie_label)
        calorie_layout.addWidget(self.daily_calorie_goal_label)

        # Add to layout
        self.layout.addLayout(date_layout)
        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.table)
        self.layout.addLayout(calorie_layout)
        self.setLayout(self.layout)

        # Load existing data
        self.load_entries()

    def add_entry(self):
        """
        Show dialog to create a new food entry.
        Allows the user to enter a food name and calories, with options to
        suggest calories from local database or quick-add from common foods.
        Saves the entry to the database for the currently selected date.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Food Entry")
        dialog.setModal(True)

        def handle_suggest(food_input, calorie_input):
            """Handle suggest button click by looking up calories for the food."""
            food_text = food_input.text().strip()
            if not food_text:
                QMessageBox.warning(dialog, "Suggest Calories", "Enter a food name to get a suggestion.")
                return

            calories = self.suggest_calories_locally(food_text)
            if calories is None:
                QMessageBox.warning(dialog, "Suggest Calories", "No calories found for the food.")
            else:
                calorie_input.setText(str(calories))

        def handle_quickadd(food_name, food_calories):
            """Handle quick-add button click by filling in the food and calorie inputs."""
            food_input.setText(food_name)
            calorie_input.setText(str(int(round(food_calories))))

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        message_label = QLabel("What food would you like to track and how many calories does it contain?")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        input_layout = QFormLayout()
        food_input = QLineEdit(dialog)
        food_input.setPlaceholderText("Enter food name")
        input_layout.addRow("Food:", food_input)
        calorie_input = QLineEdit(dialog)
        calorie_input.setPlaceholderText("Enter calories")
        input_layout.addRow("Calories:", calorie_input)
        layout.addLayout(input_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        add_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        add_button.setText("Add")
        cancel_button.setText("Cancel")
        suggest_button = button_box.addButton("Suggest", QDialogButtonBox.ButtonRole.ActionRole)
        suggest_button.clicked.connect(lambda: handle_suggest(food_input, calorie_input))
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        # A selection of 5 buttons with the most common foods and their calories.
        # TODO: See if can impliment some sort of NN model to suggest the most common foods and their calories.
        quickadd_layout = QHBoxLayout()
        most_common_foods = get_most_common_foods()
        for food in most_common_foods:
            text = f"{food[0]} | {int(round(food[1]))}"
            quickadd_button = QPushButton(text)
            # Connect the button click to the handler with the specific food data
            quickadd_button.clicked.connect(lambda checked, food=food: handle_quickadd(food[0], food[1]))
            quickadd_layout.addWidget(quickadd_button)
        layout.addLayout(quickadd_layout)

        dialog.setLayout(layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        food = food_input.text().strip()
        if not food:
            return

        try:
            calories = int(calorie_input.text())
        except ValueError:
            QMessageBox.warning(self, "Add Entry", "Calories must be a whole number.")
            return

        date_str = self.date_selector.date().toString("yyyy-MM-dd")

        add_food(food, calories, date_str)
        self.load_entries()

    def edit_entry(self):
        """
        Show dialog to edit an existing food entry.
        Prompts the user to select a row number, then shows a dialog with the
        current food name and calories pre-filled. Updates the entry in the database.
        """
        row_count = self.table.rowCount()
        if row_count == 0:
            QMessageBox.information(self, "Edit Entry", "There are no entries to edit.")
            return

        row_number, ok = QInputDialog.getInt(
            self,
            "Edit Entry",
            f"Enter row number to edit (1 - {row_count}):",
            1, 1, row_count, 1
        )
        if not ok:
            return

        # Get IDs for this date only
        date_str = self.date_selector.date().toString("yyyy-MM-dd")
        entries = get_food_entries(date_str)

        index = row_number - 1
        if index < 0 or index >= len(entries):
            QMessageBox.warning(self, "Edit Entry", "Invalid row number.")
            return

        current_food = entries[index][1]
        current_calories = entries[index][2]

        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Food Entry")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        message_label = QLabel("Edit the food name and calories:")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        input_layout = QFormLayout()

        food_input = QLineEdit(dialog)
        food_input.setPlaceholderText("Enter food name")
        food_input.setText(current_food)
        input_layout.addRow("Food:", food_input)

        calorie_input = QLineEdit(dialog)
        calorie_input.setPlaceholderText("Enter calories")
        calorie_input.setText(str(current_calories))
        input_layout.addRow("Calories:", calorie_input)

        layout.addLayout(input_layout)

        def handle_suggest():
            """Handle the suggest button click by looking up calories for the food."""
            food_text = food_input.text().strip()
            if not food_text:
                QMessageBox.warning(dialog, "Suggest Calories", "Enter a food name to get a suggestion.")
                return

            calories = self.suggest_calories_locally(food_text)
            if calories is None:
                QMessageBox.warning(dialog, "Suggest Calories", "No calories found for the food.")
            else:
                calorie_input.setText(str(calories))

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        ok_button.setText("Save")
        cancel_button.setText("Cancel")

        suggest_button = button_box.addButton("Suggest", QDialogButtonBox.ButtonRole.ActionRole)

        suggest_button.clicked.connect(handle_suggest)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        food = food_input.text().strip()
        if not food:
            return

        try:
            calories = int(calorie_input.text())
        except ValueError:
            QMessageBox.warning(self, "Edit Entry", "Calories must be a whole number.")
            return

        # Update the database entry
        update_food_entry(entries[index][0], food, calories)
        self.load_entries()

    def remove_entry(self):
        """
        Remove an entry from the database.
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
        ids = [row[0] for row in get_food_entries(date_str)]

        index = row_number - 1
        if index < 0 or index >= len(ids):
            QMessageBox.warning(self, "Remove Entry", "Invalid row number.")
            return

        delete_food_entry(ids[index])

        self.load_entries()

    def back_day(self):
        """Go back to the previous day on the date selector."""
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.load_entries()
    
    def next_day(self):
        """Go to the next day on the date selector."""
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.load_entries()

    def load_entries(self):
        """
        Load the food entries for the currently selected date.
        Populates the table with food names and calories, updates the total
        daily calorie intake label, and displays the daily calorie goal.
        Also updates label colors based on whether intake exceeds the goal.
        """
        date_str = self.date_selector.date().toString("yyyy-MM-dd")

        rows = get_food_entries(date_str)

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(row[1]))
            self.table.setItem(i, 1, QTableWidgetItem(str(row[2])))

        # Resize columns to fit content after loading data
        self.table.resizeColumnsToContents()

        # Update total calories label
        total_calories = sum(row[2] for row in rows) if rows else 0
        self.calorie_label.setText(f"Daily Calorie Intake: {total_calories}")

        daily_calorie_goal = get_daily_calorie_goal()
        if daily_calorie_goal is not None:
            self.daily_calorie_goal_label.setText(f"Daily Calorie Goal: {daily_calorie_goal}")
            # Only compare if goal is set
            if total_calories > daily_calorie_goal:
                self.calorie_label.setStyleSheet(f"color: {calories_burned_red};")
                self.daily_calorie_goal_label.setStyleSheet(f"color: {calories_burned_red};")
            else:
                self.calorie_label.setStyleSheet(f"color: {hover_light_green};")
                self.daily_calorie_goal_label.setStyleSheet(f"color: {hover_light_green};")
        else:
            self.daily_calorie_goal_label.setText("Daily Calorie Goal: --")
            # Reset to default color when no goal is set
            self.calorie_label.setStyleSheet("")
            self.daily_calorie_goal_label.setStyleSheet("")     

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
        all_entries = get_food_entries(date_str)
        
        # Delete only the selected records by mapping row indices to IDs
        for row_index in selected_rows:
            if row_index < len(all_entries):
                entry_id = all_entries[row_index][0]  # Get ID from the entry
                delete_food_entry(entry_id)
        
        self.load_entries()

    def suggest_calories(self):
        """
        Suggest calories for the food input.
        First tries the local database, then falls back to the USDA FoodData Central API.
        Updates the calorie input field with the suggested value.
        """
        calories = self.suggest_calories_locally()
        if calories:
            self.calorie_input.setText(str(calories))
        else:
            QMessageBox.warning(self, "Suggest Calories", "No calories found for the food.")
            return None

    def suggest_calories_locally(self, user_input=None):
        """
        Suggest calories based on the food input using fuzzy match (>= 0.75) from the localdatabase.
        Returns an int average calories for the closest food, or None if no match.
        """
        if user_input is None:
            user_input = self.food_input.text()

        user_input = (user_input or "").strip()
        if not user_input:
            return None

        foods = get_all_distinct_foods()
        matches = get_close_matches(user_input, [food[0] for food in foods], n=1, cutoff=0.75)
        if not matches:
            return self.suggest_calories_from_usda(user_input)

        # get_closest_matches returns a list of the names only so we need to get the calories back to get the average
        # TODO: Is this a good way? Mean of similar foods sounds reasonable but would something like Chickhen Sandwhich and Chicken Salad both get caught by the fuzzy match? They have different calorie values.
        calories = [food[1] for food in foods if food[0] == matches[0]]
        average_calories = sum(calories) / len(calories)
        return int(round(average_calories))

    def suggest_calories_from_usda(self, user_input):
        """
        Suggest calories based on the food input using the USDA FoodData Central API.
        Searches for the food, retrieves nutrient data, and extracts the calorie value.
        
        Args:
            user_input (str): The food name to search for.
        
        Returns:
            int or None: The calorie value per serving, or None if not found.
        """
        print("Now trying to suggest calories from USDA for food: ", user_input)
        if not user_input:
            return None
        
        # Step 1: Search for the food
        search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={os.getenv("USDA_API_KEY")}"
        search_payload = {"query": user_input, "pageSize": 1}
        search_response = requests.post(search_url, json=search_payload)

        if search_response.status_code != 200:
            print("Error point 1: ", search_response.status_code)
            return None

        results = search_response.json().get("foods", [])
        if not results:
            print("No results found from USDA")
            return None

        fdc_id = results[0]["fdcId"]

        # Step 2: Get the nutrient details
        food_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}?api_key={os.getenv("USDA_API_KEY")}"
        food_response = requests.get(food_url)

        if food_response.status_code != 200:
            print("No food data found from USDA")
            print("Error point 2: ", food_response.status_code)
            return None

        food_data = food_response.json()
        #print(f"Food data: {food_data}")

        # Find the calorie value
        for nutrient in food_data.get("foodNutrients", []):
            nutrient_name = nutrient.get("nutrientName")
            if not nutrient_name and isinstance(nutrient.get("nutrient"), dict):
                nutrient_name = nutrient["nutrient"].get("name")

            unit_name = nutrient.get("unitName")
            if not unit_name and isinstance(nutrient.get("nutrient"), dict):
                unit_name = nutrient["nutrient"].get("unitName")

            value = nutrient.get("value")
            if value is None:
                value = nutrient.get("amount")

            if nutrient_name and nutrient_name.lower() == "energy" and unit_name and unit_name.upper() == "KCAL":
                print (nutrient)
                print(f"Nutrient name: {nutrient_name}")
                print(f"Unit name: {unit_name}")
                print(f"Calories: {value}")
                return int(value)

        #print("No calories found for the matched food")
        return None

