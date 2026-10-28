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


if __name__ == "__main__":
    unittest.main()
