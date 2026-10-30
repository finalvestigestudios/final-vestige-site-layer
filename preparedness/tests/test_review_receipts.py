"""Synthetic-only release-HOLD review receipt tests; no live source or CMS operations."""
from __future__ import annotations

import copy
import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import source_review_queue as queue
import review_receipts as rr
from test_source_review_queue import fixture


class ReviewReceiptSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.lib, self.rows = fixture()
        self.queue = queue.build_review_queue(self.lib, rows=self.rows)
        self.fingerprints = {"first-aid-not-medical": "a" * 64}

    def build(self):
        return rr.build_manifest(self.queue, self.fingerprints)

    def refresh(self):
        self.queue["sha256_review_queue_payload"] = rr.digest({k: v for k, v in self.queue.items()
                                                                 if k != "sha256_review_queue_payload"})

    def broken(self, fragment: str):
        with self.assertRaisesRegex(ValueError, fragment):
            self.build()

    def test_two_source_citations_one_shared_review_group(self):
        x = self.build()
        self.assertEqual(x["counts"]["citation_requests"], 2)
        self.assertEqual(x["counts"]["shared_url_packets"], 1)

    def test_release_remains_hold_even_when_structural_checks_pass(self):
        x = self.build()
        self.assertEqual(x["release_state"], "HOLD")
        self.assertFalse(x["may_publish"])
        self.assertFalse(x["human_review_performed"])

    def test_every_receipt_remains_pending_and_unapproved(self):
        x = self.build()
        self.assertTrue(all(r["review_state"] == "PENDING_HUMAN" and r["approved"] is False for r in x["citations"]))
        self.assertTrue(all(r["review_state"] == "PENDING_HUMAN" and r["approved"] is False for r in x["shared_url_packets"]))

    def test_is_byte_for_byte_deterministic(self):
        self.assertEqual(self.build(), self.build())

    def test_manifest_digest_binds_all_review_requests(self):
        x = self.build()
        self.assertEqual(x["manifest_sha256"], rr.digest({k: v for k, v in x.items() if k != "manifest_sha256"}))

    def test_exact_source_queue_digest_copied(self):
        self.assertEqual(self.build()["source_queue_sha256"], self.queue["sha256_review_queue_payload"])

    def test_two_distinct_contributor_reading_scopes_preserved(self):
        x = self.build()["shared_url_packets"][0]
        self.assertEqual(x["all_source_row_keys"], ["base:0:same", "start:0:same"])
        self.assertEqual(x["cited_source_row_keys"], ["start:0:same"])
        self.assertEqual(x["uncited_source_row_keys"], ["base:0:same"])

    def test_citation_claim_scope_is_exact_not_truncated(self):
        x = self.build()["citations"][0]
        self.assertEqual(x["article_claim_scope"], self.queue["citations"][0]["author_claim_scope"] if x["source_id"] == self.queue["citations"][0]["source_id"] else next(c["author_claim_scope"] for c in self.queue["citations"] if c["source_id"] == x["source_id"]))

    def test_changed_article_body_digest_invalidates_review_request(self):
        before = [c["review_request_sha256"] for c in self.build()["citations"]]
        self.fingerprints["first-aid-not-medical"] = "b" * 64
        self.assertNotEqual(before, [c["review_request_sha256"] for c in self.build()["citations"]])

    def test_changed_reader_scope_invalidates_review_request(self):
        before = [c["review_request_sha256"] for c in self.build()["citations"]]
        self.queue["citations"][0]["author_claim_scope"] += " extra evidence checked"
        self.refresh()
        self.assertNotEqual(before, [c["review_request_sha256"] for c in self.build()["citations"]])

    def test_tampered_queue_fingerprint_fails(self):
        self.queue["citations"][0]["url"] = "https://example.test/evil"
        self.broken("fingerprint")

    def test_bad_queue_schema_fails(self):
        self.queue["schema_version"] = 2
        self.broken("release hold")

    def test_queue_marked_publishable_fails(self):
        self.queue["may_publish"] = True
        self.broken("release hold")

    def test_report_with_structural_errors_fails(self):
        self.queue["errors"].append("synthetic failed citation")
        self.broken("structural errors")

    def test_citation_count_loss_fails(self):
        self.queue["summary"]["article_source_citation_pairs"] = 1
        self.refresh()
        self.broken("citation count")

    def test_shared_url_group_loss_fails(self):
        self.queue["summary"]["shared_url_groups"] = 3
        self.refresh()
        self.broken("shared URL count")

    def test_missing_article_fingerprint_fails(self):
        self.fingerprints.clear()
        self.broken("fingerprints")

    def test_extra_article_fingerprint_fails(self):
        self.fingerprints["unrelated"] = "c" * 64
        self.broken("fingerprints")

    def test_uppercase_article_fingerprint_fails(self):
        self.fingerprints["first-aid-not-medical"] = "F" * 64
        self.broken("fingerprints")

    def test_invalid_article_fingerprint_length_fails(self):
        self.fingerprints["first-aid-not-medical"] = "a" * 63
        self.broken("fingerprints")

    def test_duplicate_article_citation_identity_fails(self):
        self.queue["citations"].append(copy.deepcopy(self.queue["citations"][0]))
        self.queue["summary"]["article_source_citation_pairs"] = 3
        self.refresh()
        self.broken("repeated article-to-source")

    def test_missing_article_specific_note_fails(self):
        self.queue["citations"][0]["author_claim_scope"] = "  "
        self.refresh()
        self.broken("no article-specific reading scope")

    def test_missing_contributor_claim_support_fails(self):
        self.queue["citations"][0]["contributor_claim_scope"] = ""
        self.refresh()
        self.broken("no contributor-specific claim")

    def test_unrelated_cluster_scope_fails(self):
        self.queue["citations"][0]["source_origin"] = "food"
        self.refresh()
        self.broken("borrowed another contributor")

    def test_shared_url_mislabel_fails(self):
        c = next(c for c in self.queue["citations"] if c["source_id"] == "same")
        c["shared_url_group"] = False
        self.refresh()
        self.broken("shared-URL flag")

    def test_shared_url_citation_wrong_physical_row_fails(self):
        c = next(c for c in self.queue["citations"] if c["source_id"] == "same")
        c["source_row_key"] = "other:40:fake"
        self.refresh()
        self.broken("distinct physical source row")

    def test_group_cited_record_count_must_match_citations(self):
        self.queue["collisions"][0]["cited_source_rows"] = ["base:0:same"]
        self.refresh()
        self.broken("cited contributor row inventory")

    def test_duplicate_group_url_fails(self):
        self.queue["collisions"].append(copy.deepcopy(self.queue["collisions"][0]))
        self.queue["summary"]["shared_url_groups"] = 2
        self.refresh()
        self.broken("duplicated shared source URL")

    def test_shared_group_duplicate_physical_key_fails(self):
        self.queue["collisions"][0]["source_row_keys"] = ["start:0:same", "start:0:same"]
        self.refresh()
        self.broken("distinct physical contributor")

    def test_unknown_shared_group_review_state_fails(self):
        self.queue["collisions"][0]["review_status"] = "auto-approved"
        self.refresh()
        self.broken("unknown shared source review state")

    def test_published_article_rejected_despite_source_checks(self):
        self.queue["citations"][0]["status"] = "published"
        self.refresh()
        self.broken("publication status changed")

    def test_previous_human_flag_never_auto_approves(self):
        self.queue["citations"][0]["human_link_checked"] = True
        self.refresh()
        x = self.build()["citations"]
        self.assertTrue(any(c["human_link_checked_prior"] for c in x))
        self.assertTrue(all(c["approved"] is False for c in x))

    def test_csv_has_all_citations_plus_header(self):
        rows = list(csv.reader(io.StringIO(rr.citation_csv(self.build()))))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][0], "review_request_sha256")

    def test_csv_formula_attack_equals_escaped(self):
        self.assertEqual(rr.safe_csv_cell("=SUM(1,2)"), "'=SUM(1,2)")

    def test_csv_formula_attack_plus_escaped(self):
        self.assertEqual(rr.safe_csv_cell("+cmd"), "'+cmd")

    def test_csv_formula_attack_leading_whitespace_escaped(self):
        self.assertEqual(rr.safe_csv_cell("  @HYPERLINK(...)"), "'  @HYPERLINK(...)")

    def test_csv_preserves_multiline_and_unicode(self):
        self.queue["citations"][0]["author_claim_scope"] = "Line one\nNew café context"
        self.refresh()
        content = rr.citation_csv(self.build())
        self.assertIn("New café context", content)
        self.assertEqual(len(list(csv.reader(io.StringIO(content)))), 3)

    def test_output_guard_allows_only_private_build_subdir(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "preparedness"
            output = root / "build" / "review-packets"
            self.assertEqual(rr.guarded_output_dir(output, root), output)

    def test_output_guard_rejects_overwrite_of_article_source_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "preparedness"
            with self.assertRaisesRegex(ValueError, "build directory"):
                rr.guarded_output_dir(root / "sources", root)

    def test_output_guard_rejects_parent_escape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "preparedness"
            with self.assertRaisesRegex(ValueError, "build directory"):
                rr.guarded_output_dir(root / "build" / ".." / "content", root)

    def test_output_guard_rejects_symlinked_build_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "preparedness"
            root.mkdir()
            (root / "build").symlink_to(Path(td), target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                rr.guarded_output_dir(root / "build" / "export", root)

    def test_source_row_scope_limits_preserved_in_packet(self):
        x = self.build()["shared_url_packets"][0]["citations"][0]
        self.assertIn("Only start excerpts were read", x["contributor_reading_limits"])

    def test_manifests_do_not_hold_human_names_or_proclaimed_approval(self):
        x = self.build()
        txt = json.dumps(x)
        self.assertNotIn('"reviewed_by"', txt)
        self.assertNotIn('"approved": true', txt)
        self.assertNotIn('"may_publish": true', txt)

    def test_reordered_citations_still_have_same_request_digests(self):
        first = {c["source_id"]: c["review_request_sha256"] for c in self.build()["citations"]}
        self.queue["citations"].reverse()
        self.refresh()
        later = {c["source_id"]: c["review_request_sha256"] for c in self.build()["citations"]}
        self.assertEqual(first, later)


if __name__ == "__main__":
    unittest.main()
