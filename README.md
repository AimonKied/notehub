# NoteHub

A lightweight, customizable note management system with GUI, CLI, Vim mode, and email integration. Perfect for developers who want a simple yet powerful note-taking solution.

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AimonKied/notehub.git
   cd notehub
   ```

2. **Install dependencies**
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

That's it! NoteHub will open in GUI mode.

## 📖 How to Use

### First Steps

When you first open NoteHub, you'll see:
- **Command Line** (top) - Type commands here
- **Notes List** (bottom left) - Your saved notes
- **Editor** (bottom right) - Write and edit notes
- **Settings button** (⚙ top right) - Customize colors

### Creating Your First Note

**Method 1: Using Commands**
1. Type in the command line: `add my-first-note`
2. Start typing in the editor
3. Press **Enter** to save (or **Shift+Enter** for new line)

**Method 2: Using Buttons**
1. Click the "New note" button
2. Enter a title
3. Write in the editor
4. Click "Save"

### Basic Commands

Type these in the command line:

| Command | What it does |
|---------|-------------|
| `help` | Show all available commands |
| `ls` | List notes in current folder |
| `add <name>` | Create a new note |
| `edit <name>` | Edit an existing note |
| `show <name>` | Display a note |
| `remove <name>` | Delete a note |
| `mkdir <folder>` | Create a new folder |
| `cd <folder>` | Navigate to folder |
| `clear` | Clear the terminal |
| `exit` | Close NoteHub |

### Todo Lists

Create checkboxes in your notes:

```
[ ] Buy groceries
[ ] Call dentist
[x] Finish project
```

**Toggle checkboxes:**
- Double-click a line with `[ ]` or `[x]`
- Or use command: `check <note-name> <line-number>`

### Organizing Notes

Create folders to organize your notes:
```bash
mkdir work
cd work
add meeting-notes
```

Navigate like in a file system:
```bash
ls, cd, pwd, mkdir       # Navigation
add, edit, remove        # Note management
show, list, done         # View notes
check <note> <line>      # Toggle checkbox
email <note>             # Send via email
help vim                 # Show Vim keybindings
```

## Vim Mode

Toggle Vim mode with **Ctrl+M** or the "Vim Mode" button.

### Visual Indicators
- **Blue border** = Normal mode (navigation)
- **Green border** = Insert mode (typing)

### Essential Keybindings

**Navigation (Normal mode):**
- `h/j/k/l` - Move left/down/up/right
- `w/b` - Jump forward/backward by word
- `0/$` - Jump to line start/end
- `gg/G` - Jump to document top/bottom

**Entering Insert mode:**
- `i` - Insert before cursor
- `a` - Insert after cursor
- `o` - New line below
- `ESC` or `kj` - Return to normal mode

**Editing (Normal mode):**
- `dd` - Delete line
- `yy` - Copy line
- `p` - Paste
- `u` - Undo
- `Enter` - Save note

**Full keybinding list:** Type `help vim` in the command line.

## 📧 Email Integration (Optional)

To send notes via email:

1. **Install notehub-email** (sibling directory)
   ```bash
   cd ..
   git clone https://github.com/AimonKied/notehub-email.git
   cd notehub-email
   # Follow setup instructions
   ```

2. **Send a note**
   ```bash
   email <note-name>
   ```

## 🎨 Features Overview

- **📝 Dual Interface** - Use GUI or CLI mode
- **⌨️ Vim Mode** - Full Vim keybindings with visual indicators
- **🗂️ Folder Organization** - Organize notes in folders
- **✅ Todo Checkboxes** - Track tasks with interactive checkboxes
- **🐚 Interactive Shell** - Familiar command-line interface
- **📧 Email Notes** - Send notes directly via email
- **🔧 Customizable** - Configure colors to your preference
- **💾 Auto-save** - Notes saved automatically
- **🖱️ Resizable Panels** - Drag to resize terminal/editor/list

## 🆘 Troubleshooting

**"Command not found: notehub"**
- Run `./install.sh` again or use `python3 main.py`

**"ModuleNotFoundError: No module named 'PyQt6'"**
- Install dependencies: `pip install -r requirements.txt`

**Email not working**
- Make sure notehub-email is installed in sibling directory
- Check notehub-email's `.env` configuration

**Vim mode cursor not visible**
- This is normal in normal mode - the border color indicates the mode
- Press `i` to enter insert mode and see the cursor

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit pull requests.
