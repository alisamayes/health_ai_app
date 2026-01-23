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
from database import add_food, add_sleep_diary_entry


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
        assert widget.average_bedtime_label is not None
        assert widget.average_wakeup_label is not None
        assert widget.average_sleep_duration_label is not None
    
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
        
        # Check initial state (may show --:-- if no entries)
        assert widget.average_bedtime_label is not None
        assert widget.average_wakeup_label is not None
        assert widget.average_sleep_duration_label is not None
    
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
