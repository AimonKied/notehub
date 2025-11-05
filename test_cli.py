from cli import Shell

def main():
    s = Shell()
    help_text = s.get_help()
    print("HELP_OUTPUT_START")
    print(help_text)
    print("HELP_OUTPUT_END")

if __name__ == "__main__":
    main()
