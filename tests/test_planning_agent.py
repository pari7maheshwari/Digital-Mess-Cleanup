import tempfile
import unittest
from pathlib import Path
from unittest import mock

from digital_mess_cleanup.planning import (
    create_cleanup_plan,
    interpret_cleanup_goal,
    validate_cleanup_plan,
    verify_cleanup_output,
)
from digital_mess_cleanup.file_utils import (
    copy_folder_to_location,
    get_desktop_folder,
    resolve_user_path,
)


class CleanupPlanningTests(unittest.TestCase):
    def test_goal_selects_requested_file_categories(self):
        categories, summary = interpret_cleanup_goal(
            "Organize my photos and documents"
        )

        self.assertEqual(categories, {"Images", "Documents"})
        self.assertIn("Documents", summary)

    def test_unknown_goal_defaults_to_all_files(self):
        categories, summary = interpret_cleanup_goal("tidy up my stuff")

        self.assertIn("Other", categories)
        self.assertIn("all file types", summary)

    def test_plan_limits_scope_and_rejects_changed_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()
            image = source / "photo.jpg"
            image.write_bytes(b"image")
            (source / "notes.txt").write_text("notes", encoding="utf-8")

            plan = create_cleanup_plan(
                source,
                root / "output",
                "Organize photos",
                False,
                "fast-model",
                0.2,
            )
            planned_files = validate_cleanup_plan(plan)
            self.assertEqual(planned_files, [image.resolve()])
            self.assertEqual(plan["file_count"], 1)
            self.assertEqual(plan["category_counts"], {"Images": 1})

            (source / "new-photo.jpg").write_bytes(b"new")
            with self.assertRaisesRegex(ValueError, "source folder changed"):
                validate_cleanup_plan(plan)

    def test_plan_rejects_download_folder_inside_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source"
            source.mkdir()
            (source / "note.txt").write_text("input", encoding="utf-8")
            output = source / "organized"

            with self.assertRaisesRegex(ValueError, "outside the source folder"):
                create_cleanup_plan(
                    source,
                    output,
                    "Organize all files",
                    False,
                    "fast-model",
                    0.2,
                )

    def test_existing_download_folder_is_left_untouched_until_download(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()
            (source / "note.txt").write_text("input", encoding="utf-8")
            output = root / "organized"
            output.mkdir()
            (output / "existing.txt").write_text("keep", encoding="utf-8")

            plan = create_cleanup_plan(
                source, output, "all files", False, "fast-model", 0.2
            )
            self.assertTrue((output / "existing.txt").is_file())
            self.assertEqual(Path(plan["output_folder"]), output.resolve())

    def test_verification_checks_copies_and_preserved_originals(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            output = root / "output"
            source.mkdir()
            output.mkdir()
            original = source / "note.txt"
            copied = output / "Documents" / "note.txt"
            original.write_text("safe", encoding="utf-8")
            copied.parent.mkdir()
            copied.write_text("safe", encoding="utf-8")
            rows = [
                {
                    "Original Path": str(original),
                    "Output Path": str(copied),
                    "Status": "Organized",
                }
            ]

            result = verify_cleanup_output(source, output, rows)

            self.assertEqual(result["verified_copies"], 1)
            self.assertEqual(result["originals_preserved"], 1)

    def test_folder_download_uses_numbered_name_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "organized"
            nested = source / "Documents"
            nested.mkdir(parents=True)
            (nested / "note.txt").write_text("keep", encoding="utf-8")
            destination = root / "Downloads" / "organized"

            copied = copy_folder_to_location(source, destination)

            self.assertEqual(copied, destination.resolve())
            self.assertEqual(
                (destination / "Documents" / "note.txt").read_text(
                    encoding="utf-8"
                ),
                "keep",
            )
            self.assertTrue(source.is_dir())
            self.assertFalse(destination.with_suffix(".zip").exists())
            (destination / "keep.txt").write_text("keep", encoding="utf-8")

            second_copy = copy_folder_to_location(source, destination)

            self.assertEqual(
                second_copy,
                destination.with_name("organized_1").resolve(),
            )
            self.assertTrue((destination / "keep.txt").is_file())
            self.assertTrue(
                (second_copy / "Documents" / "note.txt").is_file()
            )

            third_copy = copy_folder_to_location(source, destination)

            self.assertEqual(
                third_copy,
                destination.with_name("organized_2").resolve(),
            )
            self.assertTrue((destination / "keep.txt").is_file())
            self.assertTrue(
                (second_copy / "Documents" / "note.txt").is_file()
            )

    def test_user_paths_expand_environment_variables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict("os.environ", {"CLEANUP_TEST_ROOT": temp_dir}):
                resolved = resolve_user_path(
                    Path("%CLEANUP_TEST_ROOT%") / "organized"
                )

        self.assertEqual(resolved, (Path(temp_dir) / "organized").resolve())

    def test_desktop_lookup_uses_windows_desktop_identifier(self):
        desktop = Path("C:/Users/Test/OneDrive/Desktop")
        with (
            mock.patch("digital_mess_cleanup.file_utils.os.name", "nt"),
            mock.patch(
                "digital_mess_cleanup.file_utils._get_windows_known_folder",
                return_value=desktop,
            ) as get_known_folder,
        ):
            result = get_desktop_folder()

        self.assertEqual(result, desktop)
        get_known_folder.assert_called_once_with(
            0xB4BFCC3A,
            0xDB2C,
            0x424C,
            (0xB0, 0x29, 0x7F, 0xE9, 0x9A, 0x87, 0xC6, 0x41),
        )


if __name__ == "__main__":
    unittest.main()
