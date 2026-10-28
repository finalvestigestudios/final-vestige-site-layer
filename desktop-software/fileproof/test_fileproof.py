import json
import tempfile
import unittest
from pathlib import Path
from fileproof import create_manifest, verify_manifest, safe_path


class FileProofTests(unittest.TestCase):
    def test_create_verify_detect_change_and_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "docs"
            root.mkdir()
            (root / "a.txt").write_text("original", encoding="utf-8")
            (root / "b.txt").write_text("keep", encoding="utf-8")
            manifest = Path(directory) / "manifest.json"
            result = create_manifest(root, manifest)
            self.assertEqual(len(result["files"]), 2)
            self.assertEqual(verify_manifest(root, manifest)["ok"], 2)
            (root / "a.txt").write_text("modified", encoding="utf-8")
            (root / "b.txt").unlink()
            report = verify_manifest(root, manifest)
            self.assertEqual({r["status"] for r in report["results"]}, {"CHANGED", "MISSING"})

    def test_manifest_cannot_escape_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in ("../secret", "/etc/passwd", "C:/Windows/file", "a\\b"):
                with self.assertRaises(ValueError):
                    safe_path(root, path)

    def test_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.txt").write_text("hello", encoding="utf-8")
            dest = root / "proof.json"
            create_manifest(root, dest)
            with self.assertRaises(FileExistsError):
                create_manifest(root, dest)

    def test_invalid_schema_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "bad.json"
            manifest.write_text(json.dumps({"schema": "other", "files": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_manifest(root, manifest)

    def test_added_file_blocks_all_clear(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "docs"
            root.mkdir()
            (root / "original.txt").write_text("same", encoding="utf-8")
            manifest = Path(directory) / "manifest.json"
            create_manifest(root, manifest)
            (root / "surprise.txt").write_text("new", encoding="utf-8")
            result = verify_manifest(root, manifest)
            self.assertEqual(result["ok"], 1)
            self.assertEqual(result["added"], 1)
            self.assertIn({"path": "surprise.txt", "status": "ADDED"}, result["results"])

    def test_manifest_in_source_folder_is_not_false_alarm(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data.txt").write_text("unchanged", encoding="utf-8")
            manifest = root / "snapshot.json"
            create_manifest(root, manifest)
            result = verify_manifest(root, manifest)
            self.assertEqual(result["ok"], 1)
            self.assertEqual(result["added"], 0)
            self.assertEqual(result["scan_errors"], [])

    def test_rejects_malformed_file_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "docs"
            root.mkdir()
            (root / "good.txt").write_text("ok", encoding="utf-8")
            manifest_file = Path(directory) / "proof.json"
            create_manifest(root, manifest_file)
            valid = json.loads(manifest_file.read_text(encoding="utf-8"))
            for field, invalid in (("sha256", "not-a-checksum"), ("bytes", -1),
                                   ("bytes", True), ("bytes", "2")):
                with self.subTest(field=field, invalid=invalid):
                    broken = json.loads(json.dumps(valid))
                    broken["files"][0][field] = invalid
                    manifest_file.write_text(json.dumps(broken), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        verify_manifest(root, manifest_file)

    def test_initial_scan_errors_cannot_be_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "docs"
            root.mkdir()
            manifest_file = Path(directory) / "proof.json"
            manifest_file.write_text(json.dumps({
                "schema": "finalvestige.fileproof.v1", "files": [],
                "errors": [{"path": "secret.txt", "error": "permission denied"}]
            }), encoding="utf-8")
            result = verify_manifest(root, manifest_file)
            self.assertEqual(result["ok"], 0)
            self.assertEqual(len(result["scan_errors"]), 1)



if __name__ == "__main__":
    unittest.main()
