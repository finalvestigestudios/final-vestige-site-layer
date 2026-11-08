"""R280: synthetic Defender receipt contract; NO real AV or EXE clearance."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from defender_receipt_contract_r280 import EXES, DefenderReceiptRejected, require_defender_receipt

_DEFAULT_R9 = object()
R9_PIN = "a" * 64
CHECKSUMS = "b" * 64
HASHES = [f"{i:064x}" for i in range(1, 7)]


def r9():
    return {
        "status": "windows_smoke_passed", "windows_executables_verified": True,
        "checksums_sha256": CHECKSUMS,
        "artifacts": [{"name": name, "sha256": sha} for name, sha in zip(EXES, HASHES)],
    }


def defender():
    return {
        "schema": "fv-labs-offline-defender-r111-v1",
        "provider": "Microsoft Defender Antivirus",
        "status": "SIX_SCANS_ZERO_EXIT_UNCERTIFIED",
        "native_platform": "Windows 11 AMD64 workstation",
        "scanned_utc": "2026-11-08T10:11:12+00:00",
        "scanner_sha256": "c" * 64,
        "scanner_custody": "same_signed_engine_sha256_and_file_identity_observed",
        "defender_environment_observations": 7,
        "defender_active_health_checkpoints": 14,
        "defender_active_health_policy": "normal_mode_realtime_behavior_ioav_onaccess_fresh_signatures",
        "defender_environment_status": "zero_local_history_and_explicit_exclusions_observed_not_malware_clearance",
        "r9_report_sha256": R9_PIN,
        "checksums_sha256": CHECKSUMS,
        "artifacts": [{"name": name, "sha256": sha,
                       "defender_custom_scan": "zero_exit_result_remediation_ambiguous"}
                      for name, sha in zip(EXES, HASHES)],
        "release_authorized": False, "independent_malware_clearance": False,
        "premium_distribution_authorized": False,
    }


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


class DefenderReceiptContractTests(unittest.TestCase):
    def accept(self, receipt=None, r9_record=_DEFAULT_R9):
        return require_defender_receipt(
            encode(defender() if receipt is None else receipt),
            expected_r9_sha256=R9_PIN,
            r9_evidence=r9() if r9_record is _DEFAULT_R9 else r9_record)

    def deny(self, receipt=None, *, raw=None, r9_record=_DEFAULT_R9, expected_pin=R9_PIN):
        with self.assertRaises(DefenderReceiptRejected) as caught:
            require_defender_receipt(
                raw if raw is not None else encode(defender() if receipt is None else receipt),
                expected_r9_sha256=expected_pin,
                r9_evidence=r9() if r9_record is _DEFAULT_R9 else r9_record)
        self.assertEqual(str(caught.exception), "Invalid private Defender candidate receipt")

    def test_canonical_six_contract_is_admissible_synthetic_only(self):
        self.assertIsNone(self.accept())
        self.assertEqual(len(EXES), 6)
        self.assertIn("GrantAuditStudioPro.exe", EXES)
        self.assertIn("ProcureGuardStudioPro.exe", EXES)

    def test_unsupported_root_schema(self):
        for field in ("schema", "provider", "status", "native_platform",
                      "scanner_custody", "defender_active_health_policy",
                      "defender_environment_status"):
            with self.subTest(field=field):
                receipt = defender()
                receipt[field] = "PASS"
                self.deny(receipt)

    def test_missing_unexpected_or_private_fields(self):
        for field in defender():
            with self.subTest(missing=field):
                receipt = defender()
                del receipt[field]
                self.deny(receipt)
        for field in ("customer_path", "raw_stdout", "user", "credentials"):
            with self.subTest(extra=field):
                receipt = defender()
                receipt[field] = "secrets"
                self.deny(receipt)

    def test_release_and_malware_claims_must_be_literal_false(self):
        for field in ("release_authorized", "independent_malware_clearance",
                      "premium_distribution_authorized"):
            for bad in (True, 0, None, "false"):
                with self.subTest(field=field, bad=bad):
                    receipt = defender()
                    receipt[field] = bad
                    self.deny(receipt)

    def test_attestation_and_checksum_pins_are_exact(self):
        for field in ("r9_report_sha256", "checksums_sha256"):
            for bad in ("d" * 64, "A" * 64, None, True):
                with self.subTest(field=field, bad=bad):
                    receipt = defender()
                    receipt[field] = bad
                    self.deny(receipt)
        for bad in (None, True, "A" * 64, "a" * 63):
            self.deny(expected_pin=bad)

    def test_scanner_digest_must_be_exact_lower_hex(self):
        for bad in ("F" * 64, "0" * 63, None, 0, False, "x" * 64):
            receipt = defender()
            receipt["scanner_sha256"] = bad
            self.deny(receipt)

    def test_six_artifacts_require_exact_name_order_and_hashes(self):
        base = defender()
        for change in ("short", "extra", "wrongname", "swap", "wronghash", "extra_field", "missing_field", "wrong_status"):
            with self.subTest(change=change):
                receipt = copy.deepcopy(base)
                a = receipt["artifacts"]
                if change == "short": a.pop()
                elif change == "extra": a.append(copy.deepcopy(a[0]))
                elif change == "wrongname": a[0]["name"] = "Other.exe"
                elif change == "swap": a[0], a[1] = a[1], a[0]
                elif change == "wronghash": a[0]["sha256"] = "d" * 64
                elif change == "extra_field": a[0]["private_path"] = "secret"
                elif change == "missing_field": del a[0]["sha256"]
                else: a[0]["defender_custom_scan"] = "passed_and_certified"
                self.deny(receipt)

    def test_missing_or_synthetic_r9_is_rejected(self):
        for change in ("missing", "not_smoked", "wrong_status", "wrong_inventory",
                       "missing_artifact", "duplicate", "wrong_hash"):
            with self.subTest(change=change):
                old = r9()
                if change == "missing": old = None
                elif change == "not_smoked": old["windows_executables_verified"] = False
                elif change == "wrong_status": old["status"] = "integrity_only"
                elif change == "wrong_inventory": old["checksums_sha256"] = "INVALID"
                elif change == "missing_artifact": old["artifacts"].pop()
                elif change == "duplicate": old["artifacts"][1]["name"] = old["artifacts"][0]["name"]
                elif change == "wrong_hash": old["artifacts"][0]["sha256"] = None
                self.deny(r9_record=old)

    def test_counts_are_exact_and_bool_is_not_int(self):
        for field, correct in (("defender_environment_observations", 7),
                               ("defender_active_health_checkpoints", 14)):
            for bad in (True, False, "7", None, 0, correct - 1, correct + 1):
                with self.subTest(field=field, bad=bad):
                    receipt = defender()
                    receipt[field] = bad
                    self.deny(receipt)

    def test_utc_seconds_timestamp(self):
        for bad in ("2026-11-08", "2026-13-08T10:11:12+00:00",
                    "2026-11-08T10:11:12Z", "2026-11-08T10:11:12-08:00",
                    "2026-11-08T10:11:12.222+00:00", None, 44):
            with self.subTest(bad=bad):
                receipt = defender()
                receipt["scanned_utc"] = bad
                self.deny(receipt)

    def test_duplicate_json_keys_rejected_even_nested(self):
        good = encode(defender())
        self.deny(raw=good.replace(b'"provider":', b'"provider":"wrong","provider":', 1))
        self.deny(raw=good.replace(b'"name":', b'"name":"wrong","name":', 1))

    def test_nan_infinity_fractions_and_exponents_denied(self):
        raw = encode(defender())
        self.deny(raw=raw.replace(b'"defender_environment_observations":7',
                                   b'"defender_environment_observations":1e400'))
        for bad in (b'7.0', b'NaN', b'Infinity', b'-Infinity'):
            self.deny(raw=raw.replace(b'"defender_environment_observations":7',
                                       b'"defender_environment_observations":' + bad))

    def test_malformed_and_nonsensical_types_rejected_without_data_leak(self):
        for raw in (b'{', b'[]', b'null', b'"hi"', b'\xff', b'{}'):
            self.deny(raw=raw)


if __name__ == "__main__":
    unittest.main()
