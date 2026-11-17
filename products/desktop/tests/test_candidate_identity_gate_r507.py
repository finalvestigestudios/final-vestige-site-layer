"""R507 actual release_gate binding; synthetic mock paths, no executable run."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import release_gate
from build_inventory import EXPECTED


class NativeIdentityGateR507(unittest.TestCase):
    def exercise(self, hashes, *, status):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in EXPECTED:
                (root / name).write_bytes(b"not-an-executable")
            mapping = dict(zip(EXPECTED, hashes))

            def fake_hash(path):
                return "f" * 64 if path.name == "SHA256SUMS.txt" else mapping[path.name]

            with (patch.object(release_gate, "classify_smoke", return_value=status),
                  patch.object(release_gate, "check_candidate_directory"),
                  patch.object(release_gate, "_regular"),
                  patch.object(release_gate, "_inventory", return_value=mapping),
                  patch.object(release_gate, "_sha", side_effect=fake_hash),
                  patch.object(release_gate, "_pe64"),
                  patch.object(release_gate, "select_smoke_runner", return_value=object()) as select,
                  patch.object(release_gate, "run_smoke_checked") as launch):
                if len(set(hashes)) != 6 and status == "windows_smoke_passed":
                    with self.assertRaisesRegex(
                            release_gate.GateFailure,
                            "Six Windows candidate images must be distinct"):
                        release_gate.verify(root, smoke=True)
                    select.assert_not_called()
                    launch.assert_not_called()
                else:
                    result = release_gate.verify(root, smoke=True)
                    self.assertFalse(result["release_authorized"])
                    self.assertEqual(len(result["artifacts"]), 6)
                    self.assertEqual(launch.call_count, 6)

    def test_native_six_distinct_candidates_reach_smoke_boundary(self):
        self.exercise([format(i + 1, "064x") for i in range(6)],
                      status="windows_smoke_passed")

    def test_native_duplicate_free_and_premium_rejected_before_any_launch(self):
        hashes = [format(i + 1, "064x") for i in range(6)]
        hashes[-1] = hashes[0]
        self.exercise(hashes, status="windows_smoke_passed")

    def test_native_duplicate_premium_pair_rejected_before_any_launch(self):
        hashes = [format(i + 1, "064x") for i in range(6)]
        hashes[-1] = hashes[-2]
        self.exercise(hashes, status="windows_smoke_passed")

    def test_injected_synthetic_smoke_does_not_claim_native_identity_gate(self):
        hashes = ["a" * 64 for _ in EXPECTED]
        self.exercise(hashes, status="synthetic_smoke_only")


if __name__ == "__main__":
    unittest.main()
