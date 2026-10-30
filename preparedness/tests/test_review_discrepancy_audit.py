"""Offline synthetic adversarial multi-review comparison (no external source verification)."""
from __future__ import annotations

import copy
from datetime import date
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import review_discrepancy_audit as compare
import review_receipts as receipts
import review_response_audit as intake
import source_review_queue as queue
from test_source_review_queue import fixture

TODAY = date(2026, 10, 30)


class ReviewDiscrepancyTests(unittest.TestCase):
    def setUp(self):
        lib, rows = fixture()
        self.manifest = receipts.build_manifest(queue.build_review_queue(lib, rows=rows),
                                                {"first-aid-not-medical": "a" * 64})
        self.b1 = self.bundle()
        self.b2 = self.bundle()

    def bundle(self):
        return {"schema_version": 1, "manifest_sha256": self.manifest["manifest_sha256"],
                "citation_responses": [], "shared_url_responses": []}

    def cite(self, num=0, reviewer="Reviewer One"):
        source = self.manifest["citations"][num]
        return {"review_request_sha256": source["review_request_sha256"],
                "reviewer": reviewer, "reviewed_on": "2026-10-29",
                "link_check": "REACHED_SOURCE", "observed_url": source["url"],
                "source_locator": "Section three paragraph two",
                "claim_check": "SUPPORTED_IN_INSPECTED_SCOPE",
                "evidence_notes": "The synthetic test citation supports only a limited statement.",
                "reading_limits": "All other document sections remain unread.",
                "risk_flags": []}

    def group(self, reviewer="Reviewer One"):
        source = self.manifest["shared_url_packets"][0]
        return {"packet_sha256": source["packet_sha256"], "reviewer": reviewer,
                "reviewed_on": "2026-10-29", "url": source["url"],
                "row_reviews": [{"source_row_key": key, "reading_status": "INSPECTED",
                                 "source_locator": "Exact source section three",
                                 "reading_notes": "Only this section was actually inspected."}
                                for key in source["all_source_row_keys"]],
                "relationship": "CONSISTENT_LIMITED_SCOPES",
                "comparison_notes": "Contributor readings were separately compared in this synthetic fixture."}

    def reviewed_cite(self, num=0):
        self.b1["citation_responses"] = [self.cite(num, "Reviewer One")]
        self.b2["citation_responses"] = [self.cite(num, "Reviewer Two")]

    def reviewed_group(self):
        self.b1["shared_url_responses"] = [self.group("Reviewer One")]
        self.b2["shared_url_responses"] = [self.group("Reviewer Two")]

    def full_reviews(self):
        self.b1["citation_responses"] = [self.cite(n, "Reviewer One") for n in range(2)]
        self.b2["citation_responses"] = [self.cite(n, "Reviewer Two") for n in range(2)]
        self.reviewed_group()

    def run_audit(self, *bundles, previous=None):
        return compare.audit_discrepancies(self.manifest, list(bundles or [self.b1]),
                                           today=TODAY, previous=previous)

    def cite_row(self, report, num=0):
        key = self.manifest["citations"][num]["review_request_sha256"]
        return next(r for r in report["citations"] if r["review_request_sha256"] == key)

    def group_row(self, report):
        return report["shared_url_packets"][0]

    def refresh_manifest(self):
        self.manifest["manifest_sha256"] = receipts.digest({k: v for k, v in self.manifest.items()
                                                              if k != "manifest_sha256"})
        self.b1["manifest_sha256"] = self.manifest["manifest_sha256"]
        self.b2["manifest_sha256"] = self.manifest["manifest_sha256"]

    def refresh_group(self):
        g = self.manifest["shared_url_packets"][0]
        g["packet_sha256"] = receipts.digest({k: v for k, v in g.items()
                                                if k not in ("packet_sha256", "review_state", "approved", "human_tasks")})
        self.refresh_manifest()

    def test_empty_one_bundle_all_pending(self):
        x = self.run_audit()
        self.assertEqual(x["counts"]["citation_requests_with_fewer_than_two_reports"], 2)
        self.assertEqual(x["counts"]["shared_url_packets_with_fewer_than_two_reports"], 1)

    def test_zero_responses_still_hold(self):
        x = self.run_audit()
        self.assertEqual(x["release_state"], "HOLD")
        self.assertIs(x["may_publish"], False)

    def test_single_citation_unverified(self):
        self.b1["citation_responses"].append(self.cite())
        self.assertEqual(self.cite_row(self.run_audit())["state"], "SINGLE_SELF_REPORT_UNVERIFIED")

    def test_single_shared_group_unverified(self):
        self.b1["shared_url_responses"].append(self.group())
        self.assertEqual(self.group_row(self.run_audit())["state"], "SINGLE_SELF_REPORT_UNVERIFIED")

    def test_two_agreeing_self_reports_no_clearance(self):
        self.reviewed_cite()
        row = self.cite_row(self.run_audit(self.b1, self.b2))
        self.assertEqual(row["state"], "MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED")
        self.assertIs(row["source_link_independently_verified"], False)
        self.assertIs(row["safety_approved"], False)

    def test_all_claims_and_group_agree_but_still_hold(self):
        self.full_reviews()
        x = self.run_audit(self.b1, self.b2)
        self.assertEqual(self.group_row(x)["state"], "MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED")
        self.assertIs(x["independent_review_complete"], False)
        self.assertEqual(x["counts"]["qualified_safety_approvals_verified"], 0)

    def test_group_agreement_does_not_cover_missing_article_reviews(self):
        self.reviewed_group()
        x = self.run_audit(self.b1, self.b2)
        self.assertEqual(self.group_row(x)["state"], "CITATION_DEPENDENCY_HOLD")

    def test_group_only_unrelated_article_review_still_dependency_hold(self):
        self.reviewed_group()
        self.reviewed_cite(0)
        x = self.run_audit(self.b1, self.b2)
        self.assertEqual(self.group_row(x)["state"], "CITATION_DEPENDENCY_HOLD")

    def test_group_one_shared_claim_review_still_dependency_hold(self):
        self.reviewed_group()
        self.b1["citation_responses"] = [self.cite(0)]
        self.b2["citation_responses"] = []
        x = self.run_audit(self.b1, self.b2)
        self.assertEqual(self.group_row(x)["state"], "CITATION_DEPENDENCY_HOLD")
        self.assertGreater(self.group_row(x)["cited_claims_missing_second_report"], 0)

    def test_group_claim_with_risk_flag_still_dependency_hold(self):
        self.full_reviews()
        self.b1["citation_responses"][1]["risk_flags"] = ["MEDICINE"]
        x = self.run_audit(self.b1, self.b2)
        self.assertEqual(self.group_row(x)["state"], "CITATION_DEPENDENCY_HOLD")

    def test_citation_link_state_disagreement(self):
        self.reviewed_cite()
        x = self.b2["citation_responses"][0]
        x.update(link_check="NOT_REACHABLE", observed_url=None, source_locator="", claim_check="NOT_CHECKED")
        row = self.cite_row(self.run_audit(self.b1, self.b2))
        self.assertEqual(row["state"], "DISAGREEMENT_ESCALATE")
        self.assertIn("link_check", row["disagreement_dimensions"])

    def test_citation_redirect_disagreement(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0].update(link_check="REDIRECTED_SOURCE", observed_url="https://example.test/revised")
        row = self.cite_row(self.run_audit(self.b1, self.b2))
        self.assertIn("observed_url", row["disagreement_dimensions"])

    def test_citation_source_locator_disagreement(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["source_locator"] = "Section ten paragraph three"
        row = self.cite_row(self.run_audit(self.b1, self.b2))
        self.assertEqual(row["disagreement_dimensions"], ["source_locator"])

    def test_citation_claim_disagreement(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["claim_check"] = "CONTRADICTED"
        self.assertIn("claim_check", self.cite_row(self.run_audit(self.b1, self.b2))["disagreement_dimensions"])

    def test_citation_risk_flag_disagreement(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["risk_flags"] = ["WATER"]
        row = self.cite_row(self.run_audit(self.b1, self.b2))
        self.assertIn("risk_flags", row["disagreement_dimensions"])
        self.assertIn("WATER", row["risk_flags_reported_union"])

    def test_identical_adverse_claims_still_followup(self):
        self.reviewed_cite()
        for b in [self.b1, self.b2]:
            b["citation_responses"][0]["claim_check"] = "UNCERTAIN"
        self.assertEqual(self.cite_row(self.run_audit(self.b1, self.b2))["state"], "FOLLOW_UP_ESCALATE")

    def test_identical_risk_flags_still_followup(self):
        self.reviewed_cite()
        for b in [self.b1, self.b2]:
            b["citation_responses"][0]["risk_flags"] = ["FOOD"]
        self.assertEqual(self.cite_row(self.run_audit(self.b1, self.b2))["state"], "FOLLOW_UP_ESCALATE")

    def test_identical_redirects_still_followup(self):
        self.reviewed_cite()
        for b in [self.b1, self.b2]:
            b["citation_responses"][0].update(link_check="REDIRECTED_SOURCE", observed_url="https://example.test/elsewhere")
        self.assertEqual(self.cite_row(self.run_audit(self.b1, self.b2))["state"], "FOLLOW_UP_ESCALATE")

    def test_group_relationship_disagreement(self):
        self.reviewed_group()
        self.b2["shared_url_responses"][0]["relationship"] = "CONFLICTING_SCOPES"
        row = self.group_row(self.run_audit(self.b1, self.b2))
        self.assertIn("relationship", row["disagreement_dimensions"])

    def test_group_reading_status_disagreement(self):
        self.reviewed_group()
        self.b2["shared_url_responses"][0]["row_reviews"][0].update(reading_status="NOT_INSPECTED", source_locator="")
        self.b2["shared_url_responses"][0]["relationship"] = "UNRESOLVED"
        row = self.group_row(self.run_audit(self.b1, self.b2))
        self.assertIn("row_reading_status", row["disagreement_dimensions"])

    def test_group_source_locator_disagreement(self):
        self.reviewed_group()
        self.b2["shared_url_responses"][0]["row_reviews"][0]["source_locator"] = "Different page 11"
        row = self.group_row(self.run_audit(self.b1, self.b2))
        self.assertIn("row_source_locator", row["disagreement_dimensions"])

    def test_group_both_report_conflict_never_aligns(self):
        self.reviewed_group()
        for b in [self.b1, self.b2]:
            b["shared_url_responses"][0]["relationship"] = "CONFLICTING_SCOPES"
        self.assertEqual(self.group_row(self.run_audit(self.b1, self.b2))["state"], "FOLLOW_UP_ESCALATE")

    def test_group_both_unresolved_never_aligns(self):
        self.reviewed_group()
        for b in [self.b1, self.b2]:
            b["shared_url_responses"][0]["relationship"] = "UNRESOLVED"
        self.assertEqual(self.group_row(self.run_audit(self.b1, self.b2))["state"], "FOLLOW_UP_ESCALATE")

    def test_same_label_same_request_rejected(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["reviewer"] = "Reviewer One"
        self.b2["citation_responses"][0]["evidence_notes"] += " Different independently written text."
        with self.assertRaisesRegex(ValueError, "duplicate self-reported reviewer"):
            self.run_audit(self.b1, self.b2)

    def test_label_casefold_duplicate_rejected(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["reviewer"] = "REVIEWER ONE"
        with self.assertRaisesRegex(ValueError, "duplicate self-reported reviewer"):
            self.run_audit(self.b1, self.b2)

    def test_label_whitespace_duplicate_rejected(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["reviewer"] = "  Reviewer   One  "
        with self.assertRaisesRegex(ValueError, "duplicate self-reported reviewer"):
            self.run_audit(self.b1, self.b2)

    def test_unicode_fullwidth_duplicate_rejected(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["reviewer"] = "Ｒｅｖｉｅｗｅｒ Ｏｎｅ"
        with self.assertRaisesRegex(ValueError, "duplicate self-reported reviewer"):
            self.run_audit(self.b1, self.b2)

    def test_zero_width_reviewer_label_rejected(self):
        self.b1["citation_responses"].append(self.cite(reviewer="Review\u200ber One"))
        with self.assertRaisesRegex(ValueError, "invisible/control"):
            self.run_audit()

    def test_tab_reviewer_label_rejected_in_new_audit(self):
        self.b1["citation_responses"].append(self.cite(reviewer="Review\ter One"))
        with self.assertRaisesRegex(ValueError, "invisible/control"):
            self.run_audit()

    def test_same_label_different_requests_permitted(self):
        self.b1["citation_responses"] = [self.cite(0), self.cite(1)]
        self.assertEqual(self.run_audit()["counts"]["citation_self_reports"], 2)

    def test_same_label_group_and_citation_permitted(self):
        self.b1["citation_responses"].append(self.cite())
        self.b1["shared_url_responses"].append(self.group())
        self.assertEqual(self.run_audit()["counts"]["shared_url_self_reports"], 1)

    def test_duplicate_empty_bundle_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate response bundle"):
            self.run_audit(self.b1, copy.deepcopy(self.b1))

    def test_empty_bundle_list_rejected(self):
        with self.assertRaisesRegex(ValueError, "require 1 to 64"):
            compare.audit_discrepancies(self.manifest, [], today=TODAY)

    def test_65_bundles_rejected_before_intake(self):
        with self.assertRaisesRegex(ValueError, "require 1 to 64"):
            compare.audit_discrepancies(self.manifest, [{}] * 65, today=TODAY)

    def test_wrong_manifest_sha_rejected(self):
        self.b1["manifest_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "manifest binding"):
            self.run_audit()

    def test_unknown_citation_digest_rejected(self):
        self.b1["citation_responses"].append(self.cite())
        self.b1["citation_responses"][0]["review_request_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "stale/unknown"):
            self.run_audit()

    def test_duplicate_request_in_one_bundle_rejected(self):
        self.b1["citation_responses"] = [self.cite(), self.cite()]
        with self.assertRaisesRegex(ValueError, "duplicate request"):
            self.run_audit()

    def test_safety_flag_cannot_grant_approval(self):
        self.b1["citation_responses"].append(self.cite())
        self.b1["citation_responses"][0]["may_publish"] = True
        with self.assertRaisesRegex(ValueError, "unknown/missing fields"):
            self.run_audit()

    def test_inconsistent_redirect_rejected_by_upstream(self):
        self.b1["citation_responses"].append(self.cite())
        self.b1["citation_responses"][0]["observed_url"] = "https://example.test/other"
        with self.assertRaisesRegex(ValueError, "changed without redirect"):
            self.run_audit()

    def test_future_review_date_rejected_by_upstream(self):
        self.b1["citation_responses"].append(self.cite())
        self.b1["citation_responses"][0]["reviewed_on"] = "2026-11-03"
        with self.assertRaisesRegex(ValueError, "future review date"):
            self.run_audit()

    def test_shared_packet_missing_citation_detected(self):
        g = self.manifest["shared_url_packets"][0]
        g["citations"] = []
        self.refresh_group()
        with self.assertRaisesRegex(ValueError, "no citation references"):
            self.run_audit()

    def test_shared_packet_duplicate_reference_detected(self):
        g = self.manifest["shared_url_packets"][0]
        g["citations"].append(copy.deepcopy(g["citations"][0]))
        self.refresh_group()
        with self.assertRaisesRegex(ValueError, "foreign or duplicate citation"):
            self.run_audit()

    def test_shared_packet_changed_claim_scope_detected(self):
        g = self.manifest["shared_url_packets"][0]
        g["citations"][0]["article_claim_scope"] = "New, unsupported claim"
        self.refresh_group()
        with self.assertRaisesRegex(ValueError, "linked claim/scope differs"):
            self.run_audit()

    def test_shared_packet_drops_cited_row_detected(self):
        g = self.manifest["shared_url_packets"][0]
        g["cited_source_row_keys"] = []
        self.refresh_group()
        with self.assertRaisesRegex(ValueError, "physical row partition"):
            self.run_audit()

    def test_shared_packet_mispartitions_rows_detected(self):
        g = self.manifest["shared_url_packets"][0]
        g["uncited_source_row_keys"] = []
        self.refresh_group()
        with self.assertRaisesRegex(ValueError, "physical row partition"):
            self.run_audit()

    def test_shared_packet_duplicate_url_detected(self):
        g = self.manifest["shared_url_packets"][0]
        self.manifest["shared_url_packets"].append(copy.deepcopy(g))
        self.manifest["counts"]["shared_url_packets"] = 2
        self.refresh_manifest()
        with self.assertRaisesRegex(ValueError, "packet binding/uniqueness"):
            self.run_audit()

    def test_prior_identical_report_is_accepted(self):
        self.reviewed_cite()
        old = self.run_audit(self.b1, self.b2)
        self.assertEqual(old, self.run_audit(self.b1, self.b2, previous=old))

    def test_prior_hash_modified_rejected(self):
        old = self.run_audit()
        old["counts"]["citation_requests"] = 999
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.run_audit(previous=old)

    def test_prior_changed_manifest_rejected(self):
        old = self.run_audit()
        old["manifest_sha256"] = "e" * 64
        old["audit_sha256"] = receipts.digest({k: v for k, v in old.items() if k != "audit_sha256"})
        with self.assertRaisesRegex(ValueError, "corpus binding"):
            self.run_audit(previous=old)

    def test_prior_record_removed_is_rejected(self):
        self.b1["citation_responses"].append(self.cite())
        old = self.run_audit()
        self.b1["citation_responses"].clear()
        with self.assertRaisesRegex(ValueError, "disappeared or was edited"):
            self.run_audit(previous=old)

    def test_prior_record_changed_is_rejected(self):
        self.b1["citation_responses"].append(self.cite())
        old = self.run_audit()
        self.b1["citation_responses"][0]["evidence_notes"] = "This updated statement differs in content but is only self reported."
        with self.assertRaisesRegex(ValueError, "disappeared or was edited"):
            self.run_audit(previous=old)

    def test_prior_additional_distinct_review_allowed(self):
        self.b1["citation_responses"].append(self.cite())
        old = self.run_audit()
        self.b2["citation_responses"].append(self.cite(reviewer="Reviewer Two"))
        new = self.run_audit(self.b1, self.b2, previous=old)
        self.assertEqual(self.cite_row(new)["reports_received"], 2)

    def test_prior_missing_row_rejected(self):
        old = self.run_audit()
        old["citations"].pop()
        old["audit_sha256"] = receipts.digest({k: v for k, v in old.items() if k != "audit_sha256"})
        with self.assertRaisesRegex(ValueError, "review inventory"):
            self.run_audit(previous=old)

    def test_prior_duplicated_request_rejected(self):
        old = self.run_audit()
        old["citations"][1] = copy.deepcopy(old["citations"][0])
        old["audit_sha256"] = receipts.digest({k: v for k, v in old.items() if k != "audit_sha256"})
        with self.assertRaisesRegex(ValueError, "duplicate/malformed"):
            self.run_audit(previous=old)

    def test_public_report_does_not_expose_reviewer_names_or_notes(self):
        self.b1["citation_responses"].append(self.cite())
        x = self.run_audit()
        encoded = json.dumps(x)
        self.assertNotIn("Reviewer One", encoded)
        self.assertNotIn("synthetic test citation supports", encoded)
        self.assertNotIn("All other document sections", encoded)

    def test_public_report_does_not_expose_changed_observed_url(self):
        self.b1["citation_responses"].append(self.cite())
        self.b1["citation_responses"][0].update(link_check="REDIRECTED_SOURCE", observed_url="https://example.test/redir-secret")
        encoded = json.dumps(self.run_audit())
        self.assertNotIn("redir-secret", encoded)

    def test_order_of_bundles_is_stable(self):
        self.reviewed_cite()
        a = self.run_audit(self.b1, self.b2)
        b = self.run_audit(self.b2, self.b1)
        self.assertEqual(a, b)

    def test_order_of_citation_rows_is_stable(self):
        self.full_reviews()
        a = self.run_audit(self.b1, self.b2)
        self.b2["citation_responses"].reverse()
        self.assertEqual(a, self.run_audit(self.b1, self.b2))

    def test_report_has_valid_self_digest(self):
        x = self.run_audit()
        self.assertEqual(x["audit_sha256"], receipts.digest({k: v for k, v in x.items() if k != "audit_sha256"}))

    def test_queue_identity_bound(self):
        x = self.run_audit()
        self.assertEqual(x["source_queue_sha256"], self.manifest["source_queue_sha256"])

    def test_all_group_reviews_keep_scopes_unreconciled(self):
        self.full_reviews()
        x = self.run_audit(self.b1, self.b2)
        self.assertEqual(x["counts"]["independently_reconciled_shared_url_scopes"], 0)
        self.assertFalse(self.group_row(x)["crosswalk_review_state_changed"])

    def test_no_identity_authentication_even_two_labels(self):
        self.reviewed_cite()
        x = self.run_audit(self.b1, self.b2)
        self.assertEqual(x["counts"]["independently_authenticated_reviewers"], 0)

    def test_synthetic_fixture_is_limited(self):
        x = self.run_audit()
        self.assertEqual(x["counts"]["citation_requests"], 2)
        self.assertEqual(x["counts"]["shared_url_packets"], 1)

    def test_error_free_field_list(self):
        x = self.run_audit()
        for part in x["citations"] + x["shared_url_packets"]:
            self.assertNotIn("approved", part)
            self.assertIs(part["safety_approved"], False)

    def test_reader_date_difference_not_auto_disagreement(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["reviewed_on"] = "2026-10-28"
        row = self.cite_row(self.run_audit(self.b1, self.b2))
        self.assertEqual(row["state"], "MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED")

    def test_different_free_text_notes_not_semantically_approved(self):
        self.reviewed_cite()
        self.b2["citation_responses"][0]["evidence_notes"] = "This separate human note appears different in this fixture."
        row = self.cite_row(self.run_audit(self.b1, self.b2))
        self.assertEqual(row["state"], "MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED")
        self.assertIs(row["claim_independently_verified"], False)

    def test_duplicate_json_key_from_file_rejected_by_upstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "responses.json"
            p.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate object key"):
                intake.load_response_file(p)

    def test_symlinked_input_rejected_by_upstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            real = pathlib.Path(tmp) / "real.json"
            link = pathlib.Path(tmp) / "link.json"
            real.write_text("{}", encoding="utf-8")
            link.symlink_to(real)
            with self.assertRaisesRegex(ValueError, "non-symlink"):
                intake.load_response_file(link)


if __name__ == "__main__":
    unittest.main()
