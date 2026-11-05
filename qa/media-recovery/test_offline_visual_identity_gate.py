"""Synthetic-only tests; do not read or download any historical/third-party assets."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
import sys
from PIL import Image, ImageDraw

MODULE = Path(__file__).with_name("offline_visual_identity_gate.py")
spec = importlib.util.spec_from_file_location("fv_visual", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class VisualGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "original.png"
        self.cand = self.root / "candidate.webp"
        im = Image.new("RGB", (1280, 720), "#f1f1f1")
        d = ImageDraw.Draw(im)
        for i in range(0, 1280, 40):
            d.rectangle((i, (i // 2) % 400, i + 25, 600), fill=(i % 220, (i * 3) % 220, (i * 7) % 220))
        d.ellipse((80, 140, 400, 460), fill="#d1460a")
        im.save(self.src)
        im.resize((960, 540), Image.Resampling.LANCZOS).save(self.cand, quality=92)
        self.m = {
            "schema": gate.SCHEMA,
            "image_key": "285:5",
            "original_source_url": "https://images.example.org/historical.png",
            "candidate_catalog_url": "https://archives.example.org/record/45",
            "source_local_path": self.src.name,
            "candidate_local_path": self.cand.name,
            "lawful_local_copies_attested": True,
            "item_specific_rights_review": "PASS",
            "source_relationship": "same_catalog_item",
        }

    def run_gate(self):
        return gate.analyze(self.m, self.root)

    def test_resize_recode_is_similar_but_not_released(self):
        d = self.run_gate()
        self.assertEqual(d["comparison_result"], "VISUAL_SIMILARITY_REVIEW")
        self.assertFalse(d["exact_archival_identity_proven"])
        self.assertFalse(d["candidate_republication_authorized"])
        self.assertIsNone(d["browser_image_status"])
        self.assertEqual(d["candidate_dimensions"], [960, 540])
        self.assertEqual(len(d["source_sha256"]), 64)

    def test_different_scene_fails(self):
        Image.new("RGB", (960, 540), "blue").save(self.cand, "WEBP")
        self.assertEqual(self.run_gate()["comparison_result"], "VISUAL_PARITY_FAILED")

    def test_stretched_aspect_fails(self):
        Image.open(self.cand).resize((960, 500)).save(self.cand)
        self.assertFalse(self.run_gate()["geometry_pass"])

    def test_crop_rejected(self):
        Image.open(self.src).crop((0, 0, 1280, 600)).resize((960, 540)).save(self.cand)
        self.assertEqual(self.run_gate()["comparison_result"], "VISUAL_PARITY_FAILED")

    def test_over_960_rejected(self):
        Image.open(self.src).resize((1000, 562)).save(self.cand)
        self.assertFalse(self.run_gate()["geometry_pass"])

    def test_upscale_rejected(self):
        im = Image.open(self.src).resize((600, 337))
        im.save(self.src)
        self.assertFalse(self.run_gate()["geometry_pass"])

    def test_rights_hold_fails_closed(self):
        self.m["item_specific_rights_review"] = "HOLD"
        with self.assertRaisesRegex(ValueError, "rights review"):
            self.run_gate()

    def test_lawful_attestation_required(self):
        self.m["lawful_local_copies_attested"] = False
        with self.assertRaisesRegex(ValueError, "lawful"):
            self.run_gate()

    def test_subject_alternative_rejected(self):
        self.m["source_relationship"] = "same_subject_different_photo"
        with self.assertRaisesRegex(ValueError, "different-scene"):
            self.run_gate()

    def test_identical_path_rejected(self):
        self.m["candidate_local_path"] = self.m["source_local_path"]
        with self.assertRaisesRegex(ValueError, "cannot be the same"):
            self.run_gate()

    def test_traversal_rejected(self):
        self.m["candidate_local_path"] = "../candidate.webp"
        with self.assertRaisesRegex(ValueError, "traversal"):
            self.run_gate()

    def test_symlink_rejected(self):
        link = self.root / "shortcut.webp"
        link.symlink_to(self.cand)
        self.m["candidate_local_path"] = link.name
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_gate()

    def test_directory_symlink_rejected(self):
        dest = self.root / "link"
        dest.symlink_to(self.root, target_is_directory=True)
        self.m["candidate_local_path"] = "link/candidate.webp"
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_gate()

    def test_url_paths_rejected(self):
        self.m["candidate_local_path"] = "https://evil.example/photo.jpg"
        with self.assertRaisesRegex(ValueError, "URL"):
            self.run_gate()

    def test_invalid_key_rejected(self):
        self.m["image_key"] = "285/5"
        with self.assertRaisesRegex(ValueError, "key"):
            self.run_gate()

    def test_http_url_rejected(self):
        self.m["original_source_url"] = "http://bad.example/x.jpg"
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            self.run_gate()

    def test_gif_rejected(self):
        Image.new("RGB", (960, 540), "white").save(self.cand, "GIF")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            self.run_gate()

    def test_bad_media_rejected(self):
        self.cand.write_bytes(b"not a real image")
        with self.assertRaisesRegex(ValueError, "decode failed"):
            self.run_gate()

    def test_large_file_rejected(self):
        self.cand.write_bytes(b"x" * 200)
        original_limit = gate.MAX_FILE_BYTES
        try:
            gate.MAX_FILE_BYTES = 199
            with self.assertRaisesRegex(ValueError, "too large"):
                self.run_gate()
        finally:
            gate.MAX_FILE_BYTES = original_limit

    def test_transparency_change_is_not_parity(self):
        # A transparent original must not silently become an opaque replacement.
        Image.new("RGBA", (1280, 720), (210, 20, 20, 0)).save(self.src)
        Image.new("RGBA", (960, 540), (210, 20, 20, 255)).save(self.cand)
        self.assertEqual(self.run_gate()["comparison_result"], "VISUAL_PARITY_FAILED")


if __name__ == "__main__":
    unittest.main()
