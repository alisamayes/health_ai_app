"""
Utility functions and decorators for the Health App.
Contains AI request decorators and dialog helpers.
"""
import threading
import os
from PyQt6.QtCore import QObject, pyqtSignal as Signal, QDate
from PyQt6.QtWidgets import QDialog, QComboBox
from openai import OpenAI
from dotenv import load_dotenv
from enum import Enum
from typing import Callable, Optional, Tuple

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))


class AIWorker(QObject):
    """
    This class is a worker class to handle AI requests in a separate thread.
    It is used to handle the AI requests for the meal plan and shopping list.
    It was made asynchronously as intially when a user hit the send button, the app would freeze until the response was ready.
    """
    finished = Signal(str)  # Signal emitted when AI response is ready
    error = Signal(str)  # Signal emitted if there's an error
    
    def __init__(self, prompt):
        """
        Initialize the AIWorker with a prompt.
        
        Args:
            prompt (str): The prompt to send to the AI.
        """
        super().__init__()
        self.prompt = prompt
    
    def run(self):
        """
        Execute the AI request in a background thread.
        Sends the prompt to OpenAI's API and emits either a finished signal
        with the response or an error signal if something goes wrong.
        """
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


def run_ai_request(success_handler: str, error_handler: str):
    """
    Decorator factory to wrap a method that returns an AI prompt string.
    The decorator automatically sets up the AIWorker, connects handlers,
    stores the worker reference, sets the in-progress flag, and starts the thread.

    Parameters
    ----------
    success_handler : str
        The name of the method to call when the AI request succeeds.
        This method should accept a single argument (the response string).
    error_handler : str
        The name of the method to call when the AI request fails.
        This method should accept a single argument (the error message string).

    Usage
    -----
        @run_ai_request(
            success_handler="on_ai_response",
            error_handler="on_ai_error"
        )
        def my_method(self, ...):
            return "AI prompt string here"
    """

    def decorator(method):
        def wrapper(self, *args, **kwargs):
            # Get the prompt from the wrapped method
            prompt = method(self, *args, **kwargs)
            if not prompt:
                return

            # Get handler methods by name
            success_method = getattr(self, success_handler)
            error_method = getattr(self, error_handler)

            # Create worker and connect signals
            worker = AIWorker(prompt)
            worker.finished.connect(success_method)
            worker.error.connect(error_method)

            # Store worker reference to prevent garbage collection
            self.current_worker = worker
            self.ai_request_in_progress = True

            # Run AI request in background thread
            thread = threading.Thread(target=worker.run)
            thread.daemon = True
            thread.start()

        return wrapper

    return decorator


def planner_options_dialog(*, title: str, label_text: str, chips: list):
    """
    Decorator factory to wrap a method so that it first shows a chip-style options
    dialog and then passes the selected options dict into the wrapped method.

    Parameters
    ----------
    title : str
        The window title for the options dialog.
    label_text : str
        The instruction text shown above the chip buttons.
    chips : list
        List of (key, display_text) tuples. The key is used in the returned
        options dict, and display_text is shown on the button.

    Usage
    -----
        @planner_options_dialog(
            title="AI Meal Planner Options",
            label_text="Choose any options you want to include:",
            chips=[("healthy", "Healthy"), ("cheap", "Cheap")],
        )
        def my_method(self, options: dict):
            # options will be a dict like {"healthy": True, "cheap": False}
            ...
    """
    from PyQt6.QtWidgets import QDialog
    from widgets.planner_options_dialog import PlannerOptionsDialog

    def decorator(method):
        def wrapper(self, *args, **kwargs):
            dialog = PlannerOptionsDialog(
                parent=self,
                title=title,
                label_text=label_text,
                chips=chips,
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                options = dialog.values()
                return method(self, options, *args, **kwargs)
            # User cancelled – do nothing
            return None

        return wrapper

    return decorator

class DaysOfTheWeek(Enum):
    """
    A simple enum to represent a day of the week with the corresponding database column name.
    """
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

    def __str__(self):
        return self.value


def get_timeframe_dates(timeframe_selector: QComboBox, get_earliest_date_func: Optional[Callable] = None, timeframe_str: Optional[str] = None) -> Tuple[QDate, QDate]:
    """
    Calculate start and end dates based on the selected timeframe in a QComboBox.
    
    This function extracts the timeframe selection from the combo box and calculates
    the appropriate date range. It can optionally use a function to get the earliest
    available date for "Full History" timeframe.
    
    Args:
        timeframe_selector: QComboBox containing timeframe options (e.g., "1 Week", "2 Weeks", etc.)
        get_earliest_date_func: Optional callable that returns the earliest available date.
                                Can return QDate, string ("yyyy-MM-dd"), or None.
                                Used for "Full History" timeframe.
        timeframe_str: Optional string to override the combo box selection.
                       If provided, uses this instead of reading from the combo box.
    
    Returns:
        tuple: (start_qdate, end_qdate) as QDate objects
    
    Supported timeframes:
        - "1 Week": Last 7 days (6 days back from today)
        - "2 Weeks": Last 14 days (13 days back from today)
        - "1 Month": Last month (1 month back from today, inclusive)
        - "3 Months": Last 3 months (3 months back from today, inclusive)
        - "1 Year": Last year (1 year back from today, inclusive)
        - "Full History": From earliest available date to today
    """
    if timeframe_str is None:
        timeframe_str = timeframe_selector.currentText()
    end_qdate = QDate.currentDate()
    
    # Get earliest date if function provided
    earliest_qdate = None
    if get_earliest_date_func is not None:
        earliest_result = get_earliest_date_func()
        if earliest_result is not None:
            if isinstance(earliest_result, QDate):
                earliest_qdate = earliest_result
            elif isinstance(earliest_result, str):
                # Assume "yyyy-MM-dd" format
                earliest_qdate = QDate.fromString(earliest_result, "yyyy-MM-dd")
    
    # Calculate start date based on timeframe
    if timeframe_str == "1 Week":
        start_qdate = end_qdate.addDays(-6)
    elif timeframe_str == "2 Weeks":
        start_qdate = end_qdate.addDays(-13)
    elif timeframe_str == "1 Month":
        start_qdate = end_qdate.addMonths(-1).addDays(1)
    elif timeframe_str == "3 Months":
        start_qdate = end_qdate.addMonths(-3).addDays(1)
    elif timeframe_str == "1 Year":
        start_qdate = end_qdate.addYears(-1).addDays(1)
    elif timeframe_str == "Full History":
        if earliest_qdate is None:
            # No entries in database, return empty range
            start_qdate = end_qdate
        else:
            start_qdate = earliest_qdate
    else:
        # Default to 1 week if unknown timeframe
        start_qdate = end_qdate.addDays(-6)
    
    # Ensure start date doesn't go before earliest available date
    if earliest_qdate and start_qdate < earliest_qdate:
        start_qdate = earliest_qdate
    
    return start_qdate, end_qdate