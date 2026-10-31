"""R73: mocked executable smoke must not masquerade as Windows x64 evidence."""
from __future__ import annotations

import unittest

from smoke_provenance import SmokeProvenanceError, classify_smoke


def classify(**changes):
    args = {"enabled": True, "native_os": "nt", "native_arch": "AMD64",
            "runner_injected": False, "platform_override": None}
    args.update(changes)
    return classify_smoke(**args)


class SmokeProvenanceR73Tests(unittest.TestCase):
    def test_native_amd64_subprocess_is_the_only_verified_smoke(self):
        self.assertEqual(classify(), "windows_smoke_passed")

    def test_native_x86_64_arch_alias_is_accepted(self):
        self.assertEqual(classify(native_arch="x86_64"), "windows_smoke_passed")

    def test_regular_integrity_check_does_not_claim_smoke(self):
        self.assertEqual(classify(enabled=False, native_os="posix"), "integrity_only")

    def test_mocked_runner_on_native_windows_is_still_only_synthetic(self):
        self.assertEqual(classify(runner_injected=True), "synthetic_smoke_only")

    def test_native_windows_with_test_platform_override_is_synthetic(self):
        self.assertEqual(classify(platform_override="nt"), "synthetic_smoke_only")

    def test_linux_mock_runner_and_test_platform_claim_is_synthetic(self):
        self.assertEqual(classify(native_os="posix", native_arch="x86_64",
                                  runner_injected=True, platform_override="nt"),
                         "synthetic_smoke_only")

    def test_linux_with_forged_nt_and_no_mock_runner_rejected(self):
        with self.assertRaisesRegex(SmokeProvenanceError, "actual Windows"):
            classify(native_os="posix", platform_override="nt")

    def test_linux_without_override_rejected_even_with_mock_runner(self):
        with self.assertRaisesRegex(SmokeProvenanceError, "actual Windows"):
            classify(native_os="posix", runner_injected=True)

    def test_arm64_windows_real_runner_rejected(self):
        with self.assertRaisesRegex(SmokeProvenanceError, "native Windows x64"):
            classify(native_arch="ARM64")

    def test_x86_32_windows_real_runner_rejected(self):
        with self.assertRaisesRegex(SmokeProvenanceError, "native Windows x64"):
            classify(native_arch="x86")

    def test_unknown_windows_arch_real_runner_rejected(self):
        with self.assertRaises(SmokeProvenanceError):
            classify(native_arch="")

    def test_rejected_explicit_posix_claim_even_on_windows(self):
        with self.assertRaises(SmokeProvenanceError):
            classify(platform_override="posix", runner_injected=True)

    def test_invalid_bool_flag_rejected(self):
        for changes in ({"enabled": 1}, {"runner_injected": 0}):
            with self.subTest(changes=changes):
                with self.assertRaises(SmokeProvenanceError):
                    classify(**changes)

    def test_invalid_override_types_rejected(self):
        for value in (0, False, object()):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(SmokeProvenanceError):
                    classify(platform_override=value)

    def test_invalid_native_platform_types_rejected(self):
        for changes in ({"native_os": None}, {"native_arch": None}):
            with self.subTest(changes=changes):
                with self.assertRaises(SmokeProvenanceError):
                    classify(**changes)

    def test_mismatched_platform_and_arch_is_rejected(self):
        with self.assertRaises(SmokeProvenanceError):
            classify(native_os="darwin", native_arch="AMD64")

    def test_non_smoke_with_injected_runner_is_still_integrity_only(self):
        self.assertEqual(classify(enabled=False, runner_injected=True,
                                  platform_override="nt"), "integrity_only")


if __name__ == "__main__":
    unittest.main()
