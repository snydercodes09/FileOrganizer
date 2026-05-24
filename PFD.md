# Product Features Document (PFD): FileOrganizer Suite

## 1. Executive Summary
The **FileOrganizer Suite** is a cross-platform, modular Python CLI toolkit designed to automatically declutter and organize messy directories. Developed to handle both file extension-based categorization and file size-based sorting, the suite guarantees data safety through non-destructive collision resolution and intelligent empty-folder cleanup. It empowers users to quickly regain control over their file systems, whether organizing a cluttered Desktop by file type or segmenting massive media libraries by file size.

## 2. Target Audience
- **Casual PC Users:** Individuals seeking a simple, one-click solution to clean up their Desktop or Downloads folders.
- **Content Creators & Photographers:** Professionals who need to segment large batches of images or videos by size for uploading, processing, or archiving.
- **System Administrators & Developers:** Technical users requiring a modular, tested, and reliable Python script that can be scheduled or customized for server-side file management.

## 3. Core User Stories
- **As a user,** I want to run a script and have all my loose files grouped into logical folders (e.g., Documents, Images, Software) so my workspace is clean.
- **As a content creator,** I want to sort my video and image files by size buckets (e.g., 500KB-1MB, 1MB-10MB) so I can easily find heavy files to delete or compress.
- **As a user with deeply nested folders,** I want an optional "Deep Scan" feature that pulls files out of sub-folders and brings them to the organized root, deleting the leftover empty folders automatically.
- **As a cautious user,** I want to ensure that no files are overwritten if two files share the same name, and I want an audit log to see exactly where my files were moved.

## 4. Detailed Functional Requirements

### 4.1. Module: Core Utilities (`utils.py`)
This shared library powers the core mechanics of both main scripts.
- **Directory Selection (`get_target_directory`)**: Prompts the user for a target directory path. Defaults to the OS-agnostic user Desktop if left blank. Validates path existence.
- **Deep Scan Prompt (`prompt_deep_scan`)**: Pauses execution to ask the user if they want to recursively extract files from sub-directories (Y/N). Defaults to 'N'.
- **Collision Resolution (`resolve_collision`)**: Ensures 100% data safety. If a file being moved shares a name with an existing destination file, it iteratively appends a numeric suffix (e.g., `report_1.pdf`, `report_2.pdf`) until a unique path is secured.
- **Empty Folder Cleanup (`cleanup_empty_folders`)**: Performs a bottom-up (`topdown=False`) recursive traversal of the target directory. It strictly uses `os.rmdir()` to remove *only* empty directories, ensuring no orphaned files are ever deleted.

### 4.2. Feature Set 1: Extension-Based Organizer (`file_organizer.py`)
Organizes files into rigid taxonomic categories based on their extension.
- **Taxonomy Routing**: 
  - `Images`: `.jpg`, `.jpeg`, `.png`, `.gif`, `.svg`, `.heic`
  - `Documents`: `.pdf`, `.docx`, `.doc`, `.txt`, `.xlsx`, `.xls`, `.pptx`
  - `Media`: `.mp4`, `.mkv`
  - `Audio`: `.mp3`, `.wav`, `.ogg`, `.opus`
  - `Archives`: `.zip`, `.rar`, `.7z`, `.7zip`, `.tar.gz`
  - `Code`: `.py`, `.html`, `.css`, `.js`, `.md`
  - `Software`: `.exe`, `.msi`, `.iso`, `.torrent`
  - `Others`: Any unknown extension or file with no extension.
- **Shallow vs. Deep Scan**: By default, only moves root-level files. If Deep Scan is enabled, recursively extracts nested files to the root category folders.
- **Audit Trail**: Prints a live console log of every file moved. Deep Scan outputs include the original nested source path for full traceability.

### 4.3. Feature Set 2: Size-Based Sorter (`size_sorter.py`)
Segments media files by explicit byte-size thresholds.
- **Media Targeting**: Prompts the user to target `[1] Images`, `[2] Videos`, or `[3] Both`. Non-targeted files are entirely ignored.
- **Size Bucketing**: Evaluates `os.stat().st_size` to route files into precise sub-directories:
  - `0-100KB`
  - `100KB-500KB`
  - `500KB-1MB`
  - `1MB-10MB`
  - `10MB-100MB`
  - `Over_100MB`
- **Hierarchical Output**: Nests the bucketing under the media type (e.g., `Images/1MB-10MB/photo.jpg`).

## 5. Non-Functional Requirements
- **Performance**: Must utilize built-in Python `os` and `shutil` libraries for maximum I/O speed. Traversal of massive directories must minimize memory footprint by utilizing generators where applicable.
- **Security & Safety**: Under no circumstances should the script utilize destructive file commands (e.g., `os.remove` or `shutil.rmtree`). Files are *moved*, not copied/deleted, preserving disk space. Empty folder cleanup is restricted to `os.rmdir`.
- **Portability**: Must be OS-agnostic (Windows, macOS, Linux) with zero third-party dependencies (beyond `pytest` for development).
- **Testability**: Must maintain high test coverage via `pytest`, utilizing `tmp_path` fixtures to simulate complex nested directory structures and edge cases (e.g., exact byte boundary math for size sorting).

## 6. User Interface/Experience (UI/UX) Principles
- **CLI Simplicity**: Operations must require minimal keystrokes. Defaulting to the Desktop via a blank `Enter` press reduces friction.
- **Fail-Safe Defaults**: Destructive or highly transformative actions (like Deep Scan) must default to "No" to prevent accidental massive restructuring of nested system folders.
- **Transparency**: The CLI must provide clear, human-readable feedback, terminating with a summary block displaying total files moved, extracted, and empty folders purged.

## 7. Technical Stack Overview
- **Language**: Python 3.9+ (utilizing modern type hinting `from __future__ import annotations`).
- **Standard Libraries**: `os`, `sys`, `shutil`, `pathlib`.
- **Testing Framework**: `pytest` (using parameterized tests and isolated file system fixtures).
- **Version Control**: Git / GitHub.

## 8. Prioritized Feature Roadmap (MoSCoW Method)

### Must Have (Completed)
- [x] Basic root-level file organization by extension.
- [x] Collision-free file moving logic.
- [x] Bottom-up empty directory cleanup.
- [x] Optional recursive Deep Scan feature.
- [x] Modular size-based sorting for specific media types.

### Should Have (Next Phase)
- [ ] **Dry Run Mode (`--dry-run`)**: Allow users to see what *would* happen without actually moving any files.
- [ ] **Custom Configuration via JSON/YAML**: Allow power users to define their own extension-to-category mappings or size buckets without editing source code.

### Could Have (Future Exploration)
- [ ] **Undo Functionality**: Maintain a temporary state ledger allowing the user to type `python file_organizer.py --undo` to revert the last operation.
- [ ] **Duplicate Detection**: Identify true duplicate files via SHA-256 hashing and isolate them into a `Duplicates` folder.
- [ ] **Date-Based Sorter**: A third script (`date_sorter.py`) to organize photos by EXIF creation date (Year/Month/Day).

### Won't Have (Out of Scope)
- [ ] Graphical User Interface (GUI) wrapper. The tool is strictly designed for lightweight CLI execution.
- [ ] Cloud synchronization capabilities (e.g., automatically uploading the `Archives` folder to Google Drive).
