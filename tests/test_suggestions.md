# Suggested Additional Tests

## Database Tests (test_database.py)

### Food Operations - Remaining:
1. **test_add_food_negative_calories** - Test handling of negative calories (edge case - should it be allowed?)
2. **test_add_food_very_long_name** - Test with very long food names (edge case)

### Exercise Operations - Remaining:
1. **test_add_exercise_negative_calories** - Test negative calories handling

### Goals Operations - Remaining:
1. **test_get_weight_loss_timeframe** - Test retrieving weight loss timeframe (partially covered via add test)
2. **test_add_weight_multiple_entries_same_date** - Test multiple weight entries on same date (should get most recent)
3. **test_add_weight_negative_value** - Test negative weight (edge case)
4. **test_add_weight_zero_value** - Test zero weight (edge case)
5. **test_add_weight_very_large_value** - Test very large weight values

### Pantry Operations - Remaining:
1. **test_add_pantry_item_negative_weight** - Negative weight handling

### Meal Plan Operations - Remaining:
1. **test_update_meal_plan_for_day_long_text** - Test with very long meal plan text

### Timeframe/Date Range Operations - Remaining:
1. **test_timeframe_invalid_dates** - Test with invalid date formats
2. **test_timeframe_start_after_end** - Test when start date is after end date

### Integration Tests:
1. **test_food_exercise_workflow** - Add food, add exercise, verify totals
2. **test_weight_goal_workflow** - Add current weight, add target, add calorie goal, verify all
3. **test_pantry_shopping_workflow** - Add pantry items, generate shopping list, verify
4. **test_meal_plan_week_workflow** - Create meal plan, update all days, verify all days

## Widget Tests (test_widgets.py)

### FoodTracker Widget - Remaining:
1. **test_food_tracker_add_entry_dialog** - Test add entry dialog opens
2. **test_food_tracker_delete_entry** - Test deleting selected entries
3. **test_food_tracker_edit_entry** - Test editing an entry
4. **test_food_tracker_keyboard_delete** - Test Delete key functionality
5. **test_food_tracker_empty_date** - Test displaying empty date

### ExerciseTracker Widget - Remaining:
1. **test_exercise_tracker_add_entry** - Test adding entry
2. **test_exercise_tracker_delete_entry** - Test deletion

### Goals Widget - Remaining:
1. **test_goals_load_current_weight** - Test loading current weight
2. **test_goals_load_target_weight** - Test loading target weight
3. **test_goals_input_current_weight** - Test inputting current weight
4. **test_goals_input_target_weight** - Test inputting target weight
5. **test_goals_calculate_calorie_goal** - Test calorie goal calculation
6. **test_goals_graph_display** - Test graph rendering

### DayWidget Widget:
1. **test_day_widget_load_from_database** - Test loading meal plan from DB
2. **test_day_widget_save_to_database** - Test saving changes
3. **test_day_widget_empty_database** - Test with empty database
4. **test_day_widget_ai_popup** - Test AI meal plan popup

## Utility Tests (test_utils.py)

1. **test_ai_worker_very_long_prompt** - Test with very long prompt
2. **test_ai_worker_timeout** - Test timeout handling
3. **test_planner_options_dialog** - Test the options dialog (if testable)

## Edge Cases & Error Handling

1. **test_database_connection_error** - Test handling database connection failures
2. **test_invalid_date_formats** - Test various invalid date formats
3. **test_sql_injection_prevention** - Test that user input is properly sanitized
4. **test_very_large_numbers** - Test with very large calorie/weight values
5. **test_concurrent_operations** - Test multiple operations happening simultaneously
