# gui.py
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QTextEdit, QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent
from cli import Shell

NOTES_DIR = "notes"

def ensure_notes_dir():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)


class CommandLineEdit(QLineEdit):
    """Custom QLineEdit with Tab completion support."""
    
    def __init__(self, shell, parent=None):
        super().__init__(parent)
        self.shell = shell
        self.completion_matches = []
        self.completion_index = 0
        # Prevent Tab from moving focus to next widget
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def event(self, event):
        """Override event to capture Tab key before focus change."""
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Tab:
                self.handle_tab_completion()
                return True  # Event handled, don't propagate
        return super().event(event)
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Tab:
            # Already handled in event()
            return
        else:
            # Reset completion state on any other key
            self.completion_matches = []
            self.completion_index = 0
            super().keyPressEvent(event)
    
    def handle_tab_completion(self):
        """Handle Tab key press for auto-completion."""
        text = self.text()
        cursor_pos = self.cursorPosition()
        
        # Get the word at cursor position
        before_cursor = text[:cursor_pos]
        parts = before_cursor.split()
        
        if not parts:
            # No text yet, show all commands
            self.completion_matches = sorted(self.shell.commands.keys())
            self.completion_index = 0
            if self.completion_matches:
                self.setText(self.completion_matches[0])
            return
        
        # If we're completing the first word (command name)
        if len(parts) == 1 and not before_cursor.endswith(' '):
            prefix = parts[0]
            if not self.completion_matches:
                # Find all commands that start with prefix
                self.completion_matches = sorted([
                    cmd for cmd in self.shell.commands.keys() 
                    if cmd.startswith(prefix)
                ])
                self.completion_index = 0
            
            if self.completion_matches:
                # Cycle through matches
                match = self.completion_matches[self.completion_index]
                self.setText(match)
                self.completion_index = (self.completion_index + 1) % len(self.completion_matches)
        else:
            # Complete file/folder names
            self.complete_filename(parts, before_cursor)
    
    def complete_filename(self, parts, before_cursor):
        """Complete file or folder names."""
        # Get the word being completed
        if before_cursor.endswith(' '):
            prefix = ""
        else:
            prefix = parts[-1]
        
        if not self.completion_matches:
            # Get files and folders in current directory
            try:
                entries = os.listdir(self.shell.cwd)
                # Filter by prefix and add appropriate suffix
                matches = []
                for entry in sorted(entries):
                    if entry.startswith(prefix):
                        full_path = os.path.join(self.shell.cwd, entry)
                        if os.path.isdir(full_path):
                            matches.append(entry + "/")
                        elif entry.endswith(".txt"):
                            # Remove .txt extension for notes
                            matches.append(entry[:-4])
                        else:
                            matches.append(entry)
                self.completion_matches = matches
                self.completion_index = 0
            except Exception:
                return
        
        if self.completion_matches:
            # Replace the last word with the match
            match = self.completion_matches[self.completion_index]
            parts_before = parts[:-1] if len(parts) > 1 and not before_cursor.endswith(' ') else parts
            new_text = ' '.join(parts_before)
            if new_text:
                new_text += ' '
            new_text += match
            self.setText(new_text)
            self.completion_index = (self.completion_index + 1) % len(self.completion_matches)


class NoteTextEdit(QTextEdit):
    """Custom QTextEdit that saves on Enter and allows Shift+Enter for new lines.
    Also supports todo checkboxes: double-click a line to toggle [ ] <-> [x]."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.edit_mode = False  # True when in add/edit mode
        
    def mouseDoubleClickEvent(self, event):
        """Toggle todo checkbox on double-click."""
        cursor = self.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        line = cursor.selectedText()
        
        # Check if line is a todo item
        if line.strip().startswith("[ ]"):
            # Check it
            new_line = line.replace("[ ]", "[x]", 1)
            cursor.insertText(new_line)
        elif line.strip().startswith("[x]"):
            # Uncheck it
            new_line = line.replace("[x]", "[ ]", 1)
            cursor.insertText(new_line)
        else:
            # Not a todo, do normal double-click behavior
            super().mouseDoubleClickEvent(event)
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle Enter vs Shift+Enter."""
        if self.edit_mode:
            # In edit mode: Enter saves, Shift+Enter = new line
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    # Shift+Enter: insert new line
                    super().keyPressEvent(event)
                else:
                    # Enter alone: save and exit edit mode
                    if self.parent_widget:
                        self.parent_widget.finish_editing()
                    return
            else:
                super().keyPressEvent(event)
        else:
            # Normal mode: all keys work normally
            super().keyPressEvent(event)


class NoteHub(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NoteHub")
        self.resize(800, 600)

        ensure_notes_dir()

        layout = QVBoxLayout()

        # ===== Terminal-like Command Line Section =====
        terminal_label = QLabel("Command Line:")
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

        # Initialize Shell instance first (needed for CommandLineEdit)
        self.shell = Shell()

        # Use custom CommandLineEdit with Tab completion
        self.command_input = CommandLineEdit(self.shell)
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

        self.update_prompt()
        self.append_terminal("Welcome to NoteHub! Type 'help' to see all commands.\n")

        # ===== Notes Section =====
        notes_label = QLabel("Notes:")
        layout.addWidget(notes_label)

        self.note_list = QListWidget()
        self.note_list.itemClicked.connect(self.load_note)
        layout.addWidget(self.note_list)

        self.text_area = NoteTextEdit(self)
        layout.addWidget(self.text_area)

        button_layout = QHBoxLayout()

        new_btn = QPushButton("New note")
        new_btn.clicked.connect(self.new_note)
        button_layout.addWidget(new_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_note)
        button_layout.addWidget(save_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_note)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.current_note = None
        self.edit_mode_type = None  # 'add' or 'edit'
        self.refresh_notes()
        
        # Set focus to command input on startup
        self.command_input.setFocus()

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
            QMessageBox.warning(self, "Error", f"Note '{name}' not found!")

    def new_note(self):
        name, ok = QInputDialog.getText(self, "New Note", "Note title:")
        if ok and name:
            # Use current directory from shell
            path = os.path.join(self.shell.cwd, f"{name}.txt")
            if os.path.exists(path):
                QMessageBox.warning(self, "Error", "This note already exists!")
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
            QMessageBox.information(self, "Saved", f"'{self.current_note}' saved.")
        else:
            QMessageBox.warning(self, "No Note", "No note selected!")

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

    def finish_editing(self):
        """Called when user presses Enter in edit mode to save the note."""
        if not self.current_note:
            return
        
        content = self.text_area.toPlainText()
        filepath = os.path.join(self.shell.cwd, f"{self.current_note}.txt")
        
        try:
            if self.edit_mode_type == "add":
                # Create new note
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.append_terminal(f"Note '{self.current_note}' created.\n")
            elif self.edit_mode_type == "edit":
                # Update existing note
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.append_terminal(f"Note '{self.current_note}' saved.\n")
            
            # Exit edit mode and return focus to command line
            self.text_area.edit_mode = False
            self.edit_mode_type = None
            self.refresh_notes()
            self.command_input.setFocus()
        except Exception as e:
            self.append_terminal(f"Error: {str(e)}\n")

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

        # Special handling for exit command
        if command.strip() == "exit":
            self.append_terminal(f"{self.shell.prompt}{command}\n")
            self.append_terminal("Bye.\n")
            self.close()  # Close the GUI window
            return

        # Special handling for add command - activate edit mode
        cmd_parts = command.split()
        if cmd_parts and cmd_parts[0] == "add":
            self.append_terminal(f"{self.shell.prompt}{command}\n")
            if len(cmd_parts) > 1:
                note_title = cmd_parts[1]
                filepath = os.path.join(self.shell.cwd, f"{note_title}.txt")
                if os.path.exists(filepath):
                    self.append_terminal(f"Note '{note_title}' already exists. Use 'edit'.\n")
                else:
                    self.current_note = note_title
                    self.edit_mode_type = "add"
                    self.text_area.clear()
                    self.text_area.edit_mode = True
                    self.text_area.setFocus()
                    self.append_terminal(f"Editor activated. Write your note. Enter = Save, Shift+Enter = New line.\n")
            else:
                self.append_terminal("Usage: add <title>\n")
            self.command_input.clear()
            return

        # Special handling for edit command - activate edit mode
        if cmd_parts and cmd_parts[0] == "edit":
            self.append_terminal(f"{self.shell.prompt}{command}\n")
            if len(cmd_parts) > 1:
                note_title = cmd_parts[1]
                filepath = os.path.join(self.shell.cwd, f"{note_title}.txt")
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.current_note = note_title
                    self.edit_mode_type = "edit"
                    self.text_area.setPlainText(content)
                    self.text_area.edit_mode = True
                    self.text_area.setFocus()
                    # Move cursor to end
                    cursor = self.text_area.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.text_area.setTextCursor(cursor)
                    self.append_terminal(f"Editor activated. Edit your note. Enter = Save, Shift+Enter = New line.\n")
                else:
                    self.append_terminal(f"Note '{note_title}' not found.\n")
            else:
                self.append_terminal("Usage: edit <title>\n")
            self.command_input.clear()
            return

        # Special handling for show command - display in text area instead of terminal
        if cmd_parts and cmd_parts[0] == "show":
            self.append_terminal(f"{self.shell.prompt}{command}\n")
            if len(cmd_parts) > 1:
                note_title = cmd_parts[1]
                filepath = os.path.join(self.shell.cwd, f"{note_title}.txt")
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.text_area.setPlainText(content)
                    self.current_note = note_title
                    self.text_area.edit_mode = False
                    self.append_terminal(f"Note '{note_title}' displayed in editor.\n")
                else:
                    self.append_terminal(f"Note '{note_title}' not found.\n")
            else:
                self.append_terminal("Usage: show <title>\n")
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

        # Refresh notes list if remove/done/cd/mkdir commands were used
        # (add/edit are handled separately in finish_editing)
        if command.split()[0] in ["remove", "done", "cd", "mkdir"]:
            self.refresh_notes()
        
        # If check command was used and note is currently displayed, reload it
        if command.split()[0] == "check" and self.current_note:
            cmd_parts = command.split()
            if len(cmd_parts) >= 2 and cmd_parts[1] == self.current_note:
                # Reload the note in the editor
                filepath = os.path.join(self.shell.cwd, f"{self.current_note}.txt")
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.text_area.setPlainText(f.read())

def run_gui():
    app = QApplication([])
    window = NoteHub()
    window.show()
    app.exec()

