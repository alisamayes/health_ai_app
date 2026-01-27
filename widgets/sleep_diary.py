'''
SleepDiary widget for the Health App.
'''
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QSplitter, QLabel, QTableWidget, QAbstractItemView, 
    QDialog, QDialogButtonBox, QFormLayout, QDateEdit, QTimeEdit, QTableWidgetItem, QDateTimeEdit,
    QMessageBox, QInputDialog,
)
from PyQt6.QtGui import QShortcut, QKeySequence, QBrush, QColor
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime
from database import get_sleep_diary_entries, get_earliest_sleep_diary_date, add_sleep_diary_entry, delete_sleep_diary_entry, update_sleep_diary_entry
from config import calories_burned_red, hover_light_green
from utils import get_timeframe_dates


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
        self.timeframe_layout = QHBoxLayout()
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
        self.timeframe_layout.addWidget(self.timeframe_label)
        self.timeframe_layout.addWidget(self.back_button)
        self.timeframe_layout.addWidget(self.timeframe_selector)
        self.timeframe_layout.addWidget(self.next_button)
        self.time_layout.addLayout(self.timeframe_layout)

        # Input section for adding and removing sleep time entries
        self.add_button = QPushButton("Add Entry")
        self.remove_button = QPushButton("Remove Entry")
        self.edit_button = QPushButton("Edit Entry")
        self.add_button.clicked.connect(self.add_entry)
        self.remove_button.clicked.connect(self.remove_entry_button_clicked)
        self.edit_button.clicked.connect(self.edit_entry)
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.add_button)
        self.input_layout.addWidget(self.remove_button)
        self.input_layout.addWidget(self.edit_button)
        self.time_layout.addLayout(self.input_layout)
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
 
        # Enable keyboard focus and selection
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table_layout.addWidget(self.table)

        self.stats_layout = QVBoxLayout()
        # Weekday stats
        self.weekday_bedtime_label = QLabel("Weekdays - Average Bedtime: --:--")
        self.weekday_wakeup_label = QLabel("Weekdays - Average Wakeup: --:--")
        self.weekday_sleep_duration_label = QLabel("Weekdays - Average Sleep Duration: --h --m")
        # Weekend stats
        self.weekend_bedtime_label = QLabel("Weekends - Average Bedtime: --:--")
        self.weekend_wakeup_label = QLabel("Weekends - Average Wakeup: --:--")
        self.weekend_sleep_duration_label = QLabel("Weekends - Average Sleep Duration: --h --m")
        # Overall stats
        self.overall_bedtime_label = QLabel("Overall - Average Bedtime: --:--")
        self.overall_wakeup_label = QLabel("Overall - Average Wakeup: --:--")
        self.overall_sleep_duration_label = QLabel("Overall - Average Sleep Duration: --h --m")
        # Streak and percentage-of-day stats
        self.sufficient_streak_label = QLabel("Streak since last insufficient night: -- nights")
        self.percent_of_day_sleep_label = QLabel("Average % of 24h spent sleeping: --%")

        for label in [
            self.weekday_bedtime_label,
            self.weekday_wakeup_label,
            self.weekday_sleep_duration_label,
            self.weekend_bedtime_label,
            self.weekend_wakeup_label,
            self.weekend_sleep_duration_label,
            self.overall_bedtime_label,
            self.overall_wakeup_label,
            self.overall_sleep_duration_label,
            self.sufficient_streak_label,
            self.percent_of_day_sleep_label,
        ]:
            self.stats_layout.addWidget(label)

        self.table_container = QWidget()
        self.table_container.setLayout(self.table_layout)
        self.stats_container = QWidget()
        self.stats_container.setLayout(self.stats_layout)

        self.sleep_diary_splitter = QSplitter(Qt.Orientation.Vertical)
        self.sleep_diary_splitter.addWidget(self.table_container)
        self.sleep_diary_splitter.addWidget(self.stats_container)
        self.layout.addWidget(self.sleep_diary_splitter)
        self.setLayout(self.layout)
        
        # Recommended sleep for 18-64 year olds is 7-9 hours. As this age range is so broad I dont think need to use AI or anything to narrow it down
        self.reccomended_hours_min_sleep = 7
        self.reccomended_hours_max_sleep = 9
        # Convert to seconds for precise comparison
        self.reccomended_seconds_min_sleep = self.reccomended_hours_min_sleep * 3600  # 7 hours = 25200 seconds
        self.reccomended_seconds_max_sleep = self.reccomended_hours_max_sleep * 3600  # 9 hours = 32400 seconds
        
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

    def remove_entry_button_clicked(self):
        """
        Remove an entry from the sleep diary.
        """
        row_count = self.table.rowCount()
        if row_count == 0:
            QMessageBox.information(self, "Remove Entry", "There are no entries to remove.")
            return

        # Ask user for row number
        row_number, ok = QInputDialog.getInt(
            self,
            "Remove Entry",
            f"Enter row number to remove (1 - {row_count}):",
            1, 1, row_count, 1
        )
        if not ok:
            return

        # Get IDs for this timeframe
        start_qdate, end_qdate = self.get_timeframe_dates()
        rows = get_sleep_diary_entries(start_qdate, end_qdate)
        ids = [row[0] for row in rows]

        index = row_number - 1
        if index < 0 or index >= len(ids):
            QMessageBox.warning(self, "Remove Entry", "Invalid row number.")
            return

        delete_sleep_diary_entry(ids[index])

        self.load_table()

    def keyPressEvent(self, event):
        """
        Handle keyboard press events.
        If the Delete key is pressed, deletes the selected rows from the table.
        Otherwise, passes the event to the parent class.
        """
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_rows_del_key_pressed()
        else:
            # Pass other key events to the parent class
            super().keyPressEvent(event)
    
    def delete_selected_rows_del_key_pressed(self):
        """
        Delete the selected rows from the database.
        Shows a confirmation dialog before deleting. Only deletes entries
        for the currently selected timeframe.
        """
        selected_rows = sorted({index.row() for index in self.table.selectedIndexes()}, reverse=True)
        if not selected_rows:
            return

        reply = QMessageBox.question(
            self,
            "Delete Confirmation",
            f"Delete {len(selected_rows)} record(s) from database?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        start_qdate, end_qdate = self.get_timeframe_dates()
        rows = get_sleep_diary_entries(start_qdate, end_qdate)
        ids = [row[0] for row in rows]

        for row_index in selected_rows:
            if row_index < len(ids):
                delete_sleep_diary_entry(ids[row_index])
        
        self.load_table()

    def edit_entry(self):
        """
        Edit an entry from the sleep diary. If userr currently has a selected row, edit that row. Otherwise, prompt user to select a row to edit.
        """
        index = -1;
        selected_rows = sorted({index.row() for index in self.table.selectedIndexes()}, reverse=True)

        # If no rows or more than one row selected, prompt user to select a row to edit.
        if len(selected_rows) != 1:
            row_count = self.table.rowCount()
            if row_count == 0:
                QMessageBox.information(self, "Edit Entry", "There are no entries to edit.")
                return

            row_number, ok = QInputDialog.getInt(
                self,
                "Edit Entry",
                f"Enter row number to edit (1 - {row_count}):",
                1, 1, row_count, 1
            )
            if not ok:
                return
            index = row_number - 1
        else:
            index = selected_rows[0]

        # Get IDs for this timeframe
        start_qdate, end_qdate = self.get_timeframe_dates()
        row_to_edit = get_sleep_diary_entries(start_qdate, end_qdate)[index]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Sleep Entry")
        dialog.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        
        message_label = QLabel(f"Edit the sleep entry for the night of {row_to_edit[1]}:")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        input_layout = QFormLayout()
        night_input = QDateEdit(dialog)
        night_input.setDate(QDate.fromString(row_to_edit[1], "yyyy-MM-dd"))
        night_input.setDisplayFormat("dd-MM-yyyy")
        input_layout.addRow("Night:", night_input)
        # Parse the date and times from the database row
        sleep_date_qdate = QDate.fromString(row_to_edit[1], "yyyy-MM-dd")
        bedtime_qtime = QTime.fromString(row_to_edit[2], "HH:mm")
        wakeup_qtime = QTime.fromString(row_to_edit[3], "HH:mm")
        
        # Create QDateTime objects by combining QDate and QTime
        bedtime_input = QDateTimeEdit(dialog)
        input_layout.addRow("Bedtime:", bedtime_input)
        bedtime_input.setDateTime(QDateTime(sleep_date_qdate, bedtime_qtime))
        
        wakeup_input = QDateTimeEdit(dialog)
        input_layout.addRow("Wakeup:", wakeup_input)
        wakeup_input.setDateTime(QDateTime(sleep_date_qdate, wakeup_qtime))
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
        update_sleep_diary_entry(row_to_edit[0], sleep_date, bedtime, wakeup, sleep_duration)
        self.load_table()

    def get_timeframe_dates(self):
        """
        Get the start and end dates for the current timeframe.
        Returns:
            tuple: (start_qdate, end_qdate)
        """
        return get_timeframe_dates(self.timeframe_selector, get_earliest_sleep_diary_date)

    def load_table(self):
        """
        Load the table with the sleep diary entries from the database.
        """
        
        start_qdate, end_qdate = self.get_timeframe_dates()
        rows = get_sleep_diary_entries(start_qdate, end_qdate)

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
           # row[0] is "yyyy-MM-dd" from the DB - parse it correctly
           qdate = QDate.fromString(row[1], "yyyy-MM-dd")
           if qdate.isValid():
               display_date = qdate.toString("dd-MM-yyyy")
           else:
               # Fallback if date format is unexpected
               display_date = row[1]
           self.table.setItem(i, 0, QTableWidgetItem(display_date))
           self.table.setItem(i, 1, QTableWidgetItem(row[2]))  # bedtime
           self.table.setItem(i, 2, QTableWidgetItem(row[3]))  # wakeup
           
           # Sleep duration with color coding using QLabel widget for reliable styling
           duration_qtime = QTime.fromString(row[4], "HH:mm")
           duration_label = QLabel(row[4])
           duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
           if duration_qtime.isValid():
               # Convert to total seconds for precise comparison
               duration_seconds = duration_qtime.hour() * 3600 + duration_qtime.minute() * 60
               # Apply color based on recommended range (7-9 hours = 25200-32400 seconds)
               if duration_seconds < self.reccomended_seconds_min_sleep or duration_seconds > self.reccomended_seconds_max_sleep:
                   duration_label.setStyleSheet(f"color: {calories_burned_red};")
               else:
                   duration_label.setStyleSheet(f"color: {hover_light_green};")
           self.table.setCellWidget(i, 3, duration_label)
        self.load_stats()

    def load_stats(self):
        """
        Load the stats for the sleep diary.
        Calculates average bedtime, wakeup time, and sleep duration for the current timeframe.
        """
        start_qdate, end_qdate = self.get_timeframe_dates()
        rows = get_sleep_diary_entries(start_qdate, end_qdate)

        if not rows:
            self.weekday_bedtime_label.setText("Weekdays - Average Bedtime: --:--")
            self.weekday_wakeup_label.setText("Weekdays - Average Wakeup: --:--")
            self.weekday_sleep_duration_label.setText("Weekdays - Average Sleep Duration: --h --m")
            self.weekend_bedtime_label.setText("Weekends - Average Bedtime: --:--")
            self.weekend_wakeup_label.setText("Weekends - Average Wakeup: --:--")
            self.weekend_sleep_duration_label.setText("Weekends - Average Sleep Duration: --h --m")
            self.overall_bedtime_label.setText("Overall - Average Bedtime: --:--")
            self.overall_wakeup_label.setText("Overall - Average Wakeup: --:--")
            self.overall_sleep_duration_label.setText("Overall - Average Sleep Duration: --h --m")
            self.sufficient_streak_label.setText("Streak since last insufficient night: -- nights")
            self.percent_of_day_sleep_label.setText("Average % of 24h spent sleeping: --%")
            return

        # Accumulators for weekday, weekend, and overall
        stats = {
            "weekday": {"bed": [], "wake": [], "dur": []},
            "weekend": {"bed": [], "wake": [], "dur": []},
            "all": {"bed": [], "wake": [], "dur": []},
        }

        # Helper to add seconds to category lists
        def add_to_category(cat_key, bedtime_secs, wakeup_secs, duration_secs):
            if bedtime_secs is not None:
                stats[cat_key]["bed"].append(bedtime_secs)
            if wakeup_secs is not None:
                stats[cat_key]["wake"].append(wakeup_secs)
            if duration_secs is not None:
                stats[cat_key]["dur"].append(duration_secs)

        for row in rows:
            # row[1] = sleep_date "yyyy-MM-dd", row[2] = bedtime "HH:mm",
            # row[3] = wakeup "HH:mm", row[4] = duration "HH:mm"
            date_qdate = QDate.fromString(row[1], "yyyy-MM-dd")
            bedtime_qtime = QTime.fromString(row[2], "HH:mm")
            wakeup_qtime = QTime.fromString(row[3], "HH:mm")
            duration_qtime = QTime.fromString(row[4], "HH:mm")

            bedtime_secs = None
            wakeup_secs = None
            duration_secs = None

            if bedtime_qtime.isValid():
                bedtime_secs = bedtime_qtime.hour() * 3600 + bedtime_qtime.minute() * 60
                # If bedtime is between 00:00-06:00, treat as next day (add 24 hours)
                if bedtime_qtime.hour() < 6:
                    bedtime_secs += 24 * 3600

            if wakeup_qtime.isValid():
                wakeup_secs = wakeup_qtime.hour() * 3600 + wakeup_qtime.minute() * 60

            if duration_qtime.isValid():
                duration_secs = duration_qtime.hour() * 3600 + duration_qtime.minute() * 60

            # Determine weekday vs weekend (1=Mon ... 7=Sun)
            if date_qdate.isValid():
                if date_qdate.dayOfWeek() in (6, 7):
                    categories = ["weekend", "all"]
                else:
                    categories = ["weekday", "all"]
            else:
                categories = ["all"]

            for cat in categories:
                add_to_category(cat, bedtime_secs, wakeup_secs, duration_secs)

        # Helper to compute average bedtime, wakeup, and duration labels
        def format_time_from_seconds(avg_secs):
            avg_secs = avg_secs % (24 * 3600)
            qtime = QTime(0, 0, 0).addSecs(int(avg_secs))
            return qtime.toString("HH:mm")

        def format_duration_from_seconds(avg_secs):
            hours = int(avg_secs // 3600)
            minutes = int((avg_secs % 3600) // 60)
            return hours, minutes

        def update_labels_for_category(prefix, data, bedtime_label, wakeup_label, duration_label):
            if data["bed"]:
                avg_bed_secs = sum(data["bed"]) / len(data["bed"])
                bedtime_label.setText(f"{prefix} - Average Bedtime: {format_time_from_seconds(avg_bed_secs)}")
            else:
                bedtime_label.setText(f"{prefix} - Average Bedtime: --:--")

            if data["wake"]:
                avg_wake_secs = sum(data["wake"]) / len(data["wake"])
                wakeup_label.setText(f"{prefix} - Average Wakeup: {format_time_from_seconds(avg_wake_secs)}")
            else:
                wakeup_label.setText(f"{prefix} - Average Wakeup: --:--")

            if data["dur"]:
                avg_dur_secs = sum(data["dur"]) / len(data["dur"])
                h, m = format_duration_from_seconds(avg_dur_secs)
                duration_label.setText(f"{prefix} - Average Sleep Duration: {h}h {m}m")
            else:
                duration_label.setText(f"{prefix} - Average Sleep Duration: --h --m")

        # Update weekday, weekend, and overall labels
        update_labels_for_category(
            "Weekdays",
            stats["weekday"],
            self.weekday_bedtime_label,
            self.weekday_wakeup_label,
            self.weekday_sleep_duration_label,
        )
        update_labels_for_category(
            "Weekends",
            stats["weekend"],
            self.weekend_bedtime_label,
            self.weekend_wakeup_label,
            self.weekend_sleep_duration_label,
        )
        update_labels_for_category(
            "Overall",
            stats["all"],
            self.overall_bedtime_label,
            self.overall_wakeup_label,
            self.overall_sleep_duration_label,
        )

        # Highlight overall average duration based on recommended range
        if stats["all"]["dur"]:
            avg_overall_dur_secs = sum(stats["all"]["dur"]) / len(stats["all"]["dur"])
            if (
                avg_overall_dur_secs < self.reccomended_seconds_min_sleep
                or avg_overall_dur_secs > self.reccomended_seconds_max_sleep
            ):
                self.overall_sleep_duration_label.setStyleSheet(f"color: {calories_burned_red};")
            else:
                self.overall_sleep_duration_label.setStyleSheet(f"color: {hover_light_green};")

        # Compute streak since last insufficient night (within this timeframe)
        streak = 0
        for row in reversed(rows):
            duration_qtime = QTime.fromString(row[4], "HH:mm")
            if not duration_qtime.isValid():
                break
            dur_secs = duration_qtime.hour() * 3600 + duration_qtime.minute() * 60
            if (
                dur_secs < self.reccomended_seconds_min_sleep
                or dur_secs > self.reccomended_seconds_max_sleep
            ):
                break
            streak += 1
        self.sufficient_streak_label.setText(
            f"Streak since last insufficient night: {streak} night{'s' if streak != 1 else ''}"
        )

        # Compute % of 24h spent sleeping for the current timeframe
        total_sleep_secs = sum(stats["all"]["dur"]) if stats["all"]["dur"] else 0
        nights_with_entries = len(stats["all"]["dur"])
        if nights_with_entries > 0:
            # Interpret as average % of a 24h day spent sleeping on nights with entries
            avg_sleep_secs_per_night = total_sleep_secs / nights_with_entries
            percent_of_day = (avg_sleep_secs_per_night / (24 * 3600)) * 100
            self.percent_of_day_sleep_label.setText(
                f"Average % of 24h spent sleeping: {percent_of_day:.1f}%"
            )
        else:
            self.percent_of_day_sleep_label.setText("Average % of 24h spent sleeping: --%")

        """
        TODO: Work out recommended sleep duration based on age and sleep duration and show it to the user visually if not achieving it.
        """