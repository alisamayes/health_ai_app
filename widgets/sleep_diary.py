'''
SleepDiary widget for the Health App.
'''
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QSplitter, QLabel, QTableWidget, QAbstractItemView, 
    QDialog, QDialogButtonBox, QFormLayout, QDateEdit, QTimeEdit, QTableWidgetItem, QDateTimeEdit,
)
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime
from database import get_sleep_diary_entries, get_earliest_sleep_diary_date, add_sleep_diary_entry


class SleepDiary(QWidget):
    '''
    This is the sleep diary page of the app. It is used to track the sleep of the user.
    It contains an entry form to allow the user to input a bedtime and wake up time for a day as well as a graph to show their sleep pattern over time.
    This timeframe can be adjusted to show different periods of time.
    '''
    def __init__(self):
        '''
        Initialize the SleepDiary widget with date selector, input fields, and table.
        '''
        super().__init__()
        self.layout = QVBoxLayout()

        # Vertical layout that will hold all the info related to dates and sleep time inputs
        self.time_layout = QVBoxLayout()

        # Timeframe selection for choosing what period of time to show for the stats
        timeframe_layout = QHBoxLayout()
        self.timeframe_label = QLabel("Timeframe:")
        self.timeframe_label.setFixedSize(75, 25) # Set the size policy to fixed so the label doesnt stretch the layout.
        self.timeframe_selector = QComboBox()
        self.timeframe_selector.addItems(["1 Week", "2 Weeks", "1 Month", "3 Months", "1 Year", "Full History"])
        #self.timeframe_selector.currentTextChanged.connect(self.load_graphs)
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
        timeframe_layout.addWidget(self.timeframe_label)
        timeframe_layout.addWidget(self.back_button)
        timeframe_layout.addWidget(self.timeframe_selector)
        timeframe_layout.addWidget(self.next_button)
        self.time_layout.addLayout(timeframe_layout)

        # Input section for adding and removing sleep time entries
        self.add_button = QPushButton("Add Entry")
        self.remove_button = QPushButton("Remove Entry")
        self.edit_button = QPushButton("Edit Entry")
        self.add_button.clicked.connect(self.add_entry)
        self.remove_button.clicked.connect(self.remove_entry)
        self.edit_button.clicked.connect(self.edit_entry)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.remove_button)
        input_layout.addWidget(self.edit_button)
        self.time_layout.addLayout(input_layout)
        self.layout.addLayout(self.time_layout)


        # Table section to show entries for a given date
        self.table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Night", "Bedtime", "Wakeup", "Sleep Duration"])
        # Disable editing cells by double-clicking as found a user could edit the info locally. While it isnt saved to database its undesirable behaviour.
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        
        # Enable automatic column resizing to fit content
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.Stretch) 
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().ResizeMode.Stretch) 
        self.table.horizontalHeader().setSectionResizeMode(2, self.table.horizontalHeader().ResizeMode.Stretch) 
        self.table.horizontalHeader().setSectionResizeMode(3, self.table.horizontalHeader().ResizeMode.Stretch) 
        self.table.setWordWrap(True) # Enable word wrapping for long food names
        #self.table.setColumnWidth(1, 80) # Set minimum column widths
        
        
        # Enable keyboard focus and selection
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table_layout.addWidget(self.table)

        self.stats_layout = QVBoxLayout()

        self.table_container = QWidget()
        self.table_container.setLayout(self.table_layout)
        self.stats_container = QWidget()
        self.stats_container.setLayout(self.stats_layout)

        self.sleep_diary_splitter = QSplitter(Qt.Orientation.Vertical)
        self.sleep_diary_splitter.addWidget(self.table_container)
        self.sleep_diary_splitter.addWidget(self.stats_container)
        self.layout.addWidget(self.sleep_diary_splitter)
        self.setLayout(self.layout)
        self.load_table()

    def back(self):
        """
        Go back to the previous timeframe in the selector.
        Decrements the timeframe selector index if not already at the first option.
        """
        current_index = self.timeframe_selector.currentIndex()
        if current_index > 0:
            self.timeframe_selector.setCurrentIndex(current_index - 1)
        self.load_table()


    def next(self):
        """
        Go to the next timeframe in the selector.
        Increments the timeframe selector index if not already at the last option.
        """
        current_index = self.timeframe_selector.currentIndex()
        last_index = self.timeframe_selector.count() - 1
        if current_index < last_index:
            self.timeframe_selector.setCurrentIndex(current_index + 1)
        self.load_table()

    def add_entry(self):
        """
        Add a new entry to the sleep diary.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Sleep Entry")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        message_label = QLabel("What night is this sleep entry for? When did you go to bed and wake up?")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        input_layout = QFormLayout()
        night_input = QDateEdit(dialog)
        night_input.setDate(QDate.currentDate())
        night_input.setDisplayFormat("dd-MM-yyyy")
        input_layout.addRow("Night:", night_input)
        bedtime_input = QDateTimeEdit(dialog)
        input_layout.addRow("Bedtime:", bedtime_input)
        bedtime_input.setDateTime(QDateTime(QDate.currentDate(), QTime(22, 0)))
        wakeup_input = QDateTimeEdit(dialog)
        input_layout.addRow("Wakeup:", wakeup_input)
        wakeup_input.setDateTime(QDateTime(QDate.currentDate(), QTime(9, 0)))
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
        
        sleep_date = night_input.date()
        bedtime = bedtime_input.dateTime()
        wakeup = wakeup_input.dateTime()
        secs = wakeup.toSecsSinceEpoch() - bedtime.toSecsSinceEpoch()
        hours = secs / 3600
        minutes = (secs % 3600) / 60
        sleep_duration = QTime(int(hours), int(minutes))
        add_sleep_diary_entry(sleep_date, bedtime, wakeup, sleep_duration)
        self.load_table()

    def remove_entry(self):
        """
        Remove an entry from the sleep diary.
        """
        pass

    def edit_entry(self):
        """
        Edit an entry from the sleep diary.
        """
        pass

    def load_table(self):
        """
        Load the table with the sleep diary entries from the database.
        """
        timeframe_str = self.timeframe_selector.currentText()

        end_qdate = QDate.currentDate()
        earliest_qdate = get_earliest_sleep_diary_date()


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
        elif timeframe_str == "Full History": # First entry in the database to the current date.
            if earliest_qdate is None:
                # No entries in database, show empty table
                self.table.setRowCount(0)
                return
            start_qdate = earliest_qdate
        
        rows = get_sleep_diary_entries(start_qdate, end_qdate)

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
           # row[0] is "yyyy-MM-dd" from the DB - parse it correctly
           qdate = QDate.fromString(row[0], "yyyy-MM-dd")
           if qdate.isValid():
               display_date = qdate.toString("dd-MM-yyyy")
           else:
               # Fallback if date format is unexpected
               display_date = row[0]
           self.table.setItem(i, 0, QTableWidgetItem(display_date))
           self.table.setItem(i, 1, QTableWidgetItem(row[1]))  # bedtime
           self.table.setItem(i, 2, QTableWidgetItem(row[2]))  # wakeup
           self.table.setItem(i, 3, QTableWidgetItem(row[3]))  # duration

        # Resize columns to fit content after loading data
        #self.table.resizeColumnsToContents()


"""
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
"""