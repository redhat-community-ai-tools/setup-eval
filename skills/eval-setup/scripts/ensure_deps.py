# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Ensure harness-eval-lab dependencies are installed."""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    plugin_root = Path(__file__).resolve().parent.parent.parent.parent
    pyproject = plugin_root / "pyproject.toml"

    if not pyproject.exists():
        print("harness-eval-lab: pyproject.toml not found, skipping dependency check")
        return

    try:
        import harness_eval_lab  # noqa: F401
    except ImportError:
        print("harness-eval-lab: installing dependencies...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(plugin_root)],
            capture_output=True,
        )


if __name__ == "__main__":
    main()
