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

    def test_slate_has_35_items_and_status_is_derived(self):
        self.assertEqual(len(self.lib.taxonomy["slate"]), 35)
        for a in self.lib.taxonomy["slate"]:
            st = build.slate_status(self.lib, a["slug"])
            if a["slug"] in self.lib.articles:
                self.assertIn(st, ("safety-approved-draft", "drafted-pending-safety-review", "published"))
            else:
                self.assertEqual(st, "not-started")

    def test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source(self):
        """Exercise both legal and forbidden source upgrades in an isolated copy.

        Never create temporary source fragments in the actual working tree:
        other tests and parallel agents may be reading those files.
        """
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory(prefix="fvs-preparedness-test-") as td:
            sandbox = Path(td) / "preparedness"
            shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(
                "build", "__pycache__"))
            register_path = sandbox / "sources" / "register.json"
            register = json.loads(register_path.read_text(encoding="utf-8"))
            existing = next(s for s in register["sources"] if s["id"] == "nchfp-jerky")
            fixture = {**existing,
                       "id": "test-fixture-jerky-placeholder",
                       "url": "https://example.org/fvs-only-test-upgrade-placeholder",
                       "verified_on": None}
            register["sources"].append(fixture)
            register_path.write_text(json.dumps(register), encoding="utf-8")
            fragment = sandbox / "sources" / "fragments" / "_upgrade_test.json"
            upgraded = {**fixture, "verified_on": "2026-10-29",
                        "supports": "Synthetic fixture to prove controlled source upgrades."}
            fragment.write_text(json.dumps({"sources": [upgraded]}), encoding="utf-8")

            lib = build.Library(root=sandbox)
            self.assertEqual(lib.register[fixture["id"]]["verified_on"], "2026-10-29")
            errors, _ = validate.validate(lib)
            self.assertFalse([e for e in errors if "duplicate url" in e], errors)

            # A VERIFIED source cannot be silently replaced by another fragment.
            fixture["verified_on"] = "2026-10-01"
            register_path.write_text(json.dumps(register), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate source id"):
                build.Library(root=sandbox)

    def test_register_fragments_cannot_duplicate_ids(self):
        """A conflicting real source ID must fail; fixtures cannot touch shared sources.

        This test previously wrote _dup_test.json under the repository's actual
        sources/fragments directory. That races validators, builds, and parallel
        worktrees, and a crashed test could leave a contaminating source behind.
        """
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory(prefix="fvs-preparedness-duplicate-test-") as td:
            sandbox = Path(td) / "preparedness"
            shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(
                "build", "__pycache__"))
            frag = sandbox / "sources" / "fragments" / "_dup_test.json"
            frag.write_text(
                '{"sources": [{"id": "cdc-water-store", "title": "x", '
                '"url": "https://example.gov/x", "kind": "regulator", '
                '"publisher": "x", "verified_on": "2026-10-29", '
                '"supports": "Synthetic duplicate-ID rejection fixture."}]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate source id"):
                build.Library(root=sandbox)

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
        # Synthetic, in-memory source: real references may become verified
        # without silently changing the assertion or touching the source files.
        lib = build.Library()
        fixture_id = "test-fixture-unverified-source"
        lib.register[fixture_id] = {
            **lib.register["nchfp-jerky"],
            "id": fixture_id,
            "url": "https://example.org/fvs-only-test-unverified-source",
            "verified_on": None,
        }
        lib.articles["making-water-safer"]["_body"] += " {{cite:" + fixture_id + "}}"
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
        # Derived from the articles actually present, in taxonomy order, so adding a cluster cannot make this test stale.
        has_articles = {m["section"] for m in self.lib.articles.values()}
        expected = [s["slug"] for s in self.lib.taxonomy["sections"] if s["slug"] in has_articles]
        self.assertEqual(self.landing["populated_sections"], expected)
        for sec in self.lib.taxonomy["sections"]:
            if sec["slug"] not in has_articles:
                self.assertNotIn(f'id="h-{sec["slug"]}"', self.landing["inner"], f"empty section {sec['slug']} must not render")

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


class HubAndToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()

    def test_hubs_exist_only_for_populated_sections(self):
        populated = {m["section"] for m in self.lib.articles.values()}
        for sec in self.lib.taxonomy["sections"]:
            hub = build.build_hub(self.lib, sec["slug"])
            self.assertEqual(hub is not None, sec["slug"] in populated, sec["slug"])

    def test_hub_lists_every_guide_in_its_section_and_nothing_else(self):
        hub = build.build_hub(self.lib, "water")
        hrefs = re.findall(r'<h3><a href="([^"]+)">', hub["inner"])
        expected = sorted(self.lib.url_path(s) for s, m in self.lib.articles.items() if m["section"] == "water")
        self.assertEqual(sorted(hrefs), expected)
        self.assertIn('aria-label="Breadcrumb"', hub["inner"])
        self.assertEqual(hub["inner"].count("<h1"), 1)

    def test_water_planner_is_private_and_offline(self):
        built = build.build_article(self.lib, "water-planner")["inner"]
        script = "\n".join(re.findall(r"<script>(.*?)</script>", built, flags=re.S))
        self.assertIn("computeWaterPlan", script)
        for banned in ("localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "navigator.", "import("):
            self.assertNotIn(banned, script, f"planner must not use {banned}")
        self.assertNotRegex(built, r"<form[^>]+(action|method)=")
        self.assertIn("onsubmit=\"return false\"", built)

    def test_planner_has_no_invented_pet_or_medical_defaults(self):
        built = build.build_article(self.lib, "water-planner")["inner"]
        for fid in ("wp-pets", "wp-petgal", "wp-extra"):
            self.assertRegex(built, rf'id="{fid}"[^>]*value=""')

    def test_every_planner_input_has_a_label(self):
        built = build.build_article(self.lib, "water-planner")["inner"]
        for fid in re.findall(r'<input id="([a-z\-]+)"', built):
            labelled = f'for="{fid}"' in built or f'<label class="pa-tool-check"><input id="{fid}"' in built
            self.assertTrue(labelled, f"input {fid} has no label")

    def test_javascript_unit_tests(self):
        import shutil, subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        r = subprocess.run([node, str(ROOT / "tests" / "test_water_planner.js")], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class GovernanceRegressionTests(unittest.TestCase):
    """Negative tests: nothing can be published while a safety review is pending, whatever the taxonomy flag says."""

    def setUp(self):
        self.lib = build.Library()

    def _publish(self, slug):
        meta = self.lib.articles[slug]
        meta["status"]["publish"] = "published"
        meta["status"]["editorial"] = "reviewed"
        meta["published"] = "2026-11-01"
        return validate.validate(self.lib)[0]

    def test_every_pending_article_is_blocked_from_publication(self):
        pending = [s for s, m in self.lib.articles.items() if m["safety_review"]["state"] == "pending"]
        self.assertTrue(pending, "expected at least one pending article")
        for slug in pending:
            lib = build.Library()
            m = lib.articles[slug]
            m["status"]["publish"] = "published"; m["status"]["editorial"] = "reviewed"; m["published"] = "2026-11-01"
            errors = validate.validate(lib)[0]
            self.assertTrue(any(slug in e and "pending" in e for e in errors), f"{slug} could be published while pending: {errors}")

    def test_ungated_taxonomy_flag_cannot_bypass_a_pending_review(self):
        self.lib.slate["making-water-safer"]["gate"] = False
        self.lib.articles["making-water-safer"]["safety_review"] = {"state": "pending", "reviewer": None, "date": None}
        errors = self._publish("making-water-safer")
        self.assertTrue(any("CANNOT be published while a safety review is pending" in e for e in errors), errors)

    def test_every_modern_slate_item_is_gated(self):
        for a in self.lib.taxonomy["slate"]:
            if a["track"] == "modern":
                self.assertTrue(a["gate"], f"#{a['n']} {a['slug']} gives actionable guidance and must be gated")

    def test_modern_guide_cannot_be_exempt_or_ungated(self):
        self.lib.slate["water-math"]["gate"] = False
        errors, _ = validate.validate(self.lib)
        self.assertTrue(any("must be gated" in e for e in errors), errors)
        lib = build.Library()
        lib.articles["water-math"]["safety_review"] = {"state": "not-required", "reviewer": None, "date": None}
        errors, _ = validate.validate(lib)
        self.assertTrue(any("cannot be exempt" in e for e in errors), errors)

    def test_published_still_needs_editorial_review(self):
        lib = build.Library()
        m = lib.articles["making-water-safer"]
        m["status"]["publish"] = "published"; m["status"]["editorial"] = "drafted"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("before editorial review" in e for e in errors), errors)


class SourceKindTests(unittest.TestCase):
    def test_red_cross_cannot_be_called_a_regulator(self):
        lib = build.Library()
        lib.register["x-redcross"] = {"id": "x-redcross", "title": "t", "publisher": "American Red Cross", "kind": "regulator",
                                      "url": "https://www.redcross.org/x", "verified_on": "2026-10-30", "supports": "x"}
        errors, _ = validate.validate(lib)
        self.assertTrue(any("not a regulator" in e for e in errors), errors)

    def test_nonprofit_kind_is_accepted_and_unknown_kinds_are_rejected(self):
        lib = build.Library()
        lib.register["x-ok"] = {"id": "x-ok", "title": "t", "publisher": "American Red Cross", "kind": "nonprofit",
                                "url": "https://www.redcross.org/ok", "verified_on": "2026-10-30", "supports": "x"}
        errors, _ = validate.validate(lib)
        self.assertFalse([e for e in errors if "x-ok" in e], errors)
        lib.register["x-bad"] = {"id": "x-bad", "title": "t", "publisher": "Someone", "kind": "blog",
                                 "url": "https://example.org/bad", "verified_on": "2026-10-30", "supports": "x"}
        errors, _ = validate.validate(lib)
        self.assertTrue(any("unknown source kind" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
