import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "egress.py"
spec = importlib.util.spec_from_file_location("egress", MODULE_PATH)
eg = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(eg)


class EgressTests(unittest.TestCase):
    def base_manifest(self):
        return {
            "expected_count": 1,
            "stems": [
                {
                    "stem_id": "S01",
                    "filename": "POD001-S01.mp3",
                    "generation_id": "cqSyRENXcy7Og3w91G1x",
                    "expected_duration_seconds": 36.46,
                }
            ],
        }

    def test_manifest_accepts_valid_entry(self):
        self.assertEqual(eg.validate_manifest(self.base_manifest())["expected_count"], 1)

    def test_manifest_rejects_duplicate_generation(self):
        data = self.base_manifest()
        data["expected_count"] = 2
        data["stems"].append({**data["stems"][0], "stem_id": "S02", "filename": "POD001-S02.mp3"})
        with self.assertRaises(eg.EgressError):
            eg.validate_manifest(data)

    def test_manifest_rejects_path_traversal(self):
        data = self.base_manifest()
        data["stems"][0]["filename"] = "../escape.mp3"
        with self.assertRaises(eg.EgressError):
            eg.validate_manifest(data)

    def test_safe_url_policy(self):
        self.assertTrue(eg.is_safe_https_url("https://storage.googleapis.com/x/y"))
        self.assertFalse(eg.is_safe_https_url("http://storage.googleapis.com/x/y"))
        self.assertFalse(eg.is_safe_https_url("https://127.0.0.1/x"))
        self.assertFalse(eg.is_safe_https_url("https://localhost/x"))

    def test_completed_generation_parsing(self):
        payload = {
            "status": "completed",
            "id": "cqSyRENXcy7Og3w91G1x",
            "content_mime_type": "audio/mpeg",
            "content_url": "https://storage.googleapis.com/generations/x",
        }
        url, mime = eg.parse_completed_generation(payload, payload["id"])
        self.assertEqual(mime, "audio/mpeg")
        self.assertTrue(url.startswith("https://"))

    def test_completed_generation_rejects_wrong_identity(self):
        payload = {
            "status": "completed",
            "id": "different123",
            "content_mime_type": "audio/mpeg",
            "content_url": "https://storage.googleapis.com/generations/x",
        }
        with self.assertRaises(eg.EgressError):
            eg.parse_completed_generation(payload, "cqSyRENXcy7Og3w91G1x")

    def test_completed_generation_rejects_non_audio(self):
        payload = {
            "status": "completed",
            "id": "cqSyRENXcy7Og3w91G1x",
            "content_mime_type": "video/mp4",
            "content_url": "https://storage.googleapis.com/generations/x",
        }
        with self.assertRaises(eg.EgressError):
            eg.parse_completed_generation(payload, payload["id"])


if __name__ == "__main__":
    unittest.main()
