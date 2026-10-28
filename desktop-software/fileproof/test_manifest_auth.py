import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from manifest_auth import (
    authenticate_manifest, verify_authentication, load_manifest,
    save_new_manifest, read_passphrase_file,
)
from fileproof import create_manifest, verify_manifest

SAMPLE = {"schema": "finalvestige.fileproof.v1", "files": [
    {"path": "données.txt", "bytes": 1, "sha256": "f"*64}], "errors": []}
PASS = "a-long-unique-passphrase"


class ManifestAuthTests(unittest.TestCase):
    def test_sign_unicode_and_verify(self):
        protected = authenticate_manifest(SAMPLE, PASS)
        self.assertTrue(verify_authentication(protected, PASS))
        self.assertNotIn(PASS, json.dumps(protected))
        self.assertEqual(protected['authentication']['iterations'], 600_000)

    def test_signed_manifest_requires_passphrase(self):
        protected = authenticate_manifest(SAMPLE, PASS)
        with self.assertRaises(ValueError):
            verify_authentication(protected, None)
        with self.assertRaises(ValueError):
            verify_authentication(protected, "wrong-secret")

    def test_signed_fields_cannot_change(self):
        protected = authenticate_manifest(SAMPLE, PASS)
        for key, replacement in (("version", "evil"), ("files", []),
                                 ("errors", [{"path": "a", "error": "oops"}])):
            with self.subTest(key=key):
                modified = json.loads(json.dumps(protected))
                modified[key] = replacement
                with self.assertRaises(ValueError):
                    verify_authentication(modified, PASS)

    def test_downgrade_rejected_when_passphrase_supplied(self):
        self.assertFalse(verify_authentication(SAMPLE, None))
        with self.assertRaisesRegex(ValueError, "unauthenticated"):
            verify_authentication(SAMPLE, PASS)

    def test_attack_on_iteration_field_fails_fast(self):
        signed = authenticate_manifest(SAMPLE, PASS)
        signed['authentication']['iterations'] = 999_999_999
        with self.assertRaises(ValueError):
            verify_authentication(signed, PASS)

    def test_invalid_tag_fails(self):
        signed = authenticate_manifest(SAMPLE, PASS)
        signed['authentication']['tag'] = "0" * 64
        with self.assertRaises(ValueError):
            verify_authentication(signed, PASS)

    def test_short_passphrase_rejected(self):
        with self.assertRaisesRegex(ValueError, "12 characters"):
            authenticate_manifest(SAMPLE, "weak")

    def test_no_clobber_destination(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/"manifest.json"
            target.write_text("KEEP", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                save_new_manifest(target, SAMPLE)
            self.assertEqual(target.read_text(), "KEEP")

    def test_save_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/"manifest.json"
            save_new_manifest(target, authenticate_manifest(SAMPLE, PASS))
            self.assertTrue(verify_authentication(load_manifest(target), PASS))
            self.assertEqual(list(Path(d).glob('*.tmp')), [])

    def test_race_during_publication_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/"manifest.json"
            original_link = os.link

            def racer(src, dst):
                Path(dst).write_text('OTHER PROCESS', encoding='utf-8')
                return original_link(src, dst)

            with mock.patch('manifest_auth.os.link', side_effect=racer):
                with self.assertRaises(FileExistsError):
                    save_new_manifest(target, SAMPLE)
            self.assertEqual(target.read_text(encoding='utf-8'), 'OTHER PROCESS')
            self.assertEqual(list(Path(d).glob('*.tmp')), [])

    def test_invalid_json_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"proof.json"
            path.write_text('{"files":[],"files":[]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                load_manifest(path)

    def test_invalid_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"proof.json"
            path.write_text('{"files":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Non-finite"):
                load_manifest(path)

    def test_passphrase_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"secret.txt"
            path.write_text(PASS + "\n", encoding="utf-8")
            self.assertEqual(read_passphrase_file(str(path)), PASS)

    def test_integrated_signed_create_and_verify(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/"source"
            root.mkdir()
            (root/"journal.txt").write_text("record", encoding="utf-8")
            destination = Path(d)/"proof.json"
            create_manifest(root, destination, passphrase=PASS)
            result = verify_manifest(root, destination, passphrase=PASS)
            self.assertTrue(result["authenticated"])
            self.assertEqual(result["ok"], 1)
            self.assertEqual(result["added"], 0)
            with self.assertRaises(ValueError):
                verify_manifest(root, destination)

    def test_integrated_tamper_blocks_verification(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/"source"
            root.mkdir()
            (root/"journal.txt").write_text("record", encoding="utf-8")
            destination = Path(d)/"proof.json"
            create_manifest(root, destination, passphrase=PASS)
            broken = load_manifest(destination)
            broken["files"][0]["sha256"] = "0" * 64
            destination.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "authentication failed"):
                verify_manifest(root, destination, passphrase=PASS)

    def test_integrated_changed_file_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/"source"
            root.mkdir()
            path = root/"journal.txt"
            path.write_text("record", encoding="utf-8")
            destination = Path(d)/"proof.json"
            create_manifest(root, destination, passphrase=PASS)
            path.write_text("tampered", encoding="utf-8")
            result = verify_manifest(root, destination, passphrase=PASS)
            self.assertTrue(result["authenticated"])
            self.assertIn({"path": "journal.txt", "status": "CHANGED"}, result["results"])

    def test_integrated_unsigned_downgrade_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/"source"
            root.mkdir()
            destination = Path(d)/"proof.json"
            create_manifest(root, destination)
            self.assertFalse(verify_manifest(root, destination)["authenticated"])
            with self.assertRaisesRegex(ValueError, "unauthenticated"):
                verify_manifest(root, destination, passphrase=PASS)


if __name__ == "__main__":
    unittest.main()
