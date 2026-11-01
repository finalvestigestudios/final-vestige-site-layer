#!/usr/bin/env python3
"""Repinned adversarial + exact-corpus tests for R51 reconciliation."""
from __future__ import annotations
import copy
import importlib.util
import io
import contextlib
import json
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / "tools/r51_joint_review_gate.py"
spec = importlib.util.spec_from_file_location("r51_joint_gate_tests", P)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
URL = "https://example.org/shared-url-but-distinct-sources"
STATE = "PENDING_INDEPENDENT_SOURCE_SCOPE_UNIT_CONTEXT_AND_SAFETY_REVIEW"

def source(sid, fp):
    return {"source_id": sid, "original_url": URL,
            "original_source_record_sha256": fp, "article_source_origin": sid,
            "human_source_link_checked": False, "claim_supported_verified": False}

def numeric_task(i, slug, body_fp, sid, source_fp):
    return {"claim_ordinal": i, "claim_identity_sha256": str(i)*64,
            "slug": slug, "original_article_html_sha256": body_fp,
            "original_source_id_occurrences": [sid],
            "original_source_variants": [source(sid, source_fp)],
            "review_flags": ["NUMBER_TOKEN_IS_NOT_CLAIM_OR_UNIT_VERIFICATION",
                             "HUMAN_SOURCE_AND_CONTEXT_CHECK_REQUIRED"],
            "state": STATE, "source_claim_accuracy_verified": False,
            "qualified_safety_clearance": False, "may_publish": False}

def candidate(cid, slug, body_fp, sid, source_fp, placeholder=False):
    return {"candidate": cid, "article": slug, "article_html_sha256": body_fp,
            "may_publish": False, "qualified_human_review_completed": False,
            "state": "HOLD", "unevaluated_placeholder": placeholder,
            "in_r48_reviewed_appendix": not placeholder,
            "line_at_original_snapshot": None if placeholder else 12,
            "excerpt_not_independently_verified": None if placeholder else "original passage",
            "source_records": [{
                "source_id": sid, "article_scope_source_sha256": source_fp,
                "human_claim_support_verified": False,
                "all_original_contributor_variants": [{
                    "url": URL, "original_source_sha256": source_fp}]}]}

def seal(n, s):
    for report in (n, s):
        report["fingerprint_sha256"] = gate.digest({
            k: v for k, v in report.items() if k != "fingerprint_sha256"})

def make_reports():
    n = {"issue": 136, "release_state": "HOLD",
         "may_publish": False, "qualified_safety_clearance": False,
         "independent_QD_approval": False, "human_source_links_verified": False,
         "source_claim_accuracy_verified": False, "human_source_reviews_completed": False,
         "counts": {"original_numeric_claim_blocks": 2,
                    "original_accessibility_urls": 2, "unavailable_source_urls": 1,
                    "accessible_text_extractions_not_human_checks": 1,
                    "original_citation_occurrences_in_numeric_blocks": 2},
         "review_tasks": [
             numeric_task(1, "water", "a"*64, "source-a", "e"*64),
             numeric_task(2, "food", "b"*64, "source-b", "f"*64)]}
    s = {"issue": 136, "release_state": "HOLD",
         "may_publish": False, "qualified_safety_clearance": False,
         "independent_QD_approval": False, "human_source_links_verified": False,
         "claim_accuracy_verified": False,
         "counts": {"open_incidents": 2, "high": 1, "medium": 1, "low": 0,
                    "historically_blocked_sources": 1, "candidate_rows": 2,
                    "reviewable_candidates": 1, "placeholder_B09": 1,
                    "completed_independent_reviews": 0},
         "open_incidents": [
             {"id": "SX-01", "severity": "HIGH", "state": "HOLD"},
             {"id": "SX-06", "severity": "MEDIUM", "state": "HOLD"}],
         "unresolved_source_access": [{
             "source_id": "source-a", "review_state": "HOLD",
             "human_link_check_complete": False,
             "machine_retrieval_failure": "HTTP 403",
             "original_variants": [{"url": URL, "original_source_sha256": "e"*64}],
             "r48_machine_access_observations": [{"url": URL, "ok": False}]}],
         "candidate_workorders": [
             candidate("A01", "water", "a"*64, "source-a", "e"*64),
             candidate("B09", "food", "b"*64, "source-b", "f"*64, True)]}
    seal(n, s)
    return n, s

def check(n, s):
    return gate.verify_reports(n, s, expected=(2, 2, 1, 2, 2, 1))

def overwrite(n, s, dotted_path, value):
    parts = dotted_path.split(".")
    node = n if parts[0] == "n" else s
    for x in parts[1:-1]:
        node = node[int(x)] if x.isdigit() else node[x]
    k = parts[-1]
    node[int(k) if k.isdigit() else k] = value

# Every adversarial fixture is re-fingerprinted after changing an evidence field.
# A naive "hash matches itself" gate therefore cannot detect these.
MUTATIONS = {
    "numeric_release": ("n.release_state", "PASS"),
    "safety_release": ("s.release_state", "PASS"),
    "numeric_issue": ("n.issue", 99),
    "safety_issue": ("s.issue", 99),
    "numeric_publish": ("n.may_publish", True),
    "numeric_qualified": ("n.qualified_safety_clearance", True),
    "numeric_qd": ("n.independent_QD_approval", True),
    "numeric_link_check": ("n.human_source_links_verified", True),
    "safety_publish": ("s.may_publish", True),
    "safety_qualified": ("s.qualified_safety_clearance", True),
    "safety_qd": ("s.independent_QD_approval", True),
    "safety_link_check": ("s.human_source_links_verified", True),
    "numeric_claim_accuracy": ("n.source_claim_accuracy_verified", True),
    "numeric_review_done": ("n.human_source_reviews_completed", True),
    "safety_claim_accuracy": ("s.claim_accuracy_verified", True),
    "numeric_claim_count": ("n.counts.original_numeric_claim_blocks", 3),
    "access_url_count": ("n.counts.original_accessibility_urls", 3),
    "inaccessible_count": ("n.counts.unavailable_source_urls", 0),
    "access_math": ("n.counts.accessible_text_extractions_not_human_checks", 2),
    "citation_count": ("n.counts.original_citation_occurrences_in_numeric_blocks", 3),
    "incident_count": ("s.counts.open_incidents", 3),
    "candidate_count": ("s.counts.candidate_rows", 3),
    "blocked_count": ("s.counts.historically_blocked_sources", 3),
    "review_count": ("s.counts.completed_independent_reviews", 1),
    "placeholder_count": ("s.counts.placeholder_B09", 0),
    "reviewable_count": ("s.counts.reviewable_candidates", 2),
    "numeric_ordinal": ("n.review_tasks.1.claim_ordinal", 1),
    "numeric_duplicate_identity": ("n.review_tasks.1.claim_identity_sha256", "1"*64),
    "numeric_invalid_identity": ("n.review_tasks.0.claim_identity_sha256", "z"*64),
    "numeric_slug_empty": ("n.review_tasks.0.slug", ""),
    "numeric_bad_article_hash": ("n.review_tasks.0.original_article_html_sha256", "wrong"),
    "numeric_verify_claim": ("n.review_tasks.0.source_claim_accuracy_verified", True),
    "numeric_verify_safety": ("n.review_tasks.0.qualified_safety_clearance", True),
    "numeric_verify_publish": ("n.review_tasks.0.may_publish", True),
    "numeric_hold_removed": ("n.review_tasks.0.state", "APPROVED"),
    "numeric_flags_missing": ("n.review_tasks.0.review_flags", []),
    "numeric_source_id": ("n.review_tasks.0.original_source_variants.0.source_id", "source-b"),
    "numeric_source_url": ("n.review_tasks.0.original_source_variants.0.original_url", "http://bad"),
    "numeric_source_hash": ("n.review_tasks.0.original_source_variants.0.original_source_record_sha256", "wrong"),
    "numeric_source_human_link": ("n.review_tasks.0.original_source_variants.0.human_source_link_checked", True),
    "numeric_source_claim_support": ("n.review_tasks.0.original_source_variants.0.claim_supported_verified", True),
    "incident_severity": ("s.open_incidents.0.severity", "LOW"),
    "incident_state": ("s.open_incidents.0.state", "CLOSED"),
    "incident_duplicate": ("s.open_incidents.1.id", "SX-01"),
    "incident_high_count": ("s.counts.high", 0),
    "blocker_human_checked": ("s.unresolved_source_access.0.human_link_check_complete", True),
    "blocker_resolved": ("s.unresolved_source_access.0.review_state", "CLEARED"),
    "blocker_no_failure": ("s.unresolved_source_access.0.machine_retrieval_failure", ""),
    "blocker_url": ("s.unresolved_source_access.0.original_variants.0.url", "ftp://bad"),
    "blocker_hash": ("s.unresolved_source_access.0.original_variants.0.original_source_sha256", "bad"),
    "blocker_observation": ("s.unresolved_source_access.0.r48_machine_access_observations.0.ok", "verified"),
    "candidate_duplicate": ("s.candidate_workorders.1.candidate", "A01"),
    "candidate_article_missing": ("s.candidate_workorders.0.article", None),
    "candidate_hash_mismatch": ("s.candidate_workorders.0.article_html_sha256", "b"*64),
    "candidate_published": ("s.candidate_workorders.0.may_publish", True),
    "candidate_reviewed": ("s.candidate_workorders.0.qualified_human_review_completed", True),
    "candidate_state_cleared": ("s.candidate_workorders.0.state", "CLEARED"),
    "candidate_false_placeholder": ("s.candidate_workorders.0.unevaluated_placeholder", True),
    "candidate_missing_from_appendix": ("s.candidate_workorders.0.in_r48_reviewed_appendix", False),
    "b09_false_evaluated": ("s.candidate_workorders.1.unevaluated_placeholder", False),
    "b09_in_appendix": ("s.candidate_workorders.1.in_r48_reviewed_appendix", True),
    "b09_fake_line": ("s.candidate_workorders.1.line_at_original_snapshot", 55),
    "b09_fake_quote": ("s.candidate_workorders.1.excerpt_not_independently_verified", "fabricated"),
    "candidate_sources_removed": ("s.candidate_workorders.0.source_records", []),
    "candidate_human_support": ("s.candidate_workorders.0.source_records.0.human_claim_support_verified", True),
    "candidate_same_source_wrong_hash": ("s.candidate_workorders.0.source_records.0.article_scope_source_sha256", "f"*64),
    "candidate_variant_invalid": ("s.candidate_workorders.0.source_records.0.all_original_contributor_variants.0.original_source_sha256", "bad"),
}

class ValidFixture(unittest.TestCase):
    def test_valid_hold_and_cross_source_identity(self):
        n, s = make_reports()
        r = check(n, s)
        self.assertEqual(r["release_state"], "HOLD")
        self.assertFalse(r["may_publish"])
        self.assertEqual(r["counts"]["cross_report_original_source_id_matches"], 2)
        self.assertEqual(r["counts"]["blocked_historical_variants_overlapping_numeric_urls"], 1)

    def test_same_url_distinct_source_records_not_collapsed(self):
        n, s = make_reports()
        v = [r["original_source_variants"][0] for r in n["review_tasks"]]
        self.assertEqual(v[0]["original_url"], v[1]["original_url"])
        self.assertNotEqual(v[0]["original_source_record_sha256"],
                            v[1]["original_source_record_sha256"])
        self.assertEqual(check(n, s)["counts"]["cross_report_original_source_id_matches"], 2)

    def test_deterministic_without_mutation(self):
        n, s = make_reports()
        frozen = copy.deepcopy((n, s))
        self.assertEqual(check(n, s), check(n, s))
        self.assertEqual((n, s), frozen)

    def test_machine_access_today_does_not_clear_historical_failure(self):
        n, s = make_reports()
        s["unresolved_source_access"][0]["r48_machine_access_observations"][0]["ok"] = True
        seal(n, s)
        self.assertFalse(check(n, s)["human_source_links_verified"])

    def test_reject_wrong_pinned_counts(self):
        n, s = make_reports()
        with self.assertRaises(gate.IntegrationHold):
            gate.verify_reports(n, s, expected=(2, 2, 1))

    def test_reject_non_repinned_change(self):
        n, s = make_reports()
        n["counts"]["original_numeric_claim_blocks"] = 99
        with self.assertRaises(gate.IntegrationHold):
            check(n, s)

    def test_reject_missing_numeric_task(self):
        n, s = make_reports()
        n["review_tasks"].pop()
        seal(n, s)
        with self.assertRaises(gate.IntegrationHold):
            check(n, s)

    def test_reject_missing_historic_failure(self):
        n, s = make_reports()
        s["unresolved_source_access"].clear()
        seal(n, s)
        with self.assertRaises(gate.IntegrationHold):
            check(n, s)

    def test_reject_cross_article_hash_mismatch(self):
        n, s = make_reports()
        n["review_tasks"][1]["slug"] = "water"
        seal(n, s)
        with self.assertRaises(gate.IntegrationHold):
            check(n, s)

    def test_reject_original_citation_occurrence_loss(self):
        n, s = make_reports()
        n["review_tasks"][0]["original_source_id_occurrences"].append("source-a")
        seal(n, s)
        with self.assertRaises(gate.IntegrationHold):
            check(n, s)

class RepinnedAdversarialEvidence(unittest.TestCase):
    pass

def build_case(name, dotted_path, replacement):
    def test_case(self):
        n, s = make_reports()
        overwrite(n, s, dotted_path, replacement)
        seal(n, s)
        with self.assertRaises(gate.IntegrationHold, msg=name):
            check(n, s)
    test_case.__name__ = "test_reject_" + name
    return test_case

for label, (path, replacement) in MUTATIONS.items():
    setattr(RepinnedAdversarialEvidence, "test_reject_" + label,
            build_case(label, path, replacement))

class NativeRepository(unittest.TestCase):
    def test_original_35_article_report_holds(self):
        root = P.parents[2]
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exit_code = gate.main(["--repo-root", str(root)])
        self.assertEqual(exit_code, 0, stderr.getvalue())
        result = json.loads(stdout.getvalue())
        counts = result["counts"]
        self.assertEqual(counts["quantified_claims_pending"], 186)
        self.assertEqual(counts["open_safety_incidents"], 15)
        self.assertEqual(counts["historically_blocked_original_source_ids"], 25)
        self.assertEqual(counts["safety_candidate_rows_not_approvals"], 29)
        self.assertFalse(result["may_publish"])

if __name__ == "__main__":
    unittest.main()
