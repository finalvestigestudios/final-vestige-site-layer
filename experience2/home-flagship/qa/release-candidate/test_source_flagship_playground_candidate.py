"""Source custody + adversarial tests for the seven-chapter Playground-only artifact.

Run against the exact PR checkout. No network, WP credentials, CMS writes,
production source or archived live visitor records.
"""
from __future__ import annotations

import hashlib
from html import escape
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
    STAGING_ASSEMBLER_STYLE, ASSEMBLER_STAGE_CSS, PUBLIC_MARGINS_JSON,
    compose, digest, load_public_margins, read_sources, write,
)


class FullSourceFlagshipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index, cls.css, cls.js = read_sources(HOME)

    def test_genuine_source_controlled_seven_chapters(self):
        candidate, manifest = compose(self.index, self.css, self.js)
        self.assertTrue(manifest["real_source_controlled_flagship"])
        self.assertFalse(manifest["page6_live_content_included"])
        self.assertTrue(manifest["public_page6_margins_texts_included"])
        self.assertFalse(manifest["other_page6_content_included"])
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

    def test_saved_assembler_css_and_keyboard_margin_region(self):
        candidate, manifest = compose(self.index, self.css, self.js)
        stage_css = ASSEMBLER_STAGE_CSS.read_text(encoding="utf-8")
        self.assertEqual(candidate.count(STAGING_ASSEMBLER_STYLE), 1)
        self.assertIn(stage_css, candidate)
        self.assertEqual(
            manifest["assembler_saved_stage_css_sha256"],
            digest(stage_css.encode("utf-8"))
        )
        self.assertIn('role="region" aria-label="72 published historical fragments in isolated review" tabindex="0"', candidate)
        self.assertEqual(candidate.count('class="fv-margin-strip__window"'), 1)
        self.assertEqual(candidate.count("Historic fragment "), 0)
        self.assertEqual(candidate.count('class="fv-margin-strip__item"'), 72)
        self.assertIn('.wp-block-post-content > .fv-hf', candidate)
        self.assertIn('@supports selector(body:has(', candidate)

    def test_refuse_unsafe_stage_css(self):
        stage_css = ASSEMBLER_STAGE_CSS.read_text(encoding="utf-8")
        for attack in [
            stage_css + "</style><script>alert(1)</script>",
            stage_css + "\\n@import 'https://attacker.invalid/style.css';",
            stage_css + "\\nbody{background:url(https://attacker.invalid/x)}",
            "body{width:100vw!important;}",
        ]:
            with self.subTest(attack=attack[-60:]):
                with self.assertRaisesRegex(ValueError, "unsafe isolated Assembler"):
                    compose(self.index, self.css, self.js,assembler_css=attack)

    def test_source_inventory_excludes_test_stage_css(self):
        candidate, manifest = compose(self.index, self.css, self.js)
        self.assertEqual(len(manifest["source_sha256"]), 11)
        self.assertNotIn("assembler_saved_layout_playground_only.css",
                         manifest["source_sha256"])
        self.assertEqual(candidate.count("<style "), 2)
        self.assertIn("PUBLISHED MARGINS · TEST FIXTURE", candidate)


    def test_public_page6_margins_are_exact_and_not_live_jetpack(self):
        texts, provenance = load_public_margins()
        candidate, manifest = compose(self.index, self.css, self.js)
        self.assertEqual(len(texts), 72)
        self.assertEqual(len(set(texts)), 72)
        self.assertEqual(manifest["public_fragment_fixture_sha256"],
                         hashlib.sha256(PUBLIC_MARGINS_JSON.read_bytes()).hexdigest())
        self.assertEqual(manifest["published_margins_source_modified"],
                         provenance["source_modified"])
        self.assertIn("PUBLIC_PAGE6_MARGINS_WITH_SYNTHETIC_JETPACK_FIXTURE",
                      manifest["data_classification"])
        for text in (texts[0], texts[19], texts[35], texts[71]):
            self.assertIn(escape(text, quote=False), candidate)
        self.assertIn("Nearly 4,000 years ago, Nanni filed a clay complaint", candidate)
        self.assertIn("living people's information", candidate)
        self.assertIn("72 PUBLISHED MARGINS · TEST FIXTURE", candidate)
        self.assertEqual(candidate.count("jetpack/subscriptions"), 1)
        self.assertEqual(manifest["data_classification"],
                         "PUBLIC_PAGE6_MARGINS_WITH_SYNTHETIC_JETPACK_FIXTURE")

    def test_public_margins_custody_mutations_fail_closed(self):
        original = json.loads(PUBLIC_MARGINS_JSON.read_text(encoding="utf-8"))
        mutations = [
            lambda d: d["items"].pop(),
            lambda d: d["items"][15].update(index=14),
            lambda d: d["items"][9].update(text=d["items"][8]["text"]),
            lambda d: d["items"][0].update(text="<script>alert(1)</script>"),
            lambda d: d["items"][0].update(text=""),
            lambda d: d.update(source_page_id=7),
            lambda d: d.update(source_url="https://attacker.invalid/"),
            lambda d: d.update(status="PRODUCTION"),
            lambda d: d.update(fragment_count=71),
        ]
        for alter in mutations:
            bad = json.loads(json.dumps(original))
            alter(bad)
            with tempfile.TemporaryDirectory() as d:
                fp = Path(d) / "untrusted.json"
                fp.write_text(json.dumps(bad), encoding="utf-8")
                with self.subTest(mutation=str(alter)):
                    with self.assertRaises(ValueError):
                        load_public_margins(fp)

    def test_missing_chapter_target_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "chapter"):
            compose(self.index.replace('id="fv-hf-observer"', 'id="wrong"', 1), self.css, self.js)

    def test_missing_chapter_link_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "chapter"):
            compose(self.index.replace('href="#fv-hf-mind-title"', 'href="#wrong"', 1),
                    self.css, self.js)

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


    def test_wordpress_embed_uses_theme_main_without_nested_flagship_landmark(self):
        # Standalone version must retain its own semantic main region.
        self.assertEqual(self.index.count("<main>"), 1)
        self.assertEqual(self.index.count("</main>"), 1)
        candidate, manifest = compose(self.index, self.css, self.js)
        self.assertTrue(manifest["wordpress_main_landmark_adapted"])
        self.assertEqual(candidate.count('data-fv-embedded-main="wordpress-assembler"'), 1)
        self.assertNotIn("<main>", candidate)
        self.assertNotIn("</main>", candidate)
        self.assertEqual(candidate.count('class="fv-hf__chapter-nav"'), 1)
        self.assertGreaterEqual(candidate.count('href="https://finalvestige.com/focus/"'),
                         self.index.count('href="https://finalvestige.com/focus/"'))
        for bad in (
            self.index.replace("<main>", "<section>", 1),
            self.index.replace("</main>", "</section>", 1),
            self.index.replace("<main>", "<main><main>", 1),
        ):
            with self.subTest(main_mutation=bad.count("<main>")):
                with self.assertRaisesRegex(ValueError, "main landmark boundary changed"):
                    compose(bad, self.css, self.js)

if __name__ == "__main__":
    unittest.main()
