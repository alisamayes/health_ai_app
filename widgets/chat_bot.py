"""
ChatBot widget for the Health App.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from utils import run_ai_request

class ChatBot(QWidget):
    """
    This class creates the chat bot page of the app.
    It contains a chat area and an input field for the user to enter their message.
    The requests and responses are displayed in the chat area.
    """
    def __init__(self):
        """Initialize the ChatBot widget."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(40)  # Start with single line height
        self.input_field.textChanged.connect(self.adjust_input_height)
        self.send_button = QPushButton("Send")

        self.layout.addWidget(self.chat_area)
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)

        self.send_button.clicked.connect(self.handle_send)
        
        # Track if AI request is in progress
        self.ai_request_in_progress = False
        self.current_worker = None

    def adjust_input_height(self):
        """
        Adjust the input field height based on content.
        Dynamically resizes the input field as the user types, with a minimum
        height of 40px (single line) and maximum height of 120px (4-5 lines).
        """
        # Calculate the height needed for the content
        doc = self.input_field.document()
        doc_height = doc.size().height()
        
        # Get the font metrics to calculate proper line height
        font_metrics = self.input_field.fontMetrics()
        line_height = font_metrics.height()
        
        # Set a reasonable minimum and maximum height
        min_height = 40  # Single line
        max_height = 120  # About 4-5 lines max
        
        # Calculate the new height with proper line spacing and padding
        # Add extra padding to ensure the full line is visible
        new_height = max(min_height, min(doc_height + line_height + 10, max_height))
        
        # Update the height
        self.input_field.setMaximumHeight(int(new_height))

    @run_ai_request(
        success_handler="chat_bot_on_ai_response",
        error_handler="chat_bot_on_ai_error"
    )
    def handle_send(self):
        """
        Handle send button click - create async AI request.
        Displays the user message in the chat area, shows a "Thinking..." indicator,
        disables the UI, and initiates an asynchronous AI request.
        
        Returns:
            str or None: The user message prompt, or None if empty or request already in progress.
        """
        user_message = self.input_field.toPlainText().strip()
        if not user_message:
            return None
        
        # Prevent multiple simultaneous requests
        if self.ai_request_in_progress:
            return None

        # Display user message
        self.chat_area.append(f"You: {user_message}")
        self.input_field.clear()
        
        # Show "thinking" indicator
        self.chat_area.append("AI: Thinking...")
        
        # Disable send button and input
        self.set_ui_state(False)
        
        # Return the prompt for the AI worker decorator to handle
        return user_message
    
    def set_ui_state(self, enabled):
        """
        Enable or disable UI elements during AI request.
        
        Args:
            enabled (bool): True to enable UI elements, False to disable them.
        """
        self.send_button.setEnabled(enabled)
        self.input_field.setEnabled(enabled)
    
    def chat_bot_on_ai_response(self, response):
        """
        Handle successful AI response.
        Removes the "Thinking..." indicator and displays the AI response in the chat area.
        
        Args:
            response (str): The AI-generated response text.
        """
        # Remove "Thinking..." and add actual response
        text = self.chat_area.toPlainText()
        if text.endswith("AI: Thinking..."):
            text = text.rsplit("AI: Thinking...", 1)[0]
        self.chat_area.setPlainText(text)
        
        # Add the actual AI response
        self.chat_area.append(f"AI: {response}\n")
        
        # Re-enable UI
        self.set_ui_state(True)
        self.ai_request_in_progress = False
        self.current_worker = None
    
    def chat_bot_on_ai_error(self, error_message):
        """
        Handle AI request error.
        Removes the "Thinking..." indicator and displays the error message in the chat area.
        
        Args:
            error_message (str): The error message from the AI request.
        """
        # Remove "Thinking..." and add error message
        text = self.chat_area.toPlainText()
        if text.endswith("AI: Thinking..."):
            text = text.rsplit("AI: Thinking...", 1)[0]
        self.chat_area.setPlainText(text)
        
        # Add error message
        self.chat_area.append(f"AI: {error_message}\n")
        
        # Re-enable UI
        self.set_ui_state(True)
        self.ai_request_in_progress = False
        self.current_worker = None

