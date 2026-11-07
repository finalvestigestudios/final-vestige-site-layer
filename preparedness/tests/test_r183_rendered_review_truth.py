"""R183: prevent legacy safety labels from implying independent source/safety or QD approval.

The original 35-item slate stays unpublished. This suite tests draft markup; it
does not assert source truth, clinical or food safety, checkout, or release approval.
"""
from __future__ import annotations
import importlib.util
import inspect
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("preparedness_r183_build", ROOT / "tools" / "build.py")
assert SPEC is not None and SPEC.loader is not None
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)

APPROVED = {"making-water-safer", "salt-beef-salt-pork-age-of-sail"}
NOT_REQUIRED = {"navigation-before-gps", "pioneer-supply-chains-failed",
                "root-cellars-cool-storage", "sanitation-before-germ-theory"}
ALL_SLUGS = (
    "emergency-hygiene-sanitation", "family-communication-plan", "fire-making-across-time",
    "food-safety-power-outage", "go-bags", "history-of-food-preservation",
    "home-fire-escape-plan", "homemade-water-filters", "household-emergency-plan",
    "lewis-and-clark-salt-works", "making-water-safer", "medication-and-devices",
    "navigation-before-gps", "outage-heat-cold-generators", "pantry-rotation",
    "pemmican-and-dried-meats", "pickling-fermentation-old-recipes",
    "pioneer-supply-chains-failed", "pioneer-travel-rations",
    "preparedness-real-households", "pressure-canning-low-acid",
    "rain-barrels-and-cisterns", "root-cellars-cool-storage", "safe-jerky-dehydration",
    "salt-beef-salt-pork-age-of-sail", "sanitation-before-germ-theory",
    "shelter-or-evacuate", "ships-biscuit-and-hardtack",
    "smokehouses-salting-curing", "three-day-kit", "two-week-water-storage",
    "warnings-radios-offline-maps", "water-advisories-explained", "water-math",
    "water-purification-through-history",
)

def meta(slug="household-emergency-plan", state="pending", editorial="reviewed"):
    return {
        "slug": slug, "title": "Original guide", "dek": "Source-led explanation",
        "track": "modern", "section": "start-here", "tags": [],
        "_body": "<p>Original test-only body.</p>", "read_minutes": 2,
        "last_checked": "2026-11-03", "updated": "2026-11-03",
        "status": {"editorial": editorial, "publish": "draft"},
        "safety_review": {"state": state, "reviewer": "Historical record",
                          "date": "2026-11-03"},
    }

class FakeLibrary:
    taxonomy = {"tracks": {"modern": {"label": "Act Now"}}}
    def url_path(self, slug):
        return "/preparedness/" + slug + "/"

class TestR183ReviewTruth(unittest.TestCase):
    def test_roster_is_35_and_disjoint(self):
        self.assertEqual(len(ALL_SLUGS), 35)
        self.assertEqual(len(set(ALL_SLUGS)), 35)
        self.assertEqual(len(APPROVED), 2)
        self.assertEqual(len(NOT_REQUIRED), 4)
        self.assertFalse(APPROVED & NOT_REQUIRED)

    def test_historical_approval_not_independent(self):
        markup = build.review_block(meta(state="approved"))
        self.assertIn("Historical label recorded as approved by", markup)
        self.assertIn("This label has not been independently verified.", markup)
        self.assertIn("independent QD", markup)
        self.assertNotIn("<dd>Approved by ", markup)

    def test_not_required_keeps_editorial_hold(self):
        markup = build.review_block(meta(state="not-required"))
        self.assertIn("Historically marked not required", markup)
        self.assertIn("Editorial source review and independent QD", markup)

    def test_pending_needs_human_review(self):
        markup = build.review_block(meta(state="pending"))
        self.assertIn("Pending. Human source/safety review", markup)

    def test_missing_safety_field_fails_closed(self):
        m = meta()
        del m["safety_review"]
        self.assertIn("Pending. Human source/safety review", build.review_block(m))

    def test_unrecognized_state_not_approved(self):
        self.assertIn("Unrecognized safety-review state",
                      build.review_block(meta(state="greenlit")))

    def test_editorial_review_is_not_independent(self):
        self.assertIn("Editorially reviewed (not independent safety or QD approval)",
                      build.review_block(meta(editorial="reviewed")))

    def test_drafted_editorial_label(self):
        self.assertIn("Drafted; editor read-through pending",
                      build.review_block(meta(editorial="drafted")))

    def test_reviewer_html_escaped(self):
        m = meta(state="approved")
        m["safety_review"]["reviewer"] = "<img src=x onerror=alert(1)>"
        out = build.review_block(m)
        self.assertNotIn("<img", out)
        self.assertIn("&lt;img", out)

    def test_reviewer_ampersand_escaped(self):
        m = meta(state="approved")
        m["safety_review"]["reviewer"] = "A & B"
        self.assertIn("A &amp; B", build.review_block(m))

    def test_review_date_markup_escaped(self):
        m = meta(state="approved")
        m["safety_review"]["date"] = "<svg/onload=alert(1)>"
        out = build.review_block(m)
        self.assertNotIn("<svg", out)
        self.assertIn("&lt;svg", out)

    def test_all_legacy_states_card_pending(self):
        for st in ("approved", "not-required", "pending"):
            with self.subTest(st=st):
                out = build.render_card(FakeLibrary(), meta(state=st))
                self.assertIn('data-verify="pending"', out)
                self.assertNotIn('data-verify="reviewed"', out)

    def test_original_dek_preserved(self):
        self.assertIn("Source-led explanation",
                      build.render_card(FakeLibrary(), meta()))

    def test_slug_preserved(self):
        self.assertIn("/preparedness/three-day-kit/",
                      build.render_card(FakeLibrary(), meta(slug="three-day-kit")))

    def test_card_remains_draft(self):
        self.assertIn("Draft</span>", build.render_card(FakeLibrary(), meta()))

    def test_card_no_fabricated_qd(self):
        self.assertNotIn("QD PASS",
                         build.render_card(FakeLibrary(), meta(state="approved")))

    def test_builder_has_all_draft_warning(self):
        src = inspect.getsource(build.build_article)
        self.assertIn("Independent safety/source and QD verification pending", src)
        self.assertIn('if meta["status"]["publish"] != "published"', src)

    def test_builder_has_no_publication_statement(self):
        self.assertIn("Draft: not public", inspect.getsource(build.build_article))

    def test_card_no_implicit_legacy_approved_branch(self):
        self.assertNotIn('("approved", "not-required")', inspect.getsource(build.render_card))

    def test_sources_check_date_preserved(self):
        self.assertIn("November 3, 2026", build.review_block(meta()))

    def test_review_record_heading_present(self):
        self.assertIn("Review record</h2>", build.review_block(meta()))

    def test_authentic_35_metadata_custody_and_rendered_review_records(self):
        """Trusted-repository integration; requires all original 35 metadata files.

        Never silently skip if the checkout is incomplete. A passing case does
        not decide whether any source or safety claim is factually correct.
        """
        import hashlib
        import json
        roster_path = ROOT / "review" / "r178" / "safety_state_roster.json"
        roster = json.loads(roster_path.read_text(encoding="utf-8"))
        self.assertEqual(roster["schema"], "fv-preparedness-r178-35-safety-state-custody-v1")
        self.assertEqual(len(roster["articles"]), 35)
        for item in roster["articles"]:
            with self.subTest(slug=item["slug"]):
                p = ROOT / "content" / "articles" / (item["slug"] + ".meta.json")
                raw = p.read_bytes()
                h = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\\0" + raw).hexdigest()
                self.assertEqual(h, item["meta_git_blob"])
                original = json.loads(raw.decode("utf-8"))
                self.assertEqual(original["slug"], item["slug"])
                self.assertEqual(original["safety_review"]["state"], item["recorded_state"])
                self.assertEqual(original["status"]["publish"], "draft")
                rendered = build.review_block(original)
                self.assertIn("independent QD", rendered)
                self.assertNotIn("<dd>Approved by ", rendered)
                self.assertNotIn("<dd>Not required for this topic.</dd>", rendered)

def slate_test(slug):
    def case(self):
        state = ("approved" if slug in APPROVED else
                 "not-required" if slug in NOT_REQUIRED else "pending")
        m = meta(slug=slug, state=state)
        label = build.review_block(m)
        card = build.render_card(FakeLibrary(), m)
        self.assertIn("independent QD", label)
        self.assertIn('data-verify="pending"', card)
        self.assertIn("Draft</span>", card)
        if state == "approved":
            self.assertIn("not been independently verified", label)
        elif state == "not-required":
            self.assertIn("Editorial source review", label)
        else:
            self.assertIn("Pending. Human source/safety review", label)
    return case

for slug in ALL_SLUGS:
    setattr(TestR183ReviewTruth, "test_slate_" + slug.replace("-", "_"), slate_test(slug))

if __name__ == "__main__":
    unittest.main()
