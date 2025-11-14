# cli.py
import os
import argparse
import shlex
import socket
from typing import List

NOTES_DIR = "notes"


def ensure_notes_dir():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)


def add_note(title, content):
    ensure_notes_dir()
    filename = os.path.join(NOTES_DIR, f"{title}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Note '{title}' created."


def remove_note(title):
    filename = os.path.join(NOTES_DIR, f"{title}.txt")
    if os.path.exists(filename):
        os.remove(filename)
        return f"Note '{title}' deleted."
    else:
        return f"Note '{title}' not found."


def list_notes():
    ensure_notes_dir()
    notes = [f[:-4] for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]
    if notes:
        out = ["existing notes:"]
        out += [f" - {n}" for n in notes]
        return "\n".join(out)
    else:
        return "No notes available."


def mark_note_done(title):
    """Mark a note as done by appending '[DONE]' to its content."""
    ensure_notes_dir()
    filename = os.path.join(NOTES_DIR, f"{title}.txt")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        if "[DONE]" not in content:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content.rstrip() + "\n[DONE]\n")
            return f"Note '{title}' marked as done."
        else:
            return f"Note '{title}' is already done."
    else:
        return f"Note '{title}' not found."


def email_note(title, to_email: str = None):
    """Send a specific note via email using notehub-email.

    If `to_email` is provided it overrides the TO_EMAIL value from the
    notehub-email/.env configuration.
    """
    ensure_notes_dir()

    # Find the note file
    note_path = None
    for root, dirs, files in os.walk(NOTES_DIR):
        for file in files:
            if file == f"{title}.txt":
                note_path = os.path.join(root, file)
                break
        if note_path:
            break

    if not note_path:
        return f"Note '{title}' not found."

    # Path to notehub-email directory
    email_script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "notehub-email")
    email_script = os.path.join(email_script_dir, "send_note.py")

    if not os.path.exists(email_script):
        return f"Error: Email sender not found at {email_script}"

    # Import the email functions
    import sys
    sys.path.insert(0, email_script_dir)

    try:
        from send_note import load_env, read_note, send_email

        # Load environment variables
        env = load_env()

        # Require FROM_EMAIL and EMAIL_PASSWORD; TO_EMAIL is optional here
        # because a recipient may be provided directly to this function.
        required_vars = ["FROM_EMAIL", "EMAIL_PASSWORD"]
        missing_vars = [var for var in required_vars if not env.get(var)]

        if missing_vars:
            return f"Error: Missing email configuration: {', '.join(missing_vars)}\nPlease configure notehub-email/.env file."

        # Read note content
        content = read_note(note_path)
        if not content:
            return f"Error: Could not read note '{title}'."

        # Get configuration
        from_email = env["FROM_EMAIL"]
        password = env["EMAIL_PASSWORD"]
        env_to_email = env.get("TO_EMAIL")

        # Resolve final recipient: prefer function argument, then env
        final_to_email = to_email if to_email else env_to_email
        if not final_to_email:
            return "Error: No recipient specified. Provide TO_EMAIL in notehub-email/.env or pass an email address to send."

        smtp_server = env.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(env.get("SMTP_PORT", "587"))
        smtp_username = env.get("SMTP_USERNAME")

        # Prepare subject
        subject = f"Notehub Note: {title}"

        # Send email
        print(f"📧 Sending note '{title}' to {final_to_email}...")
        success = send_email(
            subject=subject,
            body=content,
            from_email=from_email,
            to_email=final_to_email,
            password=password,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            username=smtp_username,
        )

        if success:
            return f"✅ Note '{title}' sent successfully to {final_to_email}"
        else:
            return f"❌ Failed to send note '{title}'"

    except ImportError as e:
        return f"Error: Could not import email sender: {e}"
    except Exception as e:
        return f"Error sending email: {e}"


class Shell:
    """A simple in-app shell with a Bash-like prompt.
    Exposes non-interactive methods for testing and an interactive
    loop that uses readline for line editing and history.
    """

    def __init__(self):
        # Sandbox: all operations are restricted to notes/ directory
        ensure_notes_dir()
        self.sandbox_root = os.path.abspath(NOTES_DIR)
        self.cwd = self.sandbox_root  # start in notes/
        self.user = os.getenv("USER") or os.getenv("USERNAME") or "user"
        self.host = socket.gethostname().split(".")[0]
        # command name -> (function, help text)
        self.commands = {
            "help": (self._help, "Show available commands"),
            "exit": (self._exit, "Exit the shell"),
            "ls": (self._ls, "List files in current directory"),
            "pwd": (self._pwd, "Show current directory (relative to notes/)"),
            "cd": (self._cd, "Change directory: cd <path>"),
            "add": (self._add, "Create a note: add <title>"),
            "edit": (self._edit, "Edit a note: edit <title>"),
            "remove": (self._remove, "Delete a note or folder: remove <title> | remove -d <folder>"),
            "done": (self._done, "Mark a note as done: done <title>"),
            "check": (self._check, "Toggle todo checkbox: check <title> <line_number> [line_number2 ...]"),
            "show": (self._show, "Show note content: show <title>"),
            "list": (self._list, "List notes in current directory"),
            "mkdir": (self._mkdir, "Create a directory: mkdir <name>"),
            "clear": (self._clear, "Clear the console"),
            "send": (self._send, "Send a note via email: send <title> [to_email]"),
        }
        self._running = False

    def _get_relative_path(self, path: str) -> str:
        """Get path relative to sandbox root for display."""
        if path == self.sandbox_root:
            return "/"
        return "/" + os.path.relpath(path, self.sandbox_root)

    def _resolve_path(self, user_path: str) -> str:
        """Resolve user path within sandbox, preventing escape."""
        if user_path.startswith("/"):
            # absolute path within sandbox
            target = os.path.normpath(os.path.join(self.sandbox_root, user_path.lstrip("/")))
        else:
            # relative to current directory
            target = os.path.normpath(os.path.join(self.cwd, user_path))
        
        # Ensure target is within sandbox
        if not target.startswith(self.sandbox_root):
            raise ValueError("Zugriff außerhalb der notes/ Umgebung nicht erlaubt")
        return target

    @property
    def prompt(self) -> str:
        # mimic bash look: user@host:cwd$ 
        rel_path = self._get_relative_path(self.cwd)
        return f"{self.user}@{self.host}:{rel_path}$ "

    def get_help(self) -> str:
        lines = [f"{name}\t- {meta[1]}" for name, meta in self.commands.items()]
        lines.append("\nGUI Features:")
        lines.append("Ctrl+M\t- Toggle Vim mode in text editor")
        lines.append("\nFor detailed Vim keybindings, type: help vim")
        return "\n".join(lines)

    # ----- command handlers (return strings) -----
    def _help(self, args: List[str]) -> str:
        # Special handling for "help vim"
        if args and args[0].lower() == "vim":
            return self._get_vim_help()
        return self.get_help()
    
    def _get_vim_help(self) -> str:
        """Return detailed Vim mode help."""
        help_text = """Vim Mode Keybindings
====================

Activation:
  Ctrl+M         - Toggle Vim mode on/off (works in editor and command line)
  Button         - Click "Vim Mode" button

Visual Indicators:
  Blue border    - Normal mode (navigation)
  Green border   - Insert mode (editing)

Movement (Normal Mode):
  h/j/k/l        - left/down/up/right
  w              - next word start
  b              - previous word start
  e              - next word end
  0              - start of line
  ^              - first non-blank character
  $              - end of line
  gg             - go to top of document
  G              - go to bottom of document
  Ctrl+U         - page up
  Ctrl+D         - page down

Insert Mode:
  i              - insert before cursor
  a              - insert after cursor
  I              - insert at start of line
  A              - insert at end of line
  o              - open new line below
  O              - open new line above
  ESC            - return to normal mode
  kj             - return to normal mode (alternative to ESC)

Editing (Normal Mode):
  x              - delete character under cursor
  X              - delete character before cursor
  dd             - delete current line
  D              - delete to end of line
  yy             - copy current line
  p              - paste after cursor/line
  P              - paste before cursor/line
  cc             - change (delete and insert) current line
  C              - change to end of line
  u              - undo
  Ctrl+R         - redo

Saving:
  Enter          - save and exit edit mode (Normal mode only)
"""
        return help_text

    def _exit(self, args: List[str]) -> str:
        self._running = False
        return "Bye."

    def _ls(self, args: List[str]) -> str:
        try:
            target = self._resolve_path(args[0]) if args else self.cwd
            if not os.path.isdir(target):
                return f"'{args[0]}' is not a directory"
            entries = os.listdir(target)
            if not entries:
                return ""
            # Mark directories with /
            result = []
            for e in sorted(entries):
                full = os.path.join(target, e)
                if os.path.isdir(full):
                    result.append(e + "/")
                else:
                    result.append(e)
            return "\n".join(result)
        except Exception as e:
            return str(e)

    def _pwd(self, args: List[str]) -> str:
        return self._get_relative_path(self.cwd)

    def _cd(self, args: List[str]) -> str:
        try:
            if not args or args[0] == "~":
                # cd without args or cd ~ returns to sandbox root
                self.cwd = self.sandbox_root
                return ""
            target = self._resolve_path(args[0])
            if not os.path.isdir(target):
                return f"'{args[0]}' is not a directory"
            self.cwd = target
            return ""
        except Exception as e:
            return str(e)

    def _add(self, args: List[str]) -> str:
        if len(args) < 2:
            return "Usage: add <title> <content>"
        title = args[0]
        content = " ".join(args[1:])
        try:
            # Create note in current directory
            filename = os.path.join(self.cwd, f"{title}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Note '{title}' created."
        except Exception as e:
            return str(e)

    def _edit(self, args: List[str]) -> str:
        if len(args) < 2:
            return "Usage: edit <title> <text> [--replace]"
        
        title = args[0]
        filename = os.path.join(self.cwd, f"{title}.txt")
        
        try:
            # Check if --replace flag is present
            if "--replace" in args:
                replace_mode = True
                # Remove --replace from args to get the text
                text_args = [a for a in args[1:] if a != "--replace"]
                new_text = " ".join(text_args)
            else:
                replace_mode = False
                new_text = " ".join(args[1:])
            
            if not os.path.exists(filename):
                return f"Note '{title}' not found. Use 'add' to create."
            
            if replace_mode:
                # Replace entire content
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(new_text)
                return f"Note '{title}' replaced."
            else:
                # Append to existing content
                with open(filename, "r", encoding="utf-8") as f:
                    existing = f.read()
                with open(filename, "w", encoding="utf-8") as f:
                    # Add space or newline if content exists
                    if existing and not existing.endswith("\n"):
                        f.write(existing + "\n" + new_text)
                    else:
                        f.write(existing + new_text)
                return f"Text added to note '{title}'."
        except Exception as e:
            return str(e)

    def _remove(self, args: List[str]) -> str:
        if not args:
            return "Usage: remove <title> or remove -d <folder>"
        
        try:
            # Check if folder flag is present
            is_folder = False
            target_name = args[0]
            
            if args[0] in ["-d", "--folder", "--dir"]:
                is_folder = True
                if len(args) < 2:
                    return "Usage: remove -d <folder>"
                target_name = args[1]
            
            if is_folder:
                # Remove folder
                folder_path = self._resolve_path(target_name)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    import shutil
                    shutil.rmtree(folder_path)
                    return f"Folder '{target_name}' and its content deleted."
                else:
                    return f"Folder '{target_name}' not found."
            else:
                # Remove note file
                filename = os.path.join(self.cwd, f"{target_name}.txt")
                if os.path.exists(filename):
                    os.remove(filename)
                    return f"Note '{target_name}' deleted."
                else:
                    return f"Note '{target_name}' not found."
        except Exception as e:
            return str(e)

    def _list(self, args: List[str]) -> str:
        try:
            notes = [f[:-4] for f in os.listdir(self.cwd) if f.endswith(".txt")]
            if notes:
                out = ["Notes in this directory:"]
                out += [f" - {n}" for n in sorted(notes)]
                return "\n".join(out)
            else:
                return "No notes in this directory."
        except Exception as e:
            return str(e)

    def _done(self, args: List[str]) -> str:
        if not args:
            return "Usage: done <title>"
        try:
            filename = os.path.join(self.cwd, f"{args[0]}.txt")
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                if "[DONE]" not in content:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content.rstrip() + "\n[DONE]\n")
                    return f"Note '{args[0]}' marked as done."
                else:
                    return f"Note '{args[0]}' is already done."
            else:
                return f"Note '{args[0]}' not found."
        except Exception as e:
            return str(e)

    def _check(self, args: List[str]) -> str:
        if len(args) < 2:
            return "Usage: check <title> <line_number> [line_number2 ...]"
        try:
            title = args[0]
            line_numbers = [int(arg) for arg in args[1:]]
            filename = os.path.join(self.cwd, f"{title}.txt")
            
            if not os.path.exists(filename):
                return f"Note '{title}' not found."
            
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            results = []
            modified = False
            
            for line_num in line_numbers:
                if line_num < 1 or line_num > len(lines):
                    results.append(f"Line {line_num} out of range (1-{len(lines)})")
                    continue
                
                # Line numbers are 1-based, array is 0-based
                line_idx = line_num - 1
                line = lines[line_idx]
                
                # Toggle checkbox
                if "[ ]" in line:
                    lines[line_idx] = line.replace("[ ]", "[x]", 1)
                    results.append(f"Line {line_num} checked")
                    modified = True
                elif "[x]" in line:
                    lines[line_idx] = line.replace("[x]", "[ ]", 1)
                    results.append(f"Line {line_num} unchecked")
                    modified = True
                else:
                    results.append(f"Line {line_num} is not a todo item (missing [ ] or [x])")
            
            # Write back if any changes were made
            if modified:
                with open(filename, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            
            return "\n".join(results)
        except ValueError:
            return "All line numbers must be integers."
        except Exception as e:
            return str(e)

    def _show(self, args: List[str]) -> str:
        if not args:
            return "Usage: show <title>"
        try:
            filename = os.path.join(self.cwd, f"{args[0]}.txt")
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                return f"=== {args[0]} ===\n{content}"
            else:
                return f"Note '{args[0]}' not found."
        except Exception as e:
            return str(e)

    def _mkdir(self, args: List[str]) -> str:
        if not args:
            return "Usage: mkdir <name>"
        try:
            path = self._resolve_path(args[0])
            os.makedirs(path, exist_ok=True)
            return f"Directory '{args[0]}' created."
        except Exception as e:
            return str(e)

    def _clear(self, args: List[str]) -> str:
        # clear screen for interactive use
        return "\x1bc"

    def _send(self, args: List[str]) -> str:
        if not args:
            return "Usage: send <title> [to_email]"
        try:
            title = args[0]
            to_email = args[1] if len(args) > 1 else None

            # Get the absolute path relative to sandbox root
            filename = os.path.join(self.cwd, f"{title}.txt")

            # Check if note exists
            if not os.path.exists(filename):
                return f"Note '{title}' not found."

            # Call the email_note function with optional recipient
            return email_note(title, to_email)
        except Exception as e:
            return f"Error: {e}"

    # ----------------------------------------------

    def run_command(self, line: str) -> str:
        """Run a single command line (non-interactive) and return output string."""
        if not line.strip():
            return ""
        try:
            parts = shlex.split(line)
        except Exception:
            parts = line.split()
        cmd = parts[0]
        args = parts[1:]
        if cmd in self.commands:
            func = self.commands[cmd][0]
            try:
                return func(args) or ""
            except Exception as e:
                return str(e)
        else:
            return f"Command not found: {cmd}"

    def interactive(self):
        """Start the interactive shell loop (uses readline)."""
        self._running = True
        histfile = os.path.expanduser("~/.notehub_history")
        readline = None 

        try:
            import readline
            if os.path.exists(histfile):
                readline.read_history_file(histfile)
        except ImportError:
            pass 
        except Exception:
            pass 

        try:
            while self._running:
                try:
                    line = input(self.prompt)
                except EOFError:
                    print()
                    break
                out = self.run_command(line)
                if out:
                    if out == "\x1bc":
                        print(out, end="")
                    else:
                        print(out)
        finally:
            if readline:
                try:
                    readline.write_history_file(histfile)
                except Exception:
                    pass


def handle_cli(args):
    parser = argparse.ArgumentParser(description="NoteHub CLI")
    subparsers = parser.add_subparsers(dest="command")

    # reuse existing commands as subcommands for non-interactive scripts
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("title")
    add_parser.add_argument("content")

    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("title")

    email_parser = subparsers.add_parser("email", help="Send a note via email")
    email_parser.add_argument("title")
    email_parser.add_argument("to_email", nargs="?", help="Optional recipient email address")

    subparsers.add_parser("list")
    subparsers.add_parser("shell", help="Start interactive shell")

    parsed = parser.parse_args(args)

    if parsed.command == "add":
        print(add_note(parsed.title, parsed.content))
    elif parsed.command == "remove":
        print(remove_note(parsed.title))
    elif parsed.command == "email":
        # Pass optional recipient through to the email sender
        to_addr = getattr(parsed, "to_email", None)
        print(email_note(parsed.title, to_addr))
    elif parsed.command == "list":
        print(list_notes())
    elif parsed.command == "shell":
        shell = Shell()
        shell.interactive()
    else:
        parser.print_help()