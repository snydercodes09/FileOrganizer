# 📂 FileOrganizer Suite

A lightweight, automated Python suite designed to effortlessly declutter and organize directories (such as your Desktop or Downloads folder). The suite includes two main utilities:
1. **Extension-Based Organizer (`file-organizer` / `file_organizer.py`)**: Scans a target directory, categorizes loose files based on their extensions, moves them into designated category subfolders, and safely deletes any leftover empty folders to ensure a perfectly clean workspace.
2. **Size-Based Sorter (`size-sorter` / `size_sorter.py`)**: Segments Images and/or Videos into precise byte-size subfolders under targeted categories.

Both tools feature an **Optional Deep Scan** mode to recursively extract and organize files buried within nested subdirectories.

---

## ✨ Features

- **Automated Organization:** Groups files logically by type into designated category folders:
  - 🖼️ `Images/` (e.g., `.jpg`, `.png`, `.gif`, `.heic`)
  - 📄 `Documents/` (e.g., `.pdf`, `.docx`, `.txt`, `.xlsx`)
  - 🎬 `Media/` (e.g., `.mp4`, `.mkv`)
  - 🎵 `Audio/` (e.g., `.mp3`, `.wav`, `.ogg`)
  - 📦 `Archives/` (e.g., `.zip`, `.rar`, `.7z`)
  - 💻 `Code/` (e.g., `.py`, `.html`, `.css`, `.js`, `.md`)
  - ⚙️ `Software/` (e.g., `.exe`, `.msi`, `.iso`)
  - 📁 `Others/` (default for unrecognized formats)
- **Size-Based Sorting:** Sub-categorizes images and videos by size criteria (e.g., small, medium, large, huge).
- **Collision Handling:** Safely renames duplicate files (e.g., appending `_1`, `_2`) so you never accidentally overwrite or lose data.
- **Empty Folder Cleanup:** Removes leftover empty directories from your workspace automatically (files are **never** deleted).
- **Deep Scan Mode:** Prompts to optionally traverse all nested subdirectories, extracting hidden files into the root-level category folders.
- **Platform Agnostic:** Runs flawlessly on Windows, macOS, and Linux using built-in standard-library modules (`os`, `shutil`, `pathlib`).

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/snydercodes09/FileOrganizer.git
   cd FileOrganizer
   ```

2. **Python Prerequisites:**
   No external dependencies are required to run the main scripts. Python 3.9 or higher is recommended. Check your version with:
   ```bash
   python --version
   ```

3. **Install Globally:**
   To make the tools runnable anywhere in your terminal (command prompt, PowerShell, git bash, etc.) in any directory, install the package in editable mode:
   ```bash
   pip install -e .
   ```
   This exposes the `file-organizer` and `size-sorter` commands globally.

---

## 🚀 How to Run the Tools

You can run the tools either globally (if installed via `pip install -e .`) or directly using the Python scripts.

### A. Extension-Based Organizer
Declutters any directory by grouping files logically by type into clear categories.

* **Run via Global Command:**
  ```bash
  file-organizer
  ```
* **Run via Python Script:**
  ```bash
  python file_organizer.py
  ```

**What to expect during execution:**
1. **Target Directory Prompt**: The script asks for a path to clean up.
   * *Tip*: Press **`Enter`** without typing anything to default to your system's **Desktop**.
2. **Deep Scan Prompt**: It will ask:
   ```text
   Do you want to extract and organise files from all sub-folders as well? (Y/N):
   ```
   * **`N` (Default)**: Declutters only files in the root level of the target directory. Subfolders are untouched.
   * **`Y`**: Recursively crawls all sub-directories, extracts nested files to the main category folders, and safely cleans up empty folders bottom-up.
3. **Size-Sort Prompt**:
   ```text
   Do you also want to sort files by size? (Y/N):
   ```
   * **`N` (Default)**: Organizes files by extension only.
   * **`Y`**: Automatically invokes the size-sorting tool for images and videos inside the target directory.

---

### B. Size-Based Sorter
Segments Images and/or Videos into precise byte-size subfolders under targeted categories.

* **Run via Global Command:**
  ```bash
  size-sorter
  ```
* **Run via Python Script:**
  ```bash
  python size_sorter.py
  ```

**What to expect during execution:**
1. **Target Directory Prompt**: Provide the folder path (or press `Enter` for Desktop).
2. **Sorting Type Selection**:
   ```text
   What would you like to sort by size?
     [1] Images
     [2] Videos
     [3] Both
   Select an option (1/2/3):
   ```
3. **Deep Scan Prompt**: Choose whether to scan recursively (Y/N).

---

## 🧪 Running the Test Suite

The test suite contains **58 comprehensive unit and integration tests** validating file routing, name collision safeguards, and empty folder cleanup. All tests execute inside isolated temporary folders using `pytest` fixtures, keeping your system safe.

### 1. Install Pytest
If you do not have `pytest` installed, run:
```bash
python -m pip install pytest
```

### 2. Execute Tests
Run the full test suite in verbose mode:
```bash
python -m pytest test_file_organizer.py test_size_sorter.py -v
```

---

## 🛡️ Safety & Architecture Safeguards

- **Zero File Deletion**: Under no circumstances will any of your files be deleted. The scripts strictly use `shutil.move` to relocate files.
- **Safe Empty Folder Removal**: Leftover directories are cleaned up bottom-up using `os.rmdir()`. This command is guaranteed by the OS to fail if a folder contains any files or folders, acting as an automatic safety guard.
- **Collision Safeguard**: If a file with the same name already exists in the destination folder, a numeric suffix (e.g., `_1`, `_2`) is appended automatically so no files are overwritten.

---

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes and write additional tests if applicable.
4. Commit your changes (`git commit -m "Add some feature"`).
5. Push to the branch (`git push origin feature/your-feature-name`).
6. Open a Pull Request.

Please ensure all tests pass (`python -m pytest`) before submitting.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
