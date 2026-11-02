"""R68: exact source provenance + fail-closed review, independent of delivery."""
import importlib.util
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DIR = REPO / "dispatch" / "campaign-2026-mind" / "r68-origin-lock"
SPEC = importlib.util.spec_from_file_location("r68_provenance", DIR / "provenance.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
M = MOD.load_manifest()


class ProvenanceLock(unittest.TestCase):
    def test_six_unique_ids(self):
        self.assertEqual([e["id"] for e in M["editions"]], list(range(1, 7)))

    def test_exact_master_pr(self):
        self.assertEqual(M["original_master_pr"], 175)

    def test_exact_baseline_sha(self):
        self.assertEqual(M["original_master_commit"], "d57ccdba3aee8f065e143e101c2945f4f3d01647")

    def test_exact_stacked_sha(self):
        self.assertEqual(M["observed_stack_commit"], "24f559911e875155efbaa450c6e79709491c4880")

    def test_six_blobs_changed(self):
        self.assertTrue(all(e["original_blob"] != e["stacked_blob"] for e in M["editions"]))

    def test_only_one_subject_changed(self):
        changed = [e["id"] for e in M["editions"] if e["original_subject"] != e["stacked_subject"]]
        self.assertEqual(changed, [4])

    def test_provenance_blob_hasher(self):
        self.assertEqual(MOD.blob_sha(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")

    def test_blob_sha_is_length_sensitive(self):
        self.assertNotEqual(MOD.blob_sha(b"a"), MOD.blob_sha(b"a\n"))

    def test_all_sha_strings_wellformed(self):
        for e in M["editions"]:
            with self.subTest(id=e["id"]):
                self.assertRegex(e["original_blob"], r"^[a-f0-9]{40}$")
                self.assertRegex(e["stacked_blob"], r"^[a-f0-9]{40}$")

    def test_all_current_source_files_match_git_hash(self):
        result = MOD.audit()
        self.assertEqual(result["integrity_check"], "PASS", result)

    def test_all_six_source_drift(self):
        self.assertEqual(MOD.audit()["origin_drift_count"], 6)

    def test_one_subject_drift(self):
        self.assertEqual(MOD.audit()["subject_drift_count"], 1)

    def test_every_issue_release_hold(self):
        self.assertTrue(all(x["release"].startswith("HOLD_UNSENT") for x in MOD.audit()["editions"]))

    def test_two_merchant_holds(self):
        self.assertEqual([x["id"] for x in MOD.audit()["editions"] if "HOLD_MERCHANT" in x["release"]], [3, 5])

    def test_permissions_all_false(self):
        self.assertTrue(M["approvals"])
        self.assertTrue(all(v is False for v in M["approvals"].values()))

    def test_final_sha_no_approvals(self):
        self.assertTrue(all(e["founder_approved_final_sha"] is None for e in M["editions"]))

    def test_no_activation_urls(self):
        self.assertTrue(all(x is None for x in M["offer_links"].values()))

    def test_no_metrics(self):
        self.assertIsNone(M["actual_results"])
        self.assertFalse(M["tracking_enabled"])

    def test_subscriber_data_absent(self):
        self.assertFalse(M["subscriber_personal_data_included"])

    def test_real_welcome_not_proven(self):
        self.assertTrue(M["live_source_of_truth"]["welcome_fieldbook_configured"])
        self.assertFalse(M["live_source_of_truth"]["welcome_received_verified"])

    def test_nonadditive_counts_preserved(self):
        s = M["live_source_of_truth"]
        self.assertEqual((s["subscribers_total"], s["subscribers_confirmed"], s["subscribers_unconfirmed"]), (2, 2, 2))
        self.assertIsNone(s["eligible_reachable_count"])

    def test_canonical_source_edit_detected(self):
        e = M["editions"][0]
        b = (REPO / e["path"]).read_bytes()
        report = MOD.audit(override={e["path"]: b + b"\nUNREVIEWED UPDATE\n"})
        self.assertEqual(report["integrity_check"], "FAIL")
        self.assertIn("SOURCE_BLOB_CHANGED", report["editions"][0]["problems"])
        self.assertEqual(report["launch_decision"], "HOLD_UNSENT")

    def test_subject_mutation_detected(self):
        e = M["editions"][3]
        b = (REPO / e["path"]).read_bytes()
        b = b.replace(e["stacked_subject"].encode(), b"An inaccurate new subject")
        report = MOD.audit(override={e["path"]: b})
        self.assertIn("SUBJECT_MISMATCH", report["editions"][3]["problems"])

    def test_address_placeholder_cannot_disappear_silently(self):
        e = M["editions"][0]
        b = (REPO / e["path"]).read_bytes().replace(b"[[VALID_POSTAL_ADDRESS_REQUIRED]]", b"REDACTED")
        report = MOD.audit(override={e["path"]: b})
        self.assertIn("LEGAL_ADDRESS_HOLD_REMOVED", report["editions"][0]["problems"])

    def test_unsubscribe_placeholder_cannot_disappear_silently(self):
        e = M["editions"][0]
        b = (REPO / e["path"]).read_bytes().replace(
            b"[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", b"REDACTED")
        report = MOD.audit(override={e["path"]: b})
        self.assertIn("UNSUBSCRIBE_HOLD_REMOVED", report["editions"][0]["problems"])

    def test_merchant_placeholder_guard(self):
        e = M["editions"][2]
        b = (REPO / e["path"]).read_bytes().replace(
            b"[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]", b"redacted")
        report = MOD.audit(override={e["path"]: b})
        self.assertIn("MERCHANT_GATE_OR_DISCLOSURE_REMOVED", report["editions"][2]["problems"])

    def test_report_never_claims_ready_to_send(self):
        self.assertEqual(MOD.audit()["launch_decision"], "HOLD_UNSENT")

    def test_report_cannot_leak_pii(self):
        raw = json.dumps(MOD.audit()).lower()
        self.assertNotIn("@", raw)
        self.assertNotIn("mailto:", raw)

    def test_review_html_no_active_commercial_ui(self):
        html = (DIR / "review.html").read_text(encoding="utf-8").lower()
        self.assertNotRegex(html, r"<(?:script|form|iframe|img|button)\b")
        self.assertNotIn("zen12.com", html)
        self.assertNotIn("hypnosislive.com", html)

    def test_review_html_accessibility(self):
        html = (DIR / "review.html").read_text(encoding="utf-8").lower()
        self.assertIn('lang="en"', html)
        self.assertIn('href="#main"', html)
        self.assertIn("<caption>", html)
        self.assertIn('scope="col"', html)
        self.assertIn("prefers-reduced-motion", html)

    def test_no_live_wordpress_mutation(self):
        self.assertFalse(M["live_source_of_truth"]["wordpress_mutated_this_sprint"])

    def test_manifest_not_misstate_lifetime_zero(self):
        self.assertIsNone(M["live_source_of_truth"]["historical_send_total"])

    def test_all_previews_hold_marker(self):
        for path in ["README.md", "review.html", "review.txt"]:
            with self.subTest(path=path):
                self.assertIn("HOLD_UNSENT", (DIR / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
