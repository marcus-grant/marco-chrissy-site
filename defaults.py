"""Default path constants (mockable for tests)."""

from pathlib import Path


def get_output_dir() -> Path:
    """Get the default output directory path.

    Returns:
        Path object representing the output directory.
    """
    return Path("output")


def get_shared_template_paths() -> list[Path]:
    """Get default shared template directory paths.

    Returns:
        List of Path objects for shared template directories.
    """
    return [
        Path("themes/shared/templates"),
        Path("themes/shared/components"),
    ]


def get_shared_css_paths() -> list[Path]:
    """Get default shared CSS directory paths.

    Returns:
        List of Path objects for shared CSS directories.
    """
    return [
        Path("themes/shared/css"),
    ]
