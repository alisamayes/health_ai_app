"""
Graphs widget for the Health App.
"""
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from datetime import datetime, timedelta
from database import use_db, get_earliest_food_date, get_daily_calorie_goal, get_food_calorie_totals_for_timeframe, get_exercise_calorie_totals_for_timeframe
from config import (
    background_dark_gray, white, border_gray, active_dark_green,
    calories_burned_red, overburn_orange
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Graphs(QWidget):
    """
    This is the graphs page of the app. It is used to display the graphs of the calories consumed and burned over time.
    It contains a timeframe selector, a graph to show the data, and navigation buttons to increase or decrease the timeframe.
    TODO: Add in interactivness like that in the goals page so a user can click on a point and have an info popup show more exact details about the point.
    """
    def __init__(self):
        """
        Initialize the Graphs widget.
        Sets up the timeframe selector, navigation buttons, and matplotlib canvas
        for displaying calorie consumption and burn data over time.
        """
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Timeframe selection
        self.timeframe_selector = QComboBox()
        self.timeframe_selector.addItems(["1 Week", "2 Weeks", "1 Month", "3 Months", "1 Year", "Full History"])
        self.timeframe_selector.currentTextChanged.connect(self.load_graphs)

        # Navigation buttons
        self.back_button = QPushButton("<")
        self.back_button.setFixedSize(30, 25)
        self.back_button.setObjectName("navigationBtn") # Navigation buttons are smaller than the other buttons in the styling to fit the < and > symbols. Thus needs a special identifier.
        self.back_button.clicked.connect(self.back)
        self.next_button = QPushButton(">")
        self.next_button.setFixedSize(30, 25)
        self.next_button.setObjectName("navigationBtn")
        self.next_button.clicked.connect(self.next)

        # Keyboard shortcuts for navigation: < and , for previous timeframe, > and . for next timeframe
        QShortcut(QKeySequence("Shift+,"), self).activated.connect(self.back)  # < key
        QShortcut(QKeySequence(","), self).activated.connect(self.back)
        QShortcut(QKeySequence("Shift+."), self).activated.connect(self.next)  # > key
        QShortcut(QKeySequence("."), self).activated.connect(self.next)
        
        # Layout box for the timeframe naivgation
        timeframe_layout = QHBoxLayout()
        timeframe_layout.addWidget(self.back_button)
        timeframe_layout.addWidget(self.timeframe_selector)
        timeframe_layout.addWidget(self.next_button)
        self.layout.addLayout(timeframe_layout)

        # Matplotlib canvas
        self.canvas = FigureCanvas(Figure(figsize=(6, 3), dpi=100))
        self.graph = self.canvas.figure.add_subplot(111)

        self.layout.addWidget(self.canvas)

        # Ensure canvas/figure/axes respect dark theme colors (Qt stylesheets do not style Matplotlib)
        light_fg = "#ffffff"
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

        # Initial load
        self.load_graphs()

    def get_date_range(self, timeframe_label: str):
        """
        Get the date range for the graphs based on the timeframe label.
        
        Args:
            timeframe_label (str): The selected timeframe (e.g., "1 Week", "2 Weeks", "1 Month", etc.).
        
        Returns:
            tuple: (start_date_str, end_date_str) as "yyyy-MM-dd" strings, or (None, end_date_str) for "Full History".
        """
        # Find earliest entry_date in the database. The start date will not be earlier than this.
        earliest_date = get_earliest_food_date()
        earliest_qdate = QDate.fromString(earliest_date, "yyyy-MM-dd") if earliest_date else None

        end_qdate = QDate.currentDate() # End date is the current date.
        if timeframe_label == "1 Week":
            start_qdate = end_qdate.addDays(-6)
        elif timeframe_label == "2 Weeks":
            start_qdate = end_qdate.addDays(-13)
        elif timeframe_label == "1 Month":
            start_qdate = end_qdate.addMonths(-1).addDays(1)
        elif timeframe_label == "3 Months":
            start_qdate = end_qdate.addMonths(-3).addDays(1)
        elif timeframe_label == "1 Year":
            start_qdate = end_qdate.addYears(-1).addDays(1)
        elif timeframe_label == "Full History": # First entry in the database to the current date.
            start_qdate = earliest_qdate

        # If earliest date and start date < earliest date, it means we dont have entries goign that far back and so just keep the range within the bounds of known data.
        if earliest_qdate and start_qdate < earliest_qdate:
            start_qdate = earliest_qdate

        return start_qdate.toString("yyyy-MM-dd"), end_qdate.toString("yyyy-MM-dd")

    def back(self):
        """
        Go back to the previous timeframe in the selector.
        Decrements the timeframe selector index if not already at the first option.
        """
        current_index = self.timeframe_selector.currentIndex()
        if current_index > 0:
            self.timeframe_selector.setCurrentIndex(current_index - 1)


    def next(self):
        """
        Go to the next timeframe in the selector.
        Increments the timeframe selector index if not already at the last option.
        """
        current_index = self.timeframe_selector.currentIndex()
        last_index = self.timeframe_selector.count() - 1
        if current_index < last_index:
            self.timeframe_selector.setCurrentIndex(current_index + 1)

    def load_graphs(self):
        """
        Load and display the graphs based on the current timeframe.
        Fetches calorie intake and exercise data from the database, calculates
        overburn values, and displays them as stacked bar charts. Also shows
        the daily calorie goal as a horizontal line if available.
        """
        timeframe = self.timeframe_selector.currentText()
        start_str, end_str = self.get_date_range(timeframe)

        food_rows = get_food_calorie_totals_for_timeframe(start_str, end_str)
        exercise_rows = get_exercise_calorie_totals_for_timeframe(start_str, end_str)
        daily_calorie_goal = get_daily_calorie_goal()

        # Build a continuous date range and fill missing days with zero
        calorie_date_to_total = {r[0]: r[1] for r in food_rows}
        exercise_date_to_total = {r[0]: r[1] for r in exercise_rows}
        
        if start_str is None:
            if food_rows or exercise_rows:
                all_dates = []
                if food_rows:
                    all_dates.extend([r[0] for r in food_rows])
                if exercise_rows:
                    all_dates.extend([r[0] for r in exercise_rows])
                if all_dates:
                    start_date = min(datetime.strptime(d, "%Y-%m-%d").date() for d in all_dates)
                    end_date = max(datetime.strptime(d, "%Y-%m-%d").date() for d in all_dates)
                else:
                    start_date = datetime.today().date()
                    end_date = start_date
            else:
                start_date = datetime.today().date()
                end_date = start_date
        else:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

        dates = []
        food_totals = []
        exercise_totals = []
        overburn = []
        current = start_date
        index = 0
        while current <= end_date:
            key = current.strftime("%Y-%m-%d")
            dates.append(key)
            food_totals.append(calorie_date_to_total.get(key, 0))
            exercise_totals.append(exercise_date_to_total.get(key, 0) * -1)
            if food_totals[index] + exercise_totals[index] < 0:
                overburn.append(food_totals[index] + exercise_totals[index])
                exercise_totals[index] -= overburn[index]
            else:
                overburn.append(0)
            current += timedelta(days=1)
            index += 1

        # Prepare display labels in dd-MM-yyyy
        display_dates = [datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") for d in dates]

        self.graph.clear()
        if dates:
            # Plot data as bar charts
            self.graph.bar(dates, food_totals, color=active_dark_green, alpha=0.7, label='Calories Intake')
            self.graph.bar(dates, exercise_totals, color=calories_burned_red, alpha=0.7, bottom=food_totals, label='Calorie Burned')
            self.graph.bar(dates, overburn, color=overburn_orange, alpha=0.7, label='Overburn')

            # Plot horizontal line for daily calorie goal if available
            if daily_calorie_goal is not None:
                self.graph.axhline(
                    y=daily_calorie_goal,
                    color=calories_burned_red,
                    linestyle='--',
                    linewidth=1.5,
                    label='Daily Calorie Goal'
                )

            self.graph.set_title("Daily Calories - Consumed vs Burned", color=white)
            self.graph.set_xlabel("Date", color=white)
            self.graph.set_ylabel("Calories", color=white)
            self.graph.grid(True, linestyle='--', alpha=0.3)
            self.graph.legend()
            
            # Label x-axis only when number of points is manageable
            if len(dates) <= 32:
                self.graph.set_xticks(range(len(dates)))
                self.graph.set_xticklabels(display_dates, rotation=45, ha='right')
                # After you have:
                if daily_calorie_goal is not None:
                    for i in range(len(dates)):
                        if (food_totals[i] + exercise_totals[i]) > daily_calorie_goal:
                            self.graph.get_xticklabels()[i].set_color(calories_burned_red)
                        else:
                            self.graph.get_xticklabels()[i].set_color(white)

            else:
                self.graph.set_xticks([])
            self.canvas.figure.tight_layout()
        else:
            self.graph.text(0.5, 0.5, "No data for selected range", ha='center', va='center', color=border_gray, transform=self.graph.transAxes)
            self.graph.set_xticks([])
            self.graph.set_yticks([])
        self.canvas.draw()


