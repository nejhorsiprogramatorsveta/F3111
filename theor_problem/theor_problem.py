from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Quantum and thermal Ising project launcher")
    parser.add_argument(
        "command",
        nargs="?",
        default="app",
        choices=["app"],
        help="Launch the interactive Streamlit application.",
    )
    args = parser.parse_args()
    if args.command == "app":
        return subprocess.call([sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py")])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
