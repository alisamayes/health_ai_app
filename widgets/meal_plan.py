"""
MealPlan widget for the Health App.
"""
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from database import create_meal_plan_row
from widgets.day_widget import DayWidget

class MealPlan(QWidget):
    """
    This class creates the meal plan page of the app.
    It contains a layout for the days of the week, and a widget for each day.
    The widget for each day are interactive and allow the user to edit the meal list for the day.
    The meal list is saved to the database when the user edits it.
    Note: A lot of the functionality for this tab is found in the DayWidget and PlannerOptionsDialog classes.
    """
    def __init__(self):
        """
        Initialize the MealPlan widget.
        Creates the database row if it doesn't exist, sets up day widgets for each
        day of the week, and updates header button states based on settings.
        """
        super().__init__()
        # Initialize QSettings for persistent settings
        self.settings = QSettings("MindfulMauschen", "HealthApp")

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
        """
        Update the enabled/disabled state of day header buttons based on meal plan AI setting.
        Reads the meal_plan_ai_enabled setting and enables/disables all day header buttons accordingly.
        """
        meal_plan_ai_enabled = self.settings.value("meal_plan_ai_enabled", False, type=bool)
        for day_widget in self.day_widgets:
            day_widget.day_header.setEnabled(meal_plan_ai_enabled)

