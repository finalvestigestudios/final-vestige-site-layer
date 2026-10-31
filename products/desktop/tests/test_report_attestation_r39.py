"""R39: independent read-only inventory/report consistency, with synthetic stubs."""
from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

import report_attestation as att


class ReleaseReportAttestationR39Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r39-attest-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.dist = self.base / "dist"
        self.dist.mkdir()
        self.proof_dir = self.base / "proofs"
        self.proof_dir.mkdir()
        self.report = self.proof_dir / "capture.json"
        self.current = {
            "checksums_sha256": "b" * 64,
            "artifacts": [
                {"name": name, "sha256": f"{index + 1:x}" * 64,
                 "pe_machine": "AMD64", "smoke": "not_run"}
                for index, name in enumerate(att.gate.EXPECTED)
            ],
        }
        self.data = {
            "schema": 1, "status": "integrity_only", "release_authorized": False,
            "premium_entitlement_verified": False, "codesigning_verified": False,
            "malware_scan_verified": False, "windows_executables_verified": False,
            "smoke_simulated": False, "verified_utc": "2026-10-29T15:01:02+00:00",
            "checksums_sha256": self.current["checksums_sha256"],
            "artifacts": copy.deepcopy(self.current["artifacts"]),
        }
        self.write()

    def write(self, data=None):
        payload = json.dumps(self.data if data is None else data, sort_keys=True) + "\n"
        self.report.write_bytes(payload.encode("utf-8"))
        return hashlib.sha256(self.report.read_bytes()).hexdigest()

    def check(self, pin=None):
        with patch.object(att.gate, "verify", return_value=self.current) as gate_verify:
            result = att.verify_report(self.report, self.dist, expected_report_sha256=pin)
        gate_verify.assert_called_once_with(self.dist, smoke=False)
        return result

    def test_unpinned_consistency_does_not_authorize(self):
        result = self.check()
        self.assertEqual(result["candidate_consistency"], "PASS")
        self.assertEqual(result["evidence_pin"], "UNPINNED")
        self.assertFalse(result["historical_smoke_proven"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["premium_entitlement_verified"])

    def test_retained_pin_consistency(self):
        self.assertEqual(self.check(self.write())["evidence_pin"], "PINNED")

    def test_edited_evidence_breaks_independent_pin(self):
        original = self.write()
        self.data["verified_utc"] = "2026-10-29T15:01:03+00:00"
        self.write()
        with self.assertRaisesRegex(att.ReportAttestationError, "fingerprint mismatch"):
            self.check(original)

    def test_unpinned_report_can_be_rewritten_without_proving_authenticity(self):
        self.data["verified_utc"] = "2026-10-29T15:01:03+00:00"
        self.write()
        self.assertEqual(self.check()["evidence_pin"], "UNPINNED")

    def test_historical_smoke_fields_are_never_independently_attested(self):
        self.data["status"] = "windows_smoke_passed"
        self.data["windows_executables_verified"] = True
        for item in self.data["artifacts"]:
            item["smoke"] = "passed"
            item["seconds"] = 0.125
        self.write()
        self.assertFalse(self.check(self.write())["historical_smoke_proven"])

    def test_rejects_claim_of_release_approval_or_entitlement(self):
        for name in ("release_authorized", "premium_entitlement_verified",
                     "codesigning_verified", "malware_scan_verified"):
            with self.subTest(name=name):
                self.data[name] = True
                self.write()
                with self.assertRaisesRegex(att.ReportAttestationError, "falsely declares"):
                    self.check()
                self.data[name] = False

    def test_rejects_false_approval_as_strings_or_zero(self):
        for item in ("false", 0, None):
            self.data["release_authorized"] = item
            self.write()
            with self.assertRaises(att.ReportAttestationError):
                self.check()

    def test_rejects_wrong_or_extra_schema_keys(self):
        for mutation in ({"unexpected": True}, {"artifacts": None}, {"status": "ready"}):
            with self.subTest(mutation=mutation):
                d = copy.deepcopy(self.data)
                d.update(mutation)
                self.write(d)
                with self.assertRaises(att.ReportAttestationError):
                    self.check()

    def test_rejects_duplicate_json_keys(self):
        self.report.write_bytes(b'{"schema":1,"schema":1}')
        with self.assertRaisesRegex(att.ReportAttestationError, "Duplicate JSON"):
            self.check()

    def test_rejects_nonfinite_constants(self):
        self.report.write_bytes(b'{"foo": NaN}')
        with self.assertRaisesRegex(att.ReportAttestationError, "Nonfinite"):
            self.check()

    def test_rejects_invalid_utf8_and_malformed_json(self):
        for payload in (b'\xff', b'{"schema"', b'[]'):
            self.report.write_bytes(payload)
            with self.subTest(payload=payload), self.assertRaises(att.ReportAttestationError):
                self.check()

    def test_rejects_invalid_timestamp(self):
        for stamp in ("2026-02-30T10:00:00+00:00", "2026-10-29T15:01:02Z",
                      "2026-10-29T15:01:02-07:00", "2026-10-29 15:01:02+00:00"):
            self.data["verified_utc"] = stamp
            self.write()
            with self.subTest(stamp=stamp), self.assertRaises(att.ReportAttestationError):
                self.check()

    def test_rejects_invalid_checksum_hash(self):
        self.data["checksums_sha256"] = "B" * 64
        self.write()
        with self.assertRaises(att.ReportAttestationError):
            self.check()

    def test_rejects_missing_swapped_or_duplicate_artifacts(self):
        for transform in (
            lambda a: a[:-1],
            lambda a: list(reversed(a)),
            lambda a: a[:-1] + [a[0]],
        ):
            d = copy.deepcopy(self.data)
            d["artifacts"] = transform(d["artifacts"])
            self.write(d)
            with self.assertRaises(att.ReportAttestationError):
                self.check()

    def test_rejects_artifact_with_extra_fields_or_wrong_arch(self):
        for mutate in (lambda a: a.update(path="sensitive.csv"),
                       lambda a: a.update(pe_machine="x86"),
                       lambda a: a.update(sha256="Z" * 64)):
            d = copy.deepcopy(self.data)
            mutate(d["artifacts"][0])
            self.write(d)
            with self.assertRaises(att.ReportAttestationError):
                self.check()

    def test_rejects_forged_smoke_states(self):
        self.data["artifacts"][0]["smoke"] = "passed"
        self.write()
        with self.assertRaisesRegex(att.ReportAttestationError, "smoke"):
            self.check()

    def test_rejects_nonfinite_negative_and_bool_smoke_durations(self):
        self.data["status"] = "windows_smoke_passed"
        self.data["windows_executables_verified"] = True
        for item in self.data["artifacts"]:
            item["smoke"] = "passed"
            item["seconds"] = 0.01
        for seconds in (float("inf"), -1, True, "1.0"):
            self.data["artifacts"][0]["seconds"] = seconds
            self.write()
            with self.subTest(seconds=seconds), self.assertRaises(att.ReportAttestationError):
                self.check()

    def test_rejects_synthetic_runner_report_as_native_evidence(self):
        self.data["status"] = "synthetic_smoke_only"
        self.data["smoke_simulated"] = True
        for item in self.data["artifacts"]:
            item["smoke"] = "simulated"
            item["seconds"] = 0.01
        self.write()
        with self.assertRaisesRegex(att.ReportAttestationError, "synthetic"):
            self.check()

    def test_rejects_forged_native_verified_flag_on_integrity_report(self):
        self.data["windows_executables_verified"] = True
        self.write()
        with self.assertRaisesRegex(att.ReportAttestationError, "provenance"):
            self.check()

    def test_rejects_missing_native_verified_flag_on_windows_smoke(self):
        self.data["status"] = "windows_smoke_passed"
        for item in self.data["artifacts"]:
            item["smoke"] = "passed"
            item["seconds"] = 0.01
        self.write()
        with self.assertRaisesRegex(att.ReportAttestationError, "provenance"):
            self.check()

    def test_rejects_spurious_simulated_flag_on_integrity_report(self):
        self.data["smoke_simulated"] = True
        self.write()
        with self.assertRaisesRegex(att.ReportAttestationError, "provenance"):
            self.check()

    def test_rejects_nonstrict_provenance_flag_types(self):
        for key in ("smoke_simulated", "windows_executables_verified"):
            for invalid in ("false", 0, None):
                with self.subTest(key=key, invalid=invalid):
                    candidate = copy.deepcopy(self.data)
                    candidate[key] = invalid
                    self.write(candidate)
                    with self.assertRaises(att.ReportAttestationError):
                        self.check()

    def test_rejects_missing_provenance_field(self):
        for key in ("smoke_simulated", "windows_executables_verified"):
            candidate = copy.deepcopy(self.data)
            candidate.pop(key)
            self.write(candidate)
            with self.subTest(key=key), self.assertRaisesRegex(
                    att.ReportAttestationError, "schema"):
                self.check()

    def test_inventory_mismatch_fails(self):
        self.current["checksums_sha256"] = "d" * 64
        with self.assertRaisesRegex(att.ReportAttestationError, "inventory changed"):
            self.check()

    def test_candidate_image_digest_mismatch_fails(self):
        self.current["artifacts"][3]["sha256"] = "e" * 64
        with self.assertRaisesRegex(att.ReportAttestationError, "image changed"):
            self.check()

    def test_underlying_gate_fails_closed(self):
        with patch.object(att.gate, "verify", side_effect=att.gate.GateFailure("/secret")):
            with self.assertRaises(att.ReportAttestationError) as ctx:
                att.verify_report(self.report, self.dist)
        self.assertNotIn("/secret", str(ctx.exception))

    def test_rejects_symlinked_report(self):
        actual = self.proof_dir / "real.json"
        self.report.rename(actual)
        try:
            self.report.symlink_to(actual)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not available")
        with self.assertRaises(att.ReportAttestationError):
            self.check()

    def test_rejects_hardlink_alias(self):
        try:
            os.link(self.report, self.proof_dir / "alias.json")
        except (OSError, NotImplementedError):
            self.skipTest("Hardlinks not available")
        with self.assertRaises(att.ReportAttestationError):
            self.check()

    def test_rejects_report_inside_dist_or_nested_dist(self):
        nested = self.dist / "nested"
        nested.mkdir()
        for path in (self.dist / "proof.json", nested / "proof.json"):
            path.write_bytes(self.report.read_bytes())
            with self.subTest(path=path), self.assertRaisesRegex(att.ReportAttestationError, "inside"):
                with patch.object(att.gate, "verify", return_value=self.current):
                    att.verify_report(path, self.dist)

    def test_rejects_oversized_or_zero_report(self):
        for payload in (b"", b"x" * (att.MAX_REPORT_BYTES + 1)):
            self.report.write_bytes(payload)
            with self.subTest(length=len(payload)), self.assertRaises(att.ReportAttestationError):
                self.check()

    def test_rejects_invalid_independent_pin_without_reading_evidence(self):
        with patch.object(att, "_read_verified_report") as read:
            for token in ("A"*64, "0"*63, "../../a", 5):
                with self.assertRaises(att.ReportAttestationError):
                    att.verify_report(self.report, self.dist,
                                      expected_report_sha256=token)
            read.assert_not_called()

    def test_reports_are_not_modified_by_verification(self):
        initial = self.report.read_bytes()
        self.check(self.write())
        self.assertEqual(self.report.read_bytes(), initial)
        self.assertEqual(list(self.proof_dir.iterdir()), [self.report])

    def test_cli_sanitizes_invalid_evidence(self):
        self.report.write_text("/private/account/creds", encoding="utf-8")
        stderr = io.StringIO()
        with redirect_stderr(stderr), patch.object(att.gate, "verify") as verifier:
            self.assertEqual(att.main([str(self.report), str(self.dist)]), 1)
        self.assertNotIn("/private", stderr.getvalue())
        verifier.assert_not_called()

    def test_cli_success_warns_even_with_pin(self):
        stdout = io.StringIO()
        pin = self.write()
        with redirect_stdout(stdout), patch.object(att.gate, "verify", return_value=self.current):
            self.assertEqual(att.main([str(self.report), str(self.dist),
                                       "--expected-report-sha256", pin]), 0)
        self.assertIn("PINNED", stdout.getvalue())
        self.assertIn("NOT release authorized", stdout.getvalue())
        self.assertIn("NOT independently proven", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
