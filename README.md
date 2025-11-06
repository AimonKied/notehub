# NoteHub

A lightweight note management system featuring an interactive shell interface, GUI support, and seamless email integration. Built for developers who prefer the command line but want the flexibility of a graphical interface.

## Features

- 📝 GUI and CLI mode
- 🗂️ Folder organization
- ✅ Todo checkboxes
- 🐚 Interactive shell
- 📧 Email integration

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
```

## Email Setup

Requires [notehub-email](../notehub-email) configured in sibling directory.

## Notes Format

Notes are `.txt` files in `notes/` directory.

Todo checkboxes:
```
[ ] Unchecked
[x] Checked
```

Toggle with: `check <note> <line-number>`
