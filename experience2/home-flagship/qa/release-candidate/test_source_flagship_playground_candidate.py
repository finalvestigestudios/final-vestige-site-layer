"""Source custody + adversarial tests for the seven-chapter Playground-only artifact.

Run against the exact PR checkout. No network, WP credentials, CMS writes,
production source or archived live visitor records.
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = HERE.parents[1]
sys.path.insert(0, str(HERE))
from write_source_flagship_playground_candidate import (  # noqa: E402
    CSS_FILES, JS_FILES, NAV_TARGETS, NYPL_FILE, STAGING_ONLY,
    compose, digest, read_sources, write,
)


class FullSourceFlagshipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index, cls.css, cls.js = read_sources(HOME)

    def test_genuine_source_controlled_seven_chapters(self):
        candidate, manifest = compose(self.index, self.css, self.js)
        self.assertTrue(manifest["real_source_controlled_flagship"])
        self.assertFalse(manifest["page6_live_content_included"])
        self.assertEqual(manifest["release"], "HOLD")
        self.assertEqual(manifest["margin_items"], 72)
        self.assertEqual(manifest["script_source_count"], 4)
        self.assertEqual(manifest["style_source_count"], 6)
        self.assertEqual(manifest["candidate_sha256"], digest(candidate.encode()))
        self.assertIn("data-fv-home-flagship", candidate)
        self.assertIn("FV-EX2 PAGE6 REVIEW-ONLY", candidate)
        self.assertIn(STAGING_ONLY, candidate)
        self.assertEqual(candidate.count("jetpack/subscriptions"), 1)
        self.assertEqual(candidate.count('class="fv-hf__chapter-nav"'), 1)
        self.assertEqual(candidate.count('<!-- wp:html -->'), 2)
        self.assertEqual(candidate.count('<!-- /wp:html -->'), 2)
        self.assertEqual(candidate.count('<script data-fv-source='), 4)
        self.assertNotIn(NYPL_FILE, candidate)
        self.assertNotIn("NYPL believes this item is in the public domain", candidate)
        self.assertEqual(len(manifest["source_sha256"]), 11)
        for name in NAV_TARGETS:
            self.assertIn('id="' + name + '"', candidate)
            self.assertIn('href="#' + name + '"', candidate)
        for name in CSS_FILES:
            self.assertIn("/* SOURCE: " + name + " */", candidate)
        for name in JS_FILES:
            self.assertIn('data-fv-source="' + name + '"', candidate)
        self.assertIn("ARCHIVAL REFERENCE", candidate)

    def test_missing_chapter_target_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "chapter"):
            compose(self.index.replace('id="fv-hf-observer"', 'id="wrong"', 1), self.css, self.js)

    def test_missing_chapter_link_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "chapter"):
            compose(self.index.replace('href="#fv-hf-mind-title"', 'href="#wrong"', 1),
                    self.css, self.js)

    def test_masthead_gold_cta_paints_its_own_dark_backdrop(self):
        # Structural regression for the actual 1440px Assembler axe finding.
        # Contrast itself must still pass the real browser axe gate.
        css = self.css["flagship.css"]
        start = css.index(".fv-hf__mast-cta{")
        normal = css[start:css.index("}", start)]
        self.assertIn("background:#0a0a09;", normal)
        self.assertIn("color:var(--hf-gold);", normal)
        self.assertIn(
            ".fv-hf__mast-cta:hover{background:var(--hf-gold);color:#090a0a}",
            css,
        )

    def test_missing_script_file_fails_closed(self):
        altered = dict(self.js)
        del altered["reading-trail.js"]
        with self.assertRaisesRegex(ValueError, "assets"):
            compose(self.index, self.css, altered)

    def test_changed_asset_reference_order_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "asset order"):
            compose(self.index.replace('href="./flagship.css"', 'href="./unknown.css"'),
                    self.css, self.js)

    def test_fake_nypl_image_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unverified capture"):
            compose(self.index.replace("</body>", '<img src="' + NYPL_FILE + '"></body>'),
                    self.css, self.js)

    def test_fake_rights_assertion_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unverified capture"):
            compose(self.index.replace("</body>",
                    "NYPL believes this item is in the public domain</body>"), self.css, self.js)

    def test_script_close_breakout_fails_closed(self):
        altered = dict(self.js)
        altered["flagship.js"] += "\n</script><script>alert(1)</script>"
        with self.assertRaisesRegex(ValueError, "breakout"):
            compose(self.index, self.css, altered)

    def test_css_breakout_fails_closed(self):
        altered = dict(self.css)
        altered["flagship.css"] += "\n</style><script>alert(1)</script>"
        with self.assertRaisesRegex(ValueError, "breakout"):
            compose(self.index, altered, self.js)

    def test_output_hashes_and_nonoverwrite(self):
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "candidate.html"
            manifest_path = Path(d) / "manifest.json"
            report = write(HOME, output, manifest_path)
            self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),
                             report["candidate_sha256"])
            self.assertEqual(json.loads(manifest_path.read_text())["release"], "HOLD")
            with self.assertRaises(ValueError):
                write(HOME, output, manifest_path)
            self.assertFalse((Path(d) / "source-export.html").exists())

    def test_refuse_same_candidate_and_manifest_path(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "candidate.html"
            with self.assertRaises(ValueError):
                write(HOME, path, path)


if __name__ == "__main__":
    unittest.main()
