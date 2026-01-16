# Testing Guide

This directory contains tests for the Health App.

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_database.py
```

### Run tests with coverage report
```bash
pytest --cov=. --cov-report=html
```

### Run only unit tests (fast)
```bash
pytest -m unit
```

### Run only GUI tests
```bash
pytest -m gui
```

### Run only integration tests
```bash
pytest -m integration
```

## Test Structure

- `test_database.py` - Tests for database operations
- `test_widgets.py` - Tests for PyQt6 widgets (GUI)
- `test_utils.py` - Tests for utility functions
- `conftest.py` - Shared fixtures and configuration

## Test Database Isolation

**Important**: All tests automatically use a temporary test database and **never affect your main application database**. 

- Each test gets a fresh, empty test database
- The test database is automatically created before each test
- The test database is automatically deleted after each test
- Your main `health_app.db` file remains completely untouched

This is handled by the `test_db` fixture in `conftest.py` which runs automatically for all tests (`autouse=True`).

## Writing New Tests

1. Create a new test file: `test_<module_name>.py`
2. Import pytest and necessary modules
3. Use fixtures from `conftest.py` when needed
4. Mark tests appropriately:
   - `@pytest.mark.unit` - Fast unit tests
   - `@pytest.mark.gui` - GUI tests requiring PyQt6
   - `@pytest.mark.integration` - Integration tests
   - `@pytest.mark.slow` - Slow running tests

## Example Test

```python
import pytest
from database import add_food, get_food_entries

@pytest.mark.unit
def test_add_food():
    """Test adding a food entry."""
    add_food("Apple", 95, "2024-01-01")
    entries = get_food_entries("2024-01-01")
    assert len(entries) > 0
    assert entries[0][1] == "Apple"
```

## Coverage

Coverage reports are generated in HTML format. Open `htmlcov/index.html` in a browser to view detailed coverage information.
