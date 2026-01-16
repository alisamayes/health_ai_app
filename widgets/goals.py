"""
Goals widget for the Health App.
"""
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QInputDialog, QMessageBox, QDateEdit, QDialog, QDialogButtonBox, QFormLayout
)
from datetime import datetime
from database import use_db, add_weight, add_weight_loss_timeframe, add_daily_calorie_goal, get_current_weight, get_target_weight, get_weight_loss_timeframe, get_daily_calorie_goal, get_all_currnet_weight_entries, update_weight_entry, delete_weight_entry
from config import background_dark_gray, white, border_gray, active_dark_green
from utils import run_ai_request
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Goals(QWidget):
    """
    This is the goals page of the app. It is used to track the weight goal of the user.
    It contains a current weight button, a target weight button, and a weight loss value label.
    Each point on the graph is interactive and can be expanded for more info and to edit or delete the entry.
    """
    def __init__(self):
        """
        Initialize the Goals widget.
        Sets up input buttons, info labels, and a matplotlib canvas for displaying
        weight progress. Connects click events to the graph for interactive data points.
        """
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
       
        # Following buttons are for inputting and displaying the weight goal values
        input_layout = QHBoxLayout()
        self.add_current_weight_button = QPushButton("Add Current Weight")
        self.add_target_weight_button = QPushButton("Add Target Weight")
        self.calculate_daily_calorie_goal_button = QPushButton("Calculate Daily Calorie Goal")
        self.add_current_weight_button.clicked.connect(self.input_current_weight)
        self.add_target_weight_button.clicked.connect(self.input_target_weight)
        self.calculate_daily_calorie_goal_button.clicked.connect(self.calculate_daily_calorie_goal)
        input_layout.addWidget(self.add_current_weight_button)
        input_layout.addWidget(self.add_target_weight_button)
        input_layout.addWidget(self.calculate_daily_calorie_goal_button)

        # Create a container widget for the info layer
        info_container = QWidget()
        info_layout = QHBoxLayout()
        info_container.setLayout(info_layout)
        
        self.current_weight = QLabel("Current Weight: -- kg")
        self.target_weight = QLabel("Target Weight: -- kg")
        self.weight_loss_value = QLabel("Weight Loss Goal: -- kg")
        self.weight_loss_timeframe = QLabel("Timeframe: -- months")
        self.daily_calorie_goal = QLabel("Daily Calorie Goal: -- kcal")
        info_layout.addWidget(self.current_weight)
        info_layout.addWidget(self.target_weight)
        info_layout.addWidget(self.weight_loss_value)
        info_layout.addWidget(self.weight_loss_timeframe)
        info_layout.addWidget(self.daily_calorie_goal)
        
        # Calculate max height based on text height plus padding
        font_metrics = self.current_weight.fontMetrics()
        text_height = font_metrics.height()
        padding = 16  # 16 pixels of padding
        max_height = text_height + padding
        info_container.setMaximumHeight(max_height)

        self.layout.addLayout(input_layout)
        self.layout.addWidget(info_container)
        
        # Load existing values and update labels
        self.load_info()

        # Matplotlib canvas for displaying the history of weight entries
        self.canvas = FigureCanvas(Figure(figsize=(6, 3), dpi=100))
        self.graph = self.canvas.figure.add_subplot(111)

        self.layout.addWidget(self.canvas)

        # Ensure canvas/figure/axes respect dark theme colors (Qt stylesheets do not style Matplotlib)
        from config import background_dark_gray, white
        light_fg = white
        grid_color = "#5a5a5a"
        try:
            self.canvas.setStyleSheet(f"background-color: {background_dark_gray};")
            self.canvas.figure.set_facecolor(background_dark_gray)
            self.graph.set_facecolor(background_dark_gray)
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
        target_weight = get_target_weight()
        self.load_graphs(target_weight)

    def input_current_weight(self):
        """
        Show a dialog for the user to enter their current weight in kg.
        Saves the weight to the database with the current date, updates the
        current weight label, reloads info, and refreshes the graph.
        """
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
            add_weight(weight, datetime.now().strftime("%Y-%m-%d"), "current")
            
            # Update button text
            self.current_weight.setText(f"Current Weight: {weight} kg")
            # Reload to update weight loss calculation and graph
            self.load_info()
            # Get target weight for graph y-axis limit
            target_weight = get_target_weight()
            self.load_graphs(target_weight)

    def input_target_weight(self):
        """
        Show a dialog for the user to enter their target weight in kg.
        Saves the weight to the database with the current date, updates the
        target weight label, reloads info, and refreshes the graph with the new target.
        """
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
            add_weight(weight, datetime.now().strftime("%Y-%m-%d"), "target")
            
            # Update button text
            self.target_weight.setText(f"Target Weight: {weight} kg")
            # Reload to update weight loss calculation and graph
            self.load_info()
            # Refresh graph with new target weight as y-axis limit
            self.load_graphs(weight)

    def calculate_daily_calorie_goal(self):
        """
        Show a dialog for the user to enter personal information (age, height, gender,
        activity level, timeframe) and calculate a daily calorie goal using AI.
        The calculated goal is saved to the database and displayed in the label.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Daily Calorie Goal")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        input_layout = QFormLayout()
        age_input = QLineEdit(dialog)
        age_input.setPlaceholderText("Enter age")
        input_layout.addRow("Age:", age_input)
        height_input = QLineEdit(dialog)
        height_input.setPlaceholderText("Enter height in cm")
        input_layout.addRow("Height (cm):", height_input)
        gender_input = QLineEdit(dialog)
        gender_input.setPlaceholderText("Enter gender")
        input_layout.addRow("Gender:", gender_input)
        activity_level_input = QLineEdit(dialog)
        activity_level_input.setPlaceholderText("Enter activity level")
        input_layout.addRow("Activity Level:", activity_level_input)
        timeframe_input = QLineEdit(dialog)
        timeframe_input.setPlaceholderText("Enter timeframe in months")
        input_layout.addRow("Timeframe (months):", timeframe_input)
        layout.addLayout(input_layout)

        def handle_calculate():
            """Handle calculate button click in the dialog."""
            self.calculate_daily_calorie_goal_ai(
                age_input.text(), 
                height_input.text(), 
                gender_input.text(), 
                activity_level_input.text(), 
                timeframe_input.text(),
                # Strip the non numeric characters from the current and target weight
                float(self.current_weight.text().split(":")[1].split()[0]),
                float(self.target_weight.text().split(":")[1].split()[0]),
            )
            dialog.accept()  # Close the dialog after calculation
        
        button_layout = QHBoxLayout()
        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(handle_calculate)
        button_layout.addWidget(calculate_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        
        # Show the dialog
        dialog.exec()

    
    def load_info(self):
        """
        Reload all goal information from the database.
        Updates the current weight, target weight, weight loss goal, timeframe,
        and daily calorie goal labels with the latest values from the database.
        """
        current_weight = get_current_weight()
        target_weight = get_target_weight()
        daily_calorie_goal = get_daily_calorie_goal()
        weight_loss_timeframe = get_weight_loss_timeframe()
        
        # Update button texts
        if current_weight is not None:
            self.current_weight.setText(f"Current Weight: {current_weight} kg")
        else:
            self.current_weight.setText("Current Weight: -- kg")
            
        if target_weight is not None:
            self.target_weight.setText(f"Target Weight: {target_weight} kg")
        else:
            self.target_weight.setText("Target Weight: -- kg")
        
        # Update daily calorie goal display
        if daily_calorie_goal is not None:
            # Display as integer if it's a whole number, otherwise show one decimal place
            if daily_calorie_goal == int(daily_calorie_goal):
                self.daily_calorie_goal.setText(f"Daily Calorie Goal: {int(daily_calorie_goal)} kcal")
            else:
                self.daily_calorie_goal.setText(f"Daily Calorie Goal: {daily_calorie_goal:.1f} kcal")
        else:
            self.daily_calorie_goal.setText("Daily Calorie Goal: -- kcal")
        
        # Update weight loss timeframe display
        if weight_loss_timeframe is not None:
            self.weight_loss_timeframe.setText(f"Timeframe: {weight_loss_timeframe} months")
        else:
            self.weight_loss_timeframe.setText("Timeframe: -- months")

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
        """
        Load and display weight progress graph from the database.
        Plots all weight entries as a line graph with markers. Sets the y-axis
        bottom limit to the target weight if provided.
        
        Args:
            target_weight (float or None): The target weight to use as y-axis minimum, or None for default (50.0).
        """
        rows = get_all_currnet_weight_entries()

        ids = []
        dates = []
        weights = []

        # Extract IDs, dates and weights from database results
        for row in rows:
            entry_id = row[0]  # id
            weight = row[1]  # current_weight
            date_str = row[2]  # updated_date
            
            # Convert date string to datetime for proper sorting and display
            try:
                # Try parsing as date-only format first (YYYY-MM-DD)
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                ids.append(entry_id)
                dates.append(date_obj.strftime("%d-%m-%Y"))  # Format for display
                weights.append(weight)
            except ValueError:
                try:
                    # Fallback to datetime format for old entries (YYYY-MM-DD HH:MM:SS)
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    ids.append(entry_id)
                    dates.append(date_obj.strftime("%d-%m-%Y"))  # Format for display
                    weights.append(weight)
                except ValueError:
                    # Skip entries with invalid date formats
                    continue
        
        # Store data for click events
        self.ids_copy = ids.copy()
        self.dates_copy = dates.copy()
        self.weights_copy = weights.copy()

        self.graph.clear()
        
        if dates and weights:
            # Plot the weight data
            self.graph.plot(dates, weights, marker='o', color= active_dark_green, linewidth=2)
            self.graph.fill_between(range(len(weights)), weights, color= active_dark_green, alpha=0.15)
            self.graph.set_title("Weight Progress", color=white)
            self.graph.set_xlabel("Date", color=white)
            self.graph.set_ylabel("Weight (kg)", color=white)
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
                          ha='center', va='center', color=border_gray, 
                          transform=self.graph.transAxes)
            self.graph.set_xticks([])
            self.graph.set_yticks([])
            self.graph.set_title("Weight Progress", color=white)
            self.graph.set_xlabel("Date", color=white)
            self.graph.set_ylabel("Weight (kg)", color=white)
        
        # Set y-axis bottom limit to target weight if provided (apply to both cases)
        if target_weight is not None:
            self.graph.set_ylim(bottom=target_weight)
        else:
            self.graph.set_ylim(bottom=50.0)

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def on_click(self, event):
        """
        Handle click events on the graph to show data point information.
        Finds the closest data point to the click location and shows a popup
        dialog with entry details if the click is within a reasonable distance.
        
        Args:
            event: The matplotlib mouse event containing click coordinates.
        """
        
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
        """
        Show popup dialog with data point information and options to edit or delete.
        
        Args:
            date_str (str): The date string in "dd-MM-yyyy" format.
            weight (float): The weight value for this entry.
            index (int): The index of this entry in the data arrays.
        """
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
            return
        elif clicked_button == edit_button:
            entry_id = self.ids_copy[index]
            self.edit_weight_entry(date_str, weight, index, entry_id)
            return
        elif clicked_button == delete_button:
            entry_id = self.ids_copy[index]
            self.delete_weight_entry(entry_id)
            return

    def edit_weight_entry(self, current_date_str, current_weight, index, entry_id):
        """
        Show edit dialog for weight entry to edit the date and weight.
        
        Args:
            current_date_str (str): The current date string in "dd-MM-yyyy" format.
            current_weight (float): The current weight value.
            index (int): The index of this entry in the data arrays.
            entry_id (int): The database ID of the entry to update.
        """
        # Parse current date for the dialog
        current_date = datetime.strptime(current_date_str, "%d-%m-%Y")
        
        # Create custom dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Weight Entry")
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Date input
        date_edit = QDateEdit()
        date_edit.setDate(QDate.fromString(current_date_str, "dd-MM-yyyy"))
        date_edit.setDisplayFormat("dd-MM-yyyy")
        form_layout.addRow("Date:", date_edit)
        
        # Weight input
        weight_input, ok = QInputDialog.getDouble(
            dialog,
            "Edit Weight",
            "Enter new weight (kg):",
            value=current_weight,
            min=50.0,
            max=300.0,
            decimals=1
        )
        
        if not ok:
            return  # User cancelled
            
        # Create button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_date = date_edit.date()
            new_date_str = new_date.toString("yyyy-MM-dd")
            
            # Update database using the entry ID
            update_weight_entry(entry_id, weight_input, new_date_str)
            
        # Reload the graph and refresh all labels
        target_weight = get_target_weight()
        self.load_graphs(target_weight)
        
        # Force complete refresh of the canvas and axis labels
        self.canvas.figure.tight_layout()
        self.canvas.flush_events()
        self.canvas.draw()

    def delete_weight_entry(self, entry_id):
        """
        Remove weight entry from database and refresh the graph.
        
        Args:
            entry_id (int): The database ID of the entry to delete.
        """
        delete_weight_entry(entry_id)
        
        # Reload the graph and refresh all labels
        target_weight = get_target_weight()
        self.load_graphs(target_weight)
        
        # Force complete refresh of the canvas and axis labels
        self.canvas.figure.tight_layout()
        self.canvas.flush_events()
        self.canvas.draw()

    @run_ai_request(
        success_handler="daily_calories_calculation_on_ai_response",
        error_handler="daily_calories_calculation_on_ai_error"
    )
    def calculate_daily_calorie_goal_ai(self, age, height, gender, activity_level, timeframe, current_weight, target_weight):
        """
        Calculate the daily calorie goal using AI.
        Saves the timeframe to the database and builds an AI prompt with the user's
        information. The AI response is handled by daily_calories_calculation_on_ai_response.
        
        Args:
            age (str): User's age.
            height (str): User's height in cm.
            gender (str): User's gender.
            activity_level (str): User's activity level.
            timeframe (str): Weight loss timeframe in months.
            current_weight (float): Current weight in kg.
            target_weight (float): Target weight in kg.
        
        Returns:
            str: The AI prompt string.
        """
        self.weight_loss_timeframe.setText(f"Weight Loss Timeframe: {timeframe} months")
        if timeframe is not None:
            add_weight_loss_timeframe(timeframe, datetime.now().strftime("%Y-%m-%d"))

        # Build and return the AI prompt
        AI_prompt = ("Calculate the daily calorie goal for a " + str(age) + " year old " + str(gender) + " with a height of " + str(height) + " cm and an activity level of " + str(activity_level) + ". "
                "They are currently " + str(current_weight) + " kg and the target weight is " + str(target_weight) + " kg over a timeframe of " + str(timeframe) + " months. "
                "Please tailor your response in the format of only the numerical value of the daily calorie goal and nothing else.")
        return AI_prompt

    def daily_calories_calculation_on_ai_response(self, response):
        """
        Handle successful AI response for daily calorie goal calculation.
        Extracts the numeric value from the response, saves it to the database,
        and updates the daily calorie goal label.
        
        Args:
            response (str): The AI-generated response containing the calorie goal.
        """
        try:
            calorie_value = int(response)
        except ValueError:
            calorie_value = None
        
        if calorie_value is not None:
            add_daily_calorie_goal(calorie_value, datetime.now().strftime("%Y-%m-%d"))
            self.daily_calorie_goal.setText(f"Daily Calorie Goal: {calorie_value} kcal")
        else:
            self.daily_calorie_goal.setText(f"Daily Calorie Goal: {response}")

    def daily_calories_calculation_on_ai_error(self, error_message):
        """
        Handle AI request error for daily calorie goal calculation.
        
        Args:
            error_message (str): The error message from the AI request.
        """
        print(error_message)
        
