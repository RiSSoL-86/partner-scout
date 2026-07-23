import sys
from pathlib import Path


def configure_python_path() -> None:
    """Add the src package root for direct script execution."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
