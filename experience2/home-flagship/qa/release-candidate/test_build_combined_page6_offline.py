"""Offline-only tests for a saved Gutenberg release candidate; synthetic data only."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HOME / "rights"))
from build_combined_page6_offline import (  # noqa: E402
    CSS_PATH, MARKER, UnsafeCandidate, build_candidate, structural_inventory,
)
from test_withhold_unverified_nypl_capture import fixture  # noqa: E402
from withhold_unverified_nypl_capture import RECORD_LABEL  # noqa: E402

SCRIPT = HERE / "build_combined_page6_offline.py"
CSS = CSS_PATH.read_text(encoding="utf-8")


def source_fixture():
    raw = fixture()
    split = '</div><div class="fv-hf"'
    # Unlike the small upstream rights fixture, the actual page stores the
    # Margins and flagship as separate Gutenberg HTML blocks.
    assert raw.count(split) == 1
    first_style = (
        '</div><style>\n.fv-margin-strip{color:#d8d2c7}\n'
        '@keyframes fvMarginReveal{0%{opacity:.42}100%{opacity:1}}\n'
        '</style><!-- /wp:html --><!-- wp:html --><div class="fv-hf"'
    )
    return raw.replace(split, first_style, 1)


class CombinedSavedCandidateTests(unittest.TestCase):
    def setUp(self):
        self.raw = source_fixture()

    def test_candidate_preserves_every_protected_component(self):
        final, report = build_candidate(self.raw, CSS)
        self.assertNotIn("edit-017-v02-nypl-5003296-original.jpg", final)
        self.assertNotIn("NYPL believes this item is in the public domain", final)
        self.assertIn(RECORD_LABEL, final)
        self.assertEqual(final.count(MARKER), 1)
        self.assertIn("@keyframes fvMarginContrastSafe", final)
        self.assertIn("@keyframes fvMarginReveal", final)
        self.assertIn("prefers-reduced-motion: reduce", final)
        a, b = structural_inventory(self.raw), structural_inventory(final)
        self.assertEqual(a["margin_indices"], list(range(72)))
        self.assertEqual(b["margin_indices"], list(range(72)))
        self.assertEqual(a["nypl_catalog_links"], b["nypl_catalog_links"])
        self.assertEqual(a["jetpack_subscription_blocks"], b["jetpack_subscription_blocks"])
        self.assertEqual(a["focus_fieldbook_occurrences"], b["focus_fieldbook_occurrences"])
        self.assertEqual(a["inline_scripts"], b["inline_scripts"])
        self.assertEqual(a["html_blocks"], b["html_blocks"])
        self.assertEqual(report["production_release"], "HOLD")
        self.assertEqual(report["wordpress_writes"], 0)

    def test_first_block_only_insertion(self):
        from withhold_unverified_nypl_capture import patch_homepage
        rights, _ = patch_homepage(self.raw)
        final, _ = build_candidate(self.raw, CSS)
        before, tail = final.split(MARKER, 1)
        self.assertTrue(before.startswith("<!-- wp:html -->"))
        self.assertIn("</style>", tail)
        # All content following the first Gutenberg HTML close is identical
        # to the already-approved rights-only candidate.
        self.assertEqual(final.split("<!-- /wp:html -->", 1)[1],
                         rights.split("<!-- /wp:html -->", 1)[1])

    def test_duplicate_margin_index_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace('style="--i:71"', 'style="--i:70"'), CSS)

    def test_absent_jetpack_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace("jetpack/subscriptions", "wp:unknown"), CSS)

    def test_absent_focus_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace("Focus Fieldbook", "Some Other Download"), CSS)

    def test_missing_chapter_navigation_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace('class="fv-hf__chapter-nav"', 'class="missing"'), CSS)

    def test_missing_first_style_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace("<style>", "<styling>", 1), CSS)

    def test_duplicate_first_style_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace("</style>", "</style><style>p{color:red}</style>", 1), CSS)

    def test_existing_contrast_candidate_refused(self):
        candidate, _ = build_candidate(self.raw, CSS)
        with self.assertRaises(UnsafeCandidate):
            build_candidate(candidate, CSS)

    def test_external_css_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw, CSS + "\n@import 'https://evil.invalid/css';")

    def test_executable_css_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw, CSS + "\nbody{background:url(javascript:alert(1))}")

    def test_html_breakout_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw, CSS + "\n</style><script>alert(1)</script>")

    def test_missing_reduced_motion_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw, CSS.replace("prefers-reduced-motion: reduce", "unknown"))

    def test_missing_nypl_image_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace("edit-017-v02-nypl-5003296-original.jpg", "unknown.jpg"), CSS)

    def test_unreviewed_rights_assertion_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace("NYPL believes this item", "No evidence of rights review"), CSS)

    def test_missing_gutenberg_close_refused(self):
        with self.assertRaises(UnsafeCandidate):
            build_candidate(self.raw.replace("<!-- /wp:html -->", "", 1), CSS)

    def test_cli_correct_pin_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original, output, report = [root / n for n in ("raw.txt", "candidate.txt", "report.json")]
            original.write_bytes(self.raw.encode("utf-8"))
            before_bytes = original.read_bytes()
            digest = hashlib.sha256(before_bytes).hexdigest()
            run = subprocess.run([sys.executable, str(SCRIPT), "--source", str(original),
                "--expected-sha256", digest, "--output", str(output),
                "--report", str(report)], text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(original.read_bytes(), before_bytes)
            self.assertIn(MARKER, output.read_text(encoding="utf-8"))
            receipt = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(receipt["source_sha256"], digest)
            self.assertEqual(receipt["candidate_sha256"],
                             hashlib.sha256(output.read_bytes()).hexdigest())
            self.assertEqual(receipt["production_release"], "HOLD")
            self.assertNotIn("Historic fragment 71", report.read_text())

            again = subprocess.run([sys.executable, str(SCRIPT), "--source", str(original),
                "--expected-sha256", digest, "--output", str(output),
                "--report", str(report)], capture_output=True)
            self.assertNotEqual(again.returncode, 0)

    def test_cli_wrong_pin_creates_no_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original, output, report = [root / n for n in ("raw.txt", "candidate.txt", "report.json")]
            original.write_text(self.raw, encoding="utf-8")
            run = subprocess.run([sys.executable, str(SCRIPT), "--source", str(original),
                "--expected-sha256", "0" * 64, "--output", str(output),
                "--report", str(report)], capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(output.exists())
            self.assertFalse(report.exists())

    def test_cli_normalization_is_not_silent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            original, output, report = [root / n for n in ("raw.txt", "candidate.txt", "report.json")]
            original.write_bytes(self.raw.replace("\n", "\r\n").encode("utf-8"))
            wrong = hashlib.sha256(self.raw.encode("utf-8")).hexdigest()
            run = subprocess.run([sys.executable, str(SCRIPT), "--source", str(original),
                "--expected-sha256", wrong, "--output", str(output),
                "--report", str(report)], capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
