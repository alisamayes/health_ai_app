"""
PlannerOptionsDialog widget for the Health App.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QToolButton, QDialogButtonBox
)


class PlannerOptionsDialog(QDialog):
    """
    Generic popup dialog showing chip-style toggle options using checkable
    `QToolButton`s. The concrete titles, label text and chips are provided
    by the caller (or by the `planner_options_dialog` decorator).
    """

    def __init__(self, parent=None, *, title: str, label_text: str, chips: list):
        """
        Initialize the PlannerOptionsDialog with chip-style toggle buttons.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget for this dialog.
        title : str
            Window title for the dialog.
        label_text : str
            Instruction text shown above the chips.
        chips : list
            List of (key, display_text) tuples. The returned values() dict
            will be keyed by key, and display_text will be shown on each button.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self._chip_buttons: dict[str, QToolButton] = {}

        main_layout = QVBoxLayout(self)

        label = QLabel(label_text)
        main_layout.addWidget(label)

        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)

        for key, display_text in chips:
            btn = self._make_chip(display_text)
            self._chip_buttons[key] = btn
            chips_layout.addWidget(btn)

        main_layout.addLayout(chips_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def _make_chip(self, text: str) -> QToolButton:
        """
        Create a chip-style toggle button.
        
        Args:
            text (str): The text to display on the button.
        
        Returns:
            QToolButton: A checkable tool button configured as a chip.
        """
        btn = QToolButton(self)
        btn.setText(text)
        btn.setCheckable(True)
        btn.setAutoRaise(True)
        return btn

    def values(self) -> dict:
        """
        Return a dict mapping each chip key to its checked state.
        
        Returns:
            dict: Dictionary where keys are chip keys and values are booleans
                  indicating whether each chip is checked.
        """
        return {key: btn.isChecked() for key, btn in self._chip_buttons.items()}

