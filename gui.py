# gui.py
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QTextEdit, QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor
from cli import Shell

NOTES_DIR = "notes"

def ensure_notes_dir():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

class NoteHub(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NoteHub")
        self.resize(800, 600)

        ensure_notes_dir()

        layout = QVBoxLayout()

        # ===== Terminal-like Command Line Section =====
        terminal_label = QLabel("Kommandozeile (Bash-Look):")
        layout.addWidget(terminal_label)

        # Text area for terminal output (read-only, monospace font, dark theme)
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.terminal_output.setMaximumHeight(200)
        layout.addWidget(self.terminal_output)

        # Command input line (user types commands here)
        cmd_layout = QHBoxLayout()
        self.prompt_label = QLabel()
        self.prompt_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
        """)
        cmd_layout.addWidget(self.prompt_label)

        self.command_input = QLineEdit()
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: none;
                padding: 5px;
            }
        """)
        self.command_input.returnPressed.connect(self.execute_command)
        cmd_layout.addWidget(self.command_input)
        layout.addLayout(cmd_layout)

        # Initialize Shell instance
        self.shell = Shell()
        self.update_prompt()
        self.append_terminal("Willkommen bei NoteHub! Gib 'help' ein, um alle Befehle zu sehen.\n")

        # ===== Notes Section =====
        notes_label = QLabel("Notizen:")
        layout.addWidget(notes_label)

        self.note_list = QListWidget()
        self.note_list.itemClicked.connect(self.load_note)
        layout.addWidget(self.note_list)

        self.text_area = QTextEdit()
        layout.addWidget(self.text_area)

        button_layout = QHBoxLayout()

        new_btn = QPushButton("Neue Notiz")
        new_btn.clicked.connect(self.new_note)
        button_layout.addWidget(new_btn)

        save_btn = QPushButton("Speichern")
        save_btn.clicked.connect(self.save_note)
        button_layout.addWidget(save_btn)

        delete_btn = QPushButton("Löschen")
        delete_btn.clicked.connect(self.delete_note)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.current_note = None
        self.refresh_notes()

    def refresh_notes(self):
        """Refresh notes list showing only the current directory's content"""
        self.note_list.clear()
        
        # Get current directory from shell (relative to NOTES_DIR)
        current_dir = self.shell.cwd
        
        # Collect items in current directory only
        items = []
        
        try:
            entries = os.listdir(current_dir)
            
            for entry in entries:
                full_path = os.path.join(current_dir, entry)
                
                if os.path.isdir(full_path):
                    items.append(("folder", entry, False))
                elif entry.endswith(".txt"):
                    # Remove .txt extension for display
                    display_name = entry[:-4]
                    # Check if note is done
                    is_done = False
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            is_done = "[DONE]" in content
                    except Exception:
                        pass
                    items.append(("file", display_name, is_done))
        except Exception:
            pass
        
        # Sort items: folders first, then files, alphabetically
        items.sort(key=lambda x: (x[0] == "file", x[1]))
        
        # Add items to list with icons and formatting
        from PyQt6.QtWidgets import QListWidgetItem
        from PyQt6.QtGui import QFont
        
        for item_type, name, is_done in items:
            if item_type == "folder":
                self.note_list.addItem(f"📁 {name}")
            else:
                if is_done:
                    # Add checkmark and strikethrough for done notes
                    item = QListWidgetItem(f"✅ {name}")
                    font = QFont()
                    font.setStrikeOut(True)
                    item.setFont(font)
                    self.note_list.addItem(item)
                else:
                    self.note_list.addItem(f"📄 {name}")

    def load_note(self, item):
        name = item.text()
        # Remove emoji prefix if present
        if name.startswith("📁 "):
            # This is a folder, not a note - don't try to load it
            return
        if name.startswith("📄 "):
            name = name[2:].strip()
        if name.startswith("✅ "):
            name = name[2:].strip()
        
        # Use current directory from shell
        filepath = os.path.join(self.shell.cwd, f"{name}.txt")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                self.text_area.setPlainText(f.read())
            self.current_note = name
        else:
            QMessageBox.warning(self, "Fehler", f"Notiz '{name}' nicht gefunden!")

    def new_note(self):
        name, ok = QInputDialog.getText(self, "Neue Notiz", "Titel der Notiz:")
        if ok and name:
            # Use current directory from shell
            path = os.path.join(self.shell.cwd, f"{name}.txt")
            if os.path.exists(path):
                QMessageBox.warning(self, "Fehler", "Diese Notiz existiert bereits!")
                return
            with open(path, "w", encoding="utf-8") as f:
                f.write("")
            self.refresh_notes()

    def save_note(self):
        if self.current_note:
            # Use current directory from shell
            filepath = os.path.join(self.shell.cwd, f"{self.current_note}.txt")
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.text_area.toPlainText())
            QMessageBox.information(self, "Gespeichert", f"'{self.current_note}' wurde gespeichert.")
        else:
            QMessageBox.warning(self, "Keine Notiz", "Keine Notiz ausgewählt!")

    def delete_note(self):
        if self.current_note:
            # Use current directory from shell
            filepath = os.path.join(self.shell.cwd, f"{self.current_note}.txt")
            if os.path.exists(filepath):
                os.remove(filepath)
            self.text_area.clear()
            self.refresh_notes()
            self.current_note = None

    # ===== Terminal Command Line Methods =====
    def update_prompt(self):
        """Update the prompt label with the current shell prompt."""
        self.prompt_label.setText(self.shell.prompt)

    def append_terminal(self, text):
        """Append text to the terminal output area."""
        self.terminal_output.moveCursor(QTextCursor.MoveOperation.End)
        self.terminal_output.insertPlainText(text)
        self.terminal_output.moveCursor(QTextCursor.MoveOperation.End)

    def execute_command(self):
        """Execute the command entered by the user."""
        command = self.command_input.text()
        if not command.strip():
            return

        # Special handling for clear command
        if command.strip() == "clear":
            self.terminal_output.clear()
            self.command_input.clear()
            return

        # Display the command in the terminal output
        self.append_terminal(f"{self.shell.prompt}{command}\n")

        # Execute the command using the Shell
        output = self.shell.run_command(command)
        if output:
            # Don't display ANSI escape codes
            if output != "\x1bc":
                self.append_terminal(output + "\n")

        # Clear the input and update prompt (in case cwd changed)
        self.command_input.clear()
        self.update_prompt()

        # Refresh notes list if add/remove/done/cd/mkdir commands were used
        if command.split()[0] in ["add", "remove", "done", "cd", "mkdir"]:
            self.refresh_notes()

def run_gui():
    app = QApplication([])
    window = NoteHub()
    window.show()
    app.exec()

