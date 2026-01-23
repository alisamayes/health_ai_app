"""
DayWidget widget for the Health App.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QMessageBox
from utils import run_ai_request, planner_options_dialog, DaysOfTheWeek
from database import get_pantry_items, get_meal_plan_for_day, update_meal_plan_for_day

class DayWidget(QWidget):
    """
    This class represents a single day widget in the meal plan page.
    It contains a header label(button) for the day name and a QTextEdit for the meal list.
    The meal list is automatically saved to the database when changed.
    """
    def __init__(self, day_name: DaysOfTheWeek):
        """
        Initialize the DayWidget with the day name and valid days.
        """
        super().__init__()
        self.day_name = day_name
        
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
        """
        Load the meal text for this day from the database.
        
        Returns:
            str or None: The meal plan text for this day, or None if not found.
        """
        return get_meal_plan_for_day(self.day_name)
    
    def on_text_changed(self):
        """
        Handle text changes in the meal list editor.
        Automatically saves the updated text to the database when the user edits it.
        """
        new_text = self.meal_list.toPlainText()
        update_meal_plan_for_day(self.day_name, new_text)
    

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


    @staticmethod
    def _build_meal_plan_prompt(current_text: str, options: dict) -> str:
        """
        Helper to build the AI prompt for the meal plan based on current text
        and the selected dialog options.
        """

        meal_types = ["breakfast", "lunch", "dinner"]
        meal_types_text = ", ".join(meal_types)
        # Base request
        AI_promt = (
            "Can you suggest a meal plan for the day by giving me suggestions on what to eat? "
            "The meal plan should include " + meal_types_text + ". "
            "Please just provide the meal plan and nothing else. "
        )

        

        # Collect additional criteria (e.g. healthy, cheap, etc.)
        additional_criteria = [key for key, value in options.items() if value]

        # Pantry handling is special – we both use it as a flag and also
        # the items are in items[1] of the pantry_items list.
        if options.get("use_pantry"):
            pantry_items = get_pantry_items()
            AI_promt += (
                "I have the following items in my pantry: "
                + ", ".join([item[1] for item in pantry_items])
                + ". "
            )
            # Remove from criteria list so it isn't also used as an adjective.
            additional_criteria = [c for c in additional_criteria if c != "use_pantry"]

        # Turn the remaining criteria into a human-readable phrase.
        if len(additional_criteria) == 1:
            AI_promt += f"I want the meal plan to be {additional_criteria[0]}. "
        elif len(additional_criteria) > 1:
            AI_promt += "I want the meal plan to be " + ", ".join(additional_criteria) + ". "

        # Include the current meal plan in the prompt if it exists
        if current_text:
            AI_promt += (
                "The current meal plan is: "
                + current_text
                + ". You can use this as a starting point, make changes to it or scrap it entirely if it doesnt fit the criteria."
            )

        return AI_promt

    @planner_options_dialog(
        title="AI Meal Planner Options",
        label_text="Choose any options you want to include:",
        chips=[
            ("healthy", "Healthy"),
            ("cheap", "Cheap"),
            ("vegetarian", "Vegetarian"),
            ("vegan", "Vegan"),
            ("quick", "Quick"),
            ("use_pantry", "Use Pantry"),
        ],
    )
    @run_ai_request(
        success_handler="meal_plan_on_ai_response",
        error_handler="meal_plan_on_ai_error"
    )
    def ai_suggest_day_meal_plan(self, options: dict, *_, **__):
        """
        Suggest a meal plan for the day using AI with option chips.
        The chip selection dialog is injected via the @planner_options_dialog decorator.
        
        Args:
            options (dict): Dictionary of selected options from PlannerOptionsDialog.
        """
        current_text = self.meal_list.toPlainText()
        AI_promt = self._build_meal_plan_prompt(current_text, options)

        return AI_promt

    def meal_plan_on_ai_response(self, response):
        """
        Handle successful AI response for meal plan suggestions.
        
        Args:
            response (str): The AI-generated meal plan text.
        """
        self.meal_list.setPlainText(response)

    def meal_plan_on_ai_error(self, error_message):
        """
        Handle AI request error for meal plan suggestions.
        
        Args:
            error_message (str): The error message from the AI request.
        """
        print(error_message)
