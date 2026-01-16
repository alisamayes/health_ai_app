"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest
import sqlite3
import os
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from database import use_db, init_db, set_db_path, get_db_path, create_meal_plan_row


# Ensure QApplication exists for GUI tests
@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Cleanup handled by pytest-qt


@pytest.fixture(autouse=True)
def test_db(monkeypatch):
    """
    Create a temporary test database and switch all database operations to use it.
    This fixture runs automatically for all tests (autouse=True).
    Ensures tests don't affect the main application database.
    """
    # Create a temporary database file
    fd, db_path = tempfile.mkstemp(suffix='.db', prefix='test_health_app_')
    os.close(fd)
    
    # Store the original database path
    original_db_path = get_db_path()
    
    # Switch to test database
    set_db_path(db_path)
    
    # Initialize the test database with all tables
    init_db()
    
    # Create initial meal_plan row
    create_meal_plan_row()
    
    yield db_path
    
    # Restore original database path
    set_db_path(original_db_path)
    
    # Cleanup: remove temporary database
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except Exception:
            pass  # Ignore cleanup errors


@pytest.fixture
def sample_food_data():
    """Sample food data for testing."""
    return [
        ("Apple", 95, "2024-01-01"),
        ("Banana", 105, "2024-01-01"),
        ("Chicken Breast", 231, "2024-01-02"),
    ]


@pytest.fixture
def sample_exercise_data():
    """Sample exercise data for testing."""
    return [
        ("Running", 300, "2024-01-01"),
        ("Cycling", 250, "2024-01-01"),
        ("Swimming", 400, "2024-01-02"),
    ]
