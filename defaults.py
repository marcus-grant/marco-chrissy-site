"""Default path constants (mockable for tests)."""

from pathlib import Path


def get_output_dir() -> Path:
    """Get the default output directory path.

    Returns:
        Path object representing the output directory.
    """
    return Path("output")
