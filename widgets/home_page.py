"""
Home page widget for the Health App.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class HomePage(QWidget):
    """
    This is the home page of the app. It is the first page that the user sees when they open the app.
    It contains the logo, app name, and subtitle.
    """
    def __init__(self):
        """Initialize the HomePage widget with logo, title, and subtitle."""
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo label, temp image till i come up with something better
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pixmap = QPixmap("assets/legnedary_astrid_boop_upscale.png")
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        # App name, temp till i come up with something remotely acceptable
        self.title_label = QLabel("Mindful Mäuschen")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        # Optional subtitle
        self.subtitle_label = QLabel("Mäuschen's personal health app")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        self.subtitle_label.setFont(subtitle_font)
        

        # Add widgets to layout
        self.layout.addWidget(self.logo_label)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.subtitle_label)

        self.setLayout(self.layout)

    def resizeEvent(self, event):
        """Resize the logo and app name when the window is resized."""
        super().resizeEvent(event)
        # Re-scale the pixmap when window size changes
        pixmap = QPixmap("assets/legnedary_astrid_boop_upscale.png")
        if not pixmap.isNull():
            size = int(min(self.width(), self.height()) * 0.5)  # 50% of smaller dimension
            self.logo_label.setPixmap(pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
