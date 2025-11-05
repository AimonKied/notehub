# main.py
import sys
from cli import handle_cli
from gui import run_gui

def main():
    if len(sys.argv) > 1:
        # Command Line Mode with arguments
        handle_cli(sys.argv[1:])
    else:
        # GUI Mode (default) with integrated shell
        run_gui()

if __name__ == "__main__":
    main()

