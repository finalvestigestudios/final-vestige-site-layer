"""R78 isolated, synthetic/adversarial and complete 41-document review tests."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "r78_document_citation_review_matrix.py"
SPEC = importlib.util.spec_from_file_location("r78_tested", TOOL)
r78 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r78)


class TestR78DocumentMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = r78._r77().live_report()
        cls.report = r78.construct(cls.parent)
        cls.packets = cls.report["document_review_packets_NOT_APPROVED"]
        cls.r76 = cls.parent["complete_R76_evidence_UNABRIDGED_NOT_APPROVED"]

    def test_001_census_is_original_not_inflated(self):
        self.assertEqual(self.report["counts"]["articles"], 35)
        self.assertEqual(self.report["counts"]["tools"], 6)
        self.assertEqual(self.report["counts"]["distinct_source_readings_retained"], 244)
        self.assertEqual(self.report["counts"]["citation_occurrences_retained"], 2173)
        self.assertEqual(self.report["counts"]["source_variant_edges_retained"], 2359)
        self.assertEqual(self.report["counts"]["unabridged_DOM_blocks_retained"], 4070)

    def test_002_source_collisions_preserved(self):
        self.assertEqual(self.report["counts"]["shared_URL_source_groups_retained"], 32)
        self.assertEqual(self.report["counts"]["reused_source_ID_groups_retained"], 15)

    def test_003_release_guard_fields_are_explicit_false(self):
        for key in r78.HOLD_KEYS:
            self.assertIs(self.report[key], False)
        self.assertIs(self.report["publication_clearance"], False)
        self.assertEqual(self.report["release_state"], "HOLD")

    def test_004_no_human_approval_is_invented(self):
        c = self.report["counts"]
        for key in ("human_source_link_checks", "human_claim_reviews",
                    "qualified_safety_reviews", "independent_QD_approvals"):
            self.assertEqual(c[key], 0)

    def test_005_every_document_owns_distinct_private_route(self):
        routes = [p["private_draft_url"] for p in self.packets]
        self.assertEqual(len(routes), len(set(routes)))
        self.assertTrue(all(r.startswith("/preparedness/") for r in routes))

    def test_006_no_route_alias_collision_report_is_silently_resolved(self):
        self.assertEqual(self.report["route_alias_collision_review_NOT_RESOLVED"], [])

    def test_007_all_41_documents_are_unabridged(self):
        self.assertEqual(sum(len(p["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"])
                             for p in self.packets),4070)

    def test_008_consequential_review_is_lexical_only(self):
        self.assertEqual(
            self.report["counts"]["consequential_action_or_quantity_review_blocks"],
            1068)
        self.assertEqual(
            self.report["counts"]["consequential_blocks_without_same_block_citations"],
            347)

    def test_009_citation_occurrences_are_not_edges(self):
        self.assertEqual(sum(p["citation_occurrences_NOT_UNIQUE_CLAIMS"]
                             for p in self.packets),2173)
        self.assertEqual(sum(p["source_variant_edges_NOT_CLAIMS"]
                             for p in self.packets),2359)

    def test_010_original_temporal_evidence_remains_complete(self):
        parent = self.report["complete_R77_evidence_UNABRIDGED_NOT_APPROVED"]
        self.assertEqual(parent, self.parent)
        self.assertEqual(parent["fingerprint_sha256"],
                         self.report["original_R77_fingerprint_sha256"])

    def test_011_original_244_full_readings_not_deleted(self):
        readings = self.r76["all_244_unabridged_source_readings_NOT_REVIEWED"]
        self.assertEqual(len(readings),244)
        self.assertTrue(all(
            isinstance(x["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"],dict)
            for x in readings))

    def test_012_all_packets_sealed(self):
        for p in self.packets:
            self.assertEqual(p["packet_sha256"],r78.digest({
                k:v for k,v in p.items() if k!="packet_sha256"}))

    def test_013_all_block_texts_have_original_SHA(self):
        from hashlib import sha256
        for p in self.packets:
            for b in p["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]:
                self.assertEqual(
                    b["DOM_text_sha256"],
                    sha256(b["unabridged_DOM_text_NOT_REVIEWED"].encode()).hexdigest())

    def test_014_duplicate_source_IDs_remain_origin_scoped(self):
        packets=self.r76["all_origin_scoped_source_impact_packets_NOT_REVIEWED"]
        grouped={}
        for p in packets:
            grouped.setdefault(p["source_id"],set()).add(p["source_origin"])
        self.assertEqual(sum(len(v)>1 for v in grouped.values()),15)

    def test_015_local_citation_ordinals_are_distinct(self):
        for p in self.packets:
            cs=[v["citation_ordinal"] for b in
                p["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"] for v in
                b["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"]]
            self.assertEqual(cs,list(range(1,len(cs)+1)))

    def test_016_all_source_variants_keep_their_exact_URLs(self):
        for p in self.packets:
            for s in p["all_distinct_origin_scoped_sources_NOT_APPROVED"]:
                self.assertTrue(s["exact_URL_NOT_EQUIVALENCE"])
                self.assertEqual(s["human_claim_support_review"],r78.REVIEW)

    def test_017_temporal_review_is_not_freshness_approval(self):
        for p in self.packets:
            for s in p["all_distinct_origin_scoped_sources_NOT_APPROVED"]:
                self.assertIsInstance(
                    s["temporal_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"],list)

    def test_018_no_safe_medical_inference_made(self):
        self.assertNotIn("SAFE",self.report["release_state"])
        for p in self.packets:
            self.assertEqual(p["qualified_safety_review"],r78.REVIEW)
            self.assertEqual(p["independent_QD_review"],r78.REVIEW)

    def test_019_csv_row_count_is_41_and_one_way(self):
        rows=list(csv.DictReader(io.StringIO(
            r78.csv_private_document_queue(self.report))))
        self.assertEqual(len(rows),41)
        self.assertTrue(all(x["human_claim_support_review"]=="NOT_REVIEWED"
                            for x in rows))

    def test_020_csv_is_deterministic(self):
        self.assertEqual(r78.csv_private_document_queue(self.report),
                         r78.csv_private_document_queue(self.report))

    def test_021_canonical_route_normalization_is_casefolded(self):
        self.assertEqual(
            r78.route_compare_key("/preparedness/CHECK"),
            r78.route_compare_key("/preparedness/check/"))

    def test_022_route_percent_decoding_is_comparison_only(self):
        self.assertEqual(
            r78.route_compare_key("/preparedness/%66ood/"),
            "/preparedness/food/")

    def test_023_route_does_not_leak_outside_preparedness(self):
        with self.assertRaises(r78.Hold):
            r78.route_compare_key("/other/page/")

    def test_024_route_rejects_query(self):
        with self.assertRaises(r78.Hold):
            r78.route_compare_key("/preparedness/test?publish=1")

    def test_025_route_rejects_fragment(self):
        with self.assertRaises(r78.Hold):
            r78.route_compare_key("/preparedness/test#secret")

    def test_026_route_rejects_control_characters(self):
        with self.assertRaises(r78.Hold):
            r78.route_compare_key("/preparedness/test\n")

    def test_027_route_rejects_parent_traversal(self):
        with self.assertRaises(r78.Hold):
            r78.route_compare_key("/preparedness/../admin")

    def test_028_route_rejects_encoded_traversal(self):
        with self.assertRaises(r78.Hold):
            r78.route_compare_key("/preparedness/%2e%2e/admin")

    def test_029_route_rejects_duplicate_slashes(self):
        with self.assertRaises(r78.Hold):
            r78.route_compare_key("/preparedness//admin")

    def test_030_route_rejects_backslash(self):
        with self.assertRaises(r78.Hold):
            r78.route_compare_key("/preparedness/\\admin")

    def test_031_report_rejects_fingerprint_tamper(self):
        row=deepcopy(self.report)
        row["counts"]["articles"]=36
        with self.assertRaises(r78.Hold):
            r78.sealed(row)

    def test_032_report_rejects_forged_publication_even_resealed(self):
        row=deepcopy(self.report)
        row["may_publish"]=True
        row["fingerprint_sha256"]=r78.digest({
            k:v for k,v in row.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r78.Hold):
            r78.sealed(row)

    def test_033_report_rejects_forged_QD_even_resealed(self):
        row=deepcopy(self.report)
        row["independent_QD_approval"]=True
        row["fingerprint_sha256"]=r78.digest({
            k:v for k,v in row.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r78.Hold):
            r78.sealed(row)

    def test_034_source_parent_rejects_removed_source(self):
        row=deepcopy(self.parent)
        row["all_origin_scoped_temporal_review_packets_NOT_APPROVED"].pop()
        with self.assertRaises(r78.Hold):
            r78.construct(row)

    def test_035_source_parent_rejects_rewritten_original_DOM(self):
        row=deepcopy(self.parent)
        row["complete_R76_evidence_UNABRIDGED_NOT_APPROVED"][
            "all_4070_unabridged_DOM_tasks_NOT_REVIEWED"][0][
            "DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"]+=" alteration"
        with self.assertRaises(r78.Hold):
            r78.construct(row)

    def test_036_source_parent_rejects_forged_link_check(self):
        row=deepcopy(self.parent)
        row["all_origin_scoped_temporal_review_packets_NOT_APPROVED"][0][
            "human_link_check"]=True
        with self.assertRaises(r78.Hold):
            r78.construct(row)

    def test_037_source_parent_rejects_forged_QD(self):
        row=deepcopy(self.parent)
        row["independent_QD_approval"]=True
        row["fingerprint_sha256"]=r78.digest({
            k:v for k,v in row.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r78.Hold):
            r78.construct(row)

    def test_038_citation_variant_is_not_single_claim(self):
        self.assertGreater(
            self.report["counts"]["source_variant_edges_retained"],
            self.report["counts"]["citation_occurrences_retained"])

    def test_039_every_document_review_state_unapproved(self):
        self.assertEqual(
            Counter(p["human_claim_support_review"] for p in self.packets),
            Counter({r78.REVIEW:41}))

    def test_040_only_private_data_is_serialized(self):
        self.assertIn("machine_only",self.report)
        self.assertNotIn("WordPress_API_KEY",self.report)

    def test_041_fingerprint_is_reproducible(self):
        self.assertEqual(self.report["fingerprint_sha256"],
                         r78.digest({k:v for k,v in self.report.items()
                                     if k!="fingerprint_sha256"}))

    def test_042_report_counts_and_packet_sums_agree(self):
        self.assertEqual(
            sum(len(p["consequential_blocks_without_local_citations_TRIAGE_NOT_VERDICT"])
                for p in self.packets),
            self.report["counts"]["consequential_blocks_without_same_block_citations"])


def _document_test(index):
    def test(self):
        p=self.packets[index]
        self.assertEqual(
            len(p["original_DOM_block_ids_in_reading_order"]),
            len(p["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]))
        self.assertEqual(
            p["original_DOM_block_ids_in_reading_order"],
            [b["block_id"] for b in
             p["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]])
        self.assertEqual(p["human_claim_support_review"],r78.REVIEW)
        self.assertEqual(p["qualified_safety_review"],r78.REVIEW)
        self.assertEqual(p["independent_QD_review"],r78.REVIEW)
        self.assertTrue(p["private_draft_url"].startswith("/preparedness/"))
    return test


# 41 individually named, immutable original reading-order document checks.
for _index in range(41):
    setattr(TestR78DocumentMatrix,
            f"test_document_{_index + 1:02d}_unabridged_source_custody",
            _document_test(_index))


if __name__ == "__main__":
    unittest.main()
