"""Entry point for running phone_mcp as a module: python -m phone_mcp"""

import sys


def _main():
    # Route to main.py's main() which handles both CLI and serve modes
    from main import main
    main()


if __name__ == "__main__":
    _main()

