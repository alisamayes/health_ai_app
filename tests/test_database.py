"""
Unit tests for database operations.
"""
import pytest
from database import (
    add_food, get_food_entries, update_food_entry, delete_food_entry, get_all_distinct_foods,
    get_most_common_foods, get_earliest_food_date, get_food_calorie_totals_for_timeframe,
    add_exercise, get_exercise_entries, delete_exercise_entry,
    add_weight, get_current_weight, get_target_weight, get_all_currnet_weight_entries,
    add_weight_loss_timeframe, get_weight_loss_timeframe,
    add_daily_calorie_goal, get_daily_calorie_goal,
    add_pantry_item, get_pantry_items, clear_pantry, delete_pantry_items,
    add_shopping_list_item, get_shopping_list_items, clear_shopping_list, delete_shopping_list_items,
    create_meal_plan_row, get_meal_plan_for_day, update_meal_plan_for_day,
    add_sleep_diary_entry, get_sleep_diary_entries, delete_sleep_diary_entry,
    update_sleep_diary_entry, get_earliest_sleep_diary_date, get_sleep_duration_totals_for_timeframe
)
from PyQt6.QtCore import QDate, QTime, QDateTime


@pytest.mark.unit
class TestFoodOperations:
    """Tests for food-related database operations."""
    
    def test_add_food(self):
        """Test adding a food entry."""
        add_food("Apple", 95, "2024-01-01")
        entries = get_food_entries("2024-01-01")
        assert len(entries) > 0
        assert entries[0][1] == "Apple"  # food name
        assert entries[0][2] == 95  # calories
    
    def test_get_food_entries(self):
        """Test retrieving food entries for a date."""
        add_food("Banana", 105, "2024-01-01")
        entries = get_food_entries("2024-01-01")
        assert any(entry[1] == "Banana" for entry in entries)
    
    def test_update_food_entry(self):
        """Test updating a food entry."""
        add_food("Apple", 95, "2024-01-01")
        entries = get_food_entries("2024-01-01")
        entry_id = entries[0][0]
        
        update_food_entry(entry_id, "Green Apple", 100)
        updated_entries = get_food_entries("2024-01-01")
        updated_entry = next(e for e in updated_entries if e[0] == entry_id)
        assert updated_entry[1] == "Green Apple"
        assert updated_entry[2] == 100
    
    def test_delete_food_entry(self):
        """Test deleting a food entry."""
        add_food("Test Food", 50, "2024-01-01")
        entries = get_food_entries("2024-01-01")
        entry_id = entries[0][0]
        
        delete_food_entry(entry_id)
        remaining_entries = get_food_entries("2024-01-01")
        assert not any(e[0] == entry_id for e in remaining_entries)

    def test_get_all_distinct_foods(self):
        """Test retrieving all distinct foods function which is part of the quick add feature."""
        add_food("Test Food 1", 50, "2024-01-01")
        add_food("Test Food 2", 60, "2024-01-01")
        add_food("Test Food 3", 70, "2024-01-01")
        add_food("Test Food 4", 80, "2024-01-01")
        add_food("Test Food 2", 60, "2024-01-01")
        foods = get_all_distinct_foods()
        assert len(foods) == 4
        # Check Test Food 2 appears only once (as a tuple)
        food_names = [food[0] for food in foods]
        assert food_names.count("Test Food 2") == 1


@pytest.mark.unit
class TestExerciseOperations:
    """Tests for exercise-related database operations."""
    
    def test_add_exercise(self):
        """Test adding an exercise entry."""
        add_exercise("Running", 300, "2024-01-01")
        entries = get_exercise_entries("2024-01-01")
        assert len(entries) > 0
        assert entries[0][1] == "Running"
        assert entries[0][2] == 300
    
    def test_get_exercise_entries(self):
        """Test retrieving exercise entries for a date."""
        add_exercise("Cycling", 250, "2024-01-01")
        entries = get_exercise_entries("2024-01-01")
        assert any(entry[1] == "Cycling" for entry in entries)

    def test_delete_exercise_entry(self):
        """Test removing an exercise entry."""
        add_exercise("Running", 300, "2024-01-01")
        entries = get_exercise_entries("2024-01-01")
        entry_id = entries[0][0]
        delete_exercise_entry(entry_id)
        remaining_entries = get_exercise_entries("2024-01-01")
        assert not any(e[0] == entry_id for e in remaining_entries)


@pytest.mark.unit
class TestGoalsOperations:
    """Tests for goals-related database operations."""
    
    def test_add_weight_current(self):
        """Test adding current weight."""
        from datetime import datetime
        # Use today's date since we're using a clean test database
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Add new weight
        add_weight(70.5, today, "current")
        weight = get_current_weight()
        
        # Should get the weight we just added
        assert weight == 70.5
    
    def test_add_weight_target(self):
        """Test adding target weight."""
        from datetime import datetime
        # Use today's date since we're using a clean test database
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Add new target
        add_weight(65.0, today, "target")
        weight = get_target_weight()
        
        # Should get the target we just added
        assert weight == 65.0
    
    def test_add_daily_calorie_goal(self):
        """Test adding daily calorie goal."""
        from datetime import datetime
        # Use today's date since we're using a clean test database
        today = datetime.now().strftime("%Y-%m-%d")
        
        # First ensure there's a goals row to update by adding a weight entry
        add_weight(70.0, today, "current")
        
        # Add new goal
        add_daily_calorie_goal(2000, today)
        goal = get_daily_calorie_goal()
        
        # Should get the goal we just added
        assert goal == 2000


@pytest.mark.unit
class TestPantryOperations:
    """Tests for pantry-related database operations."""
    
    def test_add_pantry_item(self):
        """Test adding a pantry item."""
        add_pantry_item("Flour", 500)
        items = get_pantry_items()
        assert any(item[1] == "Flour" and item[2] == 500 for item in items)
    
    def test_clear_pantry(self):
        """Test clearing all pantry items."""
        add_pantry_item("Test Item", 100)
        clear_pantry()
        items = get_pantry_items()
        assert len(items) == 0


@pytest.mark.unit
class TestShoppingListOperations:
    """Tests for shopping list operations."""
    
    def test_add_shopping_list_item(self):
        """Test adding a shopping list item."""
        add_shopping_list_item("Milk")
        items = get_shopping_list_items()
        assert any(item[1] == "Milk" for item in items)
    
    def test_clear_shopping_list(self):
        """Test clearing all shopping list items."""
        add_shopping_list_item("Test Item")
        clear_shopping_list()
        items = get_shopping_list_items()
        assert len(items) == 0


@pytest.mark.unit
class TestMealPlanOperations:
    """Tests for meal plan operations."""
    
    def test_create_meal_plan_row(self):
        """Test creating a meal plan row."""
        create_meal_plan_row()
        day = get_meal_plan_for_day("Monday")
        assert day == ""


    def test_update_meal_plan_for_day(self):
        """Test updating a meal plan for a day."""
        food = "Breakfast: Spicy Draconic Nutrition Cube, Dinner: Sweet Draconic Nutrition Cube"
        update_meal_plan_for_day("Tuesday", food)
        assert get_meal_plan_for_day("Tuesday") == food
        assert get_meal_plan_for_day("Monday") == ""


@pytest.mark.unit
class TestFoodOperationsEdgeCases:
    """Edge case tests for food operations."""
    
    def test_get_food_entries_empty_date(self):
        """Test getting entries for a date with no entries."""
        entries = get_food_entries("2024-12-31")
        assert entries == []
    
    def test_get_food_entries_multiple_dates(self):
        """Test that entries are date-specific."""
        add_food("Monday Food", 100, "2024-01-01")
        add_food("Tuesday Food", 200, "2024-01-02")
        
        monday_entries = get_food_entries("2024-01-01")
        tuesday_entries = get_food_entries("2024-01-02")
        
        assert any(e[1] == "Monday Food" for e in monday_entries)
        assert not any(e[1] == "Tuesday Food" for e in monday_entries)
        assert any(e[1] == "Tuesday Food" for e in tuesday_entries)
        assert not any(e[1] == "Monday Food" for e in tuesday_entries)
    
    def test_get_most_common_foods(self):
        """Test getting most common foods."""
        # Add same food multiple times with different calories
        add_food("Apple", 95, "2024-01-01")
        add_food("Apple", 100, "2024-01-02")
        add_food("Apple", 90, "2024-01-03")
        add_food("Banana", 105, "2024-01-01")
        add_food("Banana", 110, "2024-01-02")
        add_food("Orange", 80, "2024-01-01")
        
        common_foods = get_most_common_foods()
        food_names = [food[0] for food in common_foods]
        
        # Apple should be first (appears 3 times)
        assert food_names[0] == "Apple"
        # Should return up to 5 items
        assert len(common_foods) <= 5


@pytest.mark.unit
class TestGoalsOperationsEdgeCases:
    """Edge case tests for goals operations."""
    
    def test_get_current_weight_none(self):
        """Test getting current weight when none exists."""
        weight = get_current_weight()
        assert weight is None
    
    def test_get_target_weight_none(self):
        """Test getting target weight when none exists."""
        weight = get_target_weight()
        assert weight is None
    
    def test_get_daily_calorie_goal_none(self):
        """Test getting calorie goal when none exists."""
        goal = get_daily_calorie_goal()
        assert goal is None
    
    def test_add_weight_loss_timeframe(self):
        """Test adding weight loss timeframe."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Need a goals row first
        add_weight(70.0, today, "current")
        add_weight_loss_timeframe(12.0, today)
        timeframe = get_weight_loss_timeframe()
        assert timeframe == 12.0
    
    def test_get_all_currnet_weight_entries(self):
        """Test getting all weight entries."""
        from datetime import datetime, timedelta
        today = datetime.now()
        
        add_weight(70.0, today.strftime("%Y-%m-%d"), "current")
        add_weight(71.0, (today + timedelta(days=1)).strftime("%Y-%m-%d"), "current")
        add_weight(72.0, (today + timedelta(days=2)).strftime("%Y-%m-%d"), "current")
        
        entries = get_all_currnet_weight_entries()
        assert len(entries) >= 3
        weights = [e[1] for e in entries]
        assert 70.0 in weights
        assert 71.0 in weights
        assert 72.0 in weights


@pytest.mark.unit
class TestPantryOperationsEdgeCases:
    """Edge case tests for pantry operations."""
    
    def test_delete_pantry_items(self):
        """Test deleting specific pantry items."""
        add_pantry_item("Item1", 100)
        add_pantry_item("Item2", 200)
        add_pantry_item("Item3", 300)
        
        items = get_pantry_items()
        item1_id = next(item[0] for item in items if item[1] == "Item1")
        item2_id = next(item[0] for item in items if item[1] == "Item2")
        
        # Create mock QListWidgetItem objects with UserRole data
        from PyQt6.QtWidgets import QListWidgetItem
        from PyQt6.QtCore import Qt
        
        mock_items = [
            type('obj', (object,), {'data': lambda self, role: item1_id if role == Qt.ItemDataRole.UserRole else None})(),
            type('obj', (object,), {'data': lambda self, role: item2_id if role == Qt.ItemDataRole.UserRole else None})(),
        ]
        
        delete_pantry_items(mock_items)
        
        remaining_items = get_pantry_items()
        remaining_names = [item[1] for item in remaining_items]
        assert "Item1" not in remaining_names
        assert "Item2" not in remaining_names
        assert "Item3" in remaining_names
    
    def test_get_pantry_items_empty(self):
        """Test getting items from empty pantry."""
        clear_pantry()
        items = get_pantry_items()
        assert items == []


@pytest.mark.unit
class TestShoppingListOperationsEdgeCases:
    """Edge case tests for shopping list operations."""
    
    def test_delete_shopping_list_items(self):
        """Test deleting specific shopping list items."""
        add_shopping_list_item("Item1")
        add_shopping_list_item("Item2")
        add_shopping_list_item("Item3")
        
        items = get_shopping_list_items()
        item1_id = next(item[0] for item in items if item[1] == "Item1")
        item2_id = next(item[0] for item in items if item[1] == "Item2")
        
        # Create mock QListWidgetItem objects
        from PyQt6.QtCore import Qt
        
        mock_items = [
            type('obj', (object,), {'data': lambda self, role: item1_id if role == Qt.ItemDataRole.UserRole else None})(),
            type('obj', (object,), {'data': lambda self, role: item2_id if role == Qt.ItemDataRole.UserRole else None})(),
        ]
        
        delete_shopping_list_items(mock_items)
        
        remaining_items = get_shopping_list_items()
        remaining_names = [item[1] for item in remaining_items]
        assert "Item1" not in remaining_names
        assert "Item2" not in remaining_names
        assert "Item3" in remaining_names
    
    def test_get_shopping_list_items_empty(self):
        """Test getting items from empty shopping list."""
        clear_shopping_list()
        items = get_shopping_list_items()
        assert items == []


@pytest.mark.unit
class TestTimeframeOperations:
    """Tests for timeframe and date range operations."""
    
    def test_get_earliest_food_date(self):
        """Test getting earliest food entry date."""
        from datetime import datetime, timedelta
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        add_food("Old Food", 100, yesterday.strftime("%Y-%m-%d"))
        add_food("New Food", 200, today.strftime("%Y-%m-%d"))
        
        earliest = get_earliest_food_date()
        assert earliest == yesterday.strftime("%Y-%m-%d")
    
    def test_get_earliest_food_date_empty(self):
        """Test getting earliest date with no entries."""
        earliest = get_earliest_food_date()
        assert earliest is None
    
    def test_get_food_calorie_totals_for_timeframe(self):
        """Test getting calorie totals for a date range."""
        from datetime import datetime, timedelta
        start = datetime.now() - timedelta(days=5)
        end = datetime.now() - timedelta(days=1)
        
        add_food("Food1", 100, start.strftime("%Y-%m-%d"))
        add_food("Food2", 200, end.strftime("%Y-%m-%d"))
        add_food("Food3", 150, (start + timedelta(days=2)).strftime("%Y-%m-%d"))
        
        totals = get_food_calorie_totals_for_timeframe(
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d")
        )
        
        # Should have entries for the dates in range
        assert len(totals) >= 3
        total_calories = sum(cal for date, cal in totals)
        assert total_calories == 450  # 100 + 200 + 150


@pytest.mark.unit
class TestSleepDiaryOperations:
    """Tests for sleep diary database operations."""
    
    def test_add_sleep_diary_entry(self):
        """Test adding a sleep diary entry."""
        sleep_date = QDate(2024, 1, 15)
        bedtime = QDateTime(QDate(2024, 1, 15), QTime(22, 30))
        wakeup = QDateTime(QDate(2024, 1, 16), QTime(7, 0))
        sleep_duration = QTime(8, 30)  # 8 hours 30 minutes
        
        add_sleep_diary_entry(sleep_date, bedtime, wakeup, sleep_duration)
        
        start_date = QDate(2024, 1, 15)
        end_date = QDate(2024, 1, 16)
        entries = get_sleep_diary_entries(start_date, end_date)
        
        assert len(entries) > 0
        assert entries[0][1] == "2024-01-15"  # sleep_date
        assert entries[0][2] == "22:30"  # bedtime
        assert entries[0][3] == "07:00"  # wakeup
        assert entries[0][4] == "08:30"  # sleep_duration
    
    def test_get_sleep_diary_entries(self):
        """Test retrieving sleep diary entries for a date range."""
        sleep_date1 = QDate(2024, 1, 10)
        bedtime1 = QDateTime(QDate(2024, 1, 10), QTime(23, 0))
        wakeup1 = QDateTime(QDate(2024, 1, 11), QTime(8, 0))
        sleep_duration1 = QTime(9, 0)
        
        sleep_date2 = QDate(2024, 1, 11)
        bedtime2 = QDateTime(QDate(2024, 1, 11), QTime(22, 0))
        wakeup2 = QDateTime(QDate(2024, 1, 12), QTime(6, 30))
        sleep_duration2 = QTime(8, 30)
        
        add_sleep_diary_entry(sleep_date1, bedtime1, wakeup1, sleep_duration1)
        add_sleep_diary_entry(sleep_date2, bedtime2, wakeup2, sleep_duration2)
        
        start_date = QDate(2024, 1, 10)
        end_date = QDate(2024, 1, 12)
        entries = get_sleep_diary_entries(start_date, end_date)
        
        assert len(entries) >= 2
        dates = [entry[1] for entry in entries]
        assert "2024-01-10" in dates
        assert "2024-01-11" in dates
    
    def test_delete_sleep_diary_entry(self):
        """Test deleting a sleep diary entry."""
        sleep_date = QDate(2024, 1, 20)
        bedtime = QDateTime(QDate(2024, 1, 20), QTime(22, 0))
        wakeup = QDateTime(QDate(2024, 1, 21), QTime(7, 0))
        sleep_duration = QTime(9, 0)
        
        add_sleep_diary_entry(sleep_date, bedtime, wakeup, sleep_duration)
        
        start_date = QDate(2024, 1, 20)
        end_date = QDate(2024, 1, 21)
        entries = get_sleep_diary_entries(start_date, end_date)
        entry_id = entries[0][0]
        
        delete_sleep_diary_entry(entry_id)
        
        remaining_entries = get_sleep_diary_entries(start_date, end_date)
        assert not any(e[0] == entry_id for e in remaining_entries)
    
    def test_update_sleep_diary_entry(self):
        """Test updating a sleep diary entry."""
        sleep_date = QDate(2024, 1, 25)
        bedtime = QDateTime(QDate(2024, 1, 25), QTime(23, 0))
        wakeup = QDateTime(QDate(2024, 1, 26), QTime(8, 0))
        sleep_duration = QTime(9, 0)
        
        add_sleep_diary_entry(sleep_date, bedtime, wakeup, sleep_duration)
        
        start_date = QDate(2024, 1, 25)
        end_date = QDate(2024, 1, 26)
        entries = get_sleep_diary_entries(start_date, end_date)
        entry_id = entries[0][0]
        
        # Update to new times
        new_bedtime = QDateTime(QDate(2024, 1, 25), QTime(22, 30))
        new_wakeup = QDateTime(QDate(2024, 1, 26), QTime(7, 30))
        new_duration = QTime(9, 0)
        
        update_sleep_diary_entry(entry_id, sleep_date, new_bedtime, new_wakeup, new_duration)
        
        updated_entries = get_sleep_diary_entries(start_date, end_date)
        updated_entry = next(e for e in updated_entries if e[0] == entry_id)
        assert updated_entry[2] == "22:30"  # bedtime
        assert updated_entry[3] == "07:30"  # wakeup
    
    def test_get_earliest_sleep_diary_date(self):
        """Test getting the earliest sleep diary date."""
        from datetime import datetime, timedelta
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        sleep_date_old = QDate.fromString(yesterday.strftime("%Y-%m-%d"), "yyyy-MM-dd")
        sleep_date_new = QDate.fromString(today.strftime("%Y-%m-%d"), "yyyy-MM-dd")
        
        bedtime_old = QDateTime(sleep_date_old, QTime(22, 0))
        wakeup_old = QDateTime(sleep_date_old.addDays(1), QTime(7, 0))
        sleep_duration_old = QTime(9, 0)
        
        bedtime_new = QDateTime(sleep_date_new, QTime(23, 0))
        wakeup_new = QDateTime(sleep_date_new.addDays(1), QTime(8, 0))
        sleep_duration_new = QTime(9, 0)
        
        add_sleep_diary_entry(sleep_date_old, bedtime_old, wakeup_old, sleep_duration_old)
        add_sleep_diary_entry(sleep_date_new, bedtime_new, wakeup_new, sleep_duration_new)
        
        earliest = get_earliest_sleep_diary_date()
        assert earliest is not None
        assert earliest.toString("yyyy-MM-dd") == yesterday.strftime("%Y-%m-%d")
    
    def test_get_earliest_sleep_diary_date_empty(self):
        """Test getting earliest date when no entries exist."""
        earliest = get_earliest_sleep_diary_date()
        assert earliest is None
    
    def test_get_sleep_duration_totals_for_timeframe(self):
        """Test getting sleep duration totals for a timeframe."""
        from datetime import datetime, timedelta
        start = datetime.now() - timedelta(days=5)
        end = datetime.now() - timedelta(days=1)
        
        # Add entries for different dates
        sleep_date1 = QDate.fromString(start.strftime("%Y-%m-%d"), "yyyy-MM-dd")
        bedtime1 = QDateTime(sleep_date1, QTime(22, 0))
        wakeup1 = QDateTime(sleep_date1.addDays(1), QTime(7, 0))
        sleep_duration1 = QTime(9, 0)  # 9 hours
        
        sleep_date2 = QDate.fromString(end.strftime("%Y-%m-%d"), "yyyy-MM-dd")
        bedtime2 = QDateTime(sleep_date2, QTime(23, 0))
        wakeup2 = QDateTime(sleep_date2.addDays(1), QTime(8, 0))
        sleep_duration2 = QTime(9, 0)  # 9 hours
        
        add_sleep_diary_entry(sleep_date1, bedtime1, wakeup1, sleep_duration1)
        add_sleep_diary_entry(sleep_date2, bedtime2, wakeup2, sleep_duration2)
        
        totals = get_sleep_duration_totals_for_timeframe(
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d")
        )
        
        # Should have entries for the dates in range
        assert len(totals) >= 2
        # Check that durations are in hours (float)
        for date_str, duration_hours in totals:
            assert isinstance(duration_hours, float)
            assert duration_hours > 0


@pytest.mark.unit
class TestSleepDiaryOperationsEdgeCases:
    """Edge case tests for sleep diary operations."""
    
    def test_get_sleep_diary_entries_empty_range(self):
        """Test getting entries for a date range with no entries."""
        start_date = QDate(2024, 12, 31)
        end_date = QDate(2024, 12, 31)
        entries = get_sleep_diary_entries(start_date, end_date)
        assert entries == []
    
    def test_get_sleep_diary_entries_date_specific(self):
        """Test that entries are date-specific."""
        sleep_date1 = QDate(2024, 2, 1)
        bedtime1 = QDateTime(sleep_date1, QTime(22, 0))
        wakeup1 = QDateTime(sleep_date1.addDays(1), QTime(7, 0))
        sleep_duration1 = QTime(9, 0)
        
        sleep_date2 = QDate(2024, 2, 2)
        bedtime2 = QDateTime(sleep_date2, QTime(23, 0))
        wakeup2 = QDateTime(sleep_date2.addDays(1), QTime(8, 0))
        sleep_duration2 = QTime(9, 0)
        
        add_sleep_diary_entry(sleep_date1, bedtime1, wakeup1, sleep_duration1)
        add_sleep_diary_entry(sleep_date2, bedtime2, wakeup2, sleep_duration2)
        
        # Get entries for first date only
        entries1 = get_sleep_diary_entries(sleep_date1, sleep_date1)
        entries2 = get_sleep_diary_entries(sleep_date2, sleep_date2)
        
        assert len(entries1) >= 1
        assert len(entries2) >= 1
        assert entries1[0][1] == "2024-02-01"
        assert entries2[0][1] == "2024-02-02"
    
    def test_sleep_diary_multiple_entries_same_date(self):
        """Test handling multiple entries for the same date (edge case)."""
        sleep_date = QDate(2024, 2, 10)
        
        # Add two entries for the same date
        bedtime1 = QDateTime(sleep_date, QTime(22, 0))
        wakeup1 = QDateTime(sleep_date.addDays(1), QTime(7, 0))
        sleep_duration1 = QTime(9, 0)
        
        bedtime2 = QDateTime(sleep_date, QTime(23, 0))
        wakeup2 = QDateTime(sleep_date.addDays(1), QTime(8, 0))
        sleep_duration2 = QTime(9, 0)
        
        add_sleep_diary_entry(sleep_date, bedtime1, wakeup1, sleep_duration1)
        add_sleep_diary_entry(sleep_date, bedtime2, wakeup2, sleep_duration2)
        
        entries = get_sleep_diary_entries(sleep_date, sleep_date)
        assert len(entries) >= 2
        
        # Test that get_sleep_duration_totals_for_timeframe averages them
        totals = get_sleep_duration_totals_for_timeframe(
            sleep_date.toString("yyyy-MM-dd"),
            sleep_date.toString("yyyy-MM-dd")
        )
        # Should have one entry with averaged duration
        assert len(totals) == 1
        date_str, avg_hours = totals[0]
        assert date_str == "2024-02-10"
        assert avg_hours == 9.0  # Both entries are 9 hours
    
    def test_sleep_diary_late_bedtime(self):
        """Test handling late bedtime (after midnight)."""
        sleep_date = QDate(2024, 2, 15)
        # Bedtime at 1 AM (next day)
        bedtime = QDateTime(sleep_date.addDays(1), QTime(1, 0))
        wakeup = QDateTime(sleep_date.addDays(1), QTime(9, 0))
        sleep_duration = QTime(8, 0)
        
        add_sleep_diary_entry(sleep_date, bedtime, wakeup, sleep_duration)
        
        entries = get_sleep_diary_entries(sleep_date, sleep_date)
        assert len(entries) >= 1
        # Bedtime should be stored as "01:00"
        assert entries[0][2] == "01:00"
    
    def test_sleep_diary_short_duration(self):
        """Test handling short sleep duration (less than recommended)."""
        sleep_date = QDate(2024, 2, 20)
        bedtime = QDateTime(sleep_date, QTime(23, 0))
        wakeup = QDateTime(sleep_date.addDays(1), QTime(5, 0))
        sleep_duration = QTime(6, 0)  # 6 hours (less than recommended 7-9)
        
        add_sleep_diary_entry(sleep_date, bedtime, wakeup, sleep_duration)
        
        entries = get_sleep_diary_entries(sleep_date, sleep_date)
        assert len(entries) >= 1
        assert entries[0][4] == "06:00"
    
    def test_sleep_diary_long_duration(self):
        """Test handling long sleep duration (more than recommended)."""
        sleep_date = QDate(2024, 2, 25)
        bedtime = QDateTime(sleep_date, QTime(22, 0))
        wakeup = QDateTime(sleep_date.addDays(1), QTime(11, 0))
        sleep_duration = QTime(13, 0)  # 13 hours (more than recommended 7-9)
        
        add_sleep_diary_entry(sleep_date, bedtime, wakeup, sleep_duration)
        
        entries = get_sleep_diary_entries(sleep_date, sleep_date)
        assert len(entries) >= 1
        assert entries[0][4] == "13:00"