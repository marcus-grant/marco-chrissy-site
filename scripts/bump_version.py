#!/usr/bin/env python3
"""Bump semantic version in project files.

Usage:
    python scripts/bump_version.py patch   # 0.2.4 -> 0.2.5
    python scripts/bump_version.py minor   # 0.2.4 -> 0.3.0
    python scripts/bump_version.py major   # 0.2.4 -> 1.0.0
"""

import re
import sys
from pathlib import Path

VERSION_FILES = [
    ("pyproject.toml", r'version = "(\d+\.\d+\.\d+)"'),
    ("galleria/__main__.py", r'version="(\d+\.\d+\.\d+)"'),
]


def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse version string into (major, minor, patch) tuple."""
    parts = version_str.split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple as string."""
    return f"{major}.{minor}.{patch}"


def bump_version(current: tuple[int, int, int], bump_type: str) -> tuple[int, int, int]:
    """Bump version according to semver rules."""
    major, minor, patch = current
    if bump_type == "major":
        return (major + 1, 0, 0)
    elif bump_type == "minor":
        return (major, minor + 1, 0)
    elif bump_type == "patch":
        return (major, minor, patch + 1)
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    match = re.search(r'version = "(\d+\.\d+\.\d+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def update_file(filepath: str, pattern: str, old_version: str, new_version: str) -> bool:
    """Update version in a file. Returns True if file was modified."""
    path = Path(filepath)
    if not path.exists():
        print(f"  [skip] {filepath} (not found)")
        return False

    content = path.read_text()
    old_pattern = pattern.replace(r"(\d+\.\d+\.\d+)", old_version)
    new_replacement = pattern.replace(r"(\d+\.\d+\.\d+)", new_version).replace("\\", "")

    # Simple string replacement
    old_str = old_pattern.replace("\\", "")
    new_str = new_replacement

    if old_str not in content:
        print(f"  [skip] {filepath} (version string not found)")
        return False

    new_content = content.replace(old_str, new_str)
    path.write_text(new_content)
    print(f"  [done] {filepath}")
    return True


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("major", "minor", "patch"):
        print("Usage: python scripts/bump_version.py [major|minor|patch]")
        sys.exit(1)

    bump_type = sys.argv[1]

    # Get current version
    current_str = get_current_version()
    current = parse_version(current_str)

    # Calculate new version
    new = bump_version(current, bump_type)
    new_str = format_version(*new)

    print(f"\nVersion {current_str} -> {new_str}\n")
    print("Updating files:")

    # Update all version files
    updated = 0
    for filepath, pattern in VERSION_FILES:
        if update_file(filepath, pattern, current_str, new_str):
            updated += 1

    print(f"\nUpdated {updated} file(s)")


if __name__ == "__main__":
    main()
