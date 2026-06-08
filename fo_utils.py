from __future__ import annotations

import os
import sys
from pathlib import Path



def get_target_directory() -> Path:
    """Prompt the user for a target directory and validate it."""
    raw_path: str = input(
        "Enter the target directory path (press Enter for current directory): "
    ).strip()

    if not raw_path:
        directory = Path.cwd()
    else:
        directory = Path(raw_path)

    if not directory.exists():
        print(f"Error: The path '{directory}' does not exist.")
        sys.exit(1)
    if not directory.is_dir():
        print(f"Error: The path '{directory}' is not a directory.")
        sys.exit(1)

    return directory


def prompt_deep_scan() -> bool:
    """Ask the user whether to enable recursive deep-scan mode."""
    response: str = input(
        "Do you want to extract and organise files from all "
        "sub-folders as well? (Y/N): "
    ).strip().lower()
    return response == "y"


def resolve_collision(dest_path: Path) -> Path:
    """Generate a collision-free file path by appending a numeric suffix."""
    if not dest_path.exists():
        return dest_path

    base_stem: str = dest_path.stem
    suffix: str = dest_path.suffix
    directory: Path = dest_path.parent

    counter: int = 1
    while True:
        new_name: str = f"{base_stem}_{counter}{suffix}"
        new_path: Path = directory / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def cleanup_empty_folders(directory: Path) -> int:
    """Recursively delete all empty sub-folders inside *directory* bottom-up."""
    removed_count: int = 0
    for dirpath_str, _, _ in os.walk(directory, topdown=False):
        dirpath = Path(dirpath_str)
        if dirpath == directory:
            continue
        try:
            remaining = list(dirpath.iterdir())
        except PermissionError:
            print(f"  Warning: Cannot access '{dirpath.name}', skipping.")
            continue

        if len(remaining) == 0:
            try:
                os.rmdir(str(dirpath))
                removed_count += 1
                print(f"  Removed empty folder: {dirpath.name}")
            except OSError as exc:
                print(f"  Warning: Could not remove '{dirpath.name}': {exc}")

    return removed_count
