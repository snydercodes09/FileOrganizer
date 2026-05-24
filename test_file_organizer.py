"""Unit tests for file_organizer.py.

All tests use pytest's ``tmp_path`` fixture so no real files
are touched during the test run.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from file_organizer import (
    deep_scan_files,
    get_category,
    move_files,
    scan_files,
)
from fo_utils import (
    cleanup_empty_folders,
    prompt_deep_scan,
    resolve_collision,
)


# ---------------------------------------------------------------------------
# get_category
# ---------------------------------------------------------------------------


class TestGetCategory:
    """Tests for extension → category mapping."""

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("photo.jpg", "Images"),
            ("photo.JPEG", "Images"),
            ("icon.png", "Images"),
            ("anim.gif", "Images"),
            ("logo.svg", "Images"),
            ("live.heic", "Images"),
        ],
    )
    def test_image_extensions(self, filename: str, expected: str) -> None:
        assert get_category(Path(filename)) == expected

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("report.pdf", "Documents"),
            ("essay.docx", "Documents"),
            ("letter.doc", "Documents"),
            ("notes.txt", "Documents"),
            ("data.xlsx", "Documents"),
            ("sheet.xls", "Documents"),
            ("slides.pptx", "Documents"),
        ],
    )
    def test_document_extensions(self, filename: str, expected: str) -> None:
        assert get_category(Path(filename)) == expected

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("movie.mp4", "Media"),
            ("clip.mkv", "Media"),
        ],
    )
    def test_media_extensions(self, filename: str, expected: str) -> None:
        assert get_category(Path(filename)) == expected

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("song.mp3", "Audio"),
            ("sound.wav", "Audio"),
            ("track.ogg", "Audio"),
            ("voice.opus", "Audio"),
        ],
    )
    def test_audio_extensions(self, filename: str, expected: str) -> None:
        assert get_category(Path(filename)) == expected

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("backup.zip", "Archives"),
            ("data.rar", "Archives"),
            ("archive.7z", "Archives"),
            ("package.7zip", "Archives"),
            ("project.tar.gz", "Archives"),
        ],
    )
    def test_archive_extensions(self, filename: str, expected: str) -> None:
        assert get_category(Path(filename)) == expected

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("script.py", "Code"),
            ("page.html", "Code"),
            ("style.css", "Code"),
            ("app.js", "Code"),
            ("readme.md", "Code"),
        ],
    )
    def test_code_extensions(self, filename: str, expected: str) -> None:
        assert get_category(Path(filename)) == expected

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("setup.exe", "Software"),
            ("installer.msi", "Software"),
            ("image.iso", "Software"),
            ("download.torrent", "Software"),
        ],
    )
    def test_software_extensions(self, filename: str, expected: str) -> None:
        assert get_category(Path(filename)) == expected

    def test_unknown_extension_returns_others(self) -> None:
        assert get_category(Path("mystery.xyz")) == "Others"

    def test_no_extension_returns_others(self) -> None:
        assert get_category(Path("Makefile")) == "Others"


# ---------------------------------------------------------------------------
# resolve_collision
# ---------------------------------------------------------------------------


class TestResolveCollision:
    """Tests for filename collision resolution."""

    def test_no_collision(self, tmp_path: Path) -> None:
        dest = tmp_path / "report.pdf"
        assert resolve_collision(dest) == dest

    def test_single_collision(self, tmp_path: Path) -> None:
        existing = tmp_path / "report.pdf"
        existing.touch()

        result = resolve_collision(existing)
        assert result == tmp_path / "report_1.pdf"

    def test_multiple_collisions(self, tmp_path: Path) -> None:
        (tmp_path / "report.pdf").touch()
        (tmp_path / "report_1.pdf").touch()
        (tmp_path / "report_2.pdf").touch()

        result = resolve_collision(tmp_path / "report.pdf")
        assert result == tmp_path / "report_3.pdf"


# ---------------------------------------------------------------------------
# scan_files
# ---------------------------------------------------------------------------


class TestScanFiles:
    """Tests for non-recursive file scanning."""

    def test_returns_only_files(self, tmp_path: Path) -> None:
        (tmp_path / "file.txt").touch()
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.txt").touch()

        result = scan_files(tmp_path)
        assert len(result) == 1
        assert result[0].name == "file.txt"

    def test_empty_directory(self, tmp_path: Path) -> None:
        assert scan_files(tmp_path) == []


# ---------------------------------------------------------------------------
# deep_scan_files
# ---------------------------------------------------------------------------


class TestDeepScanFiles:
    """Tests for recursive nested-file discovery."""

    def test_finds_deeply_nested_files(self, tmp_path: Path) -> None:
        # Create a 3-level deep structure
        level1 = tmp_path / "a"
        level2 = level1 / "b"
        level3 = level2 / "c"
        level3.mkdir(parents=True)
        (level3 / "deep.jpg").write_text("data")
        (level1 / "shallow.txt").write_text("data")

        result = deep_scan_files(tmp_path)
        names = sorted(p.name for p in result)
        assert names == ["deep.jpg", "shallow.txt"]

    def test_excludes_root_level_files(self, tmp_path: Path) -> None:
        (tmp_path / "root.pdf").write_text("data")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.png").write_text("data")

        result = deep_scan_files(tmp_path)
        assert len(result) == 1
        assert result[0].name == "nested.png"

    def test_empty_subdirectories(self, tmp_path: Path) -> None:
        (tmp_path / "emptydir").mkdir()
        assert deep_scan_files(tmp_path) == []


# ---------------------------------------------------------------------------
# move_files
# ---------------------------------------------------------------------------


class TestMoveFiles:
    """Tests for file categorisation and relocation."""

    def test_files_sorted_into_correct_folders(self, tmp_path: Path) -> None:
        files: list[Path] = []
        for name in ("photo.jpg", "report.pdf", "song.mp3", "app.py"):
            f = tmp_path / name
            f.write_text("content")
            files.append(f)

        moved = move_files(tmp_path, files)

        assert moved == 4
        assert (tmp_path / "Images" / "photo.jpg").exists()
        assert (tmp_path / "Documents" / "report.pdf").exists()
        assert (tmp_path / "Audio" / "song.mp3").exists()
        assert (tmp_path / "Code" / "app.py").exists()

    def test_unknown_extension_goes_to_others(self, tmp_path: Path) -> None:
        f = tmp_path / "data.xyz"
        f.write_text("content")

        move_files(tmp_path, [f])
        assert (tmp_path / "Others" / "data.xyz").exists()

    def test_collision_during_move(self, tmp_path: Path) -> None:
        # Pre-create the Documents folder with an existing report.pdf
        docs = tmp_path / "Documents"
        docs.mkdir()
        (docs / "report.pdf").write_text("original")

        # Create a new report.pdf in the root
        f = tmp_path / "report.pdf"
        f.write_text("duplicate")

        move_files(tmp_path, [f])

        # Original should be untouched, new file gets _1 suffix
        assert (docs / "report.pdf").read_text() == "original"
        assert (docs / "report_1.pdf").read_text() == "duplicate"


# ---------------------------------------------------------------------------
# cleanup_empty_folders
# ---------------------------------------------------------------------------


class TestCleanupEmptyFolders:
    """Tests for empty directory removal."""

    def test_removes_empty_folder(self, tmp_path: Path) -> None:
        empty = tmp_path / "EmptyDir"
        empty.mkdir()

        removed = cleanup_empty_folders(tmp_path)

        assert removed == 1
        assert not empty.exists()

    def test_preserves_non_empty_folder(self, tmp_path: Path) -> None:
        non_empty = tmp_path / "HasFile"
        non_empty.mkdir()
        (non_empty / "keep.txt").touch()

        removed = cleanup_empty_folders(tmp_path)

        assert removed == 0
        assert non_empty.exists()

    def test_mixed_folders(self, tmp_path: Path) -> None:
        (tmp_path / "Empty1").mkdir()
        (tmp_path / "Empty2").mkdir()
        full = tmp_path / "Full"
        full.mkdir()
        (full / "data.bin").touch()

        removed = cleanup_empty_folders(tmp_path)

        assert removed == 2
        assert not (tmp_path / "Empty1").exists()
        assert not (tmp_path / "Empty2").exists()
        assert full.exists()

    def test_removes_nested_empty_dirs_bottom_up(self, tmp_path: Path) -> None:
        """After deep-scan extraction, nested dirs should be removed."""
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)

        removed = cleanup_empty_folders(tmp_path)

        # All three levels (a, a/b, a/b/c) should be gone
        assert removed == 3
        assert not (tmp_path / "a").exists()


# ---------------------------------------------------------------------------
# End-to-end
# ---------------------------------------------------------------------------


class TestFullWorkflow:
    """Integration test: populate dir → organise → verify."""

    def test_end_to_end(self, tmp_path: Path) -> None:
        # Arrange — create several loose files and one pre-existing subdir
        for name in ("pic.png", "vid.mp4", "notes.txt", "backup.zip", "main.py"):
            (tmp_path / name).write_text("data")
        (tmp_path / "ExistingSubdir").mkdir()

        # Act
        files = scan_files(tmp_path)
        assert len(files) == 5  # subdir excluded

        moved = move_files(tmp_path, files)
        assert moved == 5

        removed = cleanup_empty_folders(tmp_path)

        # Assert — files in correct categories
        assert (tmp_path / "Images" / "pic.png").exists()
        assert (tmp_path / "Media" / "vid.mp4").exists()
        assert (tmp_path / "Documents" / "notes.txt").exists()
        assert (tmp_path / "Archives" / "backup.zip").exists()
        assert (tmp_path / "Code" / "main.py").exists()

        # ExistingSubdir was empty → removed; category dirs are not empty → kept
        assert not (tmp_path / "ExistingSubdir").exists()
        assert removed >= 1


# ---------------------------------------------------------------------------
# Deep-scan end-to-end
# ---------------------------------------------------------------------------


class TestDeepScanWorkflow:
    """Integration test: deep scan → extract → organise → cleanup."""

    def test_deep_scan_end_to_end(self, tmp_path: Path) -> None:
        # Root files
        (tmp_path / "root.txt").write_text("root")

        # Nested files at various depths
        sub1 = tmp_path / "ProjectA"
        sub2 = sub1 / "assets"
        sub2.mkdir(parents=True)
        (sub1 / "readme.pdf").write_text("pdf")
        (sub2 / "logo.png").write_text("png")
        (sub2 / "clip.mp4").write_text("mp4")

        sub3 = tmp_path / "Old"
        sub3.mkdir()
        (sub3 / "archive.zip").write_text("zip")

        # Step 1 — deep scan BEFORE root-level moves (collect nested
        # files while no category folders exist yet).
        nested = deep_scan_files(tmp_path)
        assert len(nested) == 4  # readme.pdf, logo.png, clip.mp4, archive.zip

        # Step 2 — shallow scan root files
        root_files = scan_files(tmp_path)
        assert len(root_files) == 1
        moved = move_files(tmp_path, root_files)
        assert moved == 1

        # Step 3 — extract nested files
        extracted = move_files(tmp_path, nested, show_source_path=True)
        assert extracted == 4

        # Step 4 — cleanup
        removed = cleanup_empty_folders(tmp_path)

        # Verify files in correct categories
        assert (tmp_path / "Documents" / "root.txt").exists()
        assert (tmp_path / "Documents" / "readme.pdf").exists()
        assert (tmp_path / "Images" / "logo.png").exists()
        assert (tmp_path / "Media" / "clip.mp4").exists()
        assert (tmp_path / "Archives" / "archive.zip").exists()

        # All nested dirs (ProjectA, ProjectA/assets, Old) should be removed
        assert not (tmp_path / "ProjectA").exists()
        assert not (tmp_path / "Old").exists()
        assert removed >= 3

    def test_deep_scan_collision_handling(self, tmp_path: Path) -> None:
        """Two files with the same name in different subdirs."""
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()
        (d1 / "photo.jpg").write_text("first")
        (d2 / "photo.jpg").write_text("second")

        nested = deep_scan_files(tmp_path)
        extracted = move_files(tmp_path, nested, show_source_path=True)
        assert extracted == 2

        images = tmp_path / "Images"
        assert (images / "photo.jpg").exists()
        assert (images / "photo_1.jpg").exists()
