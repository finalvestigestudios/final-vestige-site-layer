#!/usr/bin/env python3
"""R56 regression and adversarial tests for private safety/source crosswalk."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


gate = module("r56_review_coverage_tests", ROOT / "tools" /
              "r56_unreviewed_action_source_crosswalk.py")
fixture_module = module("r56_original_r54_fixture", ROOT / "tests" /
                        "test_r54_action_review_export.py")
r54 = fixture_module.gate
EXPECTED = fixture_module.COUNTS


def original():
    return fixture_module.fixture()


def audit(report=None, expected=EXPECTED):
    return gate.crosswalk(original() if report is None else report,
                          expected=expected)


class Positive(unittest.TestCase):
    def test_all_three_fixture_actions_remain(self):
        x = audit()
        self.assertEqual(len(x["original_unreviewed_action_rows"]), 3)
        self.assertEqual(x["counts"]["all_original_action_work_orders"], 3)

    def test_source_rows_retain_both_contributors(self):
        x = audit()
        sources = x["original_unreviewed_action_source_rows"]
        self.assertEqual(len(sources), 2)
        self.assertEqual({z["source_id"] for z in sources}, {"s1", "s2"})
        self.assertEqual({z["source_contributor_origin"] for z in sources}, {"a", "b"})

    def test_same_url_not_deduplicated(self):
        group = audit()["shared_url_variant_review_queue"][0]
        self.assertEqual(len(group["ALL_original_action_scoped_reading_occurrences"]), 2)
        self.assertEqual(len(group["distinct_source_variants_not_merged"]), 2)
        self.assertEqual(group["original_url_exact_not_canonicalized"],
                         "https://example.org/shared-record")

    def test_repeated_citation_occurrence_preserved(self):
        a = audit()["original_unreviewed_action_rows"][0]
        self.assertEqual(a["citation_source_id_occurrences_json"], ["s1", "s1"])
        self.assertEqual(a["same_block_citation_count"], 2)

    def test_original_full_scope_unicode_preserved(self):
        x = audit()
        self.assertIn("\u202e",
                      x["original_unreviewed_action_source_rows"][0]
                       ["original_source_reading_scope"])
        self.assertIn("\nline 2",
                      x["original_unreviewed_action_source_rows"][0]
                       ["original_source_reading_scope"])

    def test_uncited_work_order_kept_separate(self):
        x = audit()
        self.assertEqual(len(x["uncited_action_review_queue"]), 1)
        self.assertEqual(x["uncited_action_review_queue"][0]["block_ordinal"], 2)
        self.assertEqual(x["uncited_action_review_queue"][0]["source_readings_count"], 0)

    def test_fallbacks_empty_in_fixture(self):
        self.assertEqual(audit()["fallback_source_scope_review_queue"], [])

    def test_historical_access_includes_matching_source(self):
        x = audit()
        self.assertEqual(len(x["historical_access_hold_queue"]), 1)
        hold = x["historical_access_hold_queue"][0]
        self.assertEqual(hold["original_source_id"], "s2")
        self.assertEqual(len(hold["action_scoped_readings_if_any"]), 1)
        self.assertTrue(hold["historical_failure_only_not_current_access_verdict"])

    def test_all_safety_incidents_remain_unapproved(self):
        x = audit()
        self.assertEqual([z["incident_id"] for z in
                          x["open_safety_exceptions_without_verified_article_mapping"]],
                         ["SX-01", "SX-02"])
        self.assertIn("HUMAN_EXACT_ARTICLE", x["safety_incident_mapping_status"])

    def test_digest_determinism(self):
        self.assertEqual(audit(), audit())

    def test_input_not_mutated(self):
        r = original()
        before = copy.deepcopy(r)
        audit(r)
        self.assertEqual(r, before)

    def test_all_authorization_flags_false(self):
        x = audit()
        self.assertEqual(x["release_state"], "HOLD")
        self.assertTrue(x["machine_only"])
        self.assertEqual(x["review_state"], gate.REVIEW_STATE)
        for flag in gate.FLAGS:
            self.assertIs(x[flag], False)

    def test_valid_crosswalk_verifies(self):
        r = original()
        self.assertTrue(gate.verify_crosswalk(r, audit(r), expected=EXPECTED))

    def test_fingerprint_matches_canonical_original(self):
        x = audit()
        self.assertEqual(x["fingerprint_sha256"],
                         r54.digest({k: v for k, v in x.items()
                                     if k != "fingerprint_sha256"}))

    def test_subset_not_claiming_global_30_43_clearance(self):
        x = audit()
        self.assertIn("NOT_CLEARED",
                      x["corpus_wide_30_shared_URL_groups_and_43_fallbacks"])

    def test_fallback_scope_included_when_original_flag_true(self):
        r = original()
        r["work_orders"][0]["source_readings_in_article_scope"][0][
            "base_fallback_requires_human_review"] = True
        fixture_module.repin(r)
        x = audit(r)
        self.assertEqual(len(x["fallback_source_scope_review_queue"]), 1)
        self.assertEqual(x["fallback_source_scope_review_queue"][0]["source_id"], "s1")

    def test_historic_blocker_without_action_still_retained(self):
        r = original()
        r["blocked_historical_source_ids_not_current_link_failures"] = ["unseen"]
        fixture_module.repin(r)
        x = audit(r)
        self.assertEqual(x["historical_access_hold_queue"][0][
            "action_scoped_readings_if_any"], [])

    def test_self_rehashed_changed_scope_remains_unverified(self):
        r = original()
        r["work_orders"][0]["source_readings_in_article_scope"][0][
            "original_source_reading_scope"] = "Changed; still NOT independently verified"
        fixture_module.repin(r)
        x = audit(r)
        self.assertFalse(x["human_source_links_verified"])
        self.assertIn("Changed", x["original_unreviewed_action_source_rows"][0]
                      ["original_source_reading_scope"])

    def test_real_corpus_full_35_articles_and_water_tool(self):
        if not (ROOT / "sources" / "register.json").is_file():
            self.skipTest("original offline Preparedness corpus unavailable")
        r = r54.original_report(ROOT.parent)
        x = gate.crosswalk(r)
        c = x["counts"]
        self.assertEqual(c["all_original_action_work_orders"], 779)
        self.assertEqual(c["uncited_consequential_action_blocks"], 237)
        self.assertEqual(c["cited_consequential_action_blocks"], 542)
        self.assertEqual(c["open_safety_exceptions_without_authenticated_clearance"], 15)
        self.assertEqual(c["historical_machine_access_holds_not_current_link_failures"], 25)
        self.assertFalse(x["may_publish"])


# The original evidence is self-hashed, never trusted as an external approval.
# An unchanged original hash plus any changed evidence must be rejected.
STALE_PATHS = (
    ("schema",), ("issue",), ("release_state",), ("machine_authority",),
    ("article_count",), ("may_publish",), ("qualified_safety_clearance",),
    ("independent_QD_approval",), ("human_source_links_verified",),
    ("claim_accuracy_verified",),
    ("counts", "uncited_action_blocks"),
    ("counts", "cited_action_blocks"),
    ("counts", "open_safety_exceptions"),
    ("counts", "unresolved_historic_source_ids"),
    ("work_orders", 0, "article"),
    ("work_orders", 0, "block_ordinal"),
    ("work_orders", 0, "original_article_html_sha256"),
    ("work_orders", 0, "original_R13_flag_sha256"),
    ("work_orders", 0, "excerpt_not_factually_verified"),
    ("work_orders", 0, "review_state"),
    ("work_orders", 0, "machine_priority_not_safety_diagnosis"),
    ("work_orders", 0, "uncited_in_same_visible_block"),
    ("work_orders", 0, "source_readings_in_article_scope", 0, "source_id"),
    ("work_orders", 0, "source_readings_in_article_scope", 0, "original_url"),
    ("work_orders", 0, "source_readings_in_article_scope", 0,
     "original_source_reading_scope"),
    ("work_orders", 0, "source_readings_in_article_scope", 0,
     "original_source_supports_note"),
    ("open_safety_incidents", 0, "severity"),
    ("blocked_historical_source_ids_not_current_link_failures", 0),
)


def stale_test(path):
    def test(self):
        r = original()
        obj = r
        for key in path[:-1]:
            obj = obj[key]
        old = obj[path[-1]]
        obj[path[-1]] = (not old if isinstance(old, bool) else
                          old + 1 if isinstance(old, int) else
                          old + "_CHANGED" if isinstance(old, str) else
                          [] if isinstance(old, list) else None)
        with self.assertRaises(ValueError):
            audit(r)
    return test


class Negative(unittest.TestCase):
    def test_missing_action_fails(self):
        r = original()
        r["work_orders"].pop()
        fixture_module.repin(r)
        with self.assertRaises(ValueError):
            audit(r)

    def test_duplicate_article_ordinal_with_different_work_id_fails(self):
        r = original()
        extra = copy.deepcopy(r["work_orders"][0])
        extra["original_article_html_sha256"] = "f" * 64
        extra["work_order_id_sha256"] = r54.digest({
            "slug": extra["article"], "block_ordinal": extra["block_ordinal"],
            "original_article_html_sha256": extra["original_article_html_sha256"],
            "original_R13_flag_sha256": extra["original_R13_flag_sha256"],
            "citation_source_id_occurrences": extra["citation_source_id_occurrences"],
        })
        r["work_orders"].append(extra)
        r["counts"]["cited_action_blocks"] += 1
        fixture_module.repin(r)
        with self.assertRaises(gate.CrosswalkHold):
            audit(r, expected=(2, 4, 1, 3, 2, 1))

    def test_rehashed_claim_source_change_invalidates_old_crosswalk(self):
        r = original()
        x = audit(r)
        r["work_orders"][0]["source_readings_in_article_scope"][0][
            "original_source_reading_scope"] = "Different detailed reading"
        fixture_module.repin(r)
        with self.assertRaises(gate.CrosswalkHold):
            gate.verify_crosswalk(r, x, expected=EXPECTED)

    def test_rehashed_url_variant_change_invalidates_old_crosswalk(self):
        r = original()
        x = audit(r)
        r["work_orders"][0]["source_readings_in_article_scope"][0][
            "original_url"] = "https://other.example.org/source"
        fixture_module.repin(r)
        with self.assertRaises(gate.CrosswalkHold):
            gate.verify_crosswalk(r, x, expected=EXPECTED)

    def test_rehashed_safety_incident_change_invalidates_old_crosswalk(self):
        r = original()
        x = audit(r)
        r["open_safety_incidents"][0]["severity"] = "LOW"
        fixture_module.repin(r)
        with self.assertRaises(gate.CrosswalkHold):
            gate.verify_crosswalk(r, x, expected=EXPECTED)

    def test_rehashed_fallback_change_invalidates_old_crosswalk(self):
        r = original()
        x = audit(r)
        r["work_orders"][0]["source_readings_in_article_scope"][0][
            "base_fallback_requires_human_review"] = True
        fixture_module.repin(r)
        with self.assertRaises(gate.CrosswalkHold):
            gate.verify_crosswalk(r, x, expected=EXPECTED)

    def test_forced_approval_remains_invalid_after_rehash(self):
        r = original()
        r["qualified_safety_clearance"] = True
        fixture_module.repin(r)
        with self.assertRaises(ValueError):
            audit(r)


TAMPER_KEYS = (
    "schema", "issue", "release_state", "review_state",
    "machine_only", "source_report_R53_sha256", "counts",
    "original_unreviewed_action_rows", "original_unreviewed_action_source_rows",
    "uncited_action_review_queue", "shared_url_variant_review_queue",
    "fallback_source_scope_review_queue", "historical_access_hold_queue",
    "open_safety_exceptions_without_verified_article_mapping",
    "safety_incident_mapping_status", "limitations",
    "may_publish", "qualified_safety_clearance", "independent_QD_approval",
    "human_source_links_verified", "claim_accuracy_verified",
    "fingerprint_sha256",
)


def mutated_result_test(field):
    def test(self):
        r = original()
        x = audit(r)
        old = x[field]
        x[field] = (not old if isinstance(old, bool) else
                    old + "_FORGED" if isinstance(old, str) else
                    {} if isinstance(old, dict) else
                    old + [{"_forged": True}] if isinstance(old, list) else 0)
        with self.assertRaises(gate.CrosswalkHold):
            gate.verify_crosswalk(r, x, expected=EXPECTED)
    return test


for i, path in enumerate(STALE_PATHS):
    setattr(Negative, "test_stale_original_%02d" % i, stale_test(path))
for i, key in enumerate(TAMPER_KEYS):
    setattr(Negative, "test_forged_crosswalk_%02d_%s" % (i, key),
            mutated_result_test(key))


if __name__ == "__main__":
    unittest.main()
