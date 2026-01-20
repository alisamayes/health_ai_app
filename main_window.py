"""
Main window for the Health App.
Contains the HealthApp class that creates and manages the main application window.
"""
import os
from datetime import datetime, timedelta
from winotify import Notification, audio
from PyQt6.QtCore import QTimer, QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QSystemTrayIcon
from widgets import (
    HomePage, FoodTracker, ExerciseTracker, Graphs, Goals,
    MealPlan, Pantry, SleepDiary, ChatBot, Settings
)
from database import check_weekly_weight_entry
from config import (
    white, background_dark_gray, border_gray, button_active_light_gray,
    hover_gray, hover_light_green, active_dark_green
)


class HealthApp(QMainWindow):
    """
    This class creates the main window of the app.
    It contains the tabs for the different pages of the app.
    It also contains the startup settings for the app.
    """
    def __init__(self):
        """
        Initialize the HealthApp main window.
        Sets up the window title, geometry, icon, styling, tabs, system tray icon,
        and timers for weight reminders. Connects settings to update other widgets.
        """
        super().__init__()
        # Initialize QSettings for app preferences
        self.settings = QSettings("MindfulMauschen", "HealthApp")
        # Windows startup registry settings
        self.startup_settings = QSettings(
            "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            QSettings.Format.NativeFormat
        )
        self.setWindowTitle("Health Tracker App")
        self.setGeometry(300, 300, 1000, 600)
        # Prefer an .ico for Windows taskbar; fallback to PNG if .ico not present
        icon_path_ico = os.path.join("assets", "legnedary_astrid_boop_upscale.ico")
        icon_path_png = os.path.join("assets", "legnedary_astrid_boop_upscale.png")
        window_icon = QIcon(icon_path_ico) if os.path.exists(icon_path_ico) else QIcon(icon_path_png)
        self.setWindowIcon(window_icon)
        
        # Apply dark theme styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {background_dark_gray};
                color: {white};
            }}
            QTabWidget::pane {{
                border: 1px solid {border_gray};
                background-color: {background_dark_gray};
                border-radius: 8px;
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
            QTabBar::tab {{
                background-color: {border_gray};
                color: {white};
                padding: 8px 16px;
                margin: 2px;
                border-radius: 6px;
                border: none;
            }}
            QTabBar::tab:selected {{
                background-color: {button_active_light_gray};
            }}
            QTabBar::tab:hover {{
                background-color: {hover_gray};
            }}
            QPushButton {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton#navigationBtn {{
                padding: 2px 6px;
                min-width: 0px; /* smaller padding for  the < and > buttons which were getting cut off due to not enough space */
            }}
            QPushButton:hover {{
                background-color: {hover_light_green};
            }}
            QPushButton:pressed {{
                background-color: {active_dark_green};
            }}
            QLineEdit {{
                background-color: {background_dark_gray};
                color: {white};
                border: 2px solid {border_gray};
                padding: 8px;
                border-radius: 6px;
            }}
            QLineEdit:focus {{
                border-color: {active_dark_green};
            }}
            QDateEdit {{
                background-color: {border_gray};
                color: {white};
                border: 2px solid {border_gray};
                padding: 8px;
                border-radius: 6px;
            }}
            QDateEdit:focus {{
                border-color: {active_dark_green};
            }}
            QTableWidget {{
                background-color: {background_dark_gray};
                color: {white};
                border: 2px solid {border_gray};
                border-radius: 8px;
                gridline-color: {border_gray};
                selection-background-color: {active_dark_green};
                alternate-background-color: {background_dark_gray};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {border_gray};
                background-color: {background_dark_gray};
                color: {white};
            }}
            QTableWidget::item:selected {{
                background-color: {active_dark_green};
                color: {white};
            }}
            QTableWidget::item:alternate {{
                background-color: {background_dark_gray};
            }}
            QHeaderView {{
                background-color: {border_gray};
                color: {white};
            }}
            QHeaderView::section {{
                background-color: {border_gray} !important;
                color: {white} !important;
                padding: 8px;
                border: none;
                font-weight: bold;
                border-radius: 0px;
            }}
            QHeaderView::section:horizontal {{
                border-right: 1px solid {button_active_light_gray};
                background-color: {border_gray} !important;
                color: {white} !important;
            }}
            QHeaderView::section:vertical {{
                border-bottom: 1px solid {button_active_light_gray};
                background-color: {border_gray} !important;
                color: {white} !important;
            }}
            QTableCornerButton::section {{
                background-color: {border_gray} !important;
                border: none;
            }}
            QLabel {{
                color: {white};
            }}
            QComboBox {{
                background-color: {border_gray};
                color: {white};
                border: 2px solid transparent;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QComboBox:hover {{ 
                background-color: {border_gray};
                border-color: {hover_light_green};
            }}
            Figure {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QInputDialog {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QMessageBox {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QCheckBox {{
                color: {white};
                background-color: {background_dark_gray};
            }}
            QcheckBox:indicator:checked {{
                color: {white};
                background-color: {background_dark_gray};
            }}
            QLabel#headerLabel, QPushButton#headerLabel {{
                color: {white};
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                background-color: {border_gray};
                border-radius: 6px;
                margin-bottom: 4px;
                max-height: 20px;
                text-align: center;
            }}
            QTextEdit {{
                color: {white};
                background-color: {background_dark_gray};
                border: 1px solid {border_gray};
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }}
            QToolButton {{
                background-color: {border_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QToolButton:checked {{
                background: {active_dark_green};
                border-color: {border_gray};
            }}
            QToolButton:hover {{
                background-color: {hover_light_green};
                border-color: {border_gray};
            }}
            QDialog {{
                background-color: {background_dark_gray};
                color: {white};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QListWidget {{
                background-color: {background_dark_gray};
                color: {white};
                border: 2px solid {border_gray};
                border-radius: 6px;
            }}
            QListWidget::item {{
                padding: 8px;
            }}
            QScrollBar:vertical {{
                background: {background_dark_gray};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {border_gray};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {hover_gray};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background-color: none;
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background-color: {background_dark_gray};
                height: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {border_gray};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {hover_gray};
            }}
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {{
                background-color: none;
                width: 0px;
            }}
            QSplitter::handle {{
                background-color: {border_gray};
                border: none;
                padding: 2px;
                border-radius: 4px;
            }}
            QTimeEdit {{
                background-color: {border_gray};
                color: {white};
                border: 2px solid {border_gray};
                padding: 8px;
                border-radius: 6px;
            }}
            QTimeEdit:focus {{
                border-color: {active_dark_green};
            }}
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create and then add tabs to the tab widget
        self.home_page = HomePage()
        self.food_tracker = FoodTracker()
        self.exercise_tracker = ExerciseTracker()
        self.sleep_diary = SleepDiary()
        self.graphs = Graphs()
        self.goals = Goals()
        self.meal_plan = MealPlan()
        self.pantry = Pantry()
        self.chat_bot = ChatBot()
        self.settings = Settings()
        self.tabs.addTab(self.home_page, "Home")
        self.tabs.addTab(self.food_tracker, "Food Tracker")
        self.tabs.addTab(self.exercise_tracker, "Exercise Tracker")
        self.tabs.addTab(self.sleep_diary, "Sleep Diary")
        self.tabs.addTab(self.graphs, "Graphs")
        self.tabs.addTab(self.goals, "Goals")
        self.tabs.addTab(self.meal_plan, "Meal Plans")
        self.tabs.addTab(self.pantry, "Pantry")
        self.tabs.addTab(self.chat_bot, "Chat Bot")
        self.tabs.addTab(self.settings, "Settings")
        
        # Connect meal plan AI checkbox to update MealPlan button states
        self.settings.meal_plan_ai_checkbox.stateChanged.connect(self.meal_plan.update_header_buttons_state)

        # Setup system tray icon for desktop notifications
        icon_path_ico = os.path.join("assets", "legnedary_astrid_boop_upscale.ico")
        icon_path_png = os.path.join("assets", "legnedary_astrid_boop_upscale.png")
        tray_icon = QIcon(icon_path_ico) if os.path.exists(icon_path_ico) else QIcon(icon_path_png)
        self.tray = QSystemTrayIcon(tray_icon, self)
        self.tray.setVisible(True)
        self.tray.setToolTip("Mindful Mäuschen")
        
        # Connect the notification button in the settings page to the send_desktop_notif function
        self.settings.desktop_notif.clicked.connect(self.send_desktop_notif)   

        # Connect startup checkbox from Settings
        self.settings.startup_checkbox.stateChanged.connect(
            lambda state: self.handle_startup_toggle(state)
        )
        # Update Windows startup registry based on persistent setting
        self.update_windows_startup()
        
        # Check immediately on startup if there is a weight input for this week
        self.check_weekly_weight_reminder()
        
        # Set up a timer to check every 2 hours throughout the day
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_weekly_weight_reminder)
        self.reminder_timer.start(2 * 60 * 60 * 1000)  # 2 hours in milliseconds

    def handle_startup_toggle(self, state):
        """
        Handle startup checkbox state change.
        Updates the Windows startup registry and saves the setting to persistent storage.
        
        Args:
            state (int): The checkbox state (Qt.CheckState value).
        """
        # Update Windows startup registry based on checkbox state
        self.settings.toggle_startup(state, self.startup_settings)
        # Save the startup setting to persistent storage
        self.settings.save_startup_setting()
    
    def update_windows_startup(self):
        """
        Update Windows startup registry based on persistent setting.
        Adds or removes the app from Windows startup registry depending on
        the current checkbox state.
        """
        startup_enabled = self.settings.startup_checkbox.isChecked()
        if startup_enabled:
            app_path = self.settings.get_app_path()
            self.startup_settings.setValue("MindfulMauschen", app_path)
        else:
            self.startup_settings.remove("MindfulMauschen")
        self.startup_settings.sync()

    def check_weekly_weight_reminder(self):
        """
        Check if a weight has already been entered for this week.
        If no weight entry exists for the current week (Monday to Sunday),
        sends a desktop notification reminder.
        """
        now = datetime.now()
        # Calculate the start of the current week (Monday)
        days_since_monday = now.weekday()  # Monday is 0, Sunday is 6
        week_start = now - timedelta(days=days_since_monday)
        week_start_str = week_start.strftime("%Y-%m-%d")
        
        # Calculate the end of the current week (Sunday)
        week_end = week_start + timedelta(days=6)
        week_end_str = week_end.strftime("%Y-%m-%d")
        
        weekly_entry = check_weekly_weight_entry(week_start_str, week_end_str)
        
        # If no weight entry exists for this week, send notification
        if not weekly_entry:
            self.send_desktop_notif()

    def send_desktop_notif(self):
        """
        Send a native Windows desktop notification.
        Creates a toast notification reminding the user to log their weight.
        The notification includes audio unless silent notifications are enabled.
        """    
        # Create native Windows toast notification
        toast = Notification(
            app_id="Mindful Mäuschen",
            title="Boop! 🐭",
            msg="Beep Boop!Don't forget to log your weight for this week!",
            icon=os.path.abspath("assets/legnedary_astrid_boop_upscale.png") if os.path.exists("assets/legnedary_astrid_boop_upscale.png") else "",
            duration="long"  # Can be "short" or "long"
        )

        # If the silent notifications are disabled, set the audio to the default beep
        if not self.settings.silent_notif_checkbox.isChecked():
            toast.set_audio(audio.Default, loop=False)            
        toast.add_actions(label="Open App", launch="") 
        toast.add_actions(label="Dismiss", launch="")
        toast.show()
