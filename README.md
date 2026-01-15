# NoteHub

A lightweight, customizable note management system with GUI, CLI, Vim mode, and email integration. Perfect for developers who want a simple yet powerful note-taking solution.

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- PyQt6 (installed automatically)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AimonKied/notehub.git
   cd notehub
   ```

2. **Install dependencies**
   ```bash
   chmod +x dependencies.sh
   ./dependencies.sh
   ```
   
   Or manually:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start NoteHub**
   
   **Option A:** Install system-wide (recommended)
   ```bash
   chmod +x install.sh
   ./install.sh
   notehub
   ```
   
   **Option B:** Run directly without installation
   ```bash
   python3 main.py
   ```

   **Option C:** CLI mode with arguments
   ```bash
   python3 main.py add "note-title" "note content"
   python3 main.py list
   python3 main.py shell    # Interactive shell mode
   ```

That's it! NoteHub will open in GUI mode by default.

---

## 📖 How to Use

### Interface Overview

When you open NoteHub GUI, you'll see:

| Section | Location | Description |
|---------|----------|-------------|
| **Command Line** | Top | Type shell commands here |
| **Terminal Output** | Top (scrollable) | Shows command results and messages |
| **Notes List** | Bottom left | Your saved notes and folders (📁 folders, 📄 notes, ✅ done) |
| **Editor** | Bottom right | Write and edit note content |
| **Settings** | ⚙ button (top right) | Customize colors and appearance |
| **Vim Mode** | Button (bottom) | Toggle Vim keybindings |

> 💡 **Tip:** All panels are resizable - drag the borders to adjust sizes!

---

## 📝 Creating and Managing Notes

### Method 1: Using Commands (Recommended)

```bash
# Create a new note
add my-first-note

# Edit in the editor that opens
# Press Enter to save, Shift+Enter for new line
```

### Method 2: Using GUI Buttons

1. Click **"New note"** button
2. Enter a title in the dialog
3. Write content in the editor
4. Click **"Save"** button

### Method 3: CLI Mode (Non-Interactive)

```bash
# Create note with content directly
python3 main.py add "shopping-list" "Milk, Bread, Eggs"

# List all notes
python3 main.py list

# Delete a note
python3 main.py remove "old-note"
```

---

## 🖥️ Complete Command Reference

### Navigation Commands

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| `ls` | `ls [path]` | List files/folders in directory | `ls` or `ls work/` |
| `cd` | `cd <path>` | Change directory | `cd work` or `cd ..` or `cd ~` |
| `pwd` | `pwd` | Show current directory path | `pwd` |
| `mkdir` | `mkdir <name>` | Create a new folder | `mkdir projects` |

### Note Management Commands

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| `add` | `add <title>` | Create new note (opens editor) | `add meeting-notes` |
| `edit` | `edit <title>` | Edit existing note | `edit meeting-notes` |
| `show` | `show <title>` | Display note in editor (read-only) | `show meeting-notes` |
| `remove` | `remove <title>` | Delete a note | `remove old-note` |
| `remove -d` | `remove -d <folder>` | Delete a folder and contents | `remove -d archive` |
| `list` | `list` | List all notes in current directory | `list` |
| `done` | `done <title>` | Mark note as completed (adds [DONE]) | `done task-list` |

### Todo & Checkbox Commands

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| `check` | `check <title> <line> [line2...]` | Toggle checkbox on line(s) | `check tasks 1 3 5` |

### Email Commands

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| `send` | `send <title> [email]` | Send note via email | `send report` or `send report user@example.com` |

### Utility Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| `help` | `help` | Show all available commands |
| `help vim` | `help vim` | Show Vim keybindings reference |
| `clear` | `clear` | Clear terminal output |
| `exit` | `exit` | Close NoteHub |

---

## ✅ Todo Lists & Checkboxes

Create interactive todo lists in your notes:

```markdown
[ ] Buy groceries
[ ] Call dentist
[x] Finish project
[ ] Review code
```

### Toggling Checkboxes

**Method 1: Double-click**
- Double-click any line with `[ ]` or `[x]` in the editor

**Method 2: Command**
```bash
# Toggle single line
check my-tasks 1

# Toggle multiple lines at once
check my-tasks 1 3 5 7
```

**Method 3: Vim mode**
- Navigate to line with `j`/`k`
- The checkbox state is preserved when editing

---

## ⌨️ Vim Mode

Toggle Vim mode with **Ctrl+M** or click the **"Vim Mode"** button.

### Visual Indicators

| Border Color | Mode | Description |
|--------------|------|-------------|
| 🔵 Blue | Normal | Navigation mode - keys move cursor |
| 🟢 Green | Insert | Editing mode - keys type text |

### Mode Switching

| Key | Action |
|-----|--------|
| `i` | Enter Insert mode (before cursor) |
| `a` | Enter Insert mode (after cursor) |
| `I` | Enter Insert mode (start of line) |
| `A` | Enter Insert mode (end of line) |
| `o` | Open new line below, enter Insert |
| `O` | Open new line above, enter Insert |
| `ESC` | Return to Normal mode |
| `kj` | Return to Normal mode (quick escape) |

### Navigation (Normal Mode)

| Key | Action |
|-----|--------|
| `h` | Move left |
| `j` | Move down |
| `k` | Move up |
| `l` | Move right |
| `w` | Jump to next word |
| `b` | Jump to previous word |
| `e` | Jump to end of word |
| `0` | Jump to start of line |
| `^` | Jump to first non-blank character |
| `$` | Jump to end of line |
| `gg` | Jump to top of document |
| `G` | Jump to bottom of document |
| `Ctrl+U` | Page up |
| `Ctrl+D` | Page down |

### Editing (Normal Mode)

| Key | Action |
|-----|--------|
| `x` | Delete character under cursor |
| `X` | Delete character before cursor |
| `dd` | Delete entire line |
| `D` | Delete to end of line |
| `cc` | Change (delete & enter Insert) line |
| `C` | Change to end of line |
| `yy` | Copy (yank) current line |
| `p` | Paste after cursor |
| `P` | Paste before cursor |
| `u` | Undo |
| `Ctrl+R` | Redo |
| `Enter` | Save note and exit edit mode |

> 💡 Type `help vim` in the command line for the complete reference.

---

## 🗂️ Organizing Notes with Folders

### Creating a Folder Structure

```bash
# Create folders
mkdir work
mkdir personal
mkdir work/projects

# Navigate into folder
cd work

# Create notes inside
add meeting-notes
add weekly-report

# Go back
cd ..

# Or go to root
cd ~
```

### Notes List Icons

| Icon | Meaning |
|------|---------|
| 📁 | Folder (click to navigate) |
| 📄 | Regular note |
| ✅ | Completed note (marked with `done` command) |

---

## 📧 Email Integration

### Setup (One-time)

1. Clone the notehub-email companion:
   ```bash
   cd ..
   git clone https://github.com/AimonKied/notehub-email.git
   cd notehub-email
   ```

2. Configure `.env` file with your email credentials:
   ```env
   FROM_EMAIL=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   TO_EMAIL=default-recipient@example.com  # Optional default
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

### Sending Notes

```bash
# Send to default recipient (from .env)
send my-note

# Send to specific email
send my-note recipient@example.com
```

### CLI Email Command

```bash
python3 main.py email "note-title"
python3 main.py email "note-title" "recipient@example.com"
```

---

## 🎨 Customization & Settings

Click the **⚙** button to open settings dialog.

### Customizable Colors

| Setting | Description | Default |
|---------|-------------|---------|
| Terminal Background | Command line area background | `#1E1E1E` |
| Terminal Text | Command line text color | `#00FF00` |
| Editor Background | Note editor background | `#1E1E1E` |
| Editor Text | Note editor text color | `#FFFFFF` |
| Vim Normal Border | Border color in Vim normal mode | `#2196F3` (blue) |
| Vim Insert Border | Border color in Vim insert mode | `#4CAF50` (green) |

Settings are saved to `notehub_settings.json` and persist between sessions.

---

## 🔧 Advanced Features

### Tab Completion

Press **Tab** in the command line to auto-complete:
- Command names (first word)
- File and folder names (arguments)
- Cycle through multiple matches with repeated Tab presses

### Line Numbers

The editor displays line numbers automatically, useful for:
- Using the `check` command with line numbers
- Navigating in Vim mode
- Reference during editing

### Keyboard Shortcuts

| Shortcut | Context | Action |
|----------|---------|--------|
| `Ctrl+M` | Anywhere | Toggle Vim mode |
| `Enter` | Editor (non-Vim) | Save note |
| `Shift+Enter` | Editor (non-Vim) | Insert new line |
| `Tab` | Command line | Auto-complete |
| `Enter` | Command line | Execute command |

### Interactive Shell Mode

For terminal-only usage:
```bash
python3 main.py shell
```

This starts an interactive shell with readline support (history, line editing).

---

## 🆘 Troubleshooting

### Common Issues

**"Command not found: notehub"**
```bash
# Re-run installation
./install.sh

# Or run directly
python3 main.py
```

**"ModuleNotFoundError: No module named 'PyQt6'"**
```bash
pip install PyQt6
# Or
pip install -r requirements.txt
```

**Email not working**
- Ensure `notehub-email` folder exists in parent directory
- Check `.env` configuration in `notehub-email/`
- For Gmail, use an App Password (not your regular password)

**Vim mode cursor not visible**
- This is normal in Normal mode (block cursor may not show on all systems)
- Look at the border color to identify the mode
- Press `i` to enter Insert mode and see the cursor

**Notes not showing in list**
- Use `cd ~` to return to the notes root
- Use `ls` to see what's in the current directory
- Notes must have `.txt` extension (created automatically)

---

## 📁 File Structure

```
notehub/
├── main.py              # Entry point (GUI or CLI)
├── gui.py               # PyQt6 GUI implementation
├── cli.py               # Shell and CLI commands
├── vim_mode.py          # Vim keybindings handler
├── settings.py          # Settings dialog and persistence
├── notehub_settings.json # User preferences (auto-generated)
├── requirements.txt     # Python dependencies
├── install.sh           # System-wide installation script
├── dependencies.sh      # Dependency installation script
└── notes/               # Your notes directory (auto-created)
    ├── note1.txt
    ├── work/
    │   └── meeting.txt
    └── ...
```

---

## 🎯 Features Summary

| Feature | Description |
|---------|-------------|
| 📝 **Dual Interface** | Full GUI with integrated CLI |
| ⌨️ **Vim Mode** | Complete Vim keybindings with visual indicators |
| 🗂️ **Folder Organization** | Hierarchical note organization |
| ✅ **Todo Checkboxes** | Interactive `[ ]` / `[x]` checkboxes |
| 🐚 **Interactive Shell** | Bash-like shell with history |
| 📧 **Email Integration** | Send notes via SMTP |
| 🎨 **Customizable Themes** | Configure all colors |
| 🔢 **Line Numbers** | Editor line number display |
| ⌨️ **Tab Completion** | Command and filename completion |
| 💾 **Auto-save** | Save with Enter key |
| 🖱️ **Resizable Panels** | Adjustable interface layout |

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests
- Improve documentation

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/AimonKied/notehub/issues)
- **Email Integration:** [notehub-email](https://github.com/AimonKied/notehub-email)
