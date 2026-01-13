"""
Pantry widget for the Health App.
"""
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QDialogButtonBox, QFormLayout,
    QMessageBox, QSplitter
)
from database import add_pantry_item, add_shopping_list_item, get_pantry_items, get_shopping_list_items, clear_pantry, clear_shopping_list, delete_pantry_items, delete_shopping_list_items, get_meal_plan_for_day
from utils import run_ai_request, planner_options_dialog

class Pantry(QWidget):
    """
    This class creates the pantry page of the app.
    It contains a list of items in the pantry and a button to add a new item.
    The items are saved to the database when the user adds or removes them.
    """
    def __init__(self):
        """
        Initialize the Pantry widget.
        Sets up the pantry and shopping list sections with their respective
        buttons and list widgets. Installs event filters for keyboard handling
        and loads existing data from the database.
        """
        super().__init__()
        self.layout = QVBoxLayout()

        # Section for the pantry
        self.pantry_layout = QVBoxLayout()
        # Header for labels and buttons
        self.pantry_header_layout = QHBoxLayout()
        self.pantry_label = QLabel("Pantry")
        self.add_item_pantry_button = QPushButton("Add Item to Pantry")
        self.add_item_pantry_button.clicked.connect(self.add_entry_pantry)
        self.clear_pantry_button = QPushButton("Clear Pantry")
        self.clear_pantry_button.clicked.connect(self.clear_pantry)
        self.pantry_header_layout.addWidget(self.pantry_label)
        self.pantry_header_layout.addWidget(self.add_item_pantry_button)
        self.pantry_header_layout.addWidget(self.clear_pantry_button)
        # List of items in the pantry
        self.pantry_items = QListWidget()
        # Add the header and list to the pantry layout
        self.pantry_layout.addLayout(self.pantry_header_layout)
        self.pantry_layout.addWidget(self.pantry_items)

        # Section for the shopping list
        self.shopping_list_layout = QVBoxLayout()
        # Header for labels and buttons
        self.shopping_header_layout = QHBoxLayout()
        self.shopping_list_label = QLabel("Shopping List")
        self.add_item_shopping_button = QPushButton("Add Item to Shopping List")
        self.add_item_shopping_button.clicked.connect(self.add_entry_shopping)
        self.generate_shopping_list_button = QPushButton("Generate Shopping List")
        self.generate_shopping_list_button.clicked.connect(self.generate_shopping_list)
        self.clear_shopping_list_button = QPushButton("Clear Shopping List")
        self.clear_shopping_list_button.clicked.connect(self.clear_shopping_list)
        self.shopping_header_layout.addWidget(self.shopping_list_label)
        self.shopping_header_layout.addWidget(self.add_item_shopping_button)
        self.shopping_header_layout.addWidget(self.generate_shopping_list_button)
        self.shopping_header_layout.addWidget(self.clear_shopping_list_button)
        # List of items in the shopping list
        self.shopping_list_items = QListWidget()
        # Add the header and list to the shopping list layout
        self.shopping_list_layout.addLayout(self.shopping_header_layout)
        self.shopping_list_layout.addWidget(self.shopping_list_items)

        # Add the pantry and shopping list layouts to the main layout. They need to be in separate containers to be able to split them vertically with the splitter.
        pantry_container = QWidget()
        pantry_container.setLayout(self.pantry_layout)
        shopping_container = QWidget()
        shopping_container.setLayout(self.shopping_list_layout)

        # Install event filters so DEL works when focus is on either list widget
        self.pantry_items.installEventFilter(self)
        self.shopping_list_items.installEventFilter(self)

        # Add the pantry and shopping list containers to the splitter and add the splitter to the main layout
        self.pantry_splitter = QSplitter(Qt.Orientation.Vertical)
        self.pantry_splitter.addWidget(pantry_container)
        self.pantry_splitter.addWidget(shopping_container)
        self.layout.addWidget(self.pantry_splitter)
        self.setLayout(self.layout)

        # Load the pantry and shopping list to ensure up to date
        self.load_pantry()
        self.load_shopping_list()

    def add_entry_pantry(self):
        """
        Show dialog to create a new pantry item entry.
        Allows the user to enter an item name and weight in grams,
        then saves it to the database and refreshes the pantry list.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Add item to pantry")
        dialog.setModal(True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)

        message_label = QLabel("What item would you like to add to your pantry?")
        message_label.setWordWrap(True)
        self.layout.addWidget(message_label)

        input_layout = QFormLayout()
        item_input = QLineEdit(dialog)
        item_input.setPlaceholderText("Enter item name")
        weight_input = QLineEdit(dialog)
        weight_input.setPlaceholderText("Enter weight in grams")
        input_layout.addRow("Item:", item_input)
        input_layout.addRow("Weight:", weight_input)
        self.layout.addLayout(input_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        add_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        add_button.setText("Add")
        cancel_button.setText("Cancel")
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        self.layout.addWidget(button_box)
        dialog.setLayout(self.layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        item = item_input.text().strip()
        if not item:
            return

        try:
            weight = int(weight_input.text())
        except ValueError:
            QMessageBox.warning(self, "Add Entry", "Weight must be a whole number.")
            return

        add_pantry_item(item, weight)
        self.load_pantry()

    def add_entry_shopping(self):
        """
        Show dialog to create a new shopping list item entry.
        Allows the user to enter an item name, then saves it to the database
        and refreshes the shopping list.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Add item to shopping list")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        message_label = QLabel("What item would you like to add to your shopping list?")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        input_layout = QFormLayout()
        item_input = QLineEdit(dialog)
        item_input.setPlaceholderText("Enter item name")
        input_layout.addRow("Item:", item_input)
        layout.addLayout(input_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        add_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        add_button.setText("Add")
        cancel_button.setText("Cancel")
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        item = item_input.text().strip()
        if not item:
            return
        add_shopping_list_item(item)
        self.load_shopping_list()

    def load_pantry(self):
        """
        Load the pantry items from the database.
        Fetches all pantry items with their IDs and weights, and displays
        them in the pantry list widget in the format "item_name (weight g)".
        """
        pantry_items = get_pantry_items()
        self.pantry_items.clear()
        for item_id, item_name, weight in pantry_items:
            list_item = QListWidgetItem(f"{item_name} ({weight} g)")
            list_item.setData(Qt.ItemDataRole.UserRole, item_id)  # Store ID for deletion
            self.pantry_items.addItem(list_item)

    def load_shopping_list(self):
        """
        Load the shopping list from the database.
        Fetches all shopping list items with their IDs and displays
        them in the shopping list widget.
        """
        shopping_list_items = get_shopping_list_items()
        self.shopping_list_items.clear()
        for item_id, item_name in shopping_list_items:
            list_item = QListWidgetItem(item_name)
            list_item.setData(Qt.ItemDataRole.UserRole, item_id)  # Store ID for deletion
            self.shopping_list_items.addItem(list_item)

    def clear_pantry(self):
        """
        Clear all items from the pantry in the database.
        Deletes all rows from the pantry table and refreshes the display.
        """
        clear_pantry()
        self.load_pantry()

    def clear_shopping_list(self):
        """
        Clear all items from the shopping list in the database.
        Deletes all rows from the shopping_list table and refreshes the display.
        """
        clear_shopping_list()
        self.load_shopping_list()

    def keyPressEvent(self, event):
        """
        Handle keyboard press events.
        This is a fallback handler; Delete key presses are handled by eventFilter.
        Other key events are passed to the parent class.
        """
        super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        """
        Catch DEL key presses when focus is on one of the list widgets and
        route them to the appropriate delete handler.
        
        Args:
            obj: The object that received the event.
            event: The event that occurred.
        
        Returns:
            bool: True if the event was handled, False otherwise.
        """
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Delete:
            if obj is self.pantry_items:
                self.delete_selected_item_pantry()
                return True
            if obj is self.shopping_list_items:
                self.delete_selected_item_shopping()
                return True
        return super().eventFilter(obj, event)

    def delete_selected_item_pantry(self):
        """
        Delete the selected pantry items from the database.
        Shows a confirmation dialog before deleting. Deletes all selected items
        and refreshes the pantry list.
        """
        selected_items = self.pantry_items.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(
            self,
            "Delete Confirmation",
            f"Delete {len(selected_items)} item(s) from pantry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Delete the selected items from database and reload the pantry
        delete_pantry_items(selected_items)
        self.load_pantry()

    def delete_selected_item_shopping(self):
        """
        Delete the selected shopping list items from the database.
        Shows a confirmation dialog before deleting. Deletes all selected items
        and refreshes the shopping list.
        """
        selected_items = self.shopping_list_items.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(
            self,
            "Delete Confirmation",
            f"Delete {len(selected_items)} item(s) from shopping list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        delete_shopping_list_items(selected_items)
        self.load_shopping_list()

    @planner_options_dialog(
        title="Shopping List Options",
        label_text="For which days of the meal plan do you want to generate a shopping list for and do you want to ignore items you already have in your pantry? If ignored items will be added to the list regardless of if you already have them.",
        chips=[
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
            ("ignore_pantry", "Ignore items already in pantry"),
        ],
    )
    @run_ai_request(
        success_handler="shopping_list_on_ai_response",
        error_handler="shopping_list_on_ai_error"
    )
    def generate_shopping_list(self, options: dict, *_, **__):
        """
        Generate a shopping list based on the meal plan page using AI.
        Reads meal plans for the selected days, builds an AI prompt, and
        sends it to the AI service. The response is handled by shopping_list_on_ai_response.

        Args:
            options (dict): Dictionary of selected options from PlannerOptionsDialog.
                Keys include day names (monday, tuesday, etc.) and "ignore_pantry".
                Values are booleans indicating if the option is selected.
        
        Returns:
            str: The AI prompt string for generating the shopping list.
        """
        # get the meal plan from the meal plan page for the selected days to use for the shopping list  
        meal_plans = ""
        day_key_to_column = {
            "monday": "Monday",
            "tuesday": "Tuesday",
            "wednesday": "Wednesday",
            "thursday": "Thursday",
            "friday": "Friday",
            "saturday": "Saturday",
            "sunday": "Sunday",
        }

        for key, selected in options.items():
            if not selected or key == "ignore_pantry":
                continue
            column = day_key_to_column.get(key)
            if not column:
                continue
            meal_plan_for_day = get_meal_plan_for_day(column)
            if meal_plan_for_day:
                meal_plans += meal_plan_for_day + "\n"
        
        ai_prompt = "Generate a shopping list of ingridients based on these meal plans: " + meal_plans + "For your response please only provide an itemised list of ingridients and nothing else as this will be parsed into a list and added to the shopping list."
        
        return ai_prompt

    def shopping_list_on_ai_response(self, response):
        """
        Handle successful AI response for shopping list generation.
        Parses the response into individual items, adds them to the shopping list
        widget, and saves them to the database (skipping empty lines, headers, and formatting).
        
        Args:
            response (str): The AI-generated shopping list text.
        """        

        def is_valid_shopping_item(item: str) -> bool: 
            """AI written funtion that check if an item is a valid shopping list item (not formatting/header)."""
            item = item.strip()
            # Skip empty lines
            if not item:
                return False
            # Skip markdown headers (lines starting with #)
            if item.startswith("#"):
                return False
            # Skip common formatting patterns
            if item in ["**Shopping List:**", "### Shopping List", "Shopping List"]:
                return False
            # Skip lines that are just separators or formatting
            if item.startswith("---") or item.startswith("==="):
                return False
            # Skip lines that are just markdown list markers without content
            if item in ["-", "*", "•"]:
                return False
            # Skip lines that are just instructions or notes
            if item.lower().startswith("feel free") or item.lower().startswith("note:"):
                return False
            # Skip lines that are section headers (all caps or title case with no actual item)
            if len(item) < 3:  # Too short to be a real item
                return False
            return True
        
        for item in response.split("\n"):
            item_cleaned = item.strip()
            # Remove markdown list markers (-, *, •) and bullet points from the start
            if item_cleaned.startswith("- "):
                item_cleaned = item_cleaned[2:].strip()
            elif item_cleaned.startswith("* "):
                item_cleaned = item_cleaned[2:].strip()
            elif item_cleaned.startswith("• "):
                item_cleaned = item_cleaned[2:].strip()
            
            # Only add valid items
            if is_valid_shopping_item(item_cleaned):
                self.shopping_list_items.addItem(item_cleaned)
                add_shopping_list_item(item_cleaned)

        self.load_shopping_list()

    def shopping_list_on_ai_error(self, error_message):
        """
        Handle AI request error for shopping list generation.
        
        Args:
            error_message (str): The error message from the AI request.
        """


