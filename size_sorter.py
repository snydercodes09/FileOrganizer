"""Size Sorter — Automated file size sorter.

Scans a target directory, extracts Images or Videos (or both),
and moves them into size-based sub-folders.
"""

from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path

from fo_utils import (
    cleanup_empty_folders,
    get_target_directory,
    prompt_deep_scan,
    resolve_collision,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".heic"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"}


def get_size_category(size_bytes: int) -> str:
    """Determine the size bucket for a given file size in bytes."""
    # 100KB
    if size_bytes < 100 * 1024:
        return "0-100KB"
    # 500KB
    if size_bytes < 500 * 1024:
        return "100KB-500KB"
    # 1MB
    if size_bytes < 1 * 1024 * 1024:
        return "500KB-1MB"
    # 10MB
    if size_bytes < 10 * 1024 * 1024:
        return "1MB-10MB"
    # 100MB
    if size_bytes <= 100 * 1024 * 1024:
        return "10MB-100MB"
    # >100MB
    return "Over_100MB"


def get_file_type_category(file_path: Path, sort_images: bool, sort_videos: bool) -> str | None:
    """Return 'Images', 'Videos', or None if it should be skipped."""
    ext = file_path.suffix.lower()
    if sort_images and ext in IMAGE_EXTENSIONS:
        return "Images"
    if sort_videos and ext in VIDEO_EXTENSIONS:
        return "Videos"
    return None


def scan_files(directory: Path) -> list[Path]:
    """Return non-recursive list of files."""
    return [entry for entry in directory.iterdir() if entry.is_file()]


def deep_scan_files(directory: Path) -> list[Path]:
    """Recursively find every nested file."""
    nested_files: list[Path] = []
    
    # Simple recursive walk
    # Note: we don't try to exclude category names here since the names are variable,
    # we just collect everything. We'll filter later or skip files that don't match.
    for dirpath, _, filenames in os.walk(directory):
        d_path = Path(dirpath)
        if d_path == directory:
            continue
        for filename in filenames:
            nested_files.append(d_path / filename)

    return nested_files


def move_files(
    directory: Path,
    files: list[Path],
    sort_images: bool,
    sort_videos: bool,
    *,
    show_source_path: bool = False,
) -> int:
    """Move *files* into categorised size sub-folders under *directory*."""
    moved_count: int = 0

    for file_path in files:
        type_category = get_file_type_category(file_path, sort_images, sort_videos)
        if not type_category:
            continue

        try:
            stat_info = file_path.stat()
        except OSError as exc:
            print(f"  Warning: Cannot read size of '{file_path.name}': {exc}")
            continue

        size_category = get_size_category(stat_info.st_size)
        
        # Eg: Images/1MB-10MB
        category_dir: Path = directory / type_category / size_category
        category_dir.mkdir(parents=True, exist_ok=True)

        dest_path: Path = category_dir / file_path.name

        # Prevent source existing inside destination or overwriting itself
        if file_path.resolve() == dest_path.resolve():
            continue

        dest_path = resolve_collision(dest_path)

        try:
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
            if show_source_path:
                print(f"  Extracted: {file_path}  →  {type_category}/{size_category}/{dest_path.name}")
            else:
                print(f"  Moved: {file_path.name}  →  {type_category}/{size_category}/{dest_path.name}")
        except OSError as exc:
            print(f"  Warning: Could not move '{file_path.name}': {exc}")

    return moved_count


def prompt_sort_type() -> tuple[bool, bool]:
    """Ask what to sort. Returns (sort_images, sort_videos)."""
    print("\nWhat would you like to sort by size?")
    print("  [1] Images")
    print("  [2] Videos")
    print("  [3] Both")
    
    while True:
        resp = input("Select an option (1/2/3): ").strip()
        if resp == "1":
            return True, False
        if resp == "2":
            return False, True
        if resp == "3":
            return True, True
        print("Invalid choice. Please enter 1, 2, or 3.")


def main() -> None:
    print("=" * 55)
    print("  Size Sorter — Automated Size Organizer")
    print("=" * 55)
    print()

    directory: Path = get_target_directory()
    print(f"\nTarget directory: {directory}")

    sort_images, sort_videos = prompt_sort_type()

    print()
    deep_scan: bool = prompt_deep_scan()
    print()

    files: list[Path] = scan_files(directory)
    
    nested_files: list[Path] = []
    if deep_scan:
        nested_files = deep_scan_files(directory)

    moved_count: int = 0
    extracted_count: int = 0

    if files:
        print(f"Checking {len(files)} root-level file(s) ...")
        moved_count = move_files(directory, files, sort_images, sort_videos)
    else:
        print("No loose root-level files found.")

    if deep_scan:
        if nested_files:
            print(f"\nChecking {len(nested_files)} nested file(s) for extraction ...")
            extracted_count = move_files(
                directory, nested_files, sort_images, sort_videos, show_source_path=True
            )
        else:
            print("\nDeep scan: no nested files found.")

    total_moved: int = moved_count + extracted_count

    if total_moved == 0:
        print("\nNo matching files found to organize.")
        return

    print("\nCleaning up empty folders …")
    removed_count: int = cleanup_empty_folders(directory)

    print("\n" + "-" * 55)
    print("  Summary")
    print("-" * 55)
    print(f"  Root files moved     : {moved_count}")
    if deep_scan:
        print(f"  Nested files extracted: {extracted_count}")
    print(f"  Empty folders removed: {removed_count}")
    print("-" * 55)
    print("Done! Your directory is now size-sorted. ✓")


if __name__ == "__main__":
    import os
    main()
