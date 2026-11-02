"""R79: private-only complete source/action/neighbor context dependency tests."""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
import sys
from pathlib import Path
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "r79_context_source_workorders.py"
SPEC = importlib.util.spec_from_file_location("r79_tested", TOOL)
r79 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r79)


class TestR79ContextWorkOrders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Full unittest discovery has already constructed the exact, sealed
        # R78 report in its preceding test class. Reuse ONLY that validated
        # in-process report to avoid ~60 seconds of duplicate corpus I/O,
        # which otherwise trips the separate R18 180-second native-suite
        # watchdog. Standalone R79 runs rebuild the source themselves.
        previous = sys.modules.get("test_r78_document_citation_review_matrix")
        known_file = Path(__file__).with_name(
            "test_r78_document_citation_review_matrix.py").resolve()
        from_full_suite = (previous is not None and
                           Path(getattr(previous, "__file__", "")).resolve() == known_file)
        prior_class = getattr(previous, "TestR78DocumentMatrix", None) if from_full_suite else None
        prior_report = getattr(prior_class, "report", None)
        if prior_report is not None:
            r79._r78().sealed(prior_report)
            cls.parent = prior_report
        else:
            cls.parent = r79._r78().live_report()
        # Full independent R77 -> R78 reconstruction and R79 crosswalk
        # verification STILL run; no machine source/safety gate is skipped.
        cls.report = r79.construct(cls.parent)
        cls.actions = cls.report[
            "action_context_work_orders_LEXICAL_ONLY_NOT_APPROVED"]
        cls.sources = cls.report["source_work_orders_FULL_READINGS_NOT_APPROVED"]
        cls.docs = cls.report["document_source_dependency_orders_NOT_APPROVED"]

    def test_001_baseline_all_complete_documents(self):
        self.assertEqual((self.report["counts"]["article_drafts"],
                          self.report["counts"]["tool_drafts"]), (35, 6))
        self.assertEqual(len(self.docs), 41)

    def test_002_all_source_records_remain_unabridged(self):
        self.assertEqual(len(self.sources), 244)
        self.assertTrue(all(
            isinstance(s["candidate_research_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"], dict)
            for s in self.sources))

    def test_003_citation_occurrences_not_variant_edges(self):
        counts = self.report["counts"]
        self.assertEqual(counts["citation_occurrences_NOT_UNIQUE_CLAIMS"], 2173)
        self.assertEqual(counts["citation_source_variant_edges_NOT_CLAIMS"], 2359)

    def test_004_all_dom_blocks_kept_in_complete_parent(self):
        self.assertEqual(self.report["counts"]["unabridged_DOM_blocks"], 4070)
        self.assertEqual(sum(d["original_block_count"] for d in self.docs), 4070)

    def test_005_collision_groups_are_not_merged(self):
        c = self.report["counts"]
        self.assertEqual(c["shared_exact_URL_groups_NOT_EQUIVALENT"], 32)
        self.assertEqual(c["reused_ID_groups_NOT_EQUIVALENT"], 15)

    def test_006_complete_action_review_queue(self):
        self.assertEqual(len(self.actions), 1068)

    def test_007_all_347_citationless_actions_still_visible(self):
        self.assertEqual(sum(not p["all_local_citation_occurrences_NOT_CLAIM_PROOF"]
                             for p in self.actions), 347)

    def test_008_citationless_action_requires_review_flag(self):
        for p in self.actions:
            if not p["all_local_citation_occurrences_NOT_CLAIM_PROOF"]:
                self.assertIn("NO_SAME_BLOCK_CITATION_REVIEW_ONLY",
                              p["mechanical_review_cues_NOT_SAFETY_FINDINGS"])

    def test_009_local_citation_cannot_be_mistaken_for_safety_approval(self):
        self.assertTrue(all(p["qualified_safety_review"] == "NOT_REVIEWED"
                            for p in self.actions))

    def test_010_human_source_links_never_claimed_checked(self):
        self.assertEqual(sum(s["human_link_check"] is True for s in self.sources), 0)

    def test_011_human_claims_and_qualified_reviews_zero(self):
        c = self.report["counts"]
        self.assertEqual(tuple(c[k] for k in (
            "human_link_checks", "human_claim_reviews",
            "qualified_safety_reviews", "independent_QD_approvals")),
            (0, 0, 0, 0))

    def test_012_publication_release_gate_fail_closed(self):
        self.assertEqual(self.report["release_state"], "HOLD")
        self.assertIs(self.report["publication_clearance"], False)
        for k in r79.HOLD_KEYS:
            self.assertIs(self.report[k], False)

    def test_013_no_source_reading_dropped_for_lack_of_citation(self):
        self.assertEqual(
            self.report["counts"]["source_readings_without_citation_edges"], 2)

    def test_014_all_origin_source_keys_unique(self):
        self.assertEqual(len({(s["source_origin"], s["source_id"])
                              for s in self.sources}), 244)

    def test_015_all_source_workorders_sealed(self):
        for s in self.sources:
            self.assertEqual(s["packet_sha256"], r79.digest({
                k:v for k,v in s.items() if k != "packet_sha256"}))

    def test_016_all_action_workorders_sealed(self):
        for p in self.actions:
            self.assertEqual(p["packet_sha256"], r79.digest({
                k:v for k,v in p.items() if k != "packet_sha256"}))

    def test_017_full_candidate_research_hashes_verified(self):
        for s in self.sources:
            self.assertEqual(s["candidate_reading_sha256"],
                             r79.digest(
                                s["candidate_research_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]))

    def test_018_all_historical_research_if_present_hashed(self):
        for s in self.sources:
            historic = s["historical_research_reading_IF_PRESENT_UNABRIDGED"]
            if historic is None:
                self.assertIsNone(s["historical_reading_sha256"])
            else:
                self.assertEqual(s["historical_reading_sha256"],
                                 r79.digest(historic))

    def test_019_no_potentially_equivalent_url_variants_aliased(self):
        keys = defaultdict(set)
        for s in self.sources:
            keys[s["exact_URL_NO_ALIAS_OR_ENDORSEMENT"]].add(
                (s["source_origin"], s["source_id"]))
        self.assertEqual(sum(len(group) > 1 for group in keys.values()), 32)
        for s in self.sources:
            self.assertEqual(
                s["shared_exact_URL_distinct_source_origins_NOT_ALIASED"],
                [list(k) for k in sorted(keys[s["exact_URL_NO_ALIAS_OR_ENDORSEMENT"]])])

    def test_020_reused_source_ids_keep_independent_origins(self):
        ids = defaultdict(set)
        for s in self.sources:
            ids[s["source_id"]].add((s["source_origin"],s["source_id"]))
        self.assertEqual(sum(len(group) > 1 for group in ids.values()), 15)
        for s in self.sources:
            self.assertEqual(
                s["reused_source_ID_distinct_origins_NOT_ALIASED"],
                [list(k) for k in sorted(ids[s["source_id"]])])

    def test_021_source_edges_immutable_bipartite_total(self):
        self.assertEqual(sum(len(s[
            "every_downstream_citation_variant_edge_NOT_CLAIM_PROOF"])
            for s in self.sources), 2359)

    def test_022_all_action_texts_sha256_byte_exact(self):
        for p in self.actions:
            text = p["unabridged_action_text_NOT_SAFETY_REVIEWED"]
            self.assertEqual(p["DOM_text_sha256"],
                             hashlib.sha256(text.encode("utf-8")).hexdigest())

    def test_023_previous_context_texts_sha256_byte_exact(self):
        for p in self.actions:
            prev = p["previous_block_UNABRIDGED_CONTEXT_NOT_VERDICT"]
            if prev is not None:
                self.assertEqual(prev["DOM_text_sha256"],
                    hashlib.sha256(prev[
                        "DOM_text_UNABRIDGED_NOT_REVIEWED"].encode()).hexdigest())

    def test_024_next_context_texts_sha256_byte_exact(self):
        for p in self.actions:
            nxt = p["next_block_UNABRIDGED_CONTEXT_NOT_VERDICT"]
            if nxt is not None:
                self.assertEqual(nxt["DOM_text_sha256"],
                    hashlib.sha256(nxt[
                        "DOM_text_UNABRIDGED_NOT_REVIEWED"].encode()).hexdigest())

    def test_025_no_substituted_source_urls_in_workorders(self):
        for s in self.sources:
            self.assertEqual(s["exact_URL_NO_ALIAS_OR_ENDORSEMENT"],
                s["candidate_research_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]["url"])

    def test_026_source_packets_do_not_create_false_claims(self):
        self.assertTrue(all(s["human_claim_support_review"] == r79.REVIEW
                            for s in self.sources))

    def test_027_all_actions_have_document_order_positions(self):
        for p in self.actions:
            self.assertIsInstance(p["original_DOM_block_position_1_based"], int)
            self.assertGreater(p["original_DOM_block_position_1_based"], 0)

    def test_028_all_41_document_routes_remain_private(self):
        self.assertTrue(all(d["private_draft_url_NOT_PUBLIC"].startswith(
                            "/preparedness/") for d in self.docs))

    def test_029_complete_R78_parent_unchanged(self):
        self.assertEqual(
            self.report["complete_R78_evidence_UNABRIDGED_NOT_APPROVED"],
            self.parent)
        self.assertEqual(self.report["original_R78_fingerprint_sha256"],
                         self.parent["fingerprint_sha256"])

    def test_030_export_source_csv_is_one_way_and_has_244_rows(self):
        rows = list(csv.DictReader(io.StringIO(
            r79.csv_private_source_queue(self.report))))
        self.assertEqual(len(rows), 244)
        self.assertIn("reviewer_notes_UNTRUSTED",rows[0])
        self.assertTrue(all(r["human_claim_support_review"] == r79.REVIEW
                            for r in rows))

    def test_031_export_action_csv_is_one_way_and_has_1068_rows(self):
        rows = list(csv.DictReader(io.StringIO(
            r79.csv_private_action_queue(self.report))))
        self.assertEqual(len(rows), 1068)
        self.assertIn("reviewer_notes_UNTRUSTED",rows[0])
        self.assertTrue(all(r["qualified_safety_review"] == r79.REVIEW
                            for r in rows))

    def test_032_csv_leading_formula_equal_neutralized(self):
        self.assertEqual(r79.safe_csv_cell("=HYPERLINK(1)"),
                         "'=HYPERLINK(1)")

    def test_033_csv_leading_formula_at_neutralized(self):
        self.assertEqual(r79.safe_csv_cell("@SUM(1)"),"'@SUM(1)")

    def test_034_csv_leading_formula_plus_neutralized(self):
        self.assertEqual(r79.safe_csv_cell("+42"),"'+42")

    def test_035_csv_leading_formula_minus_neutralized(self):
        self.assertEqual(r79.safe_csv_cell("-42"),"'-42")

    def test_036_csv_formula_after_leading_whitespace_neutralized(self):
        self.assertEqual(r79.safe_csv_cell(" \t=cmd"),"' \t=cmd")

    def test_037_csv_leading_bom_neutralized(self):
        self.assertEqual(r79.safe_csv_cell("\ufeff=cmd"),"'\ufeff=cmd")

    def test_038_csv_inert_text_retained_verbatim(self):
        self.assertEqual(r79.safe_csv_cell("Ordinary review"),"Ordinary review")

    def test_039_csv_newline_preserves_unabridged_text(self):
        string = "first line\nsecond line"
        value=r79.safe_csv_cell(string)
        self.assertEqual(value,string)

    def test_040_tamper_unsealed_report_refused(self):
        row=deepcopy(self.report)
        row["counts"]["article_drafts"]=36
        with self.assertRaises(r79.Hold):
            r79.sealed(row)

    def test_041_forged_QD_even_if_rehashed_refused(self):
        row=deepcopy(self.report)
        row["independent_QD_approval"]=True
        row["fingerprint_sha256"]=r79.digest({
            k:v for k,v in row.items() if k != "fingerprint_sha256"})
        with self.assertRaises(r79.Hold):
            r79.sealed(row)

    def test_042_forged_publication_even_if_rehashed_refused(self):
        row=deepcopy(self.report)
        row["publication_clearance"]=True
        row["fingerprint_sha256"]=r79.digest({
            k:v for k,v in row.items() if k != "fingerprint_sha256"})
        with self.assertRaises(r79.Hold):
            r79.sealed(row)

    def test_043_wrong_parent_source_census_refused(self):
        row=deepcopy(self.parent)
        row["counts"]["articles"]=36
        with self.assertRaises(ValueError):
            r79.construct(row)

    def test_044_resigned_parent_article_change_still_refused(self):
        row=deepcopy(self.parent)
        doc=row["document_review_packets_NOT_APPROVED"][0]
        doc["private_draft_url"]="/preparedness/forged-route/"
        doc["packet_sha256"]=r79.digest({
            k:v for k,v in doc.items() if k != "packet_sha256"})
        row["fingerprint_sha256"]=r79.digest({
            k:v for k,v in row.items() if k != "fingerprint_sha256"})
        with self.assertRaises(ValueError):
            r79.construct(row)

    def test_045_parent_full_research_mutation_refused(self):
        row=deepcopy(self.parent)
        source=row["complete_R77_evidence_UNABRIDGED_NOT_APPROVED"][
            "complete_R76_evidence_UNABRIDGED_NOT_APPROVED"][
            "all_244_unabridged_source_readings_NOT_REVIEWED"][0]
        source["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]["title"]="forged"
        with self.assertRaises(ValueError):
            r79.construct(row)

    def test_046_exact_external_source_origins_remain_unreviewed(self):
        self.assertTrue(all(s["independent_QD_review"] == r79.REVIEW
                            for s in self.sources))

    def test_047_action_local_source_keys_are_unique(self):
        for p in self.actions:
            keys = p["distinct_origin_scoped_sources_NOT_EQUIVALENT"]
            self.assertEqual(len(keys),len(set(map(tuple,keys))))

    def test_048_action_context_never_reinterpreted_as_SAFETY_PASS(self):
        self.assertTrue(all(p["independent_QD_review"] == r79.REVIEW
                            for p in self.actions))

    def test_049_every_document_has_distinct_identity(self):
        self.assertEqual(len(set((d["kind"],d["slug"]) for d in self.docs)),41)

    def test_050_report_sha256_seal_reproducible(self):
        self.assertEqual(self.report["fingerprint_sha256"],
                         r79.digest({k:v for k,v in self.report.items()
                                     if k != "fingerprint_sha256"}))


def make_document_test(index):
    def test(self):
        row=self.docs[index]
        p=next(x for x in self.parent[
            "document_review_packets_NOT_APPROVED"]
            if (x["kind"],x["slug"])==(row["kind"],row["slug"]))
        self.assertEqual(row["original_block_count"],
                         len(p["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]))
        self.assertEqual(row["citation_occurrences_NOT_CLAIMS"],
                         p["citation_occurrences_NOT_UNIQUE_CLAIMS"])
        self.assertEqual(row["distinct_source_variant_edges_NOT_CLAIMS"],
                         p["source_variant_edges_NOT_CLAIMS"])
        self.assertEqual(row[
            "distinct_origin_scoped_source_keys_NOT_EQUIVALENT"],[
            [x["source_origin"],x["source_id"]]
            for x in p["all_distinct_origin_scoped_sources_NOT_APPROVED"]])
        self.assertEqual(row["human_claim_support_review"],r79.REVIEW)
        self.assertEqual(row["qualified_safety_review"],r79.REVIEW)
    return test


# 41 individually named full-document dependency checks + 50 safeguards = 91.
for _index in range(41):
    setattr(TestR79ContextWorkOrders,
            f"test_document_{_index+1:02d}_complete_dependency_custody",
            make_document_test(_index))


if __name__ == "__main__":
    unittest.main()
