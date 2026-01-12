"""
Utility functions and decorators for the Health App.
Contains AI request decorators and dialog helpers.
"""
import threading
import os
from PyQt6.QtCore import QObject, pyqtSignal as Signal
from PyQt6.QtWidgets import QDialog
from openai import OpenAI
from dotenv import load_dotenv

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
