# NoteHub

A lightweight note management system featuring an interactive shell interface, GUI support, Vim mode, and seamless email integration. Built for developers who prefer the command line but want the flexibility of a graphical interface.

## Features

- 📝 GUI and CLI mode
- ⌨️ Vim mode with full keybindings
- 🗂️ Folder organization
- ✅ Todo checkboxes
- 🐚 Interactive shell
- 📧 Email integration
- 🔧 Resizable interface panels

## Installation

```bash
./install.sh
```

Or run directly:
```bash
python3 main.py
```

## Usage

**GUI Mode:**
```bash
notehub
```

**NoteHub Commands:**
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

**Visual Indicators:**
- Blue border = Normal mode (navigation)
- Green border = Insert mode (editing)

**Common Keybindings:**
- `h/j/k/l` - Move left/down/up/right
- `i/a/o` - Insert mode
- `dd` - Delete line
- `yy/p` - Copy/paste
- `ESC` - Return to normal mode
- `Enter` - Save (normal mode only)

For complete keybinding list: `help vim`

## Email Setup

Requires [notehub-email](https://github.com/AimonKied/notehub-email) configured in sibling directory.

## Notes Format

Notes are `.txt` files in `notes/` directory.

Todo checkboxes:
```
[ ] Unchecked
[x] Checked
```

Toggle with: `check <note> <line-number>`
