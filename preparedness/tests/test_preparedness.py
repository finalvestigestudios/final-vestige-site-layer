"""Tests for the Preparedness Archive build and governance gates. Run:  python -I -m unittest discover -s preparedness/tests -v
No network access: every test works on files in the repository."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import validate  # noqa: E402


class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()

    def test_validator_clean(self):
        errors, _ = validate.validate(self.lib)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_slate_has_35_items_and_tracks_status(self):
        self.assertEqual(len(self.lib.taxonomy["slate"]), 35)
        built = set(self.lib.articles)
        for a in self.lib.taxonomy["slate"]:
            if a["slug"] in built:
                self.assertEqual(a["status"], "safety-approved-draft", a["slug"])
            else:
                self.assertEqual(a["status"], "not-started", a["slug"])

    def test_no_article_is_published_without_review(self):
        for slug, meta in self.lib.articles.items():
            self.assertEqual(meta["status"]["publish"], "draft", f"{slug} must stay draft until human review")

    def test_gated_articles_cannot_publish(self):
        # Prove the governance gate bites: flip one article to 'published' in memory and expect a validator error.
        lib = build.Library()
        lib.articles["making-water-safer"]["status"]["publish"] = "published"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("CANNOT be published" in e for e in errors), errors)

    def test_unverified_source_cannot_be_cited(self):
        lib = build.Library()
        lib.articles["making-water-safer"]["_body"] += " {{cite:nchfp-jerky}}"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("unverified source" in e for e in errors), errors)

    def test_unknown_citation_is_an_error(self):
        lib = build.Library()
        lib.articles["making-water-safer"]["_body"] += " {{cite:does-not-exist}}"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("unknown source id" in e for e in errors), errors)

    def test_numeric_dose_table_matches_cdc_values(self):
        """The bleach table is the highest-risk content on the site. Pin the exact CDC values."""
        body = self.lib.articles["making-water-safer"]["_body"]
        rows = re.findall(r"<tr><th scope=\"row\">(1 quart or 1 liter|1 gallon|5 gallons)</th><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td></tr>", body)
        got = {r[0]: r[1:] for r in rows}
        self.assertEqual(got["1 quart or 1 liter"][0], "2 drops")
        self.assertEqual(got["1 quart or 1 liter"][1], "0.1 mL")
        self.assertEqual(got["1 gallon"], ("8 drops", "½ mL", "A little less than ⅛ teaspoon"))
        self.assertEqual(got["5 gallons"], ("40 drops", "2½ mL", "½ teaspoon"))
        self.assertIn("double the amount", body)
        self.assertIn("at least <strong>30 minutes</strong>", body)

    def test_history_piece_gives_no_curing_numbers(self):
        """The salt-provisions article must not contain a usable curing formula."""
        body = self.lib.articles["salt-beef-salt-pork-age-of-sail"]["_body"]
        plain = re.sub(r"<[^>]+>", " ", body)
        for pat in (r"\d+\s?(?:%|percent)\s+(?:salt|brine)", r"\bppm\b", r"tablespoons? (?:of )?(?:salt|cure)", r"\d+\s?(?:°|degrees)\s?F?\b.{0,20}(?:cure|smoke|brine)", r"ounces? (?:of )?(?:salt|saltpet)"):
            self.assertIsNone(re.search(pat, plain, flags=re.I), f"possible curing quantity: {pat}")


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.landing = build.build_landing(cls.lib)
        cls.built = {s: build.build_article(cls.lib, s) for s in cls.lib.articles}

    def test_no_unresolved_tokens(self):
        for s, b in self.built.items():
            self.assertNotIn("{{", b["inner"], s)
        self.assertNotIn("{{", self.landing["inner"])

    def test_every_citation_has_a_numbered_source_entry(self):
        for s, b in self.built.items():
            cites = set(re.findall(r'href="#src-(\d+)"', b["inner"]))
            entries = set(re.findall(r'<li id="src-(\d+)"', b["inner"]))
            self.assertEqual(cites, entries, s)

    def test_internal_links_only_point_to_built_articles(self):
        built_paths = {self.lib.url_path(s) for s in self.lib.articles}
        for s, b in self.built.items():
            for href in re.findall(r'href="(/preparedness/[^"]*)"', b["inner"]):
                self.assertTrue(href in built_paths or href == "/preparedness/" or href.count("/") == 3, f"{s}: {href}")

    def test_landing_lists_only_built_articles_and_no_empty_sections(self):
        titles = re.findall(r'<h3><a href="([^"]+)">', self.landing["inner"])
        self.assertEqual(len(titles), len(self.lib.articles))
        self.assertEqual(self.landing["populated_sections"], ["water", "lost-ways"])

    def test_landing_never_names_unwritten_articles(self):
        for a in self.lib.taxonomy["slate"]:
            if a["slug"] not in self.lib.articles:
                self.assertNotIn(a["title"], self.landing["inner"], a["slug"])

    def test_article_structure_and_accessibility_hooks(self):
        for s, b in self.built.items():
            inner = b["inner"]
            self.assertEqual(inner.count("<h1"), 1, s)
            self.assertIn('aria-label="Breadcrumb"', inner)
            self.assertIn('class="pa-skip"', inner)
            self.assertIn('id="pa-main"', inner)
            self.assertNotIn("<main", inner)  # the WordPress theme template already provides <main>
            self.assertIn('rel="noopener"', inner)

    def test_jsonld_parses_and_is_not_dated_published_while_draft(self):
        for s, b in self.built.items():
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', b["inner"], flags=re.S)
            self.assertEqual(len(blocks), 1)
            data = json.loads(blocks[0])
            article = data["@graph"][0]
            self.assertNotIn("datePublished", article)
            self.assertEqual(article["@type"], "Article")
            self.assertEqual(data["@graph"][1]["@type"], "BreadcrumbList")

    def test_preview_wrapper_supplies_exactly_one_main(self):
        for s, b in self.built.items():
            page = build.preview_wrap(self.lib, b["inner"], "t", "d")
            self.assertEqual(page.count("<main>"), 1, s)
        self.assertEqual(build.preview_wrap(self.lib, self.landing["inner"], "t", "d").count("<main>"), 1)

    def test_labelled_divs_have_roles(self):
        for s, b in self.built.items():
            for tag in re.findall(r"<div[^>]*aria-label=[^>]*>", b["inner"]):
                self.assertIn("role=", tag, f"{s}: {tag}")

    def test_minified_css_is_balanced_and_smaller(self):
        m = build.minify_css(self.lib.css)
        self.assertEqual(m.count("{"), m.count("}"))
        self.assertLess(len(m), len(self.lib.css) * 0.95)
        self.assertNotIn("/*", m)
        self.assertIn("@container (min-width: 900px){", m)  # at-rule preludes must keep their spaces

    def test_wp_wrapper(self):
        out = build.wp_wrap(self.lib, "<div>x</div>")
        self.assertTrue(out.startswith("<!-- wp:html -->"))
        self.assertTrue(out.rstrip().endswith("<!-- /wp:html -->"))

    def test_css_is_fully_scoped(self):
        css = re.sub(r"/\*.*?\*/", "", self.lib.css, flags=re.S)
        # strip @media/@container wrappers, then every selector group must begin with .pa
        for sel in re.findall(r"(?:^|\})\s*([^{}@]+)\{", css):
            for part in sel.split(","):
                part = part.strip()
                if part and not part.startswith((".pa", "0%", "100%", "from", "to")):
                    self.fail(f"unscoped selector: {part}")

    def test_no_external_scripts_or_trackers(self):
        for s, b in self.built.items():
            self.assertNotRegex(b["inner"], r"<script[^>]+src=", s)
        self.assertNotRegex(self.landing["inner"], r"<script[^>]+src=")


if __name__ == "__main__":
    unittest.main()
