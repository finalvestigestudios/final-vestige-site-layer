"""R292/R363 regression: a grown >192 KiB desktop workflow must remain gated.

Uses the committed full workflow and the actual four independent CI validators.
No builds, private payloads, customer data or release authorization.
"""
from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

import ci_action_key_guard_r164 as keys
import ci_action_pin_guard as pins
import ci_artifact_policy as artifacts
import ci_source_contract as sources
from ci_workflow_budget_r292 import MAX_WORKFLOW_BYTES

WORKFLOW = Path(__file__).resolve().parents[3] / ".github/workflows/desktop-build.yml"
OLD_CEILING = 128 * 1024
PREVIOUS_REVIEWED_CEILING = 192 * 1024
GUARDS = (
    (keys, keys.verify_action_key_shape, keys.ActionKeyError, 6),
    (pins, pins.verify_action_pins, pins.ActionPinError, 6),
    (artifacts, artifacts.verify_upload_policy, artifacts.ArtifactPolicyError, 2),
    (sources, sources.verify_workflow, sources.SourceContractError, 2),
)


def full_workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def prefixed_to_budget(source: str) -> str:
    remaining = MAX_WORKFLOW_BYTES - len(source.encode("utf-8"))
    if remaining < 2:
        raise ValueError("Workflow cannot be safely padded")
    # A single large top-level YAML comment preserves the executable steps.
    result = "#" + ("x" * (remaining - 2)) + "\n" + source
    if len(result.encode("utf-8")) != MAX_WORKFLOW_BYTES:
        raise ValueError("Byte-boundary fixture was not exact")
    return result


class CIWorkflowBudgetR292(unittest.TestCase):
    def require_all_pass(self, source: str) -> None:
        for _, validator, _, expected in GUARDS:
            with self.subTest(validator=validator.__name__):
                self.assertEqual(validator(source), expected)

    def require_all_reject(self, source: str) -> None:
        for _, validator, error, _ in GUARDS:
            with self.subTest(validator=validator.__name__):
                with self.assertRaises(error):
                    validator(source)

    def test_shared_reviewed_ceiling_and_four_consumers(self):
        self.assertEqual(MAX_WORKFLOW_BYTES, 224 * 1024)
        for module, _, _, _ in GUARDS:
            with self.subTest(module=module.__name__):
                self.assertEqual(module.MAX_WORKFLOW_BYTES, MAX_WORKFLOW_BYTES)

    def test_real_checked_out_workflow_is_over_old_cap_and_passes_all_guards(self):
        source = full_workflow()
        self.assertGreater(len(source.encode("utf-8")), OLD_CEILING)
        self.assertLessEqual(len(source.encode("utf-8")), MAX_WORKFLOW_BYTES)
        self.require_all_pass(source)

    def test_previous_192kib_cap_now_rejects_real_workflow(self):
        source = full_workflow()
        self.assertGreater(len(source.encode("utf-8")), PREVIOUS_REVIEWED_CEILING)
        self.assertLessEqual(len(source.encode("utf-8")), MAX_WORKFLOW_BYTES)
        for module, validator, error, _ in GUARDS:
            with self.subTest(module=module.__name__):
                with patch.object(module, "MAX_WORKFLOW_BYTES", PREVIOUS_REVIEWED_CEILING):
                    with self.assertRaises(error):
                        validator(source)

    def test_legacy_ceiling_reproduces_full_workflow_rejection(self):
        source = full_workflow()
        for module, validator, error, _ in GUARDS:
            with self.subTest(module=module.__name__):
                with patch.object(module, "MAX_WORKFLOW_BYTES", OLD_CEILING):
                    with self.assertRaises(error):
                        validator(source)

    def test_exact_byte_ceiling_accepts_unchanged_six_app_policy(self):
        self.require_all_pass(prefixed_to_budget(full_workflow()))

    def test_one_byte_over_ceiling_fails_all_four_validators(self):
        self.require_all_reject(prefixed_to_budget(full_workflow()) + "x")

    def test_utf8_multibyte_overflow_is_rejected(self):
        exact = prefixed_to_budget(full_workflow())
        self.require_all_reject(exact.replace("x", "\u00e9", 1))

    def test_unpinned_action_still_fails_with_larger_ceiling(self):
        source = full_workflow()
        before = "actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8"
        self.assertIn(before, source)
        changed = source.replace(before, "actions/checkout@" + ("0" * 40), 1)
        with self.assertRaises(pins.ActionPinError):
            pins.verify_action_pins(changed)

    def test_executable_artifact_upload_still_denied(self):
        source = full_workflow()
        self.assertIn("dist/SHA256SUMS.txt", source)
        changed = source.replace("dist/SHA256SUMS.txt", "dist/*.exe", 1)
        with self.assertRaises(artifacts.ArtifactPolicyError):
            artifacts.verify_upload_policy(changed)

    def test_removed_source_contract_still_denied(self):
        source = full_workflow()
        before = "run: python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml"
        self.assertIn(before, source)
        changed = source.replace(before, "run: echo bypass", 1)
        with self.assertRaises(sources.SourceContractError):
            sources.verify_workflow(changed)

    def test_nul_input_still_denied_by_all_guards(self):
        self.require_all_reject(full_workflow() + "\x00")


if __name__ == "__main__":
    unittest.main()
