"""R90 deterministic historical scope/quantity review tests; SYNTHETIC IN MEMORY.

No source-fragment writes, external networking, WordPress/CMS or publication.
Every flagged cue is lexical REVIEW ONLY; no qualified safety approval.
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
PATH = ROOT / "tools" / "r90_historical_claim_scope_quantity_sequence.py"
SPEC = importlib.util.spec_from_file_location("r90_test_module", PATH)
r90 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r90)
r89 = r90.upstream()
R = r90.REVIEW
V = "a" * 64


def seal(p):
    p["sha256_seal"] = r90.digest({k:v for k,v in p.items() if k != "sha256_seal"})
    return p


def sample(before="Never use an unsafe method. {{cite:s}}",
           after="Never use an unsafe method. {{cite:s}}"):
    text = "Synthetic claim {{cite:s}}"
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    block = {"block_id":"b1", "unabridged_DOM_text_NOT_REVIEWED":text,
             "DOM_text_sha256":sha}
    row = {
        "kind":"article","slug":"synthetic","citation_ordinal":1,
        "original_DOM_block_ID":"b1","original_DOM_text_sha256":sha,
        "literal_source_ID":"s",
        "unabridged_original_DOM_text_NOT_REVIEWED":text,
        "distinct_source_variant_keys_NOT_EQUIVALENCE":[V],
        "historical_before_claim_container_UNABRIDGED_OR_NONE":before,
        "historical_after_claim_container_UNABRIDGED_OR_NONE":after,
        "human_source_review":R,"human_claim_support":R,
        "qualified_safety_review":R,"independent_QD_review":R,"may_publish":False,
    }
    doc = {
        "kind":"article","slug":"synthetic","citation_occurrences":1,
        "human_claim_support":R,"qualified_safety_review":R,
        "independent_QD_review":R,"may_publish":False,
        "all_original_DOM_blocks_UNABRIDGED_NOT_REVIEWED":[{
            "original_block_UNABRIDGED_NOT_REVIEWED":block,
            "original_citation_ordinals_IN_BLOCK":[1],
            "human_claim_support":R,"qualified_safety_review":R,"may_publish":False,
        }],
    }
    source = {
        "variant_key_sha256":V,
        "all_unabridged_cited_claim_blocks_IN_ORIGINAL_ORDER_NOT_REVIEWED":[deepcopy(row)],
        "human_source_review":R,"human_claim_support":R,
        "qualified_safety_review":R,"independent_QD_review":R,"may_publish":False,
    }
    return seal({
        "schema":r89.SCHEMA,"issue":136,"release_state":"HOLD",
        "may_publish":False,"medical_safety_approved":False,
        "human_source_approvals":0,"human_claim_approvals":0,
        "qualified_safety_approvals":0,"independent_QD_approvals":0,
        "complete_R88_original_evidence_UNABRIDGED_NOT_APPROVED":{},
        "all_41_document_complete_DOM_reading_packets_NOT_APPROVED":[doc],
        "all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED":[row],
        "all_source_variant_reverse_impact_dossiers_NOT_APPROVED":[source],
        "unpaired_historical_reviews_UNABRIDGED":[],
        "counts":{"documents":1,"complete_DOM_blocks":1,"citation_occurrences":1,
                  "distinct_source_variants":1,"source_variant_edges":1},
    })


def changed(p, fn):
    p = deepcopy(p)
    fn(p)
    return seal(p)


def flags(before, after):
    return set(r90.compare(before,after)["review_flags_NOT_SAFETY_VERDICTS"])


class Custody(unittest.TestCase):
    def setUp(self):
        self.p = sample()
        self.out = r90.index(self.p)

    def test_deterministic_index(self):
        self.assertEqual(self.out,r90.index(deepcopy(self.p)))

    def test_output_is_HOLD(self):
        self.assertEqual(self.out["release_state"],"HOLD")

    def test_no_publish(self):
        self.assertIs(self.out["may_publish"],False)

    def test_no_medical_safety_approval(self):
        self.assertIs(self.out["medical_safety_approved"],False)

    def test_no_human_source_approvals(self):
        self.assertEqual(self.out["human_source_approvals"],0)

    def test_no_human_claim_approvals(self):
        self.assertEqual(self.out["human_claim_approvals"],0)

    def test_no_qualified_safety_approvals(self):
        self.assertEqual(self.out["qualified_safety_approvals"],0)

    def test_no_QD_approvals(self):
        self.assertEqual(self.out["independent_QD_approvals"],0)

    def test_parent_unabridged(self):
        self.assertEqual(self.out["complete_R89_original_evidence_UNABRIDGED_NOT_APPROVED"],self.p)

    def test_citation_count_conserved(self):
        self.assertEqual(self.out["counts"]["citation_occurrences"],1)

    def test_source_edge_count_conserved(self):
        self.assertEqual(self.out["counts"]["source_variant_edges"],1)

    def test_source_identity_retained(self):
        row = self.out["all_original_citation_claim_scope_review_rows_NOT_APPROVED"][0]
        self.assertEqual(row["distinct_origin_scoped_source_variant_keys_NOT_ALIASES"],[V])

    def test_original_DOM_digest_retained(self):
        row = self.out["all_original_citation_claim_scope_review_rows_NOT_APPROVED"][0]
        self.assertEqual(row["original_DOM_text_sha256"],
                         self.p["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0]["original_DOM_text_sha256"])

    def test_output_seal(self):
        self.assertEqual(self.out["sha256_seal"],
                         r90.digest({k:v for k,v in self.out.items() if k != "sha256_seal"}))

    def test_verify_full_reconstruction(self):
        r90.verify(self.out,self.p)

    def test_publication_tamper_fails(self):
        self.p["may_publish"]=True
        with self.assertRaises(r90.Gate): r90.index(self.p)

    def test_medical_approval_tamper_fails(self):
        self.p["medical_safety_approved"]=True
        with self.assertRaises(r90.Gate): r90.index(self.p)

    def test_QD_approval_tamper_fails(self):
        self.p["independent_QD_approvals"]=1
        with self.assertRaises(r90.Gate): r90.index(self.p)

    def test_source_approval_tamper_fails(self):
        self.p["human_source_approvals"]=1
        with self.assertRaises(r90.Gate): r90.index(self.p)

    def test_missing_parent_seal_fails(self):
        self.p.pop("sha256_seal")
        with self.assertRaises(r90.Gate): r90.index(self.p)

    def test_corrupt_parent_seal_fails(self):
        self.p["sha256_seal"]="bad"
        with self.assertRaises(r90.Gate): r90.index(self.p)

    def test_duplicate_document_fails(self):
        p = changed(self.p,lambda x:x["all_41_document_complete_DOM_reading_packets_NOT_APPROVED"].append(
            deepcopy(x["all_41_document_complete_DOM_reading_packets_NOT_APPROVED"][0])))
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_duplicate_citation_ordinal_fails(self):
        p = changed(self.p,lambda x:x["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"].append(
            deepcopy(x["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0])))
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_missing_source_variant_fails(self):
        p = changed(self.p,lambda x:x["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"].clear())
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_duplicate_source_variant_fails(self):
        p = changed(self.p,lambda x:x["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"].append(
            deepcopy(x["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0])))
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_changed_DOM_text_fails(self):
        def change(x):
            x["all_41_document_complete_DOM_reading_packets_NOT_APPROVED"][0][
                "all_original_DOM_blocks_UNABRIDGED_NOT_REVIEWED"][0][
                "original_block_UNABRIDGED_NOT_REVIEWED"]["unabridged_DOM_text_NOT_REVIEWED"]="changed"
        p=changed(self.p,change)
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_changed_source_reverse_edge_fails(self):
        def change(x):
            x["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0][
                "all_unabridged_cited_claim_blocks_IN_ORIGINAL_ORDER_NOT_REVIEWED"].clear()
        p=changed(self.p,change)
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_changed_claim_context_fails(self):
        def change(x):
            x["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0][
                "historical_before_claim_container_UNABRIDGED_OR_NONE"]="Drifted."
        p=changed(self.p,change)
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_reviewed_citation_fails(self):
        def change(x):
            x["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0][
                "qualified_safety_review"]="PASS"
        p=changed(self.p,change)
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_changed_original_rank_fails(self):
        def change(x):
            x["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0]["citation_ordinal"]=2
        p=changed(self.p,change)
        with self.assertRaises(r90.Gate): r90.index(p)

    def test_output_false_approval_fails(self):
        o=deepcopy(self.out)
        o["qualified_safety_approvals"]=1
        o["sha256_seal"]=r90.digest({k:v for k,v in o.items() if k!="sha256_seal"})
        with self.assertRaises(r90.Gate): r90.verify(o,self.p)

    def test_output_missing_row_fails(self):
        o=deepcopy(self.out)
        o["all_original_citation_claim_scope_review_rows_NOT_APPROVED"].clear()
        o["sha256_seal"]=r90.digest({k:v for k,v in o.items() if k!="sha256_seal"})
        with self.assertRaises(r90.Gate): r90.verify(o,self.p)

    def test_expected_census_fails_closed(self):
        with self.assertRaises(r90.Gate): r90.audit(self.p,expected=r90.EXPECTED)

    def test_valid_synthetic_expected_census(self):
        self.assertEqual(r90.audit(self.p,expected=(1,1,0,1,1,1,1)),self.out)

    def test_private_CSV_rows(self):
        c=r90.private_csv(self.out,self.p)
        data=list(csv.DictReader(io.StringIO(c)))
        self.assertEqual(len(data),1)
        self.assertEqual(data[0]["qualified_safety_review"],R)
        self.assertEqual(data[0]["may_publish"],"FALSE")

    def test_private_CSV_cannot_approve(self):
        self.assertNotIn("PASS",r90.private_csv(self.out,self.p))

    def test_case_no_context_has_no_inferred_approval(self):
        row=r90.compare(None,None)
        self.assertIn("HISTORICAL_CONTEXT_SIDE_MISSING_REVIEW_ONLY",
                      row["review_flags_NOT_SAFETY_VERDICTS"])
        self.assertIs(row["may_publish"],False)

    def test_before_absent_recovered_as_none(self):
        out=r90.compare(None,"Never try this")
        self.assertIsNone(out["before_complete_relevant_clauses_NOT_REVIEWED"])

    def test_after_absent_recovered_as_none(self):
        out=r90.compare("Never try this",None)
        self.assertIsNone(out["after_complete_relevant_clauses_NOT_REVIEWED"])

    def test_invalid_context_type_is_rejected(self):
        with self.assertRaises(r90.Gate): r90.compare(123,"text")

    def test_scopes_unabridged(self):
        text="Never try this. Do not attempt without experts."
        rows=r90.scopes(text)
        self.assertEqual([x["complete_clause_UNABRIDGED_NOT_REVIEWED"] for x in rows],
                         ["Never try this.","Do not attempt without experts."])

    def test_scopes_hashes(self):
        for row in r90.scopes("Never do it. Do not do it."):
            self.assertEqual(row["complete_clause_SHA256"],
                             hashlib.sha256(row["complete_clause_UNABRIDGED_NOT_REVIEWED"].encode()).hexdigest())

    def test_qualifier_repetition_not_set(self):
        self.assertEqual(r90.qualifiers("Never again; never, never."),["never","never","never"])

    def test_range_and_units_preserved(self):
        self.assertTrue(any("5" in x and "10" in x for x in r90.quantities("5–10 minutes")))

    def test_lexical_not_medical_judgement(self):
        self.assertEqual(r90.compare("Do not do X.","Do X.")["qualified_safety_review"],R)


# Each named scenario is a separate unittest, not one repeated assertion loop.
SCENARIOS = [
    ("water_volume_changed", "Use 1 liter.", "Use 2 liters.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("units_changed", "Use 1 liter.", "Use 1 gallon.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("temperature_units_changed", "Use 40°F.", "Use 40°C.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("time_changed", "Wait 30 minutes.", "Wait 90 minutes.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("percent_changed", "A 2% solution.", "A 4% solution.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("range_changed", "Wait 5-10 minutes.", "Wait 5-20 minutes.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("fraction_changed", "Take 1/2 cup.", "Take 1/4 cup.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("threshold_changed", "Use at least 3 days.", "Use at least 5 days.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("multiple_quantities_swapped", "Use 3 liters, then 5 liters.", "Use 5 liters, then 3 liters.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("year_changed", "Recorded in 1805.", "Recorded in 1806.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("numeric_added", "Use sterile equipment.", "Use 2 sterile items.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("numeric_removed", "Prepare 2 kits.", "Prepare kits.", "QUANTITY_OR_UNIT_ORDER_OR_VALUE_CHANGED_REVIEW_ONLY"),
    ("never_removed", "Never do this.", "Do this.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("not_added", "Use this.", "Do not use this.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("unless_removed", "Try unless warned.", "Try when warned.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("must_to_may", "You must stop.", "You may stop.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("if_removed", "Stop if instructed.", "Stop when instructed.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("before_after_reordered", "Before X, after Y.", "After X, before Y.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("conditional_order_changed", "If A, never B.", "Never A, if B.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("only_gained", "Use it.", "Only use it.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("qualifier_clause_shift", "Never use A. Use B.", "Use A. Never use B.", "QUALIFIER_SCOPE_CHANGED_WITH_SAME_TOKENS_REVIEW_ONLY"),
    ("qualifier_sentence_reorder", "Never do A. You may do B.", "You may do B. Never do A.", "QUALIFIER_TOKEN_ORDER_OR_COUNT_CHANGED_REVIEW_ONLY"),
    ("same_never_new_clause", "Never use bleach. Read note.", "Read note. Never use bleach.", "QUALIFIER_SCOPE_CHANGED_WITH_SAME_TOKENS_REVIEW_ONLY"),
    ("same_quantity_new_clause", "Use 2 units. Wait.", "Wait. Use 2 units.", "QUANTITY_SCOPE_CHANGED_WITH_SAME_TOKENS_REVIEW_ONLY"),
    ("same_number_new_verb", "Use 2 liters.", "Avoid 2 liters.", "QUANTITY_SCOPE_CHANGED_WITH_SAME_TOKENS_REVIEW_ONLY"),
    ("same_number_placement", "2 liters now. Later wait.", "Later wait. 2 liters now.", "QUANTITY_SCOPE_CHANGED_WITH_SAME_TOKENS_REVIEW_ONLY"),
    ("citation_added", "A note.", "A note. {{cite:a}}", "HISTORICAL_CITATION_TOKEN_SEQUENCE_CHANGED_REVIEW_ONLY"),
    ("citation_removed", "A note {{cite:a}}", "A note.", "HISTORICAL_CITATION_TOKEN_SEQUENCE_CHANGED_REVIEW_ONLY"),
    ("citation_swapped", "{{cite:a}} {{cite:b}}", "{{cite:b}} {{cite:a}}", "HISTORICAL_CITATION_TOKEN_SEQUENCE_CHANGED_REVIEW_ONLY"),
    ("literal_link_changed", "See https://a.example/x", "See https://b.example/x", "HISTORICAL_LITERAL_URL_SEQUENCE_CHANGED_REVIEW_ONLY"),
    ("literal_link_added", "See the record", "See https://a.example/x", "HISTORICAL_LITERAL_URL_SEQUENCE_CHANGED_REVIEW_ONLY"),
    ("literal_link_removed", "See https://a.example/x", "See no link", "HISTORICAL_LITERAL_URL_SEQUENCE_CHANGED_REVIEW_ONLY"),
    ("punctuation_text_changed", "Plain text.", "Plain text!", "HISTORICAL_TEXT_DIFF_REQUIRES_CLAIM_REVIEW"),
    ("capitalization_changed", "Never do this.", "NEVER do this.", "HISTORICAL_TEXT_DIFF_REQUIRES_CLAIM_REVIEW"),
    ("word_changed", "Safe historical account.", "Changed historical account.", "HISTORICAL_TEXT_DIFF_REQUIRES_CLAIM_REVIEW"),
    ("reorder_no_flags_exempt", "Do nothing.", "Do nothing.", None),
    ("identical_quantity_exempt", "Use 2 liters.", "Use 2 liters.", None),
    ("identical_qualifier_exempt", "Never do this.", "Never do this.", None),
    ("identical_citation_exempt", "{{cite:s}}", "{{cite:s}}", None),
    ("identical_link_exempt", "https://a.example", "https://a.example", None),
]


def make_scenario(before, after, flag):
    def test(self):
        got = flags(before, after)
        if flag is None:
            self.assertEqual(got,set())
        else:
            self.assertIn(flag,got)
        output = r90.compare(before,after)
        self.assertFalse(output["may_publish"])
        self.assertEqual(output["qualified_safety_review"],R)
        self.assertEqual(output["independent_QD_review"],R)
    return test


for name,before,after,flag in SCENARIOS:
    setattr(Custody,"test_scenario_"+name,make_scenario(before,after,flag))


if __name__ == "__main__":
    unittest.main()
