"""76 synthetic, offline, read-only adversarial tests for human review intake.

All sample URLs are reserved .test domains. Reports never grant publishing authority.
"""
from __future__ import annotations

import copy
from datetime import date
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import review_response_audit as intake
import review_receipts as receipts
import source_review_queue as queue
from test_source_review_queue import fixture

TODAY = date(2026, 10, 30)


class ReviewResponseAuditTests(unittest.TestCase):
    def setUp(self):
        lib, rows = fixture()
        self.manifest = receipts.build_manifest(queue.build_review_queue(lib, rows=rows),
                                                {"first-aid-not-medical": "a" * 64})
        self.bundle = {"schema_version": 1, "manifest_sha256": self.manifest["manifest_sha256"],
                       "citation_responses": [], "shared_url_responses": []}

    def citation(self, index=0):
        record = self.manifest["citations"][index]
        return {"review_request_sha256": record["review_request_sha256"],
                "reviewer": "Synthetic Test Reviewer", "reviewed_on": "2026-10-29",
                "link_check": "REACHED_SOURCE", "observed_url": record["url"],
                "source_locator": "Section 3 paragraph 2", "claim_check": "SUPPORTED_IN_INSPECTED_SCOPE",
                "evidence_notes": "The synthetic passage supports only this narrow example.",
                "reading_limits": "The other chapters were not examined.", "risk_flags": []}

    def group(self):
        record = self.manifest["shared_url_packets"][0]
        return {"packet_sha256": record["packet_sha256"], "reviewer": "Synthetic Test Reviewer",
                "reviewed_on": "2026-10-29", "url": record["url"],
                "row_reviews": [{"source_row_key": key, "reading_status": "INSPECTED",
                                 "source_locator": "Part A paragraph 7",
                                 "reading_notes": "The synthetic excerpt was inspected only."}
                                for key in record["all_source_row_keys"]],
                "relationship": "CONSISTENT_LIMITED_SCOPES",
                "comparison_notes": "The two synthetic notes have compatible but separate reading limits."}

    def report(self):
        return intake.audit(self.manifest, self.bundle, today=TODAY)

    def reject(self, fragment):
        with self.assertRaisesRegex(ValueError, fragment):
            self.report()

    def add_cite(self):
        c = self.citation()
        self.bundle["citation_responses"].append(c)
        return c

    def add_group(self):
        g = self.group()
        self.bundle["shared_url_responses"].append(g)
        return g

    def refresh_manifest(self):
        self.manifest["manifest_sha256"] = receipts.digest({k: v for k, v in self.manifest.items()
                                                              if k != "manifest_sha256"})
        self.bundle["manifest_sha256"] = self.manifest["manifest_sha256"]

    def test_empty_input_still_hold(self):
        x = self.report()
        self.assertEqual(x["release_state"], "HOLD")
        self.assertFalse(x["may_publish"])

    def test_empty_input_all_requests_pending(self):
        x = self.report()
        self.assertEqual(x["counts"]["citation_inputs_pending"], 2)
        self.assertEqual(x["counts"]["shared_url_inputs_pending"], 1)

    def test_empty_input_does_not_create_approval(self):
        x = self.report()
        self.assertEqual(x["counts"]["qualified_safety_approvals_verified"], 0)
        self.assertFalse(x["independent_review_complete"])

    def test_valid_citation_self_report_no_safety_pass(self):
        self.add_cite()
        x = self.report()
        self.assertEqual(x["counts"]["citation_inputs_recorded"], 1)
        self.assertFalse(x["citations"][0]["safety_approved"])

    def test_valid_group_report_never_resolves_crosswalk(self):
        self.add_group()
        x = self.report()
        self.assertEqual(x["counts"]["shared_url_inputs_recorded"], 1)
        self.assertEqual(x["counts"]["source_scope_reconciliations_verified"], 0)

    def test_all_records_entered_still_hold(self):
        self.bundle["citation_responses"] = [self.citation(0), self.citation(1)]
        self.add_group()
        x = self.report()
        self.assertEqual(x["counts"]["citation_inputs_pending"], 0)
        self.assertEqual(x["counts"]["shared_url_inputs_pending"], 0)
        self.assertFalse(x["may_publish"])

    def test_deterministic_report_hash(self):
        self.add_cite()
        self.add_group()
        self.assertEqual(self.report(), self.report())
        x = self.report()
        self.assertEqual(x["audit_sha256"], receipts.digest({k: v for k, v in x.items() if k != "audit_sha256"}))

    def test_unsorted_input_same_canonical_report(self):
        self.bundle["citation_responses"] = [self.citation(0), self.citation(1)]
        before = self.report()
        self.bundle["citation_responses"].reverse()
        self.assertEqual(before, self.report())

    def test_risk_flags_force_followup(self):
        self.add_cite()["risk_flags"] = ["MEDICINE"]
        self.assertEqual(self.report()["counts"]["citation_input_followups"], 1)

    def test_risk_flags_are_canonicalized(self):
        self.add_cite()["risk_flags"] = ["WATER", "FIRE"]
        self.assertIn(["FIRE", "WATER"], [x.get("risk_flags") for x in self.report()["citations"]])

    def test_unreachable_requires_followup(self):
        c = self.add_cite()
        c.update(link_check="NOT_REACHABLE", claim_check="NOT_CHECKED", observed_url=None, source_locator="")
        self.assertEqual(self.report()["counts"]["citation_input_followups"], 1)

    def test_unattempted_requires_followup(self):
        c = self.add_cite()
        c.update(link_check="NOT_ATTEMPTED", claim_check="NOT_CHECKED", observed_url=None, source_locator="")
        self.assertEqual(self.report()["counts"]["citation_input_followups"], 1)

    def test_redirected_source_requires_followup(self):
        c = self.add_cite()
        c.update(link_check="REDIRECTED_SOURCE", observed_url="https://example.test/new-page")
        self.assertEqual(self.report()["counts"]["citation_input_followups"], 1)

    def test_contradicted_source_forces_followup(self):
        self.add_cite()["claim_check"] = "CONTRADICTED"
        self.assertEqual(self.report()["counts"]["citation_input_followups"], 1)

    def test_uncertain_source_forces_followup(self):
        self.add_cite()["claim_check"] = "UNCERTAIN"
        self.assertEqual(self.report()["counts"]["citation_input_followups"], 1)

    def test_not_checked_source_forces_followup(self):
        self.add_cite()["claim_check"] = "NOT_CHECKED"
        self.assertEqual(self.report()["counts"]["citation_input_followups"], 1)

    def test_group_conflict_forces_followup(self):
        self.add_group()["relationship"] = "CONFLICTING_SCOPES"
        self.assertEqual(self.report()["counts"]["shared_url_input_followups"], 1)

    def test_group_unresolved_forces_followup(self):
        self.add_group()["relationship"] = "UNRESOLVED"
        self.assertEqual(self.report()["counts"]["shared_url_input_followups"], 1)

    def test_partly_unread_group_forces_followup(self):
        g = self.add_group()
        g["relationship"] = "UNRESOLVED"
        g["row_reviews"][0].update(reading_status="NOT_INSPECTED", source_locator="")
        self.assertEqual(self.report()["counts"]["shared_url_input_followups"], 1)

    def test_manifest_sha_payload_tamper_rejected(self):
        self.manifest["counts"]["citation_requests"] = 100
        self.reject("SHA256 payload mismatch")

    def test_manifest_per_citation_digest_tamper_rejected(self):
        self.manifest["citations"][0]["article_claim_scope"] = "Fabricated revised scope"
        self.refresh_manifest()
        self.reject("citation request binding")

    def test_manifest_per_group_digest_tamper_rejected(self):
        self.manifest["shared_url_packets"][0]["url"] = "https://example.test/altered"
        self.refresh_manifest()
        self.reject("packet binding")

    def test_manifest_may_publish_flag_rejected(self):
        self.manifest["may_publish"] = True
        self.refresh_manifest()
        self.reject("release/HOLD")

    def test_manifest_human_review_performed_flag_rejected(self):
        self.manifest["human_review_performed"] = True
        self.refresh_manifest()
        self.reject("release/HOLD")

    def test_manifest_safety_approval_flag_rejected(self):
        self.manifest["citations"][0]["approved"] = True
        self.refresh_manifest()
        self.reject("not a pending request")

    def test_manifest_duplicate_citation_digest_rejected(self):
        self.manifest["citations"].append(copy.deepcopy(self.manifest["citations"][0]))
        self.manifest["counts"]["citation_requests"] = 3
        self.refresh_manifest()
        self.reject("uniqueness")

    def test_manifest_group_inventory_drift_rejected(self):
        self.manifest["counts"]["shared_url_packets"] = 12
        self.refresh_manifest()
        self.reject("changed citation/group inventory")

    def test_stale_response_manifest_digest_rejected(self):
        self.bundle["manifest_sha256"] = "f" * 64
        self.reject("stale/wrong")

    def test_unknown_response_field_rejected(self):
        self.add_cite()["approved"] = True
        self.reject("unknown/missing fields")

    def test_missing_response_field_rejected(self):
        self.add_cite().pop("reading_limits")
        self.reject("unknown/missing fields")

    def test_unknown_top_level_field_rejected(self):
        self.bundle["may_publish"] = True
        self.reject("unknown/missing fields")

    def test_unexpected_schema_rejected(self):
        self.bundle["schema_version"] = 2
        self.reject("stale/wrong")

    def test_unknown_citation_digest_rejected(self):
        self.add_cite()["review_request_sha256"] = "f" * 64
        self.reject("stale/unknown/duplicate")

    def test_duplicate_citation_response_rejected(self):
        self.add_cite()
        self.bundle["citation_responses"].append(self.citation())
        self.reject("stale/unknown/duplicate")

    def test_unknown_packet_digest_rejected(self):
        self.add_group()["packet_sha256"] = "f" * 64
        self.reject("stale/unknown/duplicate")

    def test_duplicate_packet_response_rejected(self):
        self.add_group()
        self.bundle["shared_url_responses"].append(self.group())
        self.reject("stale/unknown/duplicate")

    def test_future_review_date_rejected(self):
        self.add_cite()["reviewed_on"] = "2027-01-01"
        self.reject("future review date")

    def test_impossible_review_date_rejected(self):
        self.add_cite()["reviewed_on"] = "2026-02-30"
        self.reject("impossible calendar")

    def test_bad_review_date_format_rejected(self):
        self.add_cite()["reviewed_on"] = "10/29/2026"
        self.reject("expected ISO")

    def test_blank_reviewer_rejected(self):
        self.add_cite()["reviewer"] = " "
        self.reject("missing or invalid")

    def test_blank_evidence_note_rejected(self):
        self.add_cite()["evidence_notes"] = "Short"
        self.reject("missing or invalid")

    def test_blank_reading_limit_rejected(self):
        self.add_cite()["reading_limits"] = " "
        self.reject("missing or invalid")

    def test_unknown_link_state_rejected(self):
        self.add_cite()["link_check"] = "VERIFIED_SAFE"
        self.reject("unsupported link/claim")

    def test_unknown_claim_state_rejected(self):
        self.add_cite()["claim_check"] = "SAFE_TO_PUBLISH"
        self.reject("unsupported link/claim")

    def test_link_claim_without_opening_rejected(self):
        c = self.add_cite()
        c.update(link_check="NOT_REACHABLE", observed_url=None, source_locator="")
        self.reject("inaccessible source cannot support")

    def test_fake_locator_on_unread_source_rejected(self):
        c = self.add_cite()
        c.update(link_check="NOT_REACHABLE", claim_check="NOT_CHECKED", observed_url=None)
        self.reject("cannot claim source/locator")

    def test_changed_url_without_redirect_rejected(self):
        self.add_cite()["observed_url"] = "https://example.test/other"
        self.reject("URL changed without redirect")

    def test_false_redirect_rejected(self):
        self.add_cite()["link_check"] = "REDIRECTED_SOURCE"
        self.reject("without changed URL")

    def test_http_url_rejected(self):
        self.add_cite()["observed_url"] = "http://example.test/a"
        self.reject("expected HTTPS")

    def test_userinfo_url_rejected(self):
        self.add_cite()["observed_url"] = "https://reviewer@example.test/a"
        self.reject("invalid HTTPS")

    def test_nonstandard_port_url_rejected(self):
        self.add_cite()["observed_url"] = "https://example.test:444/a"
        self.reject("invalid HTTPS")

    def test_url_whitespace_rejected(self):
        self.add_cite()["observed_url"] = "https://example.test/a\n"
        self.reject("expected HTTPS")

    def test_duplicate_risk_flag_rejected(self):
        self.add_cite()["risk_flags"] = ["WATER", "WATER"]
        self.reject("invalid risk flags")

    def test_unknown_risk_flag_rejected(self):
        self.add_cite()["risk_flags"] = ["APPROVED"]
        self.reject("invalid risk flags")

    def test_group_url_swapped_rejected(self):
        self.add_group()["url"] = "https://example.test/b"
        self.reject("source URL differs")

    def test_group_extra_field_rejected(self):
        self.add_group()["safety_approved"] = True
        self.reject("unknown/missing fields")

    def test_group_missing_physical_row_rejected(self):
        self.add_group()["row_reviews"].pop()
        self.reject("physical source rows")

    def test_group_extra_physical_row_rejected(self):
        g = self.add_group()
        g["row_reviews"].append({**g["row_reviews"][0], "source_row_key": "extra:4:fake"})
        self.reject("physical source rows")

    def test_group_duplicate_physical_row_rejected(self):
        g = self.add_group()
        g["row_reviews"].append(copy.deepcopy(g["row_reviews"][0]))
        self.reject("duplicate physical source row")

    def test_group_unread_row_cannot_claim_consistency(self):
        g = self.add_group()
        g["row_reviews"][0].update(reading_status="NOT_INSPECTED", source_locator="")
        self.reject("cannot claim consistent")

    def test_group_unread_row_cannot_have_locator(self):
        g = self.add_group()
        g["relationship"] = "UNRESOLVED"
        g["row_reviews"][0]["reading_status"] = "NOT_INSPECTED"
        self.reject("cannot claim locator")

    def test_group_invalid_row_status_rejected(self):
        self.add_group()["row_reviews"][0]["reading_status"] = "AUTO_APPROVED"
        self.reject("invalid reading status")

    def test_group_invalid_relation_rejected(self):
        self.add_group()["relationship"] = "RESOLVED_NO_REVIEW"
        self.reject("invalid source-scope relation")

    def test_group_blank_comparison_note_rejected(self):
        self.add_group()["comparison_notes"] = "short"
        self.reject("missing or invalid")

    def test_group_future_date_rejected(self):
        self.add_group()["reviewed_on"] = "2030-01-01"
        self.reject("future review date")

    def test_load_response_valid_json(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "responses.json"
            p.write_text(json.dumps(self.bundle), encoding="utf-8")
            self.assertEqual(intake.load_response_file(p), self.bundle)

    def test_load_response_duplicate_key_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "responses.json"
            p.write_text('{"schema_version":1,"schema_version":2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate object key"):
                intake.load_response_file(p)

    def test_load_response_nan_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "responses.json"
            p.write_text('{"schema_version": NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid number"):
                intake.load_response_file(p)

    def test_load_response_invalid_utf8_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "responses.json"
            p.write_bytes(b"\xff\xfe")
            with self.assertRaisesRegex(ValueError, "malformed UTF-8"):
                intake.load_response_file(p)

    def test_load_response_oversize_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "responses.json"
            p.write_bytes(b"x" * 50)
            with self.assertRaisesRegex(ValueError, "size limit"):
                intake.load_response_file(p, max_bytes=40)

    def test_load_response_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / "responses.json"
            p.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(p)
            with self.assertRaisesRegex(ValueError, "non-symlink"):
                intake.load_response_file(link)

    def test_load_response_non_json_scalar_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "responses.json"
            p.write_text('"hello"', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON object required"):
                intake.load_response_file(p)

    def test_reviewer_identity_never_marked_authenticated(self):
        self.add_cite()
        self.add_group()
        output = json.dumps(self.report())
        self.assertNotIn('"reviewer_identity_authenticated": true', output)
        self.assertNotIn('"crosswalk_review_state_changed": true', output)
        self.assertNotIn('"safety_approved": true', output)

    def test_empty_template_is_digest_bound(self):
        template = intake.empty_response_template(self.manifest)
        self.assertEqual(template["manifest_sha256"], self.manifest["manifest_sha256"])
        self.assertEqual(template["citation_responses"], [])
        self.assertEqual(template["shared_url_responses"], [])
        self.assertEqual(intake.audit(self.manifest, template, today=TODAY)["release_state"], "HOLD")

    def test_empty_template_rejects_drifted_manifest(self):
        self.manifest["may_publish"] = True
        with self.assertRaisesRegex(ValueError, "release/HOLD"):
            intake.empty_response_template(self.manifest)

    def test_no_network_or_output_files(self):
        with tempfile.TemporaryDirectory() as td:
            before = set(Path(td).iterdir())
            self.add_cite()
            self.add_group()
            self.report()
            self.assertEqual(set(Path(td).iterdir()), before)


if __name__ == "__main__":
    unittest.main()
