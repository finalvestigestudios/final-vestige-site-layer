#!/usr/bin/env python3
"""R58: per-citation occurrence review docket preservation/adversarial tests."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

from test_r57_global_citation_action_bridge import (
    fixture, signed, gate as r57, CENSUS, INVENTORY, ACTIONS,
)

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "r58_occurrence_docket_test", ROOT / "tools" /
    "r58_exact_citation_occurrence_docket.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
EXPECTED = (2, 0, 4, 3, 1, 1, 2, 0, 0)


def private_bridge():
    lib, cited, action = fixture()
    for relation in cited["review_queue"]:
        n = relation["citation_occurrences"]
        relation["citation_token_codepoint_offsets"] = [
            3 + i * 23 for i in range(n)]
        relation["frozen_article_html_sha256"] = "a" * 64
        relation["frozen_source_use_sha256"] = "b" * 64
    signed(cited)
    return r57.bridge(lib, cited, action, census=CENSUS,
                      inventory=INVENTORY, action_census=ACTIONS)


def docket(bridge=None):
    return gate.create_docket(
        private_bridge() if bridge is None else bridge, expected=EXPECTED)


def resign(report):
    report["fingerprint_sha256"] = gate.digest({
        k: v for k, v in report.items() if k != "fingerprint_sha256"
    })


class Positive(unittest.TestCase):
    def test_all_individual_occurrences(self):
        self.assertEqual(len(docket()[
            "individual_original_citation_occurrence_review_queue"]), 4)

    def test_all_quoted_context_unabridged(self):
        self.assertEqual([x["original_unabridged_visible_context"] for x in
                          docket()["individual_original_citation_occurrence_review_queue"]],
                         ["original text evidence"] * 4)

    def test_per_article_citation_count(self):
        self.assertEqual(docket()["counts"]["per_article_citation_occurrences"],
                         {"a": 3, "b": 1})

    def test_unique_token_identity_across_repetitions(self):
        rows = docket()["individual_original_citation_occurrence_review_queue"]
        self.assertEqual(len({r["citation_occurrence_work_order_id_sha256"]
                              for r in rows}), 4)

    def test_codepoint_offsets_preserved(self):
        rows = docket()["individual_original_citation_occurrence_review_queue"]
        self.assertEqual([x["exact_original_token_identity"]
                          ["token_offset_codepoints_in_original_html"]
                          for x in rows], [3, 26, 3, 3])

    def test_same_url_preserves_separate_contributors(self):
        rows = docket()["individual_original_citation_occurrence_review_queue"]
        self.assertNotEqual(rows[0][
            "original_unabridged_contributor_source_record"]["_origin"],
            rows[3]["original_unabridged_contributor_source_record"]["_origin"])
        self.assertEqual(rows[0][
            "original_unabridged_contributor_source_record"]["url"],
            rows[3]["original_unabridged_contributor_source_record"]["url"])

    def test_linked_action_ids_are_not_claim_support(self):
        rows = docket()["individual_original_citation_occurrence_review_queue"]
        self.assertEqual(rows[0][
            "related_action_work_order_ids_same_article_source_ONLY_NOT_CLAIM_SUPPORT"],
            ["A"])
        self.assertEqual(rows[3][
            "related_action_work_order_ids_same_article_source_ONLY_NOT_CLAIM_SUPPORT"],
            [])

    def test_every_source_variant_reading_note_still_present(self):
        self.assertIn("human confirmation pending", docket()[
            "individual_original_citation_occurrence_review_queue"][0][
                "original_unabridged_contributor_source_record"]["notes"])

    def test_uncited_high_consequence_action_preserved(self):
        self.assertEqual(len(docket()["original_action_work_orders_NOT_REVIEWED"]), 2)
        self.assertEqual(docket()["original_action_work_orders_NOT_REVIEWED"][1][
            "source_readings_count"], 0)

    def test_full_source_groups_preserved(self):
        self.assertEqual(len(docket()["original_shared_url_evidence_NOT_REVIEWED"]), 1)

    def test_uncited_shared_url_variant_preserved(self):
        self.assertEqual(len(docket()["original_shared_url_evidence_NOT_REVIEWED"]
                             [0]["all_original_contributor_records"]), 2)

    def test_base_fallback_preserved(self):
        self.assertEqual(len(docket()["original_fallback_evidence_NOT_REVIEWED"]), 1)

    def test_source_relationships_preserved(self):
        self.assertEqual(docket()["counts"][
            "original_article_source_relationships"], 3)

    def test_human_states_never_promoted(self):
        rows = docket()["individual_original_citation_occurrence_review_queue"]
        self.assertTrue(all(r["human_claim_support_state"] == "NOT_REVIEWED"
                            and r["qualified_hazard_safety_state"] == "NOT_REVIEWED"
                            for r in rows))
        self.assertFalse(docket()["qualified_safety_clearance"])
        self.assertFalse(docket()["independent_QD_approval"])

    def test_generated_report_is_reproducible(self):
        self.assertEqual(gate.canonical(docket()), gate.canonical(docket()))

    def test_verified_original_packet(self):
        src = private_bridge()
        self.assertTrue(gate.verify_docket(src, docket(src), expected=EXPECTED))


class Negative(unittest.TestCase):
    def reject(self, edit):
        report = private_bridge()
        edit(report)
        resign(report)  # an attacker can self-hash an altered evidence packet
        with self.assertRaises(gate.DocketHold):
            gate.create_docket(report, expected=EXPECTED)

    def test_approval_flag_forged(self):
        self.reject(lambda r: r.__setitem__("may_publish", True))

    def test_machine_only_laundered(self):
        self.reject(lambda r: r.__setitem__("machine_only", False))

    def test_missing_source_relationship(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"].pop())

    def test_missing_visible_context(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0][
                        "all_citation_contexts_for_human_claim_review"].pop())

    def test_missing_offset(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0][
                        "citation_token_codepoint_offsets"].pop())

    def test_reordered_offset(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0][
                        "citation_token_codepoint_offsets"].reverse())

    def test_duplicate_offset(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0][
                        "citation_token_codepoint_offsets"].__setitem__(1, 3))

    def test_negative_offset(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0][
                        "citation_token_codepoint_offsets"].__setitem__(0, -1))

    def test_ambiguous_boolean_offset(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0][
                        "citation_token_codepoint_offsets"].__setitem__(0, True))

    def test_missing_article_html_hash(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0].__setitem__(
                        "frozen_article_html_sha256", None))

    def test_forged_original_source_hash(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0].__setitem__(
                        "original_source_record_sha256", "0" * 64))

    def test_source_origin_relabelled(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0].__setitem__(
                        "source_origin", "start"))

    def test_contributor_source_reading_relabelled(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0][
                        "original_source_record_as_selected"].__setitem__(
                            "notes", "silently replaced"))

    def test_disconnected_source_url(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][0].__setitem__(
                        "source_url", "https://example.invalid/"))

    def test_duplicate_relationship(self):
        self.reject(lambda r:
                    r["all_original_cited_relationships_unreviewed"][1].__setitem__(
                        "source_id", "s1"))

    def test_original_action_fake_review(self):
        self.reject(lambda r:
                    r["all_original_consequential_action_orders_unreviewed"][0].__setitem__(
                        "review_state", "APPROVED"))

    def test_original_scope_fake_review(self):
        self.reject(lambda r:
                    r["all_original_action_source_rows_unreviewed"][0].__setitem__(
                        "review_state", "APPROVED"))

    def test_missing_original_safety_inventory(self):
        self.reject(lambda r: r["counts"].__setitem__(
            "all_high_consequence_action_orders", 1))

    def test_census_requires_explicit_synthetic_override(self):
        with self.assertRaises(gate.DocketHold):
            gate.create_docket(private_bridge())

    def test_output_missing_task(self):
        b = private_bridge()
        output = docket(b)
        output["individual_original_citation_occurrence_review_queue"].pop()
        resign(output)
        with self.assertRaises(gate.DocketHold):
            gate.verify_docket(b, output, expected=EXPECTED)

    def test_docket_rejects_non_document(self):
        with self.assertRaises(gate.DocketHold):
            gate.create_docket([], expected=EXPECTED)


# Independent end-output adversarial mutations. Even recomputed output hashes
# cannot convert a modified private worksheet into a verified review.
TAMPERS = [
    ("schema",), ("issue",), ("release_state",), ("machine_only",),
    ("parent_R57_bridge_sha256",),
    ("counts", "original_articles"), ("counts", "water_tools"),
    ("counts", "exact_citation_occurrence_work_orders"),
    ("counts", "original_article_source_relationships"),
    ("counts", "unreviewed_action_work_orders"),
    ("counts", "unreviewed_global_shared_url_groups"),
    ("counts", "unreviewed_base_fallback_relationships"),
    ("counts", "open_safety_exceptions"),
    ("counts", "historical_machine_access_holds"),
    ("counts", "source_relationships_with_related_action_work_orders"),
    ("counts", "per_article_citation_occurrences", "a"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "citation_occurrence_work_order_id_sha256"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "exact_original_token_identity", "slug"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "exact_original_token_identity", "source_id"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "exact_original_token_identity", "source_origin"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "exact_original_token_identity", "citation_ordinal_within_article_source"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "exact_original_token_identity", "token_offset_codepoints_in_original_html"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "exact_original_token_identity", "frozen_article_html_sha256"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "exact_original_token_identity", "original_source_record_sha256"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "exact_original_token_identity", "original_visible_citation_context_sha256"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "original_unabridged_visible_context"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "original_unabridged_contributor_source_record", "notes"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "original_unabridged_contributor_source_record", "supports"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "original_unabridged_article_source_relationship", "citation_occurrences"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "related_action_work_order_ids_same_article_source_ONLY_NOT_CLAIM_SUPPORT"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "same_url_variants_human_review_required"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "base_fallback_human_scope_review_required"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "human_source_retrieval_state"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "human_claim_support_state"),
    ("individual_original_citation_occurrence_review_queue", 0,
     "qualified_hazard_safety_state"),
    ("original_action_work_orders_NOT_REVIEWED", 0, "article"),
    ("original_action_source_relationships_NOT_REVIEWED", 0, "source_id"),
    ("original_shared_url_evidence_NOT_REVIEWED", 0,
     "human_source_scope_review"),
    ("original_fallback_evidence_NOT_REVIEWED", 0,
     "qualified_safety_review"),
    ("may_publish",), ("independent_QD_approval",),
    ("qualified_safety_clearance",), ("human_source_links_verified",),
    ("claim_accuracy_verified",), ("human_source_reviews_completed",),
    ("source_claim_accuracy_verified",), ("limitations",),
    ("fingerprint_sha256",),
]


def tamper_test(path):
    def test(self):
        original = private_bridge()
        report = docket(original)
        item = report
        for step in path[:-1]:
            item = item[step]
        key = path[-1]
        old = item[key]
        item[key] = (
            not old if type(old) is bool else
            old + 1 if type(old) is int else
            "FALSE_APPROVAL" if type(old) is str else [])
        if path != ("fingerprint_sha256",):
            resign(report)
        with self.assertRaises(gate.DocketHold):
            gate.verify_docket(original, report, expected=EXPECTED)
    return test


for index, target in enumerate(TAMPERS, 1):
    setattr(Negative, "test_output_tamper_%02d_%s" %
            (index, target[-1]), tamper_test(target))


class RealCorpus(unittest.TestCase):
    def test_full_original_article_and_source_docket(self):
        # Actual source material stays in the checked-out private repo.
        r54 = r57.module("r54_action_review_export.py")
        r56 = r57.module("r56_unreviewed_action_source_crosswalk.py")
        build = r57.module("build.py")
        r25 = r57.module("citation_fallback_review_gate.py")
        lib = build.Library(ROOT)
        report = r54.original_report(ROOT.parent)
        action = r56.crosswalk(report)
        r56.verify_crosswalk(report, action)
        cited = r25.audit(lib)
        source = r57.bridge(lib, cited, action)
        r57.verify_bridge(lib, cited, action, source)
        x = gate.create_docket(source)
        self.assertEqual(len(x["individual_original_citation_occurrence_review_queue"]),
                         1959)
        self.assertEqual(x["counts"]["original_article_source_relationships"], 367)
        self.assertEqual(x["counts"]["unreviewed_global_shared_url_groups"], 30)
        self.assertEqual(x["counts"]["unreviewed_base_fallback_relationships"], 43)
        self.assertEqual(x["counts"]["open_safety_exceptions"], 15)
        self.assertEqual(x["counts"]["historical_machine_access_holds"], 25)
        self.assertTrue(gate.verify_docket(source, x))
        self.assertFalse(x["may_publish"])


if __name__ == "__main__":
    unittest.main()
