"""Adversarial tests for offline release-safe NYPL capture withholding."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from withhold_unverified_nypl_capture import (
    NYPL_FILE, NYPL_RECORD, ORIGINAL_CAPTION, REPLACEMENT_CAPTION,
    REVIEWED_CREDIT, UNVERIFIED_CLAIM, UnsafeCandidate, patch_homepage,
)

SCRIPT = Path(__file__).with_name("withhold_unverified_nypl_capture.py")
IMAGE = (
    '<img src="https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/'
    + NYPL_FILE + '?fit=1024" srcset="https://i0.wp.com/finalvestige.com/'
    'wp-content/uploads/2026/08/' + NYPL_FILE + '?fit=768 768w, '
    'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/'
    + NYPL_FILE + '?fit=1536 1536w" data-fv-archive-img>'
)


def fixture():
    margins = "".join(
        f'<span class="fv-margin-strip__item" style="--i:{i}">Historic fragment {i}</span>'
        for i in range(72)
    )
    article = (
        '<article class="fv-hf__case" data-fv-case="malbone" id="fv-hf-malbone">'
        '<div class="fv-hf__case-image fv-hf__case-image--malbone">'
        '<span class="fv-hf__case-image-fallback">1903 / RAPID TRANSIT<br>'
        'NYPL DIGITAL COLLECTIONS</span>' + IMAGE +
        '<div class="fv-hf__image-frame">ARCHIVE IMAGE 03 / NYPL 5003296</div>'
        '</div><div class="fv-hf__case-body"><p>' + ORIGINAL_CAPTION +
        '</p><p>' + UNVERIFIED_CLAIM +
        '</p><a href="' + NYPL_RECORD + '">Catalog record</a></div></article>'
    )
    return (
        '<!-- wp:html --><div class="fv-margin-strip">' + margins + '</div>'
        '<div class="fv-hf" data-fv-home-flagship><nav class="fv-hf__chapter-nav">'
        '<button data-fv-case="apollo">Apollo</button>'
        '<button data-fv-case="franklin">Franklin</button>'
        + article + '</nav>'
        '<a href="' + NYPL_RECORD + '">Read original source</a>'
        '<img src="apollo.jpg" data-fv-archive-img></div>'
        '<!-- /wp:html --><p>Keep the Focus Fieldbook</p>'
        '<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->'
    )


class RightsSafeCandidateTests(unittest.TestCase):
    def setUp(self):
        self.raw = fixture()

    def test_exact_synthetic_candidate(self):
        out, report = patch_homepage(self.raw)
        self.assertNotIn(NYPL_FILE, out)
        self.assertNotIn(UNVERIFIED_CLAIM, out)
        self.assertIn(REVIEWED_CREDIT, out)
        self.assertIn(REPLACEMENT_CAPTION, out)
        self.assertIn(NYPL_RECORD, out)
        self.assertIn("NYPL RECORD 03 / 5003296", out)\n        self.assertIn("left:clamp(16px,6%,72px)", out)\n        self.assertIn("overflow-wrap:break-word", out)
        self.assertIn("NYPL DIGITAL COLLECTIONS</span>", out)
        self.assertIn("src=\"apollo.jpg\"", out)
        self.assertEqual(report["protected_after"]["margins"], 72)
        self.assertEqual(report["protected_after"]["jetpack"], 1)
        self.assertEqual(report["protected_after"]["focus"], 1)
        self.assertEqual(report["protected_after"]["catalog_links"], 2)
        self.assertEqual(report["protected_after"]["image_controls"], 1)
        self.assertEqual(report["production_writes"], 0)
        self.assertEqual(report["status"], "OFFLINE_REVIEW_ONLY_NOT_PUBLISHED")

    def test_only_reviewed_article_is_rewritten(self):
        out, _ = patch_homepage(self.raw)
        before, article_on = self.raw.split('<article class="fv-hf__case"', 1)
        after = article_on.split("</article>", 1)[1]
        self.assertTrue(out.startswith(before))
        self.assertTrue(out.endswith(after))

    def test_image_control_inventory_does_not_count_script_selector(self):
        # Production HTML contains 3 img tags, but the selector string in its
        # inline script adds a fourth textual occurrence of the same marker.
        with_script = self.raw + "<script>document.querySelectorAll('[data-fv-archive-img]');</script>"
        out, report = patch_homepage(with_script)
        self.assertEqual(report["protected_before"]["image_controls"], 2)
        self.assertEqual(report["protected_after"]["image_controls"], 1)
        self.assertIn("document.querySelectorAll('[data-fv-archive-img]')", out)

    def test_missing_margin_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace('style="--i:71"', 'style="--i:70"'))

    def test_missing_jetpack_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace("jetpack/subscriptions", "jetpack/unknown"))

    def test_missing_focus_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace("Focus Fieldbook", "Fieldbook Gone"))

    def test_missing_flagship_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace("data-fv-home-flagship", "gone"))

    def test_missing_catalog_link_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace(NYPL_RECORD, "https://example.org/nope"))

    def test_only_one_catalog_link_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace('<a href="' + NYPL_RECORD + '">Read original source</a>', ""))

    def test_extra_rights_image_elsewhere_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw + '<img src="https://example.org/' + NYPL_FILE + '">')

    def test_broken_image_source_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace(NYPL_FILE, "different-map.jpg"))

    def test_srcset_missing_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace(' srcset="', ' dataset="'))

    def test_changed_unverified_claim_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace("NYPL believes this item", "Someone says this item"))

    def test_changed_catalog_caption_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace(ORIGINAL_CAPTION, "Unsourced impression"))

    def test_duplicate_article_fails(self):
        a = self.raw.index('<article class="fv-hf__case"')
        b = self.raw.index("</article>", a) + len("</article>")
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw[:b] + self.raw[a:b] + self.raw[b:])

    def test_missing_fallback_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace("fv-hf__case-image-fallback", "fv-hf__missing-fallback"))

    def test_changed_frame_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace("ARCHIVE IMAGE 03 / NYPL 5003296", "UNREVIEWED"))

    def test_absent_unrelated_case_fails(self):
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(self.raw.replace('data-fv-case="franklin"', 'data-fv-case="unknown"'))

    def test_no_unrelated_apollo_binary_loss(self):
        out, _ = patch_homepage(self.raw)
        self.assertIn('src="apollo.jpg" data-fv-archive-img', out)

    def test_repeat_patch_is_rejected_not_silently_idempotent(self):
        out, _ = patch_homepage(self.raw)
        with self.assertRaises(UnsafeCandidate):
            patch_homepage(out)

    def test_cli_report_and_exact_source_pin(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            original = base / "raw.html"
            result = base / "candidate.html"
            report = base / "report.json"
            original.write_text(self.raw, encoding="utf-8")
            sha = hashlib.sha256(original.read_bytes()).hexdigest()
            cmd = [sys.executable, str(SCRIPT), "--source", str(original),
                   "--output", str(result), "--report", str(report),
                   "--expected-sha256", sha]
            run = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(result.exists())
            self.assertTrue(report.exists())
            self.assertEqual(json.loads(report.read_text())["source_sha256"], sha)
            # A second attempt must not overwrite an accepted local candidate.
            again = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)

    def test_cli_windows_crlf_exact_byte_preservation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            raw_path = base / "raw-crlf.html"
            output = base / "candidate-crlf.html"
            report = base / "report-crlf.json"
            raw_bytes = self.raw.replace("><", ">\r\n<").encode("utf-8")
            raw_path.write_bytes(raw_bytes)
            sha = hashlib.sha256(raw_bytes).hexdigest()
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--source", str(raw_path),
                 "--output", str(output), "--report", str(report),
                 "--expected-sha256", sha],
                capture_output=True, text=True
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn(b"\r\n", output.read_bytes())
            self.assertEqual(json.loads(report.read_text())["source_sha256"], sha)

    def test_cli_wrong_hash_never_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            original = base / "raw.html"
            output = base / "candidate.html"
            report = base / "report.json"
            original.write_text(self.raw, encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--source", str(original),
                 "--output", str(output), "--report", str(report),
                 "--expected-sha256", "0" * 64],
                capture_output=True, text=True
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(output.exists())
            self.assertFalse(report.exists())

    def test_cli_input_equals_output_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            original = Path(temp) / "raw.html"
            report = Path(temp) / "report.json"
            original.write_text(self.raw, encoding="utf-8")
            sha = hashlib.sha256(original.read_bytes()).hexdigest()
            run = subprocess.run(
                [sys.executable, str(SCRIPT), "--source", str(original),
                 "--output", str(original), "--report", str(report),
                 "--expected-sha256", sha],
                capture_output=True, text=True
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("Refusing to overwrite", run.stderr)
            self.assertEqual(original.read_text(encoding="utf-8"), self.raw)


if __name__ == "__main__":
    unittest.main()
