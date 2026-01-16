"""
GUI tests for PyQt6 widgets.
"""
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from widgets.food_tracker import FoodTracker
from widgets.exercise_tracker import ExerciseTracker
from widgets.goals import Goals


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
