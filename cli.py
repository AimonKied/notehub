
# cli.py
import os
import argparse
import readline
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
    return f"Notiz '{title}' erstellt."


def remove_note(title):
    filename = os.path.join(NOTES_DIR, f"{title}.txt")
    if os.path.exists(filename):
        os.remove(filename)
        return f"Notiz '{title}' gelöscht."
    else:
        return f"Notiz '{title}' nicht gefunden."


def list_notes():
    ensure_notes_dir()
    notes = [f[:-4] for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]
    if notes:
        out = ["Vorhandene Notizen:"]
        out += [f" - {n}" for n in notes]
        return "\n".join(out)
    else:
        return "Keine Notizen vorhanden."


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
            return f"Notiz '{title}' als erledigt markiert."
        else:
            return f"Notiz '{title}' ist bereits erledigt."
    else:
        return f"Notiz '{title}' nicht gefunden."


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
            "help": (self._help, "Zeige verfügbare Befehle"),
            "exit": (self._exit, "Beende die Shell"),
            "ls": (self._ls, "Listet Dateien im aktuellen Verzeichnis"),
            "pwd": (self._pwd, "Zeigt das aktuelle Verzeichnis (relativ zu notes/)"),
            "cd": (self._cd, "Wechselt das Verzeichnis: cd <path>"),
            "add": (self._add, "Erstellt eine Notiz: add <title> <content>"),
            "remove": (self._remove, "Löscht eine Notiz: remove <title>"),
            "done": (self._done, "Markiert eine Notiz als erledigt: done <title>"),
            "show": (self._show, "Zeigt den Inhalt einer Notiz: show <title>"),
            "list": (self._list, "Listet Notizen im aktuellen Verzeichnis"),
            "mkdir": (self._mkdir, "Erstellt ein Verzeichnis: mkdir <name>"),
            "clear": (self._clear, "Leert die Konsole"),
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
        return "\n".join(lines)

    # ----- command handlers (return strings) -----
    def _help(self, args: List[str]) -> str:
        return self.get_help()

    def _exit(self, args: List[str]) -> str:
        self._running = False
        return "Bye."

    def _ls(self, args: List[str]) -> str:
        try:
            target = self._resolve_path(args[0]) if args else self.cwd
            if not os.path.isdir(target):
                return f"'{args[0]}' ist kein Verzeichnis"
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
                return f"'{args[0]}' ist kein Verzeichnis"
            self.cwd = target
            return ""
        except Exception as e:
            return str(e)

    def _add(self, args: List[str]) -> str:
        if len(args) < 2:
            return "Benutzung: add <title> <content>"
        title = args[0]
        content = " ".join(args[1:])
        try:
            # Create note in current directory
            filename = os.path.join(self.cwd, f"{title}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Notiz '{title}' erstellt."
        except Exception as e:
            return str(e)

    def _remove(self, args: List[str]) -> str:
        if not args:
            return "Benutzung: remove <title>"
        try:
            filename = os.path.join(self.cwd, f"{args[0]}.txt")
            if os.path.exists(filename):
                os.remove(filename)
                return f"Notiz '{args[0]}' gelöscht."
            else:
                return f"Notiz '{args[0]}' nicht gefunden."
        except Exception as e:
            return str(e)

    def _list(self, args: List[str]) -> str:
        try:
            notes = [f[:-4] for f in os.listdir(self.cwd) if f.endswith(".txt")]
            if notes:
                out = ["Notizen in diesem Verzeichnis:"]
                out += [f" - {n}" for n in sorted(notes)]
                return "\n".join(out)
            else:
                return "Keine Notizen in diesem Verzeichnis."
        except Exception as e:
            return str(e)

    def _done(self, args: List[str]) -> str:
        if not args:
            return "Benutzung: done <title>"
        try:
            filename = os.path.join(self.cwd, f"{args[0]}.txt")
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                if "[DONE]" not in content:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content.rstrip() + "\n[DONE]\n")
                    return f"Notiz '{args[0]}' als erledigt markiert."
                else:
                    return f"Notiz '{args[0]}' ist bereits erledigt."
            else:
                return f"Notiz '{args[0]}' nicht gefunden."
        except Exception as e:
            return str(e)

    def _show(self, args: List[str]) -> str:
        if not args:
            return "Benutzung: show <title>"
        try:
            filename = os.path.join(self.cwd, f"{args[0]}.txt")
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                return f"=== {args[0]} ===\n{content}"
            else:
                return f"Notiz '{args[0]}' nicht gefunden."
        except Exception as e:
            return str(e)

    def _mkdir(self, args: List[str]) -> str:
        if not args:
            return "Benutzung: mkdir <name>"
        try:
            path = self._resolve_path(args[0])
            os.makedirs(path, exist_ok=True)
            return f"Verzeichnis '{args[0]}' erstellt."
        except Exception as e:
            return str(e)

    def _clear(self, args: List[str]) -> str:
        # clear screen for interactive use
        return "\x1bc"

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
            return f"Befehl nicht gefunden: {cmd}"

    def interactive(self):
        """Start the interactive shell loop (uses readline)."""
        self._running = True
        # enable simple history across sessions
        try:
            histfile = os.path.expanduser("~/.notehub_history")
            readline.read_history_file(histfile)
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
                    # allow "+clear+" to actually clear by printing control
                    if out == "\x1bc":
                        print(out, end="")
                    else:
                        print(out)
        finally:
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

    subparsers.add_parser("list")
    subparsers.add_parser("shell", help="Starte interaktive Shell")

    parsed = parser.parse_args(args)

    if parsed.command == "add":
        print(add_note(parsed.title, parsed.content))
    elif parsed.command == "remove":
        print(remove_note(parsed.title))
    elif parsed.command == "list":
        print(list_notes())
    elif parsed.command == "shell":
        shell = Shell()
        shell.interactive()
    else:
        parser.print_help()

