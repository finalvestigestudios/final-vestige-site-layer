"""R109 six-EXE Windows11 manual evidence security contracts; synthetic only."""
import copy
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

MOD = Path(__file__).resolve().parents[1] / "scripts" / "windows11_manual_acceptance_r109.py"
spec = importlib.util.spec_from_file_location("windows11_manual_acceptance_r109", MOD)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)
DIGEST = lambda b: hashlib.sha256(b).hexdigest()
CURRENT = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


def fixture():
    hashes = {name: DIGEST(name.encode()) for name in qa.ALL}
    report = {"schema": 1, "status": "windows_smoke_passed",
              "windows_executables_verified": True, "smoke_simulated": False,
              "release_authorized": False, "premium_entitlement_verified": False,
              "checksums_sha256": DIGEST(b"real inventory"),
              "artifacts": [{"name": name, "sha256": hashes[name], "pe_machine": "AMD64",
                             "smoke": "passed", "seconds": 0.15} for name in qa.ALL]}
    raw = json.dumps(report).encode()
    return report, hashes, raw


class ManualR109(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.report, self.hashes, self.raw = fixture()
        self.template = qa.make_template(self.report, self.hashes, self.raw)
        self.review = copy.deepcopy(self.template)
        self.review.update(reviewer_id="internal-QA1", windows11_build=26100,
                           observed_utc="2026-11-01T12:00:00Z")

    def fill_witnesses(self):
        for app in qa.ALL:
            for check in qa._checks(app):
                data = ("INTERNAL SYNTHETIC QA WITNESS for " + app + " check " + check +
                        "; not a real human review. Do not distribute.\n").encode()
                filename = app.removesuffix(".exe") + "--" + check + ".txt"
                (self.dir / filename).write_bytes(data)
                self.review["apps"][app]["checks"][check] = {
                    "state": "PASS", "witness_sha256": DIGEST(data)}

    def verify(self):
        return qa.validate_review(self.review, self.template, self.dir, now=CURRENT)

    def test_canonical_six_product_inventory(self):
        self.assertEqual(len(qa.ALL), 6)
        self.assertEqual(len(qa.FREE), 4)
        self.assertEqual(len(qa.PREMIUM), 2)
        self.assertEqual(sum(len(qa._checks(p)) for p in qa.ALL), 46)

    def test_r9_six_smoke_records_match(self):
        self.assertEqual(qa.verify_r9(self.report, self.hashes), self.hashes)

    def test_template_is_pending_and_release_denied(self):
        self.assertEqual(self.template["purpose"], qa.PURPOSE)
        self.assertFalse(any(x["state"] != "NOT_RUN" for p in qa.ALL
                             for x in self.template["apps"][p]["checks"].values()))
        self.assertNotIn("release_authorized", self.template)

    def test_pending_stays_hold_without_witnesses(self):
        result = self.verify()
        self.assertEqual(result["counts"], {"PASS": 0, "FAIL": 0, "NOT_RUN": 46})
        self.assertEqual(result["status"], "REVIEW_HOLD_INCOMPLETE_OR_FAILED")
        self.assertIs(result["release_authorized"], False)

    def test_all_synthetic_witnesses_count_but_do_not_authorize_release(self):
        self.fill_witnesses()
        result = self.verify()
        self.assertEqual(result["counts"], {"PASS": 46, "FAIL": 0, "NOT_RUN": 0})
        self.assertEqual(result["status"], "MANUAL_MATRIX_COMPLETE_UNCERTIFIED")
        self.assertIs(result["release_authorized"], False)
        self.assertIs(result["premium_editor_licensed"], False)

    def test_failed_manual_check_is_hold(self):
        self.fill_witnesses()
        self.review["apps"][qa.PREMIUM[1]]["checks"][qa.PREMIUM_CHECKS[0]]["state"] = "FAIL"
        result = self.verify()
        self.assertEqual(result["counts"]["FAIL"], 1)
        self.assertEqual(result["status"], "REVIEW_HOLD_INCOMPLETE_OR_FAILED")

    def test_missing_witness_refused(self):
        self.fill_witnesses()
        (self.dir / (qa.FREE[0].removesuffix(".exe") + "--" + qa.FREE_CHECKS[0] + ".txt")).unlink()
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_witness_change_refused(self):
        self.fill_witnesses()
        name = qa.FREE[0].removesuffix(".exe") + "--" + qa.FREE_CHECKS[0] + ".txt"
        (self.dir / name).write_bytes(b"x" * 150)
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_symlink_witness_refused(self):
        self.fill_witnesses()
        name = qa.FREE[0].removesuffix(".exe") + "--" + qa.FREE_CHECKS[0] + ".txt"
        link = self.dir / name
        target = self.dir / "target"
        target.write_bytes(link.read_bytes())
        link.unlink()
        try: link.symlink_to(target)
        except (OSError, NotImplementedError): self.skipTest("symlink unavailable")
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_hardlink_witness_refused(self):
        self.fill_witnesses()
        name = qa.FREE[0].removesuffix(".exe") + "--" + qa.FREE_CHECKS[0] + ".txt"
        original = self.dir / name
        link = self.dir / "hardlink"
        try: link.hardlink_to(original)
        except OSError: self.skipTest("hardlink unavailable")
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_extra_product_refused(self):
        self.review["apps"]["unknown.exe"] = {}
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_missing_premium_refused(self):
        del self.review["apps"][qa.PREMIUM[0]]
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_candidate_hash_substitution_refused(self):
        self.review["apps"][qa.FREE[0]]["candidate_sha256"] = "a"*64
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_r9_source_drift_refused(self):
        self.review["r9_report_sha256"] = "a"*64
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_r9_duplicate_candidate_refused(self):
        self.report["artifacts"][0] = copy.deepcopy(self.report["artifacts"][1])
        with self.assertRaises(qa.ReviewHold): qa.verify_r9(self.report, self.hashes)

    def test_r9_simulated_smoke_refused(self):
        self.report["smoke_simulated"] = True
        with self.assertRaises(qa.ReviewHold): qa.verify_r9(self.report, self.hashes)

    def test_r9_missing_real_smoke_refused(self):
        self.report["artifacts"][0]["smoke"] = "simulated"
        with self.assertRaises(qa.ReviewHold): qa.verify_r9(self.report, self.hashes)

    def test_r9_premium_claim_refused(self):
        self.report["premium_entitlement_verified"] = True
        with self.assertRaises(qa.ReviewHold): qa.verify_r9(self.report, self.hashes)

    def test_r9_wrong_sha_refused(self):
        self.report["artifacts"][0]["sha256"] = "f"*64
        with self.assertRaises(qa.ReviewHold): qa.verify_r9(self.report, self.hashes)

    def test_r9_bool_type_second_refused(self):
        self.report["artifacts"][0]["seconds"] = True
        with self.assertRaises(qa.ReviewHold): qa.verify_r9(self.report, self.hashes)

    def test_windows_server_build_refused(self):
        self.review["windows11_build"] = 20348
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_bool_build_refused(self):
        self.review["windows11_build"] = True
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_unidentified_reviewer_refused(self):
        self.review["reviewer_id"] = ""
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_stale_observation_refused(self):
        self.review["observed_utc"] = "2026-08-01T00:00:00Z"
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_future_observation_refused(self):
        self.review["observed_utc"] = "2027-11-01T00:00:00Z"
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_unrecognized_check_refused(self):
        self.review["apps"][qa.FREE[0]]["checks"]["paid_editor_enabled"] = {}
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_truthy_state_refused(self):
        self.review["apps"][qa.FREE[0]]["checks"][qa.FREE_CHECKS[0]]["state"] = ["PASS"]
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_claimed_pass_without_witness_refused(self):
        self.review["apps"][qa.FREE[0]]["checks"][qa.FREE_CHECKS[0]]["state"] = "PASS"
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_unperformed_check_with_witness_refused(self):
        self.review["apps"][qa.FREE[0]]["checks"][qa.FREE_CHECKS[0]]["witness_sha256"] = "a"*64
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_native_review_rejects_non_windows_host(self):
        with patch.object(qa.os, "name", "posix"):
            with self.assertRaises(qa.ReviewHold): qa.native_win11_build()

    def test_native_review_rejects_server_product_type(self):
        class Server:
            major = 10
            build = 26100
            product_type = 3
        with patch.object(qa.os, "name", "nt"), patch.object(qa.platform, "machine", return_value="AMD64"), patch.object(qa.sys, "getwindowsversion", create=True, return_value=Server()):
            with self.assertRaises(qa.ReviewHold): qa.native_win11_build()

    def test_native_review_requires_windows11_workstation(self):
        class Workstation:
            major = 10
            build = 26100
            product_type = 1
        with patch.object(qa.os, "name", "nt"), patch.object(qa.platform, "machine", return_value="AMD64"), patch.object(qa.sys, "getwindowsversion", create=True, return_value=Workstation()):
            self.assertEqual(qa.native_win11_build(), 26100)

    def test_duplicate_json_keys_refused(self):
        with self.assertRaises(qa.ReviewHold): qa._strict_json(b'{"schema":"a","schema":"b"}')

    def test_non_utf8_witness_refused(self):
        self.fill_witnesses()
        name = qa.FREE[0].removesuffix(".exe") + "--" + qa.FREE_CHECKS[0] + ".txt"
        data = b"\xff"*120
        (self.dir / name).write_bytes(data)
        self.review["apps"][qa.FREE[0]]["checks"][qa.FREE_CHECKS[0]]["witness_sha256"] = DIGEST(data)
        with self.assertRaises(qa.ReviewHold): self.verify()

    def test_no_assert_statements_in_admission_logic(self):
        import ast
        module = ast.parse(MOD.read_text())
        self.assertFalse(any(isinstance(node, ast.Assert) for node in ast.walk(module)))

    def test_privacy_safe_cli_error_with_invalid_candidate_path(self):
        candidate = self.dir / "private-customer-ledger.csv"
        errors = io.StringIO()
        with redirect_stderr(errors):
            value = qa.main(["template", "--dist", str(candidate), "--r9-report", str(candidate),
                             "--review", str(self.dir / "review.json")])
        self.assertEqual(value, 1)
        self.assertEqual(errors.getvalue().strip(), qa.ERROR)
        self.assertNotIn("customer", errors.getvalue())


if __name__ == "__main__": unittest.main()
