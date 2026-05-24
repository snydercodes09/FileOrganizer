"""File Organizer — Automated directory decluttering utility.

Scans a target directory, categorises loose files by extension,
moves them into labelled sub-folders, and removes leftover empty
directories.  Supports an optional deep-scan mode that recursively
extracts files from all sub-folders.  Only built-in standard-library
modules are used.

Usage:
    python file_organizer.py
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from fo_utils import (
    cleanup_empty_folders,
    get_target_directory,
    prompt_deep_scan,
    resolve_collision,
)
from size_sorter import get_size_category


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Extension → category mapping.
# Keys are lowercase extensions (with leading dot).
EXTENSION_MAP: dict[str, str] = {
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".svg": "Images",
    ".heic": "Images",
    # Documents
    ".pdf": "Documents",
    ".docx": "Documents",
    ".doc": "Documents",
    ".txt": "Documents",
    ".xlsx": "Documents",
    ".xls": "Documents",
    ".pptx": "Documents",
    # Media (Video)
    ".mp4": "Media",
    ".mkv": "Media",
    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".ogg": "Audio",
    ".opus": "Audio",
    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".7zip": "Archives",
    # .tar.gz is handled as a special case in get_category()
    # Code
    ".py": "Code",
    ".html": "Code",
    ".css": "Code",
    ".js": "Code",
    ".md": "Code",
    # Software
    ".exe": "Software",
    ".msi": "Software",
    ".iso": "Software",
    ".torrent": "Software",
}

DEFAULT_CATEGORY: str = "Others"

# Names of category folders created by this script.
# Used to exclude them from deep-scan traversal.
CATEGORY_NAMES: frozenset[str] = frozenset(
    set(EXTENSION_MAP.values()) | {DEFAULT_CATEGORY}
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def scan_files(directory: Path) -> list[Path]:
    """Return a list of files in the root of *directory* (non-recursive).

    Sub-directories are intentionally ignored so that already-organised
    files are not disturbed.

    Args:
        directory: The directory to scan.

    Returns:
        A list of Path objects representing loose files.
    """
    return [entry for entry in directory.iterdir() if entry.is_file()]


def deep_scan_files(directory: Path) -> list[Path]:
    """Recursively find every file nested inside *directory*'s sub-folders.

    Uses ``os.walk()`` to traverse all levels.  Files that already
    reside directly inside a known category folder at the root level
    are skipped so they are not re-processed.

    Args:
        directory: The root target directory.

    Returns:
        A list of Path objects for every nested file discovered,
        excluding files that sit directly in the root.
    """
    nested_files: list[Path] = []

    for dirpath_str, _dirnames, filenames in os.walk(directory):
        dirpath = Path(dirpath_str)

        # Skip the root directory itself — those files are handled
        # by the normal (shallow) scan_files() call.
        if dirpath == directory:
            continue

        for filename in filenames:
            nested_files.append(dirpath / filename)

    return nested_files


def get_category(file_path: Path) -> str:
    """Determine the category folder name for a given file.

    Handles the special `.tar.gz` compound extension before falling
    back to the standard single-dot suffix lookup.

    Args:
        file_path: Path to the file whose category is needed.

    Returns:
        A category string such as ``"Images"`` or ``"Others"``.
    """
    # Special case: compound extension .tar.gz
    if file_path.name.lower().endswith(".tar.gz"):
        return "Archives"

    extension: str = file_path.suffix.lower()
    return EXTENSION_MAP.get(extension, DEFAULT_CATEGORY)


def move_files(
    directory: Path,
    files: list[Path],
    *,
    show_source_path: bool = False,
    sort_by_size: bool = False,
) -> int:
    """Move *files* into categorised sub-folders under *directory*.

    Category folders are created on demand.  Filename collisions are
    resolved by appending a numeric suffix.

    Args:
        directory: The root directory that will contain category folders.
        files: The list of file paths to organise.
        show_source_path: If ``True``, print the full original path
            of each file (useful for deep-scan audit trails).

    Returns:
        The number of files successfully moved.
    """
    moved_count: int = 0

    for file_path in files:
        category: str = get_category(file_path)
        category_dir: Path = directory / category

        if sort_by_size:
            try:
                stat_info = file_path.stat()
                size_bucket = get_size_category(stat_info.st_size)
                category_dir = category_dir / size_bucket
            except OSError as exc:
                print(f"  Warning: Cannot read size of '{file_path.name}': {exc}")

        # Create the category folder if it does not exist yet.
        category_dir.mkdir(parents=True, exist_ok=True)

        dest_path: Path = category_dir / file_path.name

        # Handle potential filename collisions.
        dest_path = resolve_collision(dest_path)

        try:
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
            if show_source_path:
                print(
                    f"  Extracted: {file_path}"
                    f"  →  {category_dir.relative_to(directory)}/{dest_path.name}"
                )
            else:
                print(
                    f"  Moved: {file_path.name}"
                    f"  →  {category_dir.relative_to(directory)}/{dest_path.name}"
                )
        except OSError as exc:
            print(f"  Warning: Could not move '{file_path.name}': {exc}")

    return moved_count


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the full file-organisation workflow.

    1. Get and validate the target directory.
    2. Ask whether to enable deep-scan mode.
    3. Scan for loose files (and nested files if deep scan is on).
    4. Move files into category folders.
    5. Clean up empty directories (bottom-up).
    6. Print a summary.
    """
    print("=" * 55)
    print("  File Organizer — Automated Directory Cleanup")
    print("=" * 55)
    print()

    # Step 1 — Target directory
    directory: Path = get_target_directory()
    print(f"\nTarget directory: {directory}\n")

    # Step 2 — Deep-scan prompt (before any file moves)
    deep_scan: bool = prompt_deep_scan()
    print()

    # Step 2.5 — Size-sort prompt
    sort_by_size: bool = input(
        "Do you also want to sort files by size? (Y/N): "
    ).strip().lower() == "y"
    print()

    # Step 3 — Collect files to organise
    files: list[Path] = scan_files(directory)
    moved_count: int = 0
    extracted_count: int = 0

    # If deep scan is enabled, collect nested files NOW — before any
    # root-level moves create new category folders whose contents
    # would otherwise be re-discovered by os.walk().
    nested_files: list[Path] = []
    if deep_scan:
        nested_files = deep_scan_files(directory)

    # Step 4a — Move root-level files
    if files:
        print(f"Found {len(files)} root-level file(s) to organise.\n")
        print("Moving root-level files …")
        moved_count = move_files(directory, files, sort_by_size=sort_by_size)
    else:
        print("No loose root-level files found.")

    # Step 4b — Extract nested files if deep scan is on
    if deep_scan:
        if nested_files:
            print(
                f"\nDeep scan found {len(nested_files)} nested file(s). "
                "Extracting …"
            )
            extracted_count = move_files(
                directory, nested_files, show_source_path=True, sort_by_size=sort_by_size
            )
        else:
            print("\nDeep scan: no nested files found.")

    total_moved: int = moved_count + extracted_count

    if total_moved == 0:
        print("\nNothing to organise — the directory is already tidy!")
        return

    # Step 5 — Clean up empty folders (bottom-up recursive)
    print("\nCleaning up empty folders …")
    removed_count: int = cleanup_empty_folders(directory)

    # Step 6 — Summary
    print("\n" + "-" * 55)
    print("  Summary")
    print("-" * 55)
    print(f"  Root files moved     : {moved_count}")
    if deep_scan:
        print(f"  Nested files extracted: {extracted_count}")
    print(f"  Empty folders removed: {removed_count}")
    print("-" * 55)
    print("Done! Your directory is now organised. ✓")


if __name__ == "__main__":
    main()
