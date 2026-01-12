"""
Settings widget for the Health App.
"""
import sys
import os
import shutil
from datetime import datetime
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QPushButton, QFileDialog, QMessageBox
)

class Settings(QWidget):
    """
    This class creates the settings page of the app.
    It contains a checkbox for each setting and a button to test the desktop notifications.
    The settings are saved to the registry on Windows.
    """
    def __init__(self):
        """
        Initialize the Settings widget.
        Sets up checkboxes for various settings, connects them to save handlers,
        and loads previously saved settings from persistent storage.
        """
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Initialize QSettings for persistent settings
        self.settings = QSettings("MindfulMauschen", "HealthApp")

        
        # Toggle checkboxes section
        self.startup_checkbox = QCheckBox("Enable app auto launch on Windows startup")
        self.food_ai_checkbox = QCheckBox("Enable AI assisted calorie suggestions when inputting food into the tracker")
        self.exercise_ai_checkbox = QCheckBox("Enable AI assisted calorie suggestions when inputting exercise into the tracker")
        self.meal_plan_ai_checkbox = QCheckBox("Enable AI assisted meal plan suggestions")
        self.silent_notif_checkbox = QCheckBox("Make desktop notifications silent")
        
        # Desktop notification test button
        self.desktop_notif = QPushButton("Desktop Notification Test")

        # Button to allow user to import a database to use for the app
        self.import_database_button = QPushButton("Import Database")
        self.import_database_button.clicked.connect(self.import_database)
        
        # Connect checkbox state changes to save settings (except startup which is handled separately)
        self.food_ai_checkbox.stateChanged.connect(self.save_settings)
        self.exercise_ai_checkbox.stateChanged.connect(self.save_settings)
        self.meal_plan_ai_checkbox.stateChanged.connect(self.save_settings)
        self.silent_notif_checkbox.stateChanged.connect(self.save_settings)
        
        # Add widgets to layout
        self.layout.addWidget(self.startup_checkbox)
        self.layout.addWidget(self.food_ai_checkbox)
        self.layout.addWidget(self.exercise_ai_checkbox)
        self.layout.addWidget(self.meal_plan_ai_checkbox)
        self.layout.addWidget(self.silent_notif_checkbox)
        self.layout.addWidget(self.desktop_notif)
        self.layout.addWidget(self.import_database_button)

        # Load saved settings
        self.load_settings()
    
    def get_app_path(self):
        """
        Get the path to the application executable or script.
        
        Returns:
            str: The path to the executable if running as compiled app,
                 or the command to run the Python script if running as script.
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as Python script
            return f'"{sys.executable}" "{os.path.abspath(__file__)}"'
    
    def is_startup_enabled(self, startup_settings):
        """
        Check if the app is set to run on Windows startup.
        
        Args:
            startup_settings (QSettings): The Windows startup registry settings object.
        
        Returns:
            bool: True if the app is in the startup registry, False otherwise.
        """
        app_name = "MindfulMauschen"
        return startup_settings.contains(app_name)
    
    def toggle_startup(self, state, startup_settings):
        """
        Enable or disable app launch on Windows startup.
        
        Args:
            state (int): The checkbox state (Qt.CheckState.Checked.value to enable).
            startup_settings (QSettings): The Windows startup registry settings object.
        """
        app_name = "MindfulMauschen"
        
        if state == Qt.CheckState.Checked.value:
            # Add to startup
            app_path = self.get_app_path()
            startup_settings.setValue(app_name, app_path)
            startup_settings.sync()
        else:
            # Remove from startup
            startup_settings.remove(app_name)
            startup_settings.sync()
    
    def load_settings(self):
        """
        Load saved settings and apply them to checkboxes.
        Temporarily blocks signals during loading to prevent save_settings
        from being called multiple times, ensuring all checkbox states are set correctly.
        """
        # Originally was having issues where toggling multiple checkboxes at once would only save one of  them
        # As such added in block signals while loading to prevent save_settings from being called and ensuring all checkbox states are saved correctly
        self.startup_checkbox.blockSignals(True)
        self.food_ai_checkbox.blockSignals(True)
        self.exercise_ai_checkbox.blockSignals(True)
        self.silent_notif_checkbox.blockSignals(True)
        self.meal_plan_ai_checkbox.blockSignals(True)
        
        # Load checkbox states (default to False if not found)
        self.startup_checkbox.setChecked(
            self.settings.value("startup_enabled", False, type=bool)
        )
        self.food_ai_checkbox.setChecked(
            self.settings.value("food_ai_enabled", False, type=bool)
        )
        self.exercise_ai_checkbox.setChecked(
            self.settings.value("exercise_ai_enabled", False, type=bool)
        )
        self.silent_notif_checkbox.setChecked(
            self.settings.value("silent_notif_enabled", False, type=bool)
        )
        self.meal_plan_ai_checkbox.setChecked(
            self.settings.value("meal_plan_ai_enabled", False, type=bool)
        )
        
        # Unblock signals after loading
        self.startup_checkbox.blockSignals(False)
        self.food_ai_checkbox.blockSignals(False)
        self.exercise_ai_checkbox.blockSignals(False)
        self.silent_notif_checkbox.blockSignals(False)
        self.meal_plan_ai_checkbox.blockSignals(False)
    
    def save_settings(self):
        """
        Save current checkbox states to persistent storage.
        Saves food_ai_enabled, exercise_ai_enabled, silent_notif_enabled,
        and meal_plan_ai_enabled settings. Note: startup_enabled is saved separately.
        """
        self.settings.setValue("food_ai_enabled", self.food_ai_checkbox.isChecked())
        self.settings.setValue("exercise_ai_enabled", self.exercise_ai_checkbox.isChecked())
        self.settings.setValue("silent_notif_enabled", self.silent_notif_checkbox.isChecked())
        self.settings.setValue("meal_plan_ai_enabled", self.meal_plan_ai_checkbox.isChecked())
        self.settings.sync()
    
    def save_startup_setting(self):
        """
        Save startup checkbox state separately.
        This is called separately from save_settings because startup requires
        special handling with the Windows registry.
        """
        self.settings.setValue("startup_enabled", self.startup_checkbox.isChecked())
        self.settings.sync()

    def import_database(self):
        """
        Allow the user to import another instance of the database to use for the app.
        While the databse persists between instances, new versions from the exe produced by pyinstaller will not be able to use the old database.
        This function allows the user to import one from file, useful for dev testing and perhaps other use cases.
        """
        # File explorer for user to find the database file to import (might need to make an export for exe users who dont have the loose source files)
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Database", "", "Database Files (*.db)")
        if file_path:
            try:
                # Backup existing database if it exists
                if os.path.exists("health_app.db"):
                    backup_path = f"health_app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy("health_app.db", backup_path)
                
                # Copy the imported database file to the app's directory
                shutil.copy(file_path, "health_app.db")
                
                QMessageBox.information(
                    self,
                    "Database Imported",
                    "Database imported successfully!\n\nPlease restart the application to see the changes."
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Import Error",
                    f"Failed to import database:\n{str(e)}"
                )

