"""R83 synthetic and adversarial citation-placement custody tests (PRIVATE HOLD)."""
from __future__ import annotations

from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "r83_citation_placement_context_custody.py"
SPEC = importlib.util.spec_from_file_location("r83_under_test", TOOL)
r83 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r83)

HELPERS = Path(__file__).with_name("test_r82_four_snapshot_citation_custody.py")
SPEC82 = importlib.util.spec_from_file_location("r83_fixture_helpers", HELPERS)
helper = importlib.util.module_from_spec(SPEC82)
SPEC82.loader.exec_module(helper)
r82 = r83.parent_module()


def sample(body, stage="rc", source=None):
    ident = source or {"x": [{"origin": "start", "source_id": "x",
                               "reading_sha256": "a" * 64}]}
    return helper.fake_article("start", "demo", stage, sources=ident, body=body)


def anchors(body):
    return r83.anchors(sample(body))


def revised(before, after):
    return r83.compare(anchors(before), anchors(after))


def reseal(report):
    report["sha256_seal"] = r83.digest(r83.canonical({
        k: v for k, v in report.items() if k != "sha256_seal"}))


class ParserCustody(unittest.TestCase):
    def test_plain_paragraph_anchor(self):
        row = anchors("<p>Use a plan {{cite:x}}.</p>")[0]
        self.assertEqual(row["scope_state"], "VISIBLE_CONTAINER_NOT_SUPPORT_PROOF")
        self.assertIn("Use a plan", row["complete_container_text_UNABRIDGED"])

    def test_inline_nested_tags_remain_same_container(self):
        row = anchors("<p>Before <strong>after</strong> {{cite:x}}.</p>")[0]
        self.assertEqual(row["complete_container_text_UNABRIDGED"],
                         "Before after {{cite:x}}.")

    def test_preserve_full_quote_and_context(self):
        text = "A" * 3000
        self.assertIn(text, anchors("<p>" + text + " {{cite:x}}</p>")[0][
            "complete_container_text_UNABRIDGED"])

    def test_exact_multibyte_byte_offset(self):
        row = anchors("<p>café 🌍 {{cite:x}}</p>")[0]
        self.assertEqual(row["literal_byte_offset"],
                         len("<p>café 🌍 ".encode("utf-8")))

    def test_two_line_offsets(self):
        rows = anchors("<p>first {{cite:x}}\nsecond {{cite:y}}</p>")
        self.assertEqual([r["line_number"] for r in rows], [1, 2])

    def test_heading_is_preserved(self):
        row = anchors("<h2>Unsafe assumption</h2><p>Do not guess {{cite:x}}</p>")[0]
        self.assertEqual(row["nearest_preceding_heading_UNABRIDGED"],
                         "Unsafe assumption")

    def test_heading_with_inline_markup(self):
        row = anchors("<h3><em>Context</em> matters</h3><p>{{cite:x}}</p>")[0]
        self.assertEqual(row["nearest_preceding_heading_UNABRIDGED"],
                         "Context matters")

    def test_citations_in_two_cells_stay_distinct(self):
        a, b = anchors("<table><tr><td>A {{cite:x}}</td><td>B {{cite:y}}</td></tr></table>")
        self.assertEqual(a["complete_container_text_UNABRIDGED"], "A {{cite:x}}")
        self.assertEqual(b["complete_container_text_UNABRIDGED"], "B {{cite:y}}")

    def test_list_item_context(self):
        a, b = anchors("<ul><li>One {{cite:x}}</li><li>Two {{cite:x}}</li></ul>")
        self.assertNotEqual(a["container_text_digest"], b["container_text_digest"])

    def test_paragraph_inside_list_uses_innermost(self):
        row = anchors("<li>Outer<p>Inner {{cite:x}}</p></li>")[0]
        self.assertEqual(row["container_kind"], "p")

    def test_blockquote_anchor(self):
        row = anchors("<blockquote>{{cite:x}}</blockquote>")[0]
        self.assertEqual(row["container_kind"], "blockquote")

    def test_missing_container_is_not_falsely_visible(self):
        row = anchors("<section>{{cite:x}}</section>")[0]
        self.assertEqual(row["scope_state"], "UNMAPPED_OR_NONVISIBLE_REVIEW")

    def test_attribute_token_is_not_claim_text(self):
        row = anchors('<p title="{{cite:x}}">No text citation</p>')[0]
        self.assertEqual(row["scope_state"], "UNMAPPED_OR_NONVISIBLE_REVIEW")

    def test_comment_citation_not_claim_text(self):
        row = anchors("<!-- {{cite:x}} --><p>Text</p>")[0]
        self.assertEqual(row["scope_state"], "UNMAPPED_OR_NONVISIBLE_REVIEW")

    def test_script_not_visible(self):
        row = anchors("<script>var x='{{cite:x}}';</script>")[0]
        self.assertEqual(row["scope_state"], "UNMAPPED_OR_NONVISIBLE_REVIEW")

    def test_style_not_visible(self):
        row = anchors("<style>/* {{cite:x}} */</style>")[0]
        self.assertEqual(row["scope_state"], "UNMAPPED_OR_NONVISIBLE_REVIEW")

    def test_noscript_is_conservative(self):
        row = anchors("<noscript><p>{{cite:x}}</p></noscript>")[0]
        self.assertEqual(row["scope_state"], "UNMAPPED_OR_NONVISIBLE_REVIEW")

    def test_template_is_conservative(self):
        row = anchors("<template><p>{{cite:x}}</p></template>")[0]
        self.assertEqual(row["scope_state"], "UNMAPPED_OR_NONVISIBLE_REVIEW")

    def test_multiple_citations_preserve_original_order(self):
        rows = anchors("<p>{{cite:b}} {{cite:a}} {{cite:b}}</p>")
        self.assertEqual([r["raw_source_id"] for r in rows], ["b", "a", "b"])

    def test_original_candidate_variants_not_aliased(self):
        many = {"x": [{"origin": "food", "source_id": "x", "reading_sha256": "a"},
                      {"origin": "start", "source_id": "x", "reading_sha256": "b"}]}
        row = r83.anchors(sample("<p>{{cite:x}}</p>", source=many))[0]
        self.assertEqual(len(row["source_candidates_NOT_ALIASED"]), 2)

    def test_all_review_states_unapproved(self):
        for row in anchors("<p>{{cite:x}}{{cite:y}}</p>"):
            self.assertFalse(row["may_publish"])
            self.assertEqual(row["human_claim_support_review"], r83.REVIEW)
            self.assertEqual(row["qualified_safety_review"], r83.REVIEW)

    def test_tampered_body_digest_fails(self):
        item = sample("<p>{{cite:x}}</p>")
        item["body_sha256"] = "a" * 64
        with self.assertRaises(r83.Hold):
            r83.anchors(item)

    def test_tampered_citation_byte_position_fails(self):
        item = sample("<p>{{cite:x}}</p>")
        item["citations_in_original_order"][0]["byte_offset"] += 1
        with self.assertRaises(r83.Hold):
            r83.anchors(item)

    def test_duplicate_byte_position_fails(self):
        item = sample("<p>{{cite:x}}{{cite:y}}</p>")
        item["citations_in_original_order"][1]["byte_offset"] = (
            item["citations_in_original_order"][0]["byte_offset"])
        with self.assertRaises(r83.Hold):
            r83.anchors(item)

    def test_empty_citation_sequence(self):
        self.assertEqual(anchors("<p>Nothing to cite.</p>"), [])

    def test_no_phrase_is_automatically_fact_checked(self):
        row = anchors("<p>Confident but unsupported claim {{cite:x}}</p>")[0]
        self.assertNotIn("PASS", str(row))
        self.assertFalse(row["may_publish"])


class ComparisonCustody(unittest.TestCase):
    def test_unchanged_text_has_no_cues(self):
        self.assertEqual(revised("<p>Same {{cite:x}}</p>",
                                 "<p>Same {{cite:x}}</p>")[0][
                                     "review_cues_NOT_VERDICTS"], [])

    def test_same_citation_new_claim_is_reviewed(self):
        row = revised("<p>Earlier claim {{cite:x}}</p>",
                      "<p>Different claim {{cite:x}}</p>")[0]
        self.assertIn("CONTAINER_CONTEXT_CHANGED_REVIEW",
                      row["review_cues_NOT_VERDICTS"])

    def test_same_claim_new_heading_is_reviewed(self):
        row = revised("<h2>Section A</h2><p>{{cite:x}}</p>",
                      "<h2>Section B</h2><p>{{cite:x}}</p>")[0]
        self.assertIn("SECTION_CONTEXT_CHANGED_REVIEW",
                      row["review_cues_NOT_VERDICTS"])

    def test_changed_position_is_reviewed(self):
        row = revised("<p>{{cite:x}}</p>", "<p>Prefix {{cite:x}}</p>")[0]
        self.assertIn("CITATION_BYTE_POSITION_CHANGED_REVIEW",
                      row["review_cues_NOT_VERDICTS"])

    def test_added_citation(self):
        row = revised("<p>No citation</p>", "<p>{{cite:x}}</p>")[0]
        self.assertEqual(row["review_cues_NOT_VERDICTS"],
                         ["CITATION_ADDED_REVIEW"])

    def test_removed_citation(self):
        row = revised("<p>{{cite:x}}</p>", "<p>No citation</p>")[0]
        self.assertEqual(row["review_cues_NOT_VERDICTS"],
                         ["CITATION_REMOVED_REVIEW"])

    def test_reordered_distinct_citations(self):
        rows = revised("<p>{{cite:x}} {{cite:y}}</p>",
                       "<p>{{cite:y}} {{cite:x}}</p>")
        self.assertTrue(all("CITATION_SEQUENCE_ORDER_CHANGED_REVIEW" in
                            r["review_cues_NOT_VERDICTS"] for r in rows))

    def test_repeated_citation_uses_occurrence_rank(self):
        rows = revised("<p>{{cite:x}}</p><p>{{cite:x}}</p>",
                       "<p>{{cite:x}}</p><p>{{cite:x}}</p>")
        self.assertEqual([r["within_ID_occurrence"] for r in rows], [1, 2])

    def test_nonvisible_pair_requires_review(self):
        row = revised('<p title="{{cite:x}}"></p>',
                      '<p title="{{cite:x}}"></p>')[0]
        self.assertIn("NONVISIBLE_OR_UNMAPPED_REVIEW",
                      row["review_cues_NOT_VERDICTS"])

    def test_nonvisible_to_visible_requires_review(self):
        row = revised('<!-- {{cite:x}} -->', "<p>{{cite:x}}</p>")[0]
        self.assertIn("NONVISIBLE_OR_UNMAPPED_REVIEW",
                      row["review_cues_NOT_VERDICTS"])

    def test_source_variant_reading_changed(self):
        x = anchors("<p>{{cite:x}}</p>")[0]
        y = deepcopy(x)
        y["source_candidates_NOT_ALIASED"][0]["reading_sha256"] = "b" * 64
        row = r83.compare([x], [y])[0]
        self.assertIn("SOURCE_CANDIDATE_VARIANTS_CHANGED_REVIEW",
                      row["review_cues_NOT_VERDICTS"])

    def test_same_id_different_origin_flagged(self):
        a = anchors("<p>{{cite:x}}</p>")[0]
        b = deepcopy(a)
        b["source_candidates_NOT_ALIASED"][0]["origin"] = "food"
        self.assertIn("SOURCE_CANDIDATE_VARIANTS_CHANGED_REVIEW",
                      r83.compare([a], [b])[0]["review_cues_NOT_VERDICTS"])

    def test_same_id_different_scope_flagged(self):
        a = anchors("<p>{{cite:x}}</p>")[0]
        b = deepcopy(a)
        b["source_scope_state"] = "MULTIPLE_ORIGIN_VARIANTS_UNRESOLVED"
        self.assertIn("SOURCE_CANDIDATE_VARIANTS_CHANGED_REVIEW",
                      r83.compare([a], [b])[0]["review_cues_NOT_VERDICTS"])

    def test_no_review_order_claims_safety(self):
        rows = revised("<p>Old {{cite:x}}</p>", "<p>New {{cite:x}}</p>")
        self.assertTrue(all(not r["may_publish"] for r in rows))
        self.assertTrue(all(r["qualified_safety_review"] == r83.REVIEW
                            for r in rows))

    def test_occurrence_key_rejects_empty_id(self):
        with self.assertRaises(r83.Hold):
            r83.occurrence_keys([{"raw_source_id": ""}])

    def test_nonevents_remain_empty(self):
        self.assertEqual(r83.compare([], []), [])


class CompleteSealedSyntheticEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r82_report = r82.construct(*helper.fake_suite())
        cls.report = r83.construct(cls.r82_report)
        r83.verify(cls.report, cls.r82_report)

    def test_29_articles(self):
        self.assertEqual(self.report["counts"]["article_groups"], 29)

    def test_116_snapshots(self):
        self.assertEqual(self.report["counts"]["four_stage_snapshots"], 116)

    def test_116_literal_citation_anchors(self):
        self.assertEqual(self.report["counts"]["four_stage_citation_anchors"], 116)

    def test_all_four_stages_kept(self):
        for row in self.report["all_29_four_stage_citation_context_packets_UNABRIDGED"]:
            self.assertEqual(set(row["four_snapshot_citation_anchors_NOT_APPROVED"]),
                             set(r83.STAGES))

    def test_no_medical_approval(self):
        self.assertFalse(self.report["medical_safety_approved"])

    def test_zero_claim_safety_QD_approvals(self):
        for field in ("human_claim_approvals", "qualified_safety_approvals",
                      "independent_QD_approvals", "human_source_approvals"):
            self.assertEqual(self.report[field], 0)

    def test_exact_r82_seal_retained(self):
        self.assertEqual(self.report["exact_r82_evidence_sha256_seal"],
                         self.r82_report["sha256_seal"])

    def test_separate_candidate_sha_retained(self):
        self.assertEqual(self.report["separate_RC_sha"],
                         self.r82_report["separate_RC_sha"])

    def test_deterministic_rebuild(self):
        self.assertEqual(self.report["sha256_seal"],
                         r83.construct(self.r82_report)["sha256_seal"])

    def test_review_rows_not_verdicts(self):
        for row in self.report["all_29_four_stage_citation_context_packets_UNABRIDGED"]:
            self.assertFalse(row["may_publish"])
            self.assertEqual(row["human_claim_support_review"], "NOT_REVIEWED")

    def test_complete_context_not_truncated(self):
        row = self.report["all_29_four_stage_citation_context_packets_UNABRIDGED"][0]
        self.assertIn("Synthetic",
                      row["four_snapshot_citation_anchors_NOT_APPROVED"]["rc"][0][
                          "complete_container_text_UNABRIDGED"])

    def test_csv_has_review_only_columns(self):
        text = r83.reviewer_csv(self.report, self.r82_report)
        headers = next(csv.reader(io.StringIO(text)))
        self.assertIn("human_review", headers)
        self.assertIn("release", headers)

    def test_csv_escapes_spreadsheet_formulas(self):
        # inherited safety encoder ensures no new CSV formula surface
        for value in ("=SUM(1,2)", "@HYPERLINK", "+cmd", "-cmd"):
            self.assertTrue(r82.safe_csv(value).startswith("'"))

    def test_tampered_report_fails(self):
        corrupt = deepcopy(self.report)
        corrupt["counts"]["article_groups"] = 35
        with self.assertRaises(r83.Hold):
            r83.verify(corrupt, self.r82_report)

    def test_resealed_false_publication_still_fails(self):
        corrupt = deepcopy(self.report)
        corrupt["may_publish"] = True
        reseal(corrupt)
        with self.assertRaises(r83.Hold):
            r83.verify(corrupt, self.r82_report)

    def test_resealed_fake_QD_still_fails(self):
        corrupt = deepcopy(self.report)
        corrupt["independent_QD_approvals"] = 1
        reseal(corrupt)
        with self.assertRaises(r83.Hold):
            r83.verify(corrupt, self.r82_report)

    def test_resealed_deleted_citation_still_fails(self):
        corrupt = deepcopy(self.report)
        corrupt["all_29_four_stage_citation_context_packets_UNABRIDGED"][0][
            "four_snapshot_citation_anchors_NOT_APPROVED"]["rc"].clear()
        reseal(corrupt)
        with self.assertRaises(r83.Hold):
            r83.verify(corrupt, self.r82_report)

    def test_resealed_modified_source_origin_still_fails(self):
        corrupt = deepcopy(self.report)
        corrupt["all_29_four_stage_citation_context_packets_UNABRIDGED"][0][
            "four_snapshot_citation_anchors_NOT_APPROVED"]["rc"][0][
                "source_candidates_NOT_ALIASED"][0]["origin"] = "alias"
        reseal(corrupt)
        with self.assertRaises(r83.Hold):
            r83.verify(corrupt, self.r82_report)

    def test_resealed_forged_context_still_fails(self):
        corrupt = deepcopy(self.report)
        corrupt["all_29_four_stage_citation_context_packets_UNABRIDGED"][0][
            "four_snapshot_citation_anchors_NOT_APPROVED"]["rc"][0][
                "complete_container_text_UNABRIDGED"] = "REWRITTEN"
        reseal(corrupt)
        with self.assertRaises(r83.Hold):
            r83.verify(corrupt, self.r82_report)

    def test_mismatched_r82_parent_rejected(self):
        bad = deepcopy(self.r82_report)
        bad["human_source_approvals"] = 1
        with self.assertRaises((ValueError, r83.Hold)):
            r83.construct(bad)

    def test_no_gaps_between_citation_orders(self):
        for row in self.report["all_29_four_stage_citation_context_packets_UNABRIDGED"]:
            for events in row["four_snapshot_citation_anchors_NOT_APPROVED"].values():
                self.assertEqual([e["ordinal"] for e in events],
                                 list(range(len(events))))


# Distinct tests rather than one subTest: exercise byte-order and container edits
# at scale, without touching any actual article/source or shared working-tree file.
class ManyAdversarialEdits(unittest.TestCase):
    pass


def _edit_case(number):
    def case(self):
        before = "<h2>Section</h2><p>" + "X" * number + " {{cite:x}}</p>"
        after = "<h2>Section</h2><p>" + "X" * number + " NOT THE SAME {{cite:x}}</p>"
        row = revised(before, after)[0]
        self.assertIn("CONTAINER_CONTEXT_CHANGED_REVIEW",
                      row["review_cues_NOT_VERDICTS"])
        self.assertEqual(row["human_claim_support_review"], "NOT_REVIEWED")
        self.assertFalse(row["may_publish"])
    return case


for i in range(1, 25):
    setattr(ManyAdversarialEdits, f"test_changed_claim_context_{i:02d}",
            _edit_case(i))


if __name__ == "__main__":
    unittest.main()
