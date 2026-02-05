"""
GUI tests for PyQt6 widgets.
"""
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QDate, QTime, QDateTime
from widgets.food_tracker import FoodTracker
from widgets.exercise_tracker import ExerciseTracker
from widgets.goals import Goals
from widgets.sleep_diary import SleepDiary
from database import add_food, add_sleep_diary_entry, add_exercise


@pytest.mark.gui
class TestFoodTracker:
    """Tests for FoodTracker widget."""
    
    def test_food_tracker_initialization(self, qtbot):
        """Test that FoodTracker initializes correctly."""
        widget = FoodTracker()
        qtbot.addWidget(widget)
        
        assert widget.table is not None
        assert widget.date_selector is not None
        assert widget.add_button is not None
    
    def test_add_entry_button_exists(self, qtbot):
        """Test that add entry button exists and is clickable."""
        widget = FoodTracker()
        qtbot.addWidget(widget)
        
        assert widget.add_button.isEnabled()
        assert widget.add_button.text() == "Add Entry"
    
    def test_suggest_calories_locally(self, qtbot):
        """Test suggesting calories locally. Add an apple to the database and suggest calories for it."""
        add_food("Apple", 95, "2024-01-01")
        add_food("Banana", 105, "2024-01-01")
        add_food("Banana", 95, "2024-01-01")
        widget = FoodTracker()
        qtbot.addWidget(widget)
        calories = widget.suggest_calories_locally("Apple")
        assert calories == 95
        calories = widget.suggest_calories_locally("Banana")
        assert calories == 100

    def test_food_tracker_load_entries(self, qtbot):
        """Test loading entries from database."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        add_food("Test Food", 150, today)
        widget = FoodTracker()
        qtbot.addWidget(widget)
        assert widget.table.rowCount() >= 1
        assert any(widget.table.item(i, 0).text() == "Test Food" for i in range(widget.table.rowCount()))

    def test_food_tracker_date_navigation(self, qtbot):
        """Test back/next day buttons."""
        widget = FoodTracker()
        qtbot.addWidget(widget)
        initial_date = widget.date_selector.date()
        qtbot.mouseClick(widget.back_day_button, Qt.MouseButton.LeftButton)
        assert widget.date_selector.date() < initial_date
        qtbot.mouseClick(widget.next_day_button, Qt.MouseButton.LeftButton)
        assert widget.date_selector.date() == initial_date


@pytest.mark.gui
class TestExerciseTracker:
    """Tests for ExerciseTracker widget."""
    
    def test_exercise_tracker_initialization(self, qtbot):
        """Test that ExerciseTracker initializes correctly."""
        widget = ExerciseTracker()
        qtbot.addWidget(widget)
        
        assert widget.table is not None
        assert widget.date_selector is not None
        assert widget.add_button is not None

    def test_exercise_tracker_load_entries(self, qtbot):
        """Test loading entries from database."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        add_exercise("Running", 300, today)
        widget = ExerciseTracker()
        qtbot.addWidget(widget)
        assert widget.table.rowCount() >= 1
        assert any(widget.table.item(i, 0).text() == "Running" for i in range(widget.table.rowCount()))

    def test_exercise_tracker_date_navigation(self, qtbot):
        """Test back/next day buttons."""
        widget = ExerciseTracker()
        qtbot.addWidget(widget)
        initial_date = widget.date_selector.date()
        qtbot.mouseClick(widget.back_day_button, Qt.MouseButton.LeftButton)
        assert widget.date_selector.date() < initial_date
        qtbot.mouseClick(widget.next_day_button, Qt.MouseButton.LeftButton)
        assert widget.date_selector.date() == initial_date


@pytest.mark.gui
class TestGoals:
    """Tests for Goals widget."""
    
    def test_goals_initialization(self, qtbot):
        """Test that Goals widget initializes correctly."""
        widget = Goals()
        qtbot.addWidget(widget)
        
        assert widget.current_weight is not None
        assert widget.target_weight is not None
        assert widget.canvas is not None


@pytest.mark.gui
class TestSleepDiary:
    """Tests for SleepDiary widget."""
    
    def test_sleep_diary_initialization(self, qtbot):
        """Test that SleepDiary initializes correctly."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        assert widget.table is not None
        assert widget.timeframe_selector is not None
        assert widget.add_button is not None
        assert widget.remove_button is not None
        assert widget.edit_button is not None
        assert widget.back_button is not None
        assert widget.next_button is not None
        # Stats labels for weekdays, weekends, overall, streak and percentage
        assert widget.weekday_bedtime_label is not None
        assert widget.weekday_wakeup_label is not None
        assert widget.weekday_sleep_duration_label is not None
        assert widget.weekend_bedtime_label is not None
        assert widget.weekend_wakeup_label is not None
        assert widget.weekend_sleep_duration_label is not None
        assert widget.overall_bedtime_label is not None
        assert widget.overall_wakeup_label is not None
        assert widget.overall_sleep_duration_label is not None
        assert widget.sufficient_streak_label is not None
        assert widget.percent_of_day_sleep_label is not None
    
    def test_timeframe_selector_options(self, qtbot):
        """Test that timeframe selector has correct options."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        expected_options = ["1 Week", "2 Weeks", "1 Month", "3 Months", "1 Year", "Full History"]
        assert widget.timeframe_selector.count() == len(expected_options)
        for i, option in enumerate(expected_options):
            assert widget.timeframe_selector.itemText(i) == option
    
    def test_timeframe_navigation_back(self, qtbot):
        """Test timeframe navigation back button."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # Start at index 1 (2 Weeks)
        widget.timeframe_selector.setCurrentIndex(1)
        initial_index = widget.timeframe_selector.currentIndex()
        
        # Click back button
        qtbot.mouseClick(widget.back_button, Qt.MouseButton.LeftButton)
        
        # Should be at index 0 (1 Week)
        assert widget.timeframe_selector.currentIndex() == 0
    
    def test_timeframe_navigation_next(self, qtbot):
        """Test timeframe navigation next button."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # Start at index 0 (1 Week)
        widget.timeframe_selector.setCurrentIndex(0)
        
        # Click next button
        qtbot.mouseClick(widget.next_button, Qt.MouseButton.LeftButton)
        
        # Should be at index 1 (2 Weeks)
        assert widget.timeframe_selector.currentIndex() == 1
    
    def test_timeframe_navigation_back_at_start(self, qtbot):
        """Test that back button doesn't go below index 0."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # Start at index 0
        widget.timeframe_selector.setCurrentIndex(0)
        
        # Click back button
        qtbot.mouseClick(widget.back_button, Qt.MouseButton.LeftButton)
        
        # Should still be at index 0
        assert widget.timeframe_selector.currentIndex() == 0
    
    def test_timeframe_navigation_next_at_end(self, qtbot):
        """Test that next button doesn't go beyond last index."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # Start at last index
        last_index = widget.timeframe_selector.count() - 1
        widget.timeframe_selector.setCurrentIndex(last_index)
        
        # Click next button
        qtbot.mouseClick(widget.next_button, Qt.MouseButton.LeftButton)
        
        # Should still be at last index
        assert widget.timeframe_selector.currentIndex() == last_index
    
    def test_get_timeframe_dates(self, qtbot):
        """Test getting timeframe dates."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # Test 1 Week timeframe
        widget.timeframe_selector.setCurrentIndex(0)
        start_date, end_date = widget.get_timeframe_dates()
        
        assert start_date is not None
        assert end_date is not None
        assert isinstance(start_date, QDate)
        assert isinstance(end_date, QDate)
        assert start_date <= end_date
    
    def test_load_table_with_entries(self, qtbot):
        """Test loading table with sleep diary entries."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # Add a test entry
        sleep_date = QDate.currentDate()
        bedtime = QDateTime(sleep_date, QTime(22, 30))
        wakeup = QDateTime(sleep_date.addDays(1), QTime(7, 0))
        sleep_duration = QTime(8, 30)
        
        add_sleep_diary_entry(sleep_date, bedtime, wakeup, sleep_duration)
        
        # Reload table
        widget.load_table()
        
        # Table should have at least one row
        assert widget.table.rowCount() >= 1
    
    def test_load_table_empty(self, qtbot):
        """Test loading table with no entries."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # Table should be empty initially (or have 0 rows if no data)
        # This depends on whether there's existing test data
        assert widget.table is not None
    
    def test_stats_labels_initial_state(self, qtbot):
        """Test that stats labels show default values when no entries."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # With no entries, stats should show placeholder values
        assert widget.weekday_bedtime_label.text() == "Weekdays - Average Bedtime: --:--"
        assert widget.weekday_wakeup_label.text() == "Weekdays - Average Wakeup: --:--"
        assert widget.weekday_sleep_duration_label.text() == "Weekdays - Average Sleep Duration: --h --m"
        assert widget.weekend_bedtime_label.text() == "Weekends - Average Bedtime: --:--"
        assert widget.weekend_wakeup_label.text() == "Weekends - Average Wakeup: --:--"
        assert widget.weekend_sleep_duration_label.text() == "Weekends - Average Sleep Duration: --h --m"
        assert widget.overall_bedtime_label.text() == "Overall - Average Bedtime: --:--"
        assert widget.overall_wakeup_label.text() == "Overall - Average Wakeup: --:--"
        assert widget.overall_sleep_duration_label.text() == "Overall - Average Sleep Duration: --h --m"
        assert widget.sufficient_streak_label.text() == "Streak since last insufficient night: -- nights"
        assert widget.percent_of_day_sleep_label.text() == "Average % of 24h spent sleeping: --%"
    
    def test_table_column_count(self, qtbot):
        """Test that table has correct number of columns."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        assert widget.table.columnCount() == 4
        headers = [widget.table.horizontalHeaderItem(i).text() 
                  for i in range(widget.table.columnCount())]
        assert headers == ["Night", "Bedtime", "Wakeup", "Sleep Duration"]
    
    def test_table_not_editable(self, qtbot):
        """Test that table cells are not directly editable."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        # Table should not allow direct editing
        assert widget.table.editTriggers() == widget.table.EditTrigger.NoEditTriggers
    
    def test_add_button_exists(self, qtbot):
        """Test that add entry button exists and is enabled."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        assert widget.add_button.isEnabled()
        assert widget.add_button.text() == "Add Entry"
    
    def test_remove_button_exists(self, qtbot):
        """Test that remove entry button exists."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        assert widget.remove_button is not None
        assert widget.remove_button.text() == "Remove Entry"
    
    def test_edit_button_exists(self, qtbot):
        """Test that edit entry button exists."""
        widget = SleepDiary()
        qtbot.addWidget(widget)
        
        assert widget.edit_button is not None
        assert widget.edit_button.text() == "Edit Entry"

    def test_stats_with_weekday_and_weekend_entries(self, qtbot):
        """Test that stats labels update correctly for weekday, weekend, streak and % of day."""
        widget = SleepDiary()
        qtbot.addWidget(widget)

        # Use "Full History" timeframe so all added entries are included
        full_history_index = None
        for i in range(widget.timeframe_selector.count()):
            if widget.timeframe_selector.itemText(i) == "Full History":
                full_history_index = i
                break
        if full_history_index is not None:
            widget.timeframe_selector.setCurrentIndex(full_history_index)

        # Create one weekday night with 8h sleep (within recommended range)
        today = QDate.currentDate()
        # Find most recent weekday (Mon–Fri) on or before today
        weekday_date = today
        while weekday_date.dayOfWeek() in (6, 7):
            weekday_date = weekday_date.addDays(-1)

        weekday_bedtime = QDateTime(weekday_date, QTime(23, 0))
        weekday_wakeup = QDateTime(weekday_date.addDays(1), QTime(7, 0))
        weekday_duration = QTime(8, 0)  # 8 hours, sufficient
        add_sleep_diary_entry(weekday_date, weekday_bedtime, weekday_wakeup, weekday_duration)

        # Create one weekend night with 6h sleep (insufficient)
        weekend_date = today
        # Find most recent weekend (Sat/Sun) on or before today
        while weekend_date.dayOfWeek() not in (6, 7):
            weekend_date = weekend_date.addDays(-1)

        weekend_bedtime = QDateTime(weekend_date, QTime(23, 0))
        weekend_wakeup = QDateTime(weekend_date.addDays(1), QTime(5, 0))
        weekend_duration = QTime(6, 0)  # 6 hours, insufficient
        add_sleep_diary_entry(weekend_date, weekend_bedtime, weekend_wakeup, weekend_duration)

        # Reload table and stats
        widget.load_table()

        # Weekday stats: bedtime / wakeup should be concrete times, duration 8h 0m
        assert "Weekdays - Average Bedtime:" in widget.weekday_bedtime_label.text()
        assert "Weekdays - Average Wakeup:" in widget.weekday_wakeup_label.text()
        assert "Weekdays - Average Sleep Duration: 8h 0m" in widget.weekday_sleep_duration_label.text()

        # Weekend stats: duration 6h 0m
        assert "Weekends - Average Sleep Duration: 6h 0m" in widget.weekend_sleep_duration_label.text()

        # Overall duration is average of 8h and 6h => 7h
        assert "Overall - Average Sleep Duration: 7h 0m" in widget.overall_sleep_duration_label.text()

        # Streak since last insufficient night should be 1 because the most recent
        # entry in this timeframe is sufficient (8h) and the previous one is insufficient
        assert widget.sufficient_streak_label.text().startswith(
            "Streak since last insufficient night: 1 night"
        )

        # Percentage of day spent sleeping should be ~29.2% for 7h average
        assert widget.percent_of_day_sleep_label.text().startswith(
            "Average % of 24h spent sleeping: "
        )
        assert "29.2%" in widget.percent_of_day_sleep_label.text()
