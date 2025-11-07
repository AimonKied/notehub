"""
Vim mode keybindings and handlers for NoteHub text editor.
Provides Normal and Insert mode functionality similar to Vim.
"""

from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt


class VimMode:
    """Handles Vim mode state and keybindings for text editor."""
    
    def __init__(self, text_edit):
        self.text_edit = text_edit
        self.enabled = False
        self.current_mode = "normal"  # "normal" or "insert"
        self.command_buffer = ""  # For multi-key commands like "dd", "gg"
        self.last_insert_key = ""  # For "jk" escape sequence
        self.last_insert_time = 0  # Timestamp for last insert key
        
    def toggle(self):
        """Toggle Vim mode on/off."""
        self.enabled = not self.enabled
        if self.enabled:
            self.current_mode = "normal"
            # Don't use setReadOnly, it hides cursor - we handle readonly in keyPressEvent
            self.text_edit.setReadOnly(False)
        else:
            self.current_mode = "normal"
            self.text_edit.setReadOnly(False)
        self.update_visual_indicator()
        return self.enabled
    
    def update_visual_indicator(self):
        """Update visual indicator of current Vim mode."""
        if self.enabled:
            if self.current_mode == "insert":
                # Insert mode: green border, thin cursor
                self.text_edit.setStyleSheet("QTextEdit { border: 2px solid #4CAF50; }")
                self.text_edit.setCursorWidth(2)
            else:
                # Normal mode: blue border, thicker block cursor
                self.text_edit.setStyleSheet("QTextEdit { border: 2px solid #2196F3; }")
                self.text_edit.setCursorWidth(10)  # Block cursor
        else:
            # Vim mode off: no special border
            self.text_edit.setStyleSheet("")
            self.text_edit.setCursorWidth(2)
    
    def enter_insert_mode(self, cursor=None):
        """Switch to insert mode at current cursor position."""
        self.current_mode = "insert"
        # Don't use setReadOnly - we handle this in keyPressEvent
        self.update_visual_indicator()
        if cursor:
            self.text_edit.setTextCursor(cursor)
    
    def enter_normal_mode(self):
        """Switch to normal mode."""
        self.current_mode = "normal"
        # Don't use setReadOnly - we handle this in keyPressEvent
        # Reset insert mode tracking
        self.last_insert_key = ""
        self.update_visual_indicator()
    
    def handle_insert_mode_key(self, event):
        """
        Handle key press in Vim insert mode.
        Returns 'normal' if should switch to normal mode (kj pressed).
        Returns None otherwise (key should be processed normally).
        """
        import time
        text = event.text()
        current_time = time.time()
        
        # Check for "kj" escape sequence
        if text == 'k':
            self.last_insert_key = 'k'
            self.last_insert_time = current_time
            return None  # Process 'k' normally
        elif text == 'j' and self.last_insert_key == 'k':
            # Check if 'j' was pressed within 0.5 seconds of 'k'
            if current_time - self.last_insert_time < 0.5:
                # Delete the 'k' that was just typed
                cursor = self.text_edit.textCursor()
                cursor.deletePreviousChar()
                self.text_edit.setTextCursor(cursor)
                # Switch to normal mode
                return 'normal'
        
        # Reset tracking if any other key
        if text != 'k':
            self.last_insert_key = ""
        
        return None
    
    def handle_normal_mode_key(self, event):
        """
        Handle key press in Vim normal mode.
        Returns True if key was handled, False otherwise.
        Returns 'save' if Enter was pressed (to signal save action).
        """
        key = event.key()
        text = event.text()
        cursor = self.text_edit.textCursor()
        
        # Enter key in normal mode - save and exit edit mode
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return 'save'
        
        # Movement keys
        if text == 'h':
            self._move_left(cursor)
        elif text == 'j':
            self._move_down(cursor)
        elif text == 'k':
            self._move_up(cursor)
        elif text == 'l':
            self._move_right(cursor)
        
        # Word movement
        elif text == 'w':
            self._move_next_word(cursor)
        elif text == 'b':
            self._move_previous_word(cursor)
        elif text == 'e':
            self._move_end_of_word(cursor)
        
        # Line movement
        elif text == '0':
            self._move_start_of_line(cursor)
        elif text == '^':
            self._move_first_non_blank(cursor)
        elif text == '$':
            self._move_end_of_line(cursor)
        
        # Document movement
        elif text == 'g':
            if self.command_buffer == 'g':
                # gg - go to top
                self._move_to_top(cursor)
                self.command_buffer = ""
            else:
                self.command_buffer = 'g'
                return True
        elif text == 'G':
            self._move_to_bottom(cursor)
        
        # Page movement
        elif event.key() == Qt.Key.Key_U and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._page_up()
        elif event.key() == Qt.Key.Key_D and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._page_down()
        
        # Insert modes
        elif text == 'i':
            self._insert_before_cursor(cursor)
        elif text == 'a':
            self._insert_after_cursor(cursor)
        elif text == 'I':
            self._insert_at_line_start(cursor)
        elif text == 'A':
            self._insert_at_line_end(cursor)
        elif text == 'o':
            self._insert_line_below(cursor)
        elif text == 'O':
            self._insert_line_above(cursor)
        
        # Delete operations
        elif text == 'x':
            self._delete_char(cursor)
        elif text == 'X':
            self._delete_char_before(cursor)
        elif text == 'd':
            if self.command_buffer == 'd':
                # dd - delete line
                self._delete_line(cursor)
                self.command_buffer = ""
            elif self.command_buffer == '':
                self.command_buffer = 'd'
                return True
        elif text == 'D':
            self._delete_to_end_of_line(cursor)
        
        # Copy/Paste operations
        elif text == 'y':
            if self.command_buffer == 'y':
                # yy - yank (copy) line
                self._yank_line(cursor)
                self.command_buffer = ""
            elif self.command_buffer == '':
                self.command_buffer = 'y'
                return True
        elif text == 'p':
            self._paste_after(cursor)
        elif text == 'P':
            self._paste_before(cursor)
        
        # Change operations
        elif text == 'c':
            if self.command_buffer == 'c':
                # cc - change line
                self._change_line(cursor)
                self.command_buffer = ""
            elif self.command_buffer == '':
                self.command_buffer = 'c'
                return True
        elif text == 'C':
            self._change_to_end_of_line(cursor)
        
        # Undo/Redo
        elif text == 'u':
            self._undo()
        elif event.key() == Qt.Key.Key_R and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._redo()
        
        # Search (basic)
        elif text == '/':
            # Future: implement search
            pass
        
        # Visual mode (future)
        elif text == 'v':
            # Future: implement visual mode
            pass
        
        else:
            # Key not handled
            self.command_buffer = ""
            return False
        
        # Clear command buffer if not building a command
        if self.command_buffer not in ['d', 'y', 'c', 'g']:
            self.command_buffer = ""
        
        return True
    
    # ========== Movement Functions ==========
    
    def _move_left(self, cursor):
        """Move cursor left (h)."""
        cursor.movePosition(QTextCursor.MoveOperation.Left)
        self.text_edit.setTextCursor(cursor)
    
    def _move_down(self, cursor):
        """Move cursor down (j)."""
        cursor.movePosition(QTextCursor.MoveOperation.Down)
        self.text_edit.setTextCursor(cursor)
    
    def _move_up(self, cursor):
        """Move cursor up (k)."""
        cursor.movePosition(QTextCursor.MoveOperation.Up)
        self.text_edit.setTextCursor(cursor)
    
    def _move_right(self, cursor):
        """Move cursor right (l)."""
        cursor.movePosition(QTextCursor.MoveOperation.Right)
        self.text_edit.setTextCursor(cursor)
    
    def _move_next_word(self, cursor):
        """Move to next word (w)."""
        cursor.movePosition(QTextCursor.MoveOperation.NextWord)
        self.text_edit.setTextCursor(cursor)
    
    def _move_previous_word(self, cursor):
        """Move to previous word (b)."""
        cursor.movePosition(QTextCursor.MoveOperation.PreviousWord)
        self.text_edit.setTextCursor(cursor)
    
    def _move_end_of_word(self, cursor):
        """Move to end of word (e)."""
        cursor.movePosition(QTextCursor.MoveOperation.EndOfWord)
        self.text_edit.setTextCursor(cursor)
    
    def _move_start_of_line(self, cursor):
        """Move to start of line (0)."""
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        self.text_edit.setTextCursor(cursor)
    
    def _move_first_non_blank(self, cursor):
        """Move to first non-blank character (^)."""
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        # Skip whitespace
        while cursor.position() < self.text_edit.document().characterCount():
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
            char = cursor.selectedText()
            if char and not char.isspace():
                cursor.clearSelection()
                cursor.movePosition(QTextCursor.MoveOperation.Left)
                break
            cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)
    
    def _move_end_of_line(self, cursor):
        """Move to end of line ($)."""
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        self.text_edit.setTextCursor(cursor)
    
    def _move_to_top(self, cursor):
        """Move to top of document (gg)."""
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.text_edit.setTextCursor(cursor)
    
    def _move_to_bottom(self, cursor):
        """Move to bottom of document (G)."""
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_edit.setTextCursor(cursor)
    
    def _page_up(self):
        """Page up (Ctrl+U)."""
        for _ in range(15):  # Scroll ~15 lines
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Up)
            self.text_edit.setTextCursor(cursor)
    
    def _page_down(self):
        """Page down (Ctrl+D)."""
        for _ in range(15):  # Scroll ~15 lines
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Down)
            self.text_edit.setTextCursor(cursor)
    
    # ========== Insert Mode Functions ==========
    
    def _insert_before_cursor(self, cursor):
        """Insert before cursor (i)."""
        self.enter_insert_mode(cursor)
    
    def _insert_after_cursor(self, cursor):
        """Insert after cursor (a)."""
        cursor.movePosition(QTextCursor.MoveOperation.Right)
        self.enter_insert_mode(cursor)
    
    def _insert_at_line_start(self, cursor):
        """Insert at beginning of line (I)."""
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        self.enter_insert_mode(cursor)
    
    def _insert_at_line_end(self, cursor):
        """Insert at end of line (A)."""
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        self.enter_insert_mode(cursor)
    
    def _insert_line_below(self, cursor):
        """Insert new line below (o)."""
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        cursor.insertText("\n")
        self.enter_insert_mode(cursor)
    
    def _insert_line_above(self, cursor):
        """Insert new line above (O)."""
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.insertText("\n")
        cursor.movePosition(QTextCursor.MoveOperation.Up)
        self.enter_insert_mode(cursor)
    
    # ========== Delete Functions ==========
    
    def _delete_char(self, cursor):
        """Delete character under cursor (x)."""
        cursor.deleteChar()
        self.text_edit.setTextCursor(cursor)
    
    def _delete_char_before(self, cursor):
        """Delete character before cursor (X)."""
        cursor.deletePreviousChar()
        self.text_edit.setTextCursor(cursor)
    
    def _delete_line(self, cursor):
        """Delete entire line (dd)."""
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()  # Delete the newline
        self.text_edit.setTextCursor(cursor)
    
    def _delete_to_end_of_line(self, cursor):
        """Delete from cursor to end of line (D)."""
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        self.text_edit.setTextCursor(cursor)
    
    # ========== Copy/Paste Functions ==========
    
    def _yank_line(self, cursor):
        """Copy (yank) entire line (yy)."""
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        text = cursor.selectedText()
        self.text_edit.copy()
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)
    
    def _paste_after(self, cursor):
        """Paste after cursor (p)."""
        cursor.movePosition(QTextCursor.MoveOperation.Right)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.paste()
    
    def _paste_before(self, cursor):
        """Paste before cursor (P)."""
        self.text_edit.setTextCursor(cursor)
        self.text_edit.paste()
    
    # ========== Change Functions ==========
    
    def _change_line(self, cursor):
        """Delete line and enter insert mode (cc)."""
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        self.enter_insert_mode(cursor)
    
    def _change_to_end_of_line(self, cursor):
        """Delete to end of line and enter insert mode (C)."""
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        self.enter_insert_mode(cursor)
    
    # ========== Undo/Redo Functions ==========
    
    def _undo(self):
        """Undo last change (u)."""
        self.text_edit.undo()
    
    def _redo(self):
        """Redo last undone change (Ctrl+R)."""
        self.text_edit.redo()
