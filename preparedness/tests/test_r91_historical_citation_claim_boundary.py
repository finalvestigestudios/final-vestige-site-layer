"""R91 citation-to-claim-boundary safeguards: purely synthetic, isolated fixtures.

No real source approvals, file writes, network, WordPress, publishing or CMS.
"""
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
    "r91_test_private", ROOT / "tools" / "r91_historical_citation_claim_boundary.py")
r91 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r91)
r90 = r91.upstream()
r89 = r90.upstream()
R = r91.REVIEW
V = "a" * 64


def seal(p):
    p["sha256_seal"] = r90.digest({k:v for k,v in p.items() if k != "sha256_seal"})
    return p


def sample(before="Never use this. {{cite:s}}",
           after="Never use this. {{cite:s}}"):
    raw = "Synthetic article text {{cite:s}}"
    sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    source_row = {
        "kind":"article", "slug":"synthetic", "citation_ordinal":1,
        "original_DOM_block_ID":"b1", "original_DOM_text_sha256":sha,
        "literal_source_ID":"s", "unabridged_original_DOM_text_NOT_REVIEWED":raw,
        "distinct_source_variant_keys_NOT_EQUIVALENCE":[V],
        "historical_before_claim_container_UNABRIDGED_OR_NONE":before,
        "historical_after_claim_container_UNABRIDGED_OR_NONE":after,
        "human_source_review":R, "human_claim_support":R,
        "qualified_safety_review":R, "independent_QD_review":R,
        "may_publish":False,
    }
    doc = {
        "kind":"article", "slug":"synthetic", "citation_occurrences":1,
        "human_claim_support":R, "qualified_safety_review":R,
        "independent_QD_review":R, "may_publish":False,
        "all_original_DOM_blocks_UNABRIDGED_NOT_REVIEWED":[{
            "original_block_UNABRIDGED_NOT_REVIEWED":{
                "block_id":"b1", "unabridged_DOM_text_NOT_REVIEWED":raw,
                "DOM_text_sha256":sha,
            },
            "original_citation_ordinals_IN_BLOCK":[1],
            "human_claim_support":R, "qualified_safety_review":R,
            "may_publish":False,
        }],
    }
    variant = {
        "variant_key_sha256":V,
        "all_unabridged_cited_claim_blocks_IN_ORIGINAL_ORDER_NOT_REVIEWED":[deepcopy(source_row)],
        "human_source_review":R, "human_claim_support":R,
        "qualified_safety_review":R, "independent_QD_review":R,
        "may_publish":False,
    }
    p = seal({
        "schema":r89.SCHEMA, "issue":136, "release_state":"HOLD",
        "may_publish":False, "medical_safety_approved":False,
        "human_source_approvals":0, "human_claim_approvals":0,
        "qualified_safety_approvals":0, "independent_QD_approvals":0,
        "complete_R88_original_evidence_UNABRIDGED_NOT_APPROVED":{},
        "all_41_document_complete_DOM_reading_packets_NOT_APPROVED":[doc],
        "all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED":[source_row],
        "all_source_variant_reverse_impact_dossiers_NOT_APPROVED":[variant],
        "unpaired_historical_reviews_UNABRIDGED":[],
        "counts":{"documents":1, "complete_DOM_blocks":1,
                  "citation_occurrences":1, "distinct_source_variants":1,
                  "source_variant_edges":1},
    })
    return r90.index(p)


def altered(parent, edit):
    parent = deepcopy(parent)
    edit(parent)
    return seal(parent)


def flags(before, after):
    return set(r91.compare(before, after)["review_cues_NOT_SAFETY_FINDINGS"])


class R91Custody(unittest.TestCase):
    def setUp(self):
        self.parent = sample()
        self.report = r91.index(self.parent)

    def test_complete_parent_preserved(self):
        self.assertEqual(self.report["complete_R90_original_evidence_UNABRIDGED_NOT_APPROVED"],
                         self.parent)

    def test_full_citation_row_preserved(self):
        self.assertEqual(self.report["counts"]["citation_occurrences"], 1)

    def test_doc_census_preserved(self):
        self.assertEqual(self.report["counts"]["documents"], 1)

    def test_source_edges_preserved(self):
        self.assertEqual(self.report["counts"]["source_variant_edges"], 1)

    def test_variant_identity_preserved(self):
        row = self.report["all_literal_citation_claim_boundary_review_rows_NOT_APPROVED"][0]
        self.assertEqual(row["distinct_origin_scoped_source_variant_keys_NOT_ALIASES"], [V])

    def test_source_id_preserved(self):
        row = self.report["all_literal_citation_claim_boundary_review_rows_NOT_APPROVED"][0]
        self.assertEqual(row["literal_source_ID"], "s")

    def test_original_block_receipt_preserved(self):
        row = self.report["all_literal_citation_claim_boundary_review_rows_NOT_APPROVED"][0]
        self.assertEqual(row["original_DOM_text_sha256"],
                         self.parent["all_original_citation_claim_scope_review_rows_NOT_APPROVED"][0]["original_DOM_text_sha256"])

    def test_hard_hold(self):
        self.assertEqual(self.report["release_state"], "HOLD")

    def test_no_publication(self):
        self.assertIs(self.report["may_publish"], False)

    def test_no_medical_safety(self):
        self.assertIs(self.report["medical_safety_approved"], False)

    def test_no_source_approval(self):
        self.assertEqual(self.report["human_source_approvals"], 0)

    def test_no_claim_approval(self):
        self.assertEqual(self.report["human_claim_approvals"], 0)

    def test_no_qualified_safety_approval(self):
        self.assertEqual(self.report["qualified_safety_approvals"], 0)

    def test_no_QD_approval(self):
        self.assertEqual(self.report["independent_QD_approvals"], 0)

    def test_no_rank_identity_inference(self):
        row = self.report["all_literal_citation_claim_boundary_review_rows_NOT_APPROVED"][0]
        self.assertFalse(row["citation_claim_boundary_review_NOT_SAFETY_VERDICT"]
                         ["rank_alignment_proves_claim_identity"])

    def test_repeatability(self):
        self.assertEqual(self.report, r91.index(deepcopy(self.parent)))

    def test_hash_receipt(self):
        self.assertEqual(self.report["sha256_seal"], r91.digest({
            k:v for k,v in self.report.items() if k!="sha256_seal"}))

    def test_verify_exact_report(self):
        r91.verify(self.report, self.parent)

    def test_verify_mutated_report_fails(self):
        out=deepcopy(self.report)
        out["may_publish"] = True
        with self.assertRaises(r91.Gate): r91.verify(out, self.parent)

    def test_verify_resealed_missing_row_fails(self):
        out=deepcopy(self.report)
        out["all_literal_citation_claim_boundary_review_rows_NOT_APPROVED"].clear()
        seal(out)
        with self.assertRaises(r91.Gate): r91.verify(out, self.parent)

    def test_mutated_parent_seal_fails(self):
        self.parent["sha256_seal"]="BAD"
        with self.assertRaises(r91.Gate): r91.index(self.parent)

    def test_false_parent_human_approval_fails(self):
        p=altered(self.parent, lambda x:x.update(human_claim_approvals=1))
        with self.assertRaises(r91.Gate): r91.index(p)

    def test_false_parent_medical_approval_fails(self):
        p=altered(self.parent, lambda x:x.update(medical_safety_approved=True))
        with self.assertRaises(r91.Gate): r91.index(p)

    def test_false_parent_QD_approval_fails(self):
        p=altered(self.parent, lambda x:x.update(independent_QD_approvals=1))
        with self.assertRaises(r91.Gate): r91.index(p)

    def test_false_parent_citation_approval_fails(self):
        def edit(p):
            p["all_original_citation_claim_scope_review_rows_NOT_APPROVED"][0]["qualified_safety_review"]="PASS"
        with self.assertRaises(r91.Gate): r91.index(altered(self.parent, edit))

    def test_parent_lost_citation_fails(self):
        def edit(p):
            p["all_original_citation_claim_scope_review_rows_NOT_APPROVED"].clear()
        with self.assertRaises(r91.Gate): r91.index(altered(self.parent, edit))

    def test_parent_duplicate_citation_fails(self):
        def edit(p):
            rows = p["all_original_citation_claim_scope_review_rows_NOT_APPROVED"]
            rows.append(deepcopy(rows[0]))
        with self.assertRaises(r91.Gate): r91.index(altered(self.parent, edit))

    def test_source_relabel_fails(self):
        def edit(p):
            p["all_original_citation_claim_scope_review_rows_NOT_APPROVED"][0]["literal_source_ID"]="other"
        with self.assertRaises(r91.Gate): r91.index(altered(self.parent, edit))

    def test_source_variant_substitution_fails(self):
        def edit(p):
            p["all_original_citation_claim_scope_review_rows_NOT_APPROVED"][0]["distinct_origin_scoped_source_variant_keys_NOT_ALIASES"]=["b"*64]
        with self.assertRaises(r91.Gate): r91.index(altered(self.parent, edit))

    def test_original_DOM_context_substitution_fails(self):
        def edit(p):
            p["all_original_citation_claim_scope_review_rows_NOT_APPROVED"][0]["original_DOM_text_sha256"]="c"*64
        with self.assertRaises(r91.Gate): r91.index(altered(self.parent, edit))

    def test_original_historical_text_substitution_fails(self):
        def edit(p):
            p["complete_R89_original_evidence_UNABRIDGED_NOT_APPROVED"]["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0]["historical_before_claim_container_UNABRIDGED_OR_NONE"]="Changed"
        with self.assertRaises(r91.Gate): r91.index(altered(self.parent, edit))

    def test_expected_full_slate_rejects_tiny_fixture(self):
        with self.assertRaises(r91.Gate): r91.audit(self.parent, expected=r91.EXPECTED)

    def test_private_csv_one_row(self):
        rows=list(csv.DictReader(io.StringIO(r91.private_csv(self.report,self.parent))))
        self.assertEqual(len(rows),1)

    def test_private_csv_not_approval(self):
        row=list(csv.DictReader(io.StringIO(r91.private_csv(self.report,self.parent))))[0]
        self.assertEqual(row["qualified_safety_review"],R)
        self.assertEqual(row["may_publish"],"FALSE")

    def test_private_csv_no_full_text(self):
        self.assertNotIn("Never use this",r91.private_csv(self.report,self.parent))

    def test_private_csv_spreadsheet_injection_disarmed(self):
        p=sample("Never. {{cite:s}}", "Never. {{cite:s}}")
        r = p["all_original_citation_claim_scope_review_rows_NOT_APPROVED"][0]
        s = p["complete_R89_original_evidence_UNABRIDGED_NOT_APPROVED"]["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0]
        r["literal_source_ID"] = s["literal_source_ID"] = "=HYPERLINK(1)"
        seal(p)
        out=r91.index(p)
        self.assertIn("'=HYPERLINK",r91.private_csv(out,p))

    def test_unicode_codepoint_offsets(self):
        p=r91.positions("🧭 Ocean {{cite:é}}")
        self.assertEqual(p[0]["token_start_CODEPOINT_OFFSET"],len("🧭 Ocean "))

    def test_clause_literal_text_preserved(self):
        text="Never A. Use B {{cite:s}}"
        self.assertEqual(r91.positions(text)[0]["complete_original_clause_UNABRIDGED_NOT_REVIEWED"],
                         "Use B {{cite:s}}")

    def test_empty_id_rejected(self):
        with self.assertRaises(r91.Gate): r91.positions("{{cite: }}")

    def test_invalid_context_rejected(self):
        with self.assertRaises(r91.Gate): r91.compare(123,"x")

    def test_none_context_not_approved(self):
        self.assertIn("ONE_OR_BOTH_HISTORICAL_CONTEXTS_MISSING_REVIEW_ONLY",
                      flags(None,None))

    def test_zero_citation_context_allowed(self):
        self.assertEqual(r91.positions("No citations here."),[])

    def test_repeated_source_ordinals(self):
        self.assertEqual([x["same_source_rank_IN_CONTEXT_NOT_CLAIM_IDENTITY"] for x in
                          r91.positions("A {{cite:s}}. B {{cite:s}}.")],[1,2])


# Each adversarial and negative case is a distinct test method.
SCENARIOS = [
 ("cross_sentence", "A {{cite:s}}. B.", "A. B {{cite:s}}.", "SAME_CITATION_ORDER_MOVED_ACROSS_CLAUSE_BOUNDARY_REVIEW_ONLY"),
 ("cross_clause_semicolon", "A {{cite:s}}; B.", "A; B {{cite:s}}.", "SAME_CITATION_ORDER_MOVED_ACROSS_CLAUSE_BOUNDARY_REVIEW_ONLY"),
 ("cross_newline", "A {{cite:s}}\nB", "A\nB {{cite:s}}", "SAME_CITATION_ORDER_MOVED_ACROSS_CLAUSE_BOUNDARY_REVIEW_ONLY"),
 ("cross_question", "A {{cite:s}}? B.", "A? B {{cite:s}}.", "SAME_CITATION_ORDER_MOVED_ACROSS_CLAUSE_BOUNDARY_REVIEW_ONLY"),
 ("cross_exclamation", "A {{cite:s}}! B.", "A! B {{cite:s}}.", "SAME_CITATION_ORDER_MOVED_ACROSS_CLAUSE_BOUNDARY_REVIEW_ONLY"),
 ("same_clause_move", "A {{cite:s}} B.", "A B {{cite:s}}.", "SAME_CITATION_ORDER_REPOSITIONED_IN_SAME_CLAUSE_REVIEW_ONLY"),
 ("same_clause_move_reverse", "A B {{cite:s}}.", "{{cite:s}} A B.", "SAME_CITATION_ORDER_REPOSITIONED_IN_SAME_CLAUSE_REVIEW_ONLY"),
 ("retained_id_new_warning", "Do X {{cite:s}}.", "Never do X {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("retained_id_removed_warning", "Never do X {{cite:s}}.", "Do X {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("retained_id_number", "Use 5 {{cite:s}}.", "Use 50 {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("retained_id_unit", "5 hours {{cite:s}}.", "5 days {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("retained_id_qualifier", "Only use A {{cite:s}}.", "Always use A {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("retained_id_temperature", "30 C {{cite:s}}.", "50 C {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("retained_id_name", "Study A {{cite:s}}.", "Study B {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("retained_id_emoji", "🧭 A {{cite:s}}.", "🧭 B {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("repeated_source", "A {{cite:s}}. B {{cite:s}}.", "A {{cite:s}}. B {{cite:s}}.", "REPEATED_SOURCE_RANK_DOES_NOT_PROVE_SAME_CLAIM_REVIEW_ONLY"),
 ("repeated_reorder", "A {{cite:s}}. B {{cite:s}}.", "B {{cite:s}}. A {{cite:s}}.", "REPEATED_SOURCE_RANK_DOES_NOT_PROVE_SAME_CLAIM_REVIEW_ONLY"),
 ("repeated_triple", "A {{cite:s}}{{cite:s}}{{cite:s}}.", "A {{cite:s}}{{cite:s}}{{cite:s}}.", "REPEATED_SOURCE_RANK_DOES_NOT_PROVE_SAME_CLAIM_REVIEW_ONLY"),
 ("citation_swap", "{{cite:a}} {{cite:b}}", "{{cite:b}} {{cite:a}}", "CITATION_ID_ORDER_OR_OCCURRENCE_CHANGED_REVIEW_ONLY"),
 ("citation_added", "A", "A {{cite:a}}", "CITATION_ID_ORDER_OR_OCCURRENCE_CHANGED_REVIEW_ONLY"),
 ("citation_removed", "A {{cite:a}}", "A", "CITATION_ID_ORDER_OR_OCCURRENCE_CHANGED_REVIEW_ONLY"),
 ("citation_changed", "A {{cite:a}}", "A {{cite:b}}", "CITATION_ID_ORDER_OR_OCCURRENCE_CHANGED_REVIEW_ONLY"),
 ("citation_new_duplicate", "A {{cite:a}}", "A {{cite:a}} {{cite:a}}", "CITATION_ID_ORDER_OR_OCCURRENCE_CHANGED_REVIEW_ONLY"),
 ("citation_deleted_duplicate", "A {{cite:a}} {{cite:a}}", "A {{cite:a}}", "CITATION_ID_ORDER_OR_OCCURRENCE_CHANGED_REVIEW_ONLY"),
 ("same_no_claim_change", "A {{cite:s}}.", "A {{cite:s}}.", None),
 ("same_emoji", "🧭 A {{cite:s}}.", "🧭 A {{cite:s}}.", None),
 ("same_unicode", "é {{cite:s}}.", "é {{cite:s}}.", None),
 ("same_number", "5 L {{cite:s}}.", "5 L {{cite:s}}.", None),
 ("same_warning", "Never {{cite:s}}.", "Never {{cite:s}}.", None),
 ("same_blank", "", "", None),
 ("changed_no_citations", "Historical A.", "Historical B.", "TEXT_CHANGED_NO_PROOF_OF_CITATION_SUPPORT_REVIEW_ONLY"),
 ("no_citations_unchanged", "Historical A.", "Historical A.", None),
 ("space_changes", "A {{cite:s}}.", "A  {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("line_end_change", "A {{cite:s}}.\n", "A {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("punctuation_change", "A {{cite:s}}.", "A {{cite:s}}!", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("case_change", "A {{cite:s}}.", "a {{cite:s}}.", "SAME_CITATION_ORDER_CLAIM_CONTEXT_CHANGED_REVIEW_ONLY"),
 ("changed_source_rank", "A {{cite:s}}. B {{cite:s}}.", "A {{cite:t}}. B {{cite:s}}.", "CITATION_ID_ORDER_OR_OCCURRENCE_CHANGED_REVIEW_ONLY"),
 ("changed_citation_position_only", "{{cite:s}} text", "text {{cite:s}}", "SAME_CITATION_ORDER_REPOSITIONED_IN_SAME_CLAUSE_REVIEW_ONLY"),
]


def scenario(before, after, expected):
    def run(self):
        result = r91.compare(before, after)
        found = set(result["review_cues_NOT_SAFETY_FINDINGS"])
        if expected is None:
            self.assertFalse(found, found)
        else:
            self.assertIn(expected, found)
        self.assertIs(result["may_publish"],False)
        self.assertEqual(result["human_claim_support"],R)
        self.assertEqual(result["qualified_safety_review"],R)
        self.assertEqual(result["independent_QD_review"],R)
        self.assertIs(result["rank_alignment_proves_claim_identity"],False)
    return run


for name,before,after,want in SCENARIOS:
    setattr(R91Custody,"test_case_"+name,scenario(before,after,want))


if __name__ == "__main__":
    unittest.main()
