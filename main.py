import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Process Manager Elite - GUI and CLI Process Killer")
    parser.add_argument('--cli', action='store_true', help="Run in Command Line Interface mode")
    args = parser.parse_args()

    if args.cli:
        from src.cli.interface import CLIInterface
        app = CLIInterface()
        app.run()
    else:
        from src.gui.app import GUIApp
        app = GUIApp()
        app.mainloop()

if __name__ == "__main__":
    main()
