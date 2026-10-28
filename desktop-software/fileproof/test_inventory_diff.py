import tempfile
import unittest
from pathlib import Path
from inventory_diff import inventory_additions


class InventoryDiffTests(unittest.TestCase):
    def test_new_file_and_nested_path_and_manifest_exclusion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "nested").mkdir()
            (root / "nested" / "original.txt").write_text("original", encoding="utf-8")
            (root / "nested" / "added.txt").write_text("added", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            additions, errors = inventory_additions(root, {"nested/original.txt"}, manifest)
            self.assertEqual(additions, [{"path": "nested/added.txt", "status": "ADDED"}])
            self.assertEqual(errors, [])

    def test_symlinked_directory_is_not_traversed(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as other:
            root = Path(directory)
            (Path(other) / "secret.txt").write_text("do not read", encoding="utf-8")
            try:
                (root / "external").symlink_to(other, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation unavailable")
            additions, errors = inventory_additions(root, set(), root / "manifest.json")
            self.assertEqual(additions, [{"path": "external", "status": "UNTRACKED_LINK"}])
            self.assertEqual(errors, [])

    def test_link_to_manifest_is_still_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            try:
                (root / "link.json").symlink_to(manifest)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation unavailable")
            additions, errors = inventory_additions(root, set(), manifest)
            self.assertEqual(additions, [{"path": "link.json", "status": "UNTRACKED_LINK"}])
            self.assertEqual(errors, [])

    def test_missing_folder_is_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                inventory_additions(Path(directory) / "missing", set(), Path(directory) / "manifest.json")


if __name__ == "__main__":
    unittest.main()
