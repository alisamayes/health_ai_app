"""
Graphs widget for the Health App.
"""
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QSplitter
from datetime import datetime, timedelta
from database import use_db, get_earliest_food_date, get_earliest_sleep_diary_date, get_daily_calorie_goal, get_food_calorie_totals_for_timeframe, get_exercise_calorie_totals_for_timeframe, get_sleep_duration_totals_for_timeframe
from config import (
    background_dark_gray, white, border_gray, active_dark_green,
    calories_burned_red, overburn_orange, hover_light_green
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils import get_timeframe_dates

class Graphs(QWidget):
    """
    This is the graphs page of the app. It is used to display the graphs of the calories consumed and burned over time,
    as well as sleep duration data over time.
    It contains a timeframe selector, graphs to show the data, and navigation buttons to increase or decrease the timeframe.
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

        # Two separate matplotlib canvases (calories, sleep) in a vertical splitter
        self.calorie_fig = Figure(figsize=(6, 4), dpi=100)
        self.calorie_canvas = FigureCanvas(self.calorie_fig)
        self.calorie_graph = self.calorie_fig.add_subplot(111)

        self.sleep_fig = Figure(figsize=(6, 4), dpi=100)
        self.sleep_canvas = FigureCanvas(self.sleep_fig)
        self.sleep_graph = self.sleep_fig.add_subplot(111)

        self.graphs_splitter = QSplitter(Qt.Orientation.Vertical)
        self.graphs_splitter.addWidget(self.calorie_canvas)
        self.graphs_splitter.addWidget(self.sleep_canvas)
        self.layout.addWidget(self.graphs_splitter)

        # Ensure canvas/figure/axes respect dark theme colors (Qt stylesheets do not style Matplotlib)
        light_fg = "#ffffff"
        grid_color = "#5a5a5a"
        try:
            for canvas, fig, ax in [
                (self.calorie_canvas, self.calorie_fig, self.calorie_graph),
                (self.sleep_canvas, self.sleep_fig, self.sleep_graph),
            ]:
                canvas.setStyleSheet(f"background-color: {background_dark_gray};")
                fig.set_facecolor(background_dark_gray)
                ax.set_facecolor(background_dark_gray)
                for spine in ax.spines.values():
                    spine.set_color(grid_color)
                ax.tick_params(colors=light_fg)
                ax.title.set_color(light_fg)
                ax.xaxis.label.set_color(light_fg)
                ax.yaxis.label.set_color(light_fg)
        except Exception:
            pass

        # Initial load
        self.load_graphs()

    def _get_earliest_date_for_graphs(self):
        """
        Get the earliest date from both food and sleep diary databases.
        Returns QDate or None.
        """
        earliest_food_date = get_earliest_food_date()
        earliest_sleep_date = get_earliest_sleep_diary_date()
        
        # Convert food date string to QDate if it exists
        food_qdate = None
        if earliest_food_date:
            food_qdate = QDate.fromString(earliest_food_date, "yyyy-MM-dd")
        
        # Use the earliest of the two dates
        if food_qdate and earliest_sleep_date:
            return food_qdate if food_qdate < earliest_sleep_date else earliest_sleep_date
        elif food_qdate:
            return food_qdate
        elif earliest_sleep_date:
            return earliest_sleep_date
        else:
            return None

    def get_date_range(self, timeframe_label: str):
        """
        Get the date range for the graphs based on the timeframe label.
        Considers both food and sleep diary data to determine the earliest available date.
        
        Args:
            timeframe_label (str): The selected timeframe (e.g., "1 Week", "2 Weeks", "1 Month", etc.).
        
        Returns:
            tuple: (start_date_str, end_date_str) as "yyyy-MM-dd" strings, or (None, end_date_str) for "Full History".
        """
        # Use the shared utility function to calculate dates
        start_qdate, end_qdate = get_timeframe_dates(
            self.timeframe_selector, 
            self._get_earliest_date_for_graphs,
            timeframe_str=timeframe_label
        )
        
        return start_qdate.toString("yyyy-MM-dd") if start_qdate else None, end_qdate.toString("yyyy-MM-dd")

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
        Additionally displays sleep duration data in a second graph.
        """
        timeframe = self.timeframe_selector.currentText()
        start_str, end_str = self.get_date_range(timeframe)

        # Load calorie data
        food_rows = get_food_calorie_totals_for_timeframe(start_str, end_str)
        exercise_rows = get_exercise_calorie_totals_for_timeframe(start_str, end_str)
        daily_calorie_goal = get_daily_calorie_goal()

        # Load sleep duration data
        sleep_rows = get_sleep_duration_totals_for_timeframe(start_str, end_str)

        # Build a continuous date range and fill missing days with zero
        calorie_date_to_total = {r[0]: r[1] for r in food_rows}
        exercise_date_to_total = {r[0]: r[1] for r in exercise_rows}
        sleep_date_to_total = {r[0]: r[1] for r in sleep_rows}
        
        if start_str is None:
            all_dates = []
            if food_rows:
                all_dates.extend([r[0] for r in food_rows])
            if exercise_rows:
                all_dates.extend([r[0] for r in exercise_rows])
            if sleep_rows:
                all_dates.extend([r[0] for r in sleep_rows])
            if all_dates:
                start_date = min(datetime.strptime(d, "%Y-%m-%d").date() for d in all_dates)
                end_date = max(datetime.strptime(d, "%Y-%m-%d").date() for d in all_dates)
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
        sleep_durations = []
        current = start_date
        index = 0
        while current <= end_date:
            key = current.strftime("%Y-%m-%d")
            dates.append(key)
            food_totals.append(calorie_date_to_total.get(key, 0))
            exercise_totals.append(exercise_date_to_total.get(key, 0) * -1)
            sleep_durations.append(sleep_date_to_total.get(key, None))
            if food_totals[index] + exercise_totals[index] < 0:
                overburn.append(food_totals[index] + exercise_totals[index])
                exercise_totals[index] -= overburn[index]
            else:
                overburn.append(0)
            current += timedelta(days=1)
            index += 1

        # Prepare display labels in dd-MM-yyyy
        display_dates = [datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") for d in dates]

        # Clear both graphs
        self.calorie_graph.clear()
        self.sleep_graph.clear()

        if dates:
            # Plot the graphs. Calories on top as a bar chart, sleep duration on bottom as a line chart.
            self.calorie_graph.bar(dates, food_totals, color=active_dark_green, alpha=0.7, label='Calories Intake')
            self.calorie_graph.bar(dates, exercise_totals, color=calories_burned_red, alpha=0.7, bottom=food_totals, label='Calorie Burned')
            self.calorie_graph.bar(dates, overburn, color=overburn_orange, alpha=0.7, label='Overburn')
            if sleep_durations:
                self.sleep_graph.plot(dates, sleep_durations, color=hover_light_green, marker='o', linewidth=2, markersize=4, label='Sleep Duration')

            # Plot horizontal line for daily calorie goal if available on calories graph
            if daily_calorie_goal is not None:
                self.calorie_graph.axhline(
                    y=daily_calorie_goal,
                    color=calories_burned_red,
                    linestyle='--',
                    linewidth=1.5,
                    label='Daily Calorie Goal'
                )
            # Add horizontal lines for recommended range (7-9 hours) on sleep graph
            self.sleep_graph.axhline(y=7, color=calories_burned_red, linestyle='--', linewidth=1, alpha=0.5, label='Recommended Min (7h)')
            self.sleep_graph.axhline(y=9, color=calories_burned_red, linestyle='--', linewidth=1, alpha=0.5, label='Recommended Max (9h)')

            # Label the calorie graph
            self.calorie_graph.set_title("Daily Calories - Consumed vs Burned", color=white)
            self.calorie_graph.set_xlabel("Date", color=white)
            self.calorie_graph.set_ylabel("Calories", color=white)
            self.calorie_graph.grid(True, linestyle='--', alpha=0.3)
            self.calorie_graph.legend()

            # Label the sleep graph
            self.sleep_graph.set_title("Daily Sleep Duration", color=white)
            self.sleep_graph.set_xlabel("Date", color=white)
            self.sleep_graph.set_ylabel("Hours", color=white)
            self.sleep_graph.grid(True, linestyle='--', alpha=0.3)
            self.sleep_graph.legend()
            
            # Label x-axis only when number of points is manageable
            if len(dates) <= 32:
                self.calorie_graph.set_xticks(range(len(dates)))
                self.calorie_graph.set_xticklabels(display_dates, rotation=45, ha='right')
                self.sleep_graph.set_xticks(range(len(dates)))
                self.sleep_graph.set_xticklabels(display_dates, rotation=45, ha='right')
                if daily_calorie_goal is not None:
                    for i in range(len(dates)):
                        if (food_totals[i] + exercise_totals[i]) > daily_calorie_goal:
                            self.calorie_graph.get_xticklabels()[i].set_color(calories_burned_red)
                        else:
                            self.calorie_graph.get_xticklabels()[i].set_color(white)
                            
            else:
                self.calorie_graph.set_xticks([])
                self.sleep_graph.set_xticks([])
        else:
            self.calorie_graph.text(0.5, 0.5, "No data for selected range", ha='center', va='center', color=border_gray, transform=self.calorie_graph.transAxes)
            self.calorie_graph.set_xticks([])
            self.calorie_graph.set_yticks([])
            self.sleep_graph.text(0.5, 0.5, "No sleep data for selected range", ha='center', va='center', color=border_gray, transform=self.sleep_graph.transAxes)
            self.sleep_graph.set_xticks([])
            self.sleep_graph.set_yticks([])               

        self.calorie_fig.tight_layout()
        self.sleep_fig.tight_layout()
        self.calorie_canvas.draw()
        self.sleep_canvas.draw()


