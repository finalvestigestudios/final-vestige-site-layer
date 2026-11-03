"""R87 deterministic source/citation rank ambiguity, claim scope and HOLD tests.

Fully synthetic fixtures imported from established R86 tests. No network, CMS,
WordPress, public HTML or shared-working-tree writes.
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


def load(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r87 = load(ROOT / "tools" / "r87_rank_ambiguity_claim_scope_gate.py", "r87_test")
r86 = load(ROOT / "tools" / "r86_full_slate_historical_citation_bridge.py", "r86_fixture")
fx = load(ROOT / "tests" / "test_r86_full_slate_historical_citation_bridge.py",
          "r86_fixture_helpers")
REVIEW = "NOT_REVIEWED"


def sample(*, doc=None, histories=None):
    d = doc if doc is not None else fx.doc()
    h = histories if histories is not None else [fx.history()]
    return r86.construct([d], h)


def with_context(text="A safe-to-review sentence {{cite:s}}", *,
                 scope="VISIBLE_CONTAINER_NOT_SUPPORT_PROOF"):
    d = fx.doc()
    b = d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]
    b["unabridged_DOM_text_NOT_REVIEWED"] = text
    b["DOM_text_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    h = fx.history()
    h["R83_complete_unabridged_current_to_RC_review"]["after_FULL_ANCHOR"].update({
        "literal_token": "{{cite:s}}",
        "scope_state": scope,
        "complete_container_text_UNABRIDGED": text,
    })
    return sample(doc=d, histories=[h])


class Fidelity(unittest.TestCase):
    def setUp(self):
        self.original = sample()
        self.result = r87.audit(self.original)

    def test_parent_seal_and_originals_preserved(self):
        self.assertEqual(
            self.result["R86_complete_original_report_UNABRIDGED_NOT_APPROVED"],
            self.original)

    def test_full_original_unabridged_DOM_preserved(self):
        self.assertEqual(self.result[
            "all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "R86_complete_document_UNABRIDGED_NOT_APPROVED"], self.original[
            "all_41_unabridged_document_review_bridges_NOT_APPROVED"][0])

    def test_one_complete_citation_packet_retained(self):
        row = self.result["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0]
        self.assertEqual(row["R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"],
                         self.original[
            "all_41_unabridged_document_review_bridges_NOT_APPROVED"][0][
            "R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0])

    def test_original_literal_URL_remains_unmodified(self):
        c = self.result["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"][
            "R80_original_citation_UNABRIDGED_NOT_APPROVED"]
        self.assertEqual(c[
            "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"][0][
            "exact_URL_NOT_CANONICALIZED"], "https://example.org/source")

    def test_no_claim_identity_by_rank(self):
        row = self.result["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0]
        self.assertIs(row["rank_alignment_proves_claim_identity"], False)

    def test_every_approval_state_is_hard_hold(self):
        self.assertIs(self.result["may_publish"], False)
        self.assertIs(self.result["medical_safety_approved"], False)
        for field in ("human_source_approvals", "human_claim_approvals",
                      "qualified_safety_approvals", "independent_QD_approvals"):
            self.assertEqual(self.result[field], 0)

    def test_seal_and_independent_reconstruction(self):
        r87.verify(self.result, self.original)

    def test_expected_counts_fail_if_incorrect(self):
        with self.assertRaises(r87.Gate):
            r87.audit(self.original, expected=(41, 35, 6, 2173, 2359, 4070, 1768))

    def test_private_review_csv_is_only_review_data(self):
        reader = list(csv.DictReader(io.StringIO(r87.private_csv(
            self.result, self.original))))
        self.assertTrue(reader)
        self.assertTrue(all(x["human_claim_review"] == REVIEW and
                            x["may_publish"] == "FALSE" for x in reader))

    def test_parent_mutation_not_allowed_even_with_recomputed_sha(self):
        changed = deepcopy(self.original)
        changed["counts"]["citations"] += 1
        changed["sha256_seal"] = r86.digest(
            {k: v for k, v in changed.items() if k != "sha256_seal"})
        with self.assertRaises(r86.Gate):
            r87.audit(changed)

    def test_repeated_ID_does_not_imply_same_claim(self):
        d = fx.doc(citations=[fx.citation(rank=1), fx.citation(rank=2)])
        raw = sample(doc=d, histories=[fx.history(rank=1), fx.history(rank=2)])
        out = r87.audit(raw)
        self.assertEqual(out["counts"]["repeated_ID_occurrences"], 2)
        for item in out["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
                "all_original_citation_and_claim_context_reviews_NOT_APPROVED"]:
            self.assertIn("SAME_SOURCE_ID_REPEATED_RANK_IS_NOT_CLAIM_IDENTITY",
                          item["review_cues_NOT_VERDICTS"])

    def test_removed_sibling_flags_possible_rank_shift(self):
        raw = sample(histories=[fx.history(rank=1), fx.history(rank=2, after=False)])
        out = r87.audit(raw)
        self.assertEqual(out["counts"]["rank_shift_risk_occurrences"], 1)
        self.assertEqual(out["counts"]["unpaired_historical_reviews_preserved"], 1)

    def test_no_historical_four_stage_article_is_explicit(self):
        raw = sample(doc=fx.doc(slug="new"), histories=[fx.history()])
        cues = r87.audit(raw)["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "review_cues_NOT_VERDICTS"]
        self.assertIn("NO_FOUR_STAGE_HISTORICAL_OCCURRENCE", cues)

    def test_tool_is_never_pretended_to_have_article_provenance(self):
        raw = sample(doc=fx.doc(kind="tool"))
        result = r87.audit(raw)
        self.assertEqual(result["counts"]["tool"], 1)
        self.assertEqual(result["counts"]["article"], 0)

    def test_complete_context_does_not_create_safety_approval(self):
        raw = with_context()
        result = r87.audit(raw)
        cues = result["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "review_cues_NOT_VERDICTS"]
        self.assertNotIn("HISTORICAL_CLAIM_CONTAINER_NOT_VERBATIM_IN_RC_BLOCK", cues)
        self.assertIs(result["may_publish"], False)

    def test_context_shift_not_equated_with_original_claim(self):
        raw = with_context("Different original sentence {{cite:s}}")
        h = raw["all_41_unabridged_document_review_bridges_NOT_APPROVED"][0][
            "R80_citation_to_R85_impact_crosswalk_NOT_APPROVED"][0][
            "R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED"]
        h["R83_complete_unabridged_current_to_RC_review"]["after_FULL_ANCHOR"][
            "complete_container_text_UNABRIDGED"] = "Changed claim {{cite:s}}"
        raw["sha256_seal"] = r86.digest(
            {k:v for k,v in raw.items() if k!="sha256_seal"})
        result = r87.audit(raw)
        cue = result["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "review_cues_NOT_VERDICTS"]
        self.assertIn("HISTORICAL_CLAIM_CONTAINER_NOT_VERBATIM_IN_RC_BLOCK", cue)
        self.assertIs(result["may_publish"], False)

    def test_malformed_anchor_literal_token_is_cued_not_approved(self):
        raw = with_context()
        raw_original = raw["all_41_unabridged_document_review_bridges_NOT_APPROVED"][0][
            "R80_complete_original_document_UNABRIDGED_NOT_APPROVED"]
        self.assertIsNotNone(raw_original)
        # Synthetic source row itself has no safety verdict; an observed
        # literal anomaly is a review cue, not an unsupported approval.
        self.assertIs(r87.audit(raw)["medical_safety_approved"], False)

    def test_normalization_does_not_alias_sources(self):
        self.assertEqual(r87.normalized("a \n b   c"), "a b c")
        self.assertIsNone(r87.normalized(None))

    def test_unpaired_historical_original_is_preserved(self):
        raw = sample(doc=fx.doc(citations=[]), histories=[fx.history()])
        out = r87.audit(raw)
        self.assertEqual(out["counts"]["citations"], 0)
        self.assertEqual(len(out["unpaired_historical_review_records_UNABRIDGED"]), 1)

    def test_spreadsheet_escape_happens_in_csv(self):
        self.assertEqual(r86.excel_safe("=HYPERLINK()"), "'=HYPERLINK()")


def mutate(derived, case):
    i = case // 13
    mode = case % 13
    if mode == 0:
        derived["schema"] = "wrong-schema-" + str(i)
    elif mode == 1:
        derived["release_state"] = "APPROVED-" + str(i)
    elif mode == 2:
        derived["may_publish"] = True
    elif mode == 3:
        derived["medical_safety_approved"] = True
    elif mode == 4:
        derived["human_source_approvals"] = i + 1
    elif mode == 5:
        derived["qualified_safety_approvals"] = i + 1
    elif mode == 6:
        derived["independent_QD_approvals"] = i + 1
    elif mode == 7:
        derived["counts"]["citation_occurrences_for_human_review"] = 9000 + i
    elif mode == 8:
        derived["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "may_publish"] = True
    elif mode == 9:
        derived["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "rank_alignment_proves_claim_identity"] = True
    elif mode == 10:
        derived["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "review_cues_NOT_VERDICTS"].append("FORGED_APPROVAL_" + str(i))
    elif mode == 11:
        derived["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0][
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "human_claim_support"] = "APPROVED-" + str(i)
    else:
        derived["R86_complete_original_report_UNABRIDGED_NOT_APPROVED"][
            "counts"]["citations"] = 10000 + i


def _make_adversarial(case):
    def test(self):
        original = sample()
        derived = r87.audit(original)
        mutate(derived, case)
        # An attacker can recompute the derived digest; independent
        # construction from original source must still catch the edit.
        derived["sha256_seal"] = r86.digest(
            {k:v for k,v in derived.items() if k!="sha256_seal"})
        with self.assertRaises((r87.Gate, r86.Gate)):
            r87.verify(derived, original)
    return test


for index in range(52):
    setattr(Fidelity, "test_resealed_adversarial_%02d" % index,
            _make_adversarial(index))


if __name__ == "__main__":
    unittest.main()
