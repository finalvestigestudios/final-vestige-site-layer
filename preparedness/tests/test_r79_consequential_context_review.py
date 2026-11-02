"""R79: independent contextual reviewer work orders; synthetic mutation guards."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest

TOOL=Path(__file__).resolve().parents[1]/"tools"/"r79_consequential_context_review.py"
SPEC=importlib.util.spec_from_file_location("r79_under_test",TOOL)
r79=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r79)


def synthetic(text, citations=(), ident="b"):
    return {
        "block_id":ident,
        "unabridged_DOM_text_NOT_REVIEWED":text,
        "DOM_text_sha256":hashlib.sha256(text.encode()).hexdigest(),
        "citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF":
            list(citations)}


class TestR79Conservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Live report reconstructs the source provenance exactly once.
        cls.report=r79.live_report()
        cls.parent=cls.report["complete_R78_evidence_UNABRIDGED_NOT_APPROVED"]
        cls.orders=cls.report["review_orders_347_NOT_UNSUPPORTED_OR_UNSAFE_VERDICTS"]
        # Verified once for all CSV assertions; avoid rebuilding an entire
        # seven-cluster evidence tree for every serialization-only test.
        cls.private_csv=r79.csv_private_queue(cls.report)
        cls.docs=cls.parent["document_review_packets_NOT_APPROVED"]
        cls.lookup={(d["kind"],d["slug"]):d for d in cls.docs}

    def test_001_all_original_docs_conserved(self):
        self.assertEqual((self.report["counts"]["articles"],
                          self.report["counts"]["tools"]),(35,6))

    def test_002_all_original_readings_conserved(self):
        self.assertEqual(self.report["counts"]["source_readings_preserved"],244)

    def test_003_original_citation_occurrences_conserved(self):
        self.assertEqual(self.report["counts"]["citation_occurrences_preserved"],2173)

    def test_004_source_variant_edges_are_not_citations(self):
        self.assertEqual(self.report["counts"]["origin_scoped_source_variant_edges_preserved"],2359)

    def test_005_original_DOM_blocks_conserved(self):
        self.assertEqual(self.report["counts"]["original_DOM_blocks_preserved"],4070)

    def test_006_original_shared_URL_groups_unresolved(self):
        self.assertEqual(self.report["counts"]["shared_URL_groups_unresolved"],32)

    def test_007_original_reused_source_ID_groups_unresolved(self):
        self.assertEqual(self.report["counts"]["reused_ID_groups_unresolved"],15)

    def test_008_all_lexical_candidates_conserved(self):
        self.assertEqual(self.report["counts"]["consequential_lexical_review_blocks"],1068)

    def test_009_347_uncited_lexical_review_orders(self):
        self.assertEqual(len(self.orders),347)
        self.assertEqual(self.report["counts"][
            "consequential_without_same_block_citation_review_orders"],347)

    def test_010_all_41_document_summaries(self):
        self.assertEqual(len(self.report["document_workload_overview_41_PRIVATE"]),41)

    def test_011_all_work_orders_original_text(self):
        for t in self.orders:
            self.assertEqual(
                hashlib.sha256(t["full_consequential_text_NOT_SAFETY_VERIFIED"]
                .encode()).hexdigest(),t["original_R72_DOM_text_sha256"])

    def test_012_no_same_block_citation_claimed(self):
        self.assertTrue(all(t["local_citations"]==[] for t in self.orders))

    def test_013_block_ids_are_unique_in_document(self):
        keys=[(t["kind"],t["slug"],t["block_id"]) for t in self.orders]
        self.assertEqual(len(keys),len(set(keys)))

    def test_014_original_reading_position_preserved(self):
        for t in self.orders:
            d=self.lookup[(t["kind"],t["slug"])]
            pos=t["original_block_index_1_based"]-1
            self.assertEqual(d["original_DOM_block_ids_in_reading_order"][pos],
                             t["block_id"])

    def test_015_nearby_text_is_unabridged(self):
        for t in self.orders:
            for n in t["neighboring_blocks_WITH_FULL_TEXT_NOT_SAFETY_VERIFIED"]:
                self.assertEqual(
                    hashlib.sha256(n["full_neighbor_text_NOT_SAFETY_VERIFIED"]
                    .encode()).hexdigest(),n["original_DOM_text_sha256"])

    def test_016_nearby_distance_never_zero(self):
        for t in self.orders:
            for n in t["neighboring_blocks_WITH_FULL_TEXT_NOT_SAFETY_VERIFIED"]:
                self.assertIn(n["signed_block_distance_NOT_SUPPORT"],(-2,-1,1,2))

    def test_017_nearby_citations_keep_original_variants(self):
        for t in self.orders:
            d=self.lookup[(t["kind"],t["slug"])]
            pos=t["original_block_index_1_based"]-1
            for n in t["neighboring_blocks_WITH_FULL_TEXT_NOT_SAFETY_VERIFIED"]:
                original=d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][
                    pos+n["signed_block_distance_NOT_SUPPORT"]]
                self.assertEqual(
                    n["all_neighbor_citations_NOT_CLAIM_SUPPORT"],
                    original["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"])

    def test_018_nearest_left_is_actually_nearest(self):
        for t in self.orders:
            d=self.lookup[(t["kind"],t["slug"])]
            pos=t["original_block_index_1_based"]-1
            expect=r79.nearest_cited(d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"],pos,-1)
            self.assertEqual(t["nearest_prior_cited_block_NOT_CLAIM_SUPPORT"],expect)

    def test_019_nearest_right_is_actually_nearest(self):
        for t in self.orders:
            d=self.lookup[(t["kind"],t["slug"])]
            pos=t["original_block_index_1_based"]-1
            expect=r79.nearest_cited(d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"],pos,1)
            self.assertEqual(t["nearest_next_cited_block_NOT_CLAIM_SUPPORT"],expect)

    def test_020_every_packet_has_immutable_fingerprint(self):
        for t in self.orders:
            self.assertEqual(t["packet_sha256"],r79.digest({
                k:v for k,v in t.items() if k!="packet_sha256"}))

    def test_021_previous_R78_report_fully_preserved(self):
        self.assertEqual(self.report["complete_R78_evidence_UNABRIDGED_NOT_APPROVED"],
                         self.parent)

    def test_022_previous_R78_fingerprint_preserved(self):
        self.assertEqual(self.report["original_R78_fingerprint_sha256"],
                         self.parent["fingerprint_sha256"])

    def test_023_release_state_is_hold(self):
        self.assertEqual(self.report["release_state"],"HOLD")
        self.assertIs(self.report["publication_clearance"],False)

    def test_024_every_approval_gate_is_false(self):
        for k in r79.HOLD_KEYS:
            self.assertIs(self.report[k],False)

    def test_025_human_review_counts_are_zero(self):
        for k in ("human_link_checks","human_claim_support_reviews",
                  "qualified_safety_reviews","independent_QD_approvals"):
            self.assertEqual(self.report["counts"][k],0)

    def test_026_work_orders_do_not_infer_safety(self):
        for t in self.orders:
            self.assertEqual(t["qualified_safety_review"],r79.REVIEW)
            self.assertEqual(t["human_claim_support_review"],r79.REVIEW)
            self.assertEqual(t["independent_QD_review"],r79.REVIEW)

    def test_027_csv_is_one_way_and_carries_347_rows(self):
        rows=list(csv.DictReader(io.StringIO(self.private_csv)))
        self.assertEqual(len(rows),347)
        self.assertTrue(all(x["qualified_safety_review"]==r79.REVIEW for x in rows))

    def test_028_csv_round_trip_full_text_preserved(self):
        rows=list(csv.DictReader(io.StringIO(self.private_csv)))
        self.assertEqual(len(rows),len(self.orders))
        for i,(row,order) in enumerate(zip(rows,self.orders)):
            self.assertEqual(row["block_id"],order["block_id"],i)
            # Formula-injection-safe cells can deliberately get a leading apostrophe.
            raw=order["full_consequential_text_NOT_SAFETY_VERIFIED"]
            self.assertEqual(row["full_consequential_text_NOT_VERDICT"],
                             r79._csv_safe(raw))

    def test_029_csv_output_deterministic(self):
        # A fresh one-way export must be byte-identical with the previously
        # source-verified export; never cache verification in production.
        self.assertEqual(self.private_csv, r79.csv_private_queue(self.report))

    def test_030_report_fingerprint_exact(self):
        self.assertEqual(self.report["fingerprint_sha256"],r79.digest({
            k:v for k,v in self.report.items() if k!="fingerprint_sha256"}))

    def test_031_forged_publish_gate_rejected_even_resealed(self):
        row=deepcopy(self.report);row["may_publish"]=True
        row["fingerprint_sha256"]=r79.digest({
            k:v for k,v in row.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r79.Hold):r79.sealed(row)

    def test_032_forged_QD_rejected_even_resealed(self):
        row=deepcopy(self.report);row["independent_QD_approval"]=True
        row["fingerprint_sha256"]=r79.digest({
            k:v for k,v in row.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r79.Hold):r79.sealed(row)

    def test_033_forged_qualified_safety_clearance_rejected(self):
        row=deepcopy(self.report);row["qualified_safety_clearance"]=True
        row["fingerprint_sha256"]=r79.digest({
            k:v for k,v in row.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r79.Hold):r79.sealed(row)

    def test_034_removing_review_packet_is_detected(self):
        row=deepcopy(self.report)
        row["review_orders_347_NOT_UNSUPPORTED_OR_UNSAFE_VERDICTS"].pop()
        row["fingerprint_sha256"]=r79.digest({
            k:v for k,v in row.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r79.Hold):r79.verify(row)

    def test_035_rewriting_consequential_text_is_detected(self):
        row=deepcopy(self.report)
        row["review_orders_347_NOT_UNSUPPORTED_OR_UNSAFE_VERDICTS"][0][
            "full_consequential_text_NOT_SAFETY_VERIFIED"]="altered"
        row["fingerprint_sha256"]=r79.digest({
            k:v for k,v in row.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r79.Hold):r79.verify(row)

    def test_036_forced_source_link_approval_in_parent_rejected(self):
        parent=deepcopy(self.parent)
        parent["complete_R77_evidence_UNABRIDGED_NOT_APPROVED"][
            "all_origin_scoped_temporal_review_packets_NOT_APPROVED"][0][
            "human_link_check"]=True
        with self.assertRaises(ValueError):r79.construct(parent)


class TestR79Synthetic(unittest.TestCase):
    def setUp(self):
        self.blocks=[
            synthetic("first cited", [{"citation_ordinal":1}], "first"),
            synthetic("uncited emergency passage",[],"middle"),
            synthetic("next cited", [{"citation_ordinal":2}],"next"),
            synthetic("end without source",[],"end")]

    def test_037_nearest_cited_left(self):
        self.assertEqual(r79.nearest_cited(self.blocks,1,-1)[
            "signed_block_distance_NOT_EVIDENCE_OF_SUPPORT"],-1)

    def test_038_nearest_cited_right(self):
        self.assertEqual(r79.nearest_cited(self.blocks,1,1)[
            "signed_block_distance_NOT_EVIDENCE_OF_SUPPORT"],1)

    def test_039_nearest_cited_left_empty(self):
        self.assertIsNone(r79.nearest_cited(self.blocks,0,-1))

    def test_040_nearest_cited_right_empty(self):
        self.assertIsNone(r79.nearest_cited(self.blocks,2,1))

    def test_041_full_context_uses_both_sides(self):
        self.assertEqual([x["signed_block_distance_NOT_SUPPORT"]
                          for x in r79.context(self.blocks,1)],[-1,1,2])

    def test_042_context_respects_document_boundary(self):
        self.assertEqual([x["signed_block_distance_NOT_SUPPORT"]
                          for x in r79.context(self.blocks,0)],[1,2])

    def test_043_context_small_radius(self):
        self.assertEqual([x["signed_block_distance_NOT_SUPPORT"]
                          for x in r79.context(self.blocks,1,radius=1)],[-1,1])

    def test_044_context_invalid_negative_index(self):
        with self.assertRaises(r79.Hold):r79.context(self.blocks,-1)

    def test_045_context_invalid_past_end(self):
        with self.assertRaises(r79.Hold):r79.context(self.blocks,4)

    def test_046_context_invalid_radius_zero(self):
        with self.assertRaises(r79.Hold):r79.context(self.blocks,1,radius=0)

    def test_047_context_invalid_radius_above_eight(self):
        with self.assertRaises(r79.Hold):r79.context(self.blocks,1,radius=9)

    def test_048_invalid_nearest_direction_zero(self):
        with self.assertRaises(r79.Hold):r79.nearest_cited(self.blocks,1,0)

    def test_049_invalid_nearest_direction_two(self):
        with self.assertRaises(r79.Hold):r79.nearest_cited(self.blocks,1,2)

    def test_050_invalid_nearest_index(self):
        with self.assertRaises(r79.Hold):r79.nearest_cited(self.blocks,9,-1)

    def test_051_no_citations_returns_none(self):
        only=[synthetic("one",[]),synthetic("two",[])]
        self.assertIsNone(r79.nearest_cited(only,0,1))

    def test_052_nearest_skips_uncited_between(self):
        self.assertEqual(r79.nearest_cited(self.blocks,3,-1)[
            "signed_block_distance_NOT_EVIDENCE_OF_SUPPORT"],-1)

    def test_053_nearest_full_text_unabridged(self):
        self.assertEqual(r79.nearest_cited(self.blocks,1,1)[
            "full_cited_block_text_NOT_SAFETY_VERIFIED"],"next cited")

    def test_054_neighbor_citations_conserved(self):
        ctx=r79.context(self.blocks,1)
        self.assertEqual(ctx[0]["all_neighbor_citations_NOT_CLAIM_SUPPORT"],
                         [{"citation_ordinal":1}])

    def test_055_csv_neutralizes_equals(self):
        self.assertTrue(r79._csv_safe("=2+3").startswith("'"))

    def test_056_csv_neutralizes_plus(self):
        self.assertTrue(r79._csv_safe("+cmd").startswith("'"))

    def test_057_csv_neutralizes_minus(self):
        self.assertTrue(r79._csv_safe("-cmd").startswith("'"))

    def test_058_csv_neutralizes_at(self):
        self.assertTrue(r79._csv_safe("@SUM(A1)").startswith("'"))

    def test_059_csv_neutralizes_leading_whitespace(self):
        self.assertTrue(r79._csv_safe("   =cmd").startswith("'"))

    def test_060_csv_neutralizes_zero_width_space(self):
        self.assertTrue(r79._csv_safe("\u200b=cmd").startswith("'"))

    def test_061_csv_preserves_neutral_text(self):
        self.assertEqual(r79._csv_safe("Emergency kit"),"Emergency kit")

    def test_062_empty_citation_collection_is_not_reviewed(self):
        self.assertEqual(r79.citations(self.blocks[1]),[])

    def test_063_missing_citation_collection_fails_closed(self):
        with self.assertRaises(r79.Hold):r79.citations({"block_id":"x"})

    def test_064_context_malformed_block_fails_closed(self):
        with self.assertRaises(KeyError):
            r79.context([synthetic("origin",[],"first"),{"block_id":"x"}],0)

    def test_065_digest_stable_for_key_order(self):
        self.assertEqual(r79.digest({"a":1,"b":2}),r79.digest({"b":2,"a":1}))

    def test_066_digest_rejects_nan(self):
        with self.assertRaises(ValueError):r79.digest({"value":float("nan")})

    def test_067_report_schema_name_not_approval(self):
        self.assertIn("hold",r79.SCHEMA)

    def test_068_significant_lost_neighbor_is_revealed(self):
        x=r79.nearest_cited(self.blocks,3,-1)
        self.assertEqual(x["block_id"],"next")
        self.assertEqual(x["all_neighbor_citations_WITH_DISTINCT_SOURCE_ORIGINS_NOT_SUPPORT"],
                         [{"citation_ordinal":2}])


def _document_test(index):
    def test(self):
        d=self.docs[index]
        actual=[w for w in self.orders
                if (w["kind"],w["slug"])==(d["kind"],d["slug"])]
        self.assertEqual(len(actual),len(d[
            "consequential_blocks_without_local_citations_TRIAGE_NOT_VERDICT"]))
        self.assertEqual({w["block_id"] for w in actual},
                         set(d["consequential_blocks_without_local_citations_TRIAGE_NOT_VERDICT"]))
        self.assertTrue(all(w["private_draft_url_NOT_PUBLISHED"]==
                            d["private_draft_url"] for w in actual))
    return test


for _index in range(41):
    setattr(TestR79Conservation,
            f"test_document_{_index+1:02d}_consequential_queue_custody",
            _document_test(_index))


if __name__=="__main__":
    unittest.main()
