# settings.py
import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QColorDialog
)
from PyQt6.QtGui import QColor

SETTINGS_FILE = "notehub_settings.json"
DEFAULT_SETTINGS = {
    "terminal_bg": "#1e1e1e",
    "terminal_fg": "#00ff00",
    "vim_normal_border": "#2196F3",
    "vim_insert_border": "#4CAF50",
    "editor_bg": "#ffffff",
    "editor_fg": "#000000"
}


def load_settings():
    """Load settings from JSON file or return defaults."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Save settings to JSON file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


class SettingsDialog(QDialog):
    """Dialog for configuring NoteHub colors and settings."""
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("NoteHub Settings")
        self.settings = current_settings or DEFAULT_SETTINGS.copy()
        self.color_buttons = {}
        
        layout = QVBoxLayout()
        
        # Color settings grid
        grid = QGridLayout()
        
        color_options = [
            ("terminal_bg", "Terminal Background"),
            ("terminal_fg", "Terminal Text"),
            ("vim_normal_border", "Vim Normal Border"),
            ("vim_insert_border", "Vim Insert Border"),
            ("editor_bg", "Editor Background"),
            ("editor_fg", "Editor Text")
        ]
        
        for row, (key, label) in enumerate(color_options):
            label_widget = QLabel(label + ":")
            grid.addWidget(label_widget, row, 0)
            
            color_btn = QPushButton()
            color_btn.setFixedSize(100, 30)
            color_btn.setStyleSheet(f"background-color: {self.settings[key]};")
            color_btn.clicked.connect(lambda checked, k=key: self.pick_color(k))
            self.color_buttons[key] = color_btn
            grid.addWidget(color_btn, row, 1)
        
        layout.addLayout(grid)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addWidget(reset_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def pick_color(self, key):
        """Open color picker for a specific setting."""
        current_color = QColor(self.settings[key])
        color = QColorDialog.getColor(current_color, self, f"Choose {key}")
        if color.isValid():
            self.settings[key] = color.name()
            self.color_buttons[key].setStyleSheet(f"background-color: {color.name()};")
    
    def reset_defaults(self):
        """Reset all colors to defaults."""
        self.settings = DEFAULT_SETTINGS.copy()
        for key, btn in self.color_buttons.items():
            btn.setStyleSheet(f"background-color: {self.settings[key]};")
