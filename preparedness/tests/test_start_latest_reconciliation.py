"""Regression guards for latest Start Here source-scope and safety editorial rebase.

Assertions below establish the presence of review warnings and locked evidence;
they do not certify infant, medication, fire, food, or legal advice as safe.
"""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import evidence_freeze
import validate

START_HEAD = "2122d856fce9f64887c16df3d52e64be9f59a55b"
FEMA_URL = "https://www.ready.gov/sites/default/files/2024-03/ready.gov_power-outage_hazard-info-sheet.pdf"
SLUGS = (
    "go-bags", "household-emergency-plan",
    "preparedness-real-households", "three-day-kit",
)


class StartRevisionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.rows = json.loads(
            (ROOT / "sources" / "fragments" / "start.json").read_text(encoding="utf-8")
        )["sources"]

    def body(self, slug):
        return self.lib.articles[slug]["_body"].lower()

    def test_exact_contributor_commit_is_recorded(self):
        self.assertEqual(self.lib.crosswalk["source_head_commits"]["start"], START_HEAD)

    def test_new_fema_entry_limits_reading_to_english_pdf_pages(self):
        s = next(row for row in self.rows if row["id"] == "start-fema-power-sheet")
        self.assertEqual(s["kind"], "regulator")
        self.assertEqual(s["verified_on"], "2026-10-30")
        self.assertIn("pages 1-2", s["supports"].lower())
        self.assertIn("pages 3-34", s["notes"].lower())
        self.assertIn("not read", s["notes"].lower())
        self.assertIs(s["human_link_check"], False)

    def test_latest_source_row_count_and_no_claimed_human_checks(self):
        self.assertEqual(len(self.rows), 29)
        self.assertTrue(all(row["human_link_check"] is False for row in self.rows))

    def test_fema_url_has_four_preserved_independent_contributor_scopes(self):
        group = self.lib.crosswalk_groups[FEMA_URL]
        self.assertEqual(len(group["variants"]), 4)
        self.assertEqual(
            {v["origin"] for v in group["variants"]},
            {"start", "shelter", "food", "health"},
        )
        self.assertEqual(
            group["review_status"], "pending-human-source-and-reading-scope-review"
        )

    def test_entire_source_inventory_remains_exhaustive(self):
        self.assertEqual(self.lib.crosswalk["raw_source_rows"], 244)
        self.assertEqual(self.lib.crosswalk["unique_source_urls"], 202)
        self.assertEqual(self.lib.crosswalk["duplicate_url_groups"], 32)
        self.assertEqual(self.lib.crosswalk["duplicate_id_groups"], 15)

    def test_all_thirty_shared_source_groups_still_pending(self):
        self.assertEqual(len(self.lib.crosswalk_groups), 32)
        self.assertTrue(all(
            g["review_status"] == "pending-human-source-and-reading-scope-review"
            for g in self.lib.crosswalk_groups.values()
        ))

    def test_all_longform_articles_and_water_planner_remain(self):
        self.assertEqual(sum(m.get("kind") != "tool" for m in self.lib.articles.values()), 35)
        self.assertEqual(sum(m.get("kind") == "tool" for m in self.lib.articles.values()), 6)
        for slug, m in self.lib.articles.items():
            if m.get("kind") != "tool":
                with self.subTest(slug=slug):
                    self.assertGreaterEqual(build.word_count(m["_body"]), 1800)

    def test_four_revised_articles_remain_unpublished_and_safety_gated(self):
        for slug in SLUGS:
            with self.subTest(slug=slug):
                m = self.lib.articles[slug]
                self.assertEqual(m["status"]["publish"], "draft")
                self.assertEqual(m["safety_review"]["state"], "pending")
                self.assertTrue(self.lib.slate[slug]["gate"])
                self.assertEqual(self.lib.article_origins[slug], "start")

    def test_new_fema_source_cited_only_under_owning_start_scope(self):
        m = self.lib.articles["three-day-kit"]
        self.assertIn("{{cite:start-fema-power-sheet}}", m["_body"])
        self.assertIn("start-fema-power-sheet", m["source_use"])
        self.assertEqual(self.lib.source_for(m, "start-fema-power-sheet")["_origin"], "start")

    def test_essential_refrigerated_medicine_warnings_retained(self):
        body = self.body("three-day-kit")
        self.assertIn("pharmacist", body)
        self.assertIn("do not stop", body)
        self.assertIn("refrigerated medication", body)

    def test_two_hour_and_four_hour_food_disagreement_is_explicit(self):
        body = self.body("three-day-kit")
        self.assertIn("40°f", body)
        self.assertIn("the two fema sources differ", body)
        self.assertIn("when in doubt", body)

    def test_generator_twenty_foot_distance_is_not_a_safety_promise(self):
        body = self.body("three-day-kit")
        self.assertIn("20 feet", body)
        self.assertIn("not a promise of safety", body)
        self.assertIn("carbon monoxide", body)

    def test_household_drill_keeps_mains_and_critical_services_on(self):
        body = self.body("household-emergency-plan")
        self.assertIn("do not switch off the main breaker", body)
        for phrase in ("refrigerator", "smoke", "carbon monoxide",
                       "sump pump", "medical", "nonessential"):
            self.assertIn(phrase, body)

    def test_infant_acetaminophen_has_no_unsupervised_dose(self):
        body = self.body("go-bags")
        self.assertIn("no unsupervised dosing", body)
        self.assertIn("pediatrician", body)
        self.assertIn("acetaminophen", body)

    def test_infant_feeding_cleaning_and_formula_caveats_retained(self):
        body = self.body("go-bags")
        self.assertIn("starred items", body)
        self.assertIn("ready-to-feed", body)
        self.assertIn("cannot clean", body)

    def test_pregnancy_birth_supply_reference_is_context_only(self):
        body = self.body("go-bags")
        self.assertIn("emergency birth supplies: context, not instructions", body)
        self.assertIn("not covered here", body)

    def test_hud_template_reading_limit_and_legal_caution_retained(self):
        body = self.body("preparedness-real-households")
        self.assertIn("12 of its 79 pages", body)
        self.assertIn("not giving legal advice", body)
        self.assertIn("did not read", body)

    def test_fire_education_remains_fire_specific(self):
        body = self.body("preparedness-real-households")
        self.assertIn("fire only, and building by building", body)
        self.assertIn("fire department", body)

    def test_safety_and_independent_qd_have_not_been_approved(self):
        record = self.lib.crosswalk["reconciliation_20261030"]
        self.assertEqual(record["clinical_and_safety_review"], "PENDING")
        self.assertEqual(record["independent_qd_reapproval"], "PENDING")
        self.assertIs(record["human_link_review"], False)

    def test_attempted_publication_without_new_human_review_is_rejected(self):
        for slug in SLUGS:
            with self.subTest(slug=slug):
                lib = build.Library()
                m = lib.articles[slug]
                m["status"]["publish"] = "published"
                m["status"]["editorial"] = "reviewed"
                errors, _ = validate.validate(lib)
                self.assertTrue(any(
                    slug in e and "safety review is pending" in e for e in errors
                ), (slug, errors))

    def test_crosswalk_and_seventy_two_input_file_integrity(self):
        self.assertEqual(evidence_freeze.verify(self.lib), [])


    def test_all_citations_in_every_article_and_tool_have_individual_scope_notes(self):
        import re
        for slug, meta in self.lib.articles.items():
            cited = set(re.findall(r"\{\{cite:([a-z0-9-]+)\}\}", meta["_body"]))
            with self.subTest(slug=slug):
                self.assertEqual(cited, set(meta.get("source_use", {})))

    def test_deleted_water_guide_reading_scope_note_fails_validation(self):
        lib = build.Library()
        del lib.articles["homemade-water-filters"]["source_use"]["cdc-find-clean-water"]
        errors, _ = validate.validate(lib)
        self.assertTrue(any(
            "homemade-water-filters" in e and "source_use reading-scope note" in e
            for e in errors
        ), errors)

    def test_deleted_start_guide_reading_scope_note_fails_validation(self):
        lib = build.Library()
        del lib.articles["preparedness-real-households"]["source_use"]["start-ready-plan"]
        errors, _ = validate.validate(lib)
        self.assertTrue(any(
            "preparedness-real-households" in e and "source_use reading-scope note" in e
            for e in errors
        ), errors)


if __name__ == "__main__":
    unittest.main()
