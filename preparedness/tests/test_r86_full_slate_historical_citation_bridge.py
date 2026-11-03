"""R86 synthetic/adversarial full-slate citation bridge, private HOLD only."""
from __future__ import annotations

from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r86_under_test", ROOT / "tools" / "r86_full_slate_historical_citation_bridge.py")
r86 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r86)
REVIEW = "NOT_REVIEWED"


def citation(sid="s", origin="water", url="https://example.org/source", rank=1):
    return {
        "raw_source_id": sid, "citation_ordinal": rank,
        "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT": [{
            "source_origin": origin, "source_id": sid,
            "complete_source_reading_sha256": "a" * 64,
            "exact_URL_NOT_CANONICALIZED": url}],
        "human_claim_support_review": REVIEW,
        "qualified_safety_review": REVIEW}


def block(citations=None, text="complete unreviewed instruction"):
    citations = list(citations or [])
    return {"block_id": "block-001", "DOM_text_sha256":
            hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "unabridged_DOM_text_NOT_REVIEWED": text,
            "citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF": citations,
            "human_claim_support_review": REVIEW,
            "qualified_safety_review": REVIEW}


def doc(kind="article", slug="one", citations=None, route=None):
    citations = list([citation()] if citations is None else citations)
    b = block(citations)
    return {"kind": kind, "slug": slug,
            "private_draft_url": route or "/preparedness/" + slug + "/",
            "original_DOM_block_ids_in_reading_order": [b["block_id"]],
            "all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED": [b],
            "citation_occurrences_NOT_UNIQUE_CLAIMS": len(citations),
            "source_variant_edges_NOT_CLAIMS": sum(len(c[
                "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]) for c in citations),
            "human_claim_support_review": REVIEW,
            "qualified_safety_review": REVIEW,
            "independent_QD_review": REVIEW}


def history(slug="one", sid="s", rank=1, origin="water",
            url="https://example.org/source", after=True, cues=None):
    anchor = {"raw_source_id": sid, "human_claim_support_review": REVIEW,
              "qualified_safety_review": REVIEW, "may_publish": False}
    edges = {"exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED": [{
        "origin": origin, "literal_source_ID": sid,
        "reading_sha256": "a" * 64,
        "literal_URL_UNVERIFIED_UNCHANGED": url,
        "human_claim_support": REVIEW,
        "qualified_safety_review": REVIEW}],
        "human_claim_support": REVIEW,
        "qualified_safety_review": REVIEW, "may_publish": False}
    return {"origin": origin,
            "path": "preparedness/content/articles/" + slug + ".body.html",
            "literal_raw_source_ID": sid, "within_ID_occurrence": rank,
            "R83_complete_unabridged_current_to_RC_review": {
                "raw_source_id": sid, "within_ID_occurrence": rank,
                "before_FULL_ANCHOR": deepcopy(anchor),
                "after_FULL_ANCHOR": deepcopy(anchor) if after else None,
                "human_claim_support_review": REVIEW,
                "qualified_safety_review": REVIEW, "may_publish": False},
            "exact_RC_source_edges_NOT_APPROVED": edges if after else None,
            "review_cues_NOT_VERDICTS": list(cues or []),
            "human_claim_review": REVIEW,
            "qualified_safety_review": REVIEW, "may_publish": False}


class CoreBridge(unittest.TestCase):
    def test_matching_literal_source_rank_retained(self):
        packets, missing, counts = r86.bridge_documents([doc()], [history()])
        self.assertEqual((counts["matched_historical_rows"], len(missing)), (1, 0))
        self.assertEqual(packets[0]["historical_scope_NOT_APPROVAL"],
                         "FOUR_STAGE_CONTRIBUTOR_HISTORY_REVIEW")

    def test_exact_original_R80_packet_retained(self):
        d = doc()
        packets, _, _ = r86.bridge_documents([d], [history()])
        self.assertEqual(d, packets[0]["R80_complete_original_document_UNABRIDGED_NOT_APPROVED"])

    def test_complete_R85_review_retained(self):
        h = history(cues=["CHANGED_CONTEXT"])
        packets, _, _ = r86.bridge_documents([doc()], [h])
        x = packets[0]["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0]
        self.assertEqual(h, x["R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED"])
        self.assertIn("CHANGED_CONTEXT", x["review_cues_NOT_VERDICTS"])

    def test_unchanged_source_has_no_claim_support_verdict(self):
        p, _, _ = r86.bridge_documents([doc()], [history()])
        x = p[0]["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0]
        self.assertEqual(x["review_cues_NOT_VERDICTS"], [])
        self.assertEqual(x["human_claim_support"], REVIEW)
        self.assertIs(x["may_publish"], False)

    def test_literal_URL_changed_without_auto_alias(self):
        p, _, _ = r86.bridge_documents([doc()], [history(url="https://other.org/")])
        self.assertIn("R80_TO_R85_DISTINCT_SOURCE_VARIANTS_DIFFER", p[0][
            "R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0][
            "review_cues_NOT_VERDICTS"])

    def test_source_reading_sha_changed_without_approval(self):
        h = history()
        h["exact_RC_source_edges_NOT_APPROVED"][
            "exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0]["reading_sha256"] = "b" * 64
        p, _, _ = r86.bridge_documents([doc()], [h])
        self.assertIn("R80_TO_R85_DISTINCT_SOURCE_VARIANTS_DIFFER", p[0][
            "R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0][
            "review_cues_NOT_VERDICTS"])

    def test_source_missing_in_rc_still_preserved_in_leftovers(self):
        p, left, counts = r86.bridge_documents([doc()], [history(after=False)])
        self.assertEqual(len(left), 0)
        self.assertIn("R85_RC_CITATION_ABSENT_IN_HISTORICAL_SNAPSHOT",
                      p[0]["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0][
                          "review_cues_NOT_VERDICTS"])

    def test_removed_historical_citation_without_R80_occurrence_retained(self):
        h = history(after=False, sid="old")
        p, left, counts = r86.bridge_documents([doc()], [h])
        self.assertEqual(len(left), 1)
        self.assertEqual(left[0]["R85_original_comparison_UNABRIDGED_NOT_APPROVED"], h)
        self.assertEqual(counts["historical_only_or_unpaired_rows"], 1)

    def test_modern_nonhistorical_article_kept_explicitly_uncovered(self):
        p, _, counts = r86.bridge_documents([doc(slug="modern")], [history()])
        self.assertEqual(counts["documents_outside_history"], 1)
        self.assertEqual(p[0]["historical_scope_NOT_APPROVAL"],
                         "NO_FOUR_STAGE_CONTRIBUTOR_HISTORY")

    def test_tool_never_gets_article_history(self):
        p, _, _ = r86.bridge_documents([doc(kind="tool")], [history()])
        self.assertEqual(p[0]["historical_scope_NOT_APPROVAL"],
                         "NO_FOUR_STAGE_CONTRIBUTOR_HISTORY")

    def test_document_citation_ordinal_conserved(self):
        d = doc(citations=[citation(rank=41)])
        p, _, _ = r86.bridge_documents([d], [history()])
        self.assertEqual(p[0]["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0][
            "R80_original_citation_UNABRIDGED_NOT_APPROVED"]["citation_ordinal"], 41)

    def test_repeated_source_id_occurrences_are_distinct(self):
        d = doc(citations=[citation(rank=1), citation(rank=2)])
        h = [history(rank=1), history(rank=2)]
        p, _, counts = r86.bridge_documents([d], h)
        self.assertEqual(counts["matched_historical_rows"], 2)
        self.assertEqual([x["R80_within_source_ID_occurrence_rank"] for x in p[0][
            "R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"]], [1, 2])

    def test_same_URL_different_origins_stay_two_sources(self):
        d = doc()
        d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0][
            "citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"][0][
            "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"].append({
                "source_origin": "history", "source_id": "s",
                "complete_source_reading_sha256": "b" * 64,
                "exact_URL_NOT_CANONICALIZED": "https://example.org/source"})
        d["source_variant_edges_NOT_CLAIMS"] = 2
        p, _, counts = r86.bridge_documents([d], [history()])
        self.assertEqual(counts["source_edges"], 2)
        self.assertIn("R80_TO_R85_DISTINCT_SOURCE_VARIANTS_DIFFER", p[0][
            "R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0][
            "review_cues_NOT_VERDICTS"])

    def test_no_citations_document_is_preserved(self):
        d = doc(citations=[])
        p, left, counts = r86.bridge_documents([d], [])
        self.assertEqual(counts["citations"], 0)
        self.assertEqual(len(p[0]["R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"]), 0)

    def test_two_distinct_documents_remain_distinct(self):
        d = [doc(slug="one"),doc(slug="two")]
        p, _, count = r86.bridge_documents(d, [history(slug="one"),history(slug="two")])
        self.assertEqual([x["slug"] for x in p], ["one","two"])
        self.assertEqual(count["documents"], 2)

    def test_csv_retains_hard_hold(self):
        d, h = [doc()], [history(cues=["CHANGED_CONTEXT"])]
        report = r86.construct(d, h)
        s = r86.private_csv(report, d, h)
        rows = list(csv.DictReader(io.StringIO(s)))
        self.assertEqual(rows[0]["human_claim_support"], REVIEW)
        self.assertEqual(rows[0]["may_publish"], "FALSE")

    def test_checksum_detects_artificial_approval(self):
        d, h = [doc()], [history()]
        report = r86.construct(d, h)
        report["may_publish"] = True
        with self.assertRaises(r86.Gate):
            r86.verify(report, d, h)

    def test_resealed_mutation_still_cannot_survive_reconstruction(self):
        d, h = [doc()], [history()]
        report = r86.construct(d, h)
        report["counts"]["citations"] = 900
        report["sha256_seal"] = r86.digest({
            k: v for k, v in report.items() if k != "sha256_seal"})
        with self.assertRaises(r86.Gate):
            r86.verify(report, d, h)

    def test_parent_fingerprint_is_part_of_exact_verification(self):
        d, h = [doc()], [history()]
        report = r86.construct(d,h,r80_fingerprint="a",r85_seal="b")
        with self.assertRaises(r86.Gate):
            r86.verify(report,d,h,r80_fingerprint="wrong",r85_seal="b")

    def test_require_full_census_rejects_toy_data(self):
        with self.assertRaises(r86.Gate):
            r86.construct([doc()],[history()],enforce_census=True)

    def test_spreadsheet_formula_prefix_quarantine(self):
        for raw in ("=1+2", "+CMD()", "-5", "@SUM(A1)", " \t=calc",
                    "\ufeff=1", "\u200b@HI", "\u2060+1"):
            with self.subTest(raw=raw):
                self.assertTrue(r86.excel_safe(raw).startswith("'"))

    def test_plain_csv_value_does_not_gain_formula_prefix(self):
        self.assertEqual(r86.excel_safe("preparedness"), "preparedness")

    def test_ambiguous_percent_encoded_url_does_not_create_approval(self):
        d = doc(route="/preparedness/%6Fne/")
        p, _, _ = r86.bridge_documents([d], [])
        self.assertFalse(p[0]["may_publish"])

    def test_all_uncited_research_not_present_as_claim_approval(self):
        d = doc(citations=[])
        p, _, c = r86.bridge_documents([d], [])
        self.assertFalse(p[0]["may_publish"])
        self.assertEqual(c["source_edges"], 0)


class MutationGuards(unittest.TestCase):
    def mutate_document(self, change):
        d=doc()
        change(d)
        with self.assertRaises((r86.Gate, KeyError, TypeError, ValueError)):
            r86.bridge_documents([d], [history()])

    def mutate_history(self, change):
        h=history()
        change(h)
        with self.assertRaises((r86.Gate, KeyError, TypeError, ValueError)):
            r86.bridge_documents([doc()], [h])

    def test_duplicate_document(self):
        with self.assertRaises(r86.Gate):
            r86.bridge_documents([doc(),doc()], [history()])

    def test_route_case_collision(self):
        with self.assertRaises(r86.Gate):
            r86.bridge_documents(
                [doc(slug="one"),doc(slug="two",route="/Preparedness/one/")], [])

    def test_two_origins_one_slug_collision(self):
        with self.assertRaises(r86.Gate):
            r86.bridge_documents([doc()], [history(),history(origin="food",rank=2)])

    def test_duplicate_historical_rank_collision(self):
        with self.assertRaises(r86.Gate):
            r86.bridge_documents([doc()], [history(), history()])

    def test_same_citation_ordinal_twice_rejected(self):
        self.mutate_document(lambda d: d[
            "all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0][
            "citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"].append(
                citation(rank=1)))

    def test_untrusted_doc_path_rejected(self):
        for bad in ("../secret", "article.html", "", 3):
            with self.subTest(bad=bad):
                with self.assertRaises((r86.Gate, TypeError)):
                    r86.slug_for(bad)

    def test_rc_removal_with_fake_remaining_edge_rejected(self):
        h=history(after=False)
        h["exact_RC_source_edges_NOT_APPROVED"] = history()[
            "exact_RC_source_edges_NOT_APPROVED"]
        with self.assertRaises(r86.Gate):
            r86.bridge_documents([doc()], [h])


def add_generated_mutation_tests():
    doc_mutations = {
        "published_QD_status":lambda d:d.__setitem__("independent_QD_review","APPROVED"),
        "source_claim_approved":lambda d:d.__setitem__("human_claim_support_review","PASSED"),
        "safety_cleared":lambda d:d.__setitem__("qualified_safety_review","PASSED"),
        "wrong_kind":lambda d:d.__setitem__("kind","page"),
        "empty_slug":lambda d:d.__setitem__("slug",""),
        "relative_route":lambda d:d.__setitem__("private_draft_url","/"),
        "query_route":lambda d:d.__setitem__("private_draft_url","/preparedness/one/?draft=1"),
        "fragment_route":lambda d:d.__setitem__("private_draft_url","/preparedness/one/#frag"),
        "reordered_DOM":lambda d:d.__setitem__("original_DOM_block_ids_in_reading_order",["wrong"]),
        "forged_DOM_text":lambda d:d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0].__setitem__("unabridged_DOM_text_NOT_REVIEWED","other"),
        "block_claim_approved":lambda d:d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0].__setitem__("human_claim_support_review","APPROVED"),
        "block_safety_approved":lambda d:d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0].__setitem__("qualified_safety_review","APPROVED"),
        "citation_claim_approved":lambda d:d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"][0].__setitem__("human_claim_support_review","APPROVED"),
        "citation_safety_approved":lambda d:d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"][0].__setitem__("qualified_safety_review","CLEARED"),
        "missing_source_variants":lambda d:d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"][0].__setitem__("source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT",[]),
        "source_identity_substitution":lambda d:d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"][0]["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"][0].__setitem__("source_id","other"),
        "source_duplicate_edge":lambda d:d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"][0]["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"].append(deepcopy(d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"][0]["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"][0])),
        "wrong_citation_count":lambda d:d.__setitem__("citation_occurrences_NOT_UNIQUE_CLAIMS",3),
        "wrong_source_edge_count":lambda d:d.__setitem__("source_variant_edges_NOT_CLAIMS",3),
        "lost_block":lambda d:d.__setitem__("all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED",[]),
    }
    historical_mutations = {
        "human_claim_approved":lambda h:h.__setitem__("human_claim_review","APPROVED"),
        "human_safety_approved":lambda h:h.__setitem__("qualified_safety_review","PASSED"),
        "may_publish":lambda h:h.__setitem__("may_publish",True),
        "missing_cues":lambda h:h.__setitem__("review_cues_NOT_VERDICTS",None),
        "negative_rank":lambda h:h.__setitem__("within_ID_occurrence",-1),
        "string_rank":lambda h:h.__setitem__("within_ID_occurrence","1"),
        "empty_source_ID":lambda h:h.__setitem__("literal_raw_source_ID",""),
        "changed_R83_rank":lambda h:h["R83_complete_unabridged_current_to_RC_review"].__setitem__("within_ID_occurrence",2),
        "changed_R83_ID":lambda h:h["R83_complete_unabridged_current_to_RC_review"].__setitem__("raw_source_id","reassigned"),
        "original_context_approved":lambda h:h["R83_complete_unabridged_current_to_RC_review"].__setitem__("human_claim_support_review","PASSED"),
        "after_citation_reassigned":lambda h:h["R83_complete_unabridged_current_to_RC_review"]["after_FULL_ANCHOR"].__setitem__("raw_source_id","other"),
        "after_citation_approved":lambda h:h["R83_complete_unabridged_current_to_RC_review"]["after_FULL_ANCHOR"].__setitem__("qualified_safety_review","CLEARED"),
        "edge_approved":lambda h:h["exact_RC_source_edges_NOT_APPROVED"].__setitem__("human_claim_support","APPROVED"),
        "edge_qualified":lambda h:h["exact_RC_source_edges_NOT_APPROVED"].__setitem__("qualified_safety_review","APPROVED"),
        "edge_public":lambda h:h["exact_RC_source_edges_NOT_APPROVED"].__setitem__("may_publish",True),
        "source_candidate_approved":lambda h:h["exact_RC_source_edges_NOT_APPROVED"]["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0].__setitem__("human_claim_support","APPROVED"),
        "source_candidate_safety":lambda h:h["exact_RC_source_edges_NOT_APPROVED"]["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0].__setitem__("qualified_safety_review","APPROVED"),
        "duplicate_candidate":lambda h:h["exact_RC_source_edges_NOT_APPROVED"]["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"].append(deepcopy(h["exact_RC_source_edges_NOT_APPROVED"]["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0])),
        "foreign_article_path":lambda h:h.__setitem__("path","../../outside.body.html"),
        "missing_anchor":lambda h:(h["R83_complete_unabridged_current_to_RC_review"].__setitem__("before_FULL_ANCHOR",None), h["R83_complete_unabridged_current_to_RC_review"].__setitem__("after_FULL_ANCHOR",None)),
    }
    for name, fn in doc_mutations.items():
        def test(self, fn=fn):
            self.mutate_document(fn)
        setattr(MutationGuards,"test_doc_mutation_"+name,test)
    for name, fn in historical_mutations.items():
        def test(self, fn=fn):
            self.mutate_history(fn)
        setattr(MutationGuards,"test_history_mutation_"+name,test)


add_generated_mutation_tests()


if __name__ == "__main__":
    unittest.main()
