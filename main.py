"""
Main entry point for the Health App.
Initializes the database and starts the application.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from database import init_db
from main_window import HealthApp


# --- Run App ---
if __name__ == "__main__":
    init_db()
    # Ensure proper taskbar icon on Windows by setting AppUserModelID before creating windows
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MindfulMauschen.HealthApp.1.0")
        except Exception:
            pass
    app = QApplication(sys.argv)
    icon_path_ico = os.path.join("assets", "legnedary_astrid_boop_upscale.ico")
    icon_path_png = os.path.join("assets", "legnedary_astrid_boop_upscale.png")
    app_icon = QIcon(icon_path_ico) if os.path.exists(icon_path_ico) else QIcon(icon_path_png)
    app.setWindowIcon(app_icon)
    window = HealthApp()
    window.show()
    sys.exit(app.exec())
