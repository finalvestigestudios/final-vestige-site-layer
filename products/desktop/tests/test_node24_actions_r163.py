"""R163: require six upstream-verified Node24 action pins and evidence-only uploads.

Synthetic data only. A green source test is not physical Windows acceptance, an
upstream signature, premium entitlement, or permission to release executables.
"""
from __future__ import annotations

import contextlib
import io
import re
import tempfile
import unittest
from pathlib import Path

import ci_action_pin_guard as pins
import ci_artifact_policy as artifacts
import ci_source_contract as provenance


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github/workflows/desktop-build.yml"
MANUAL = ROOT / "products/desktop/docs/NODE24_ACTIONS_R163.md"
EXPECTED = {
    "actions/checkout": "08c6903cd8c0fde910a37f88322edcfb5dd907a8",
    "actions/setup-python": "e797f83bcb11b83ae66e0230d6156d7c80228e7c",
    "actions/upload-artifact": "b7c566a772e6b6bfb58ed0dc250532a479d7789f",
}
PRIOR = {
    "actions/checkout": "11bd71901bbe5b1630ceea73d27597364c9af683",
    "actions/setup-python": "a26af69be951a213d495a4c3e4e4022e16d87065",
    "actions/upload-artifact": "ea165f8d65b6e75b540449e92b4886f43607fa02",
}
GOOD = (
    "jobs:\n  source-tests:\n    steps:\n"
    + "".join(f"      - uses: {name}@{sha}\n" for name, sha in EXPECTED.items())
    + "  windows-build:\n    steps:\n"
    + "".join(f"      - uses: {name}@{sha}\n" for name, sha in EXPECTED.items())
)


class Node24R163(unittest.TestCase):
    def actual(self):
        return WORKFLOW.read_text(encoding="utf-8")

    def rejected(self, candidate):
        with self.assertRaises(pins.ActionPinError):
            pins.verify_action_pins(candidate)

    def test_expected_upstream_node24_commit_inventory(self):
        self.assertEqual(pins.APPROVED, EXPECTED)

    def test_node24_pins_are_exact_git_ids(self):
        self.assertEqual(len(pins.APPROVED), 3)
        for name, sha in pins.APPROVED.items():
            with self.subTest(action=name):
                self.assertRegex(sha, r"^[a-f0-9]{40}$")

    def test_all_six_action_references_required(self):
        self.assertEqual(pins.verify_action_pins(GOOD), 6)

    def test_reject_old_checkout_commit(self):
        self.rejected(GOOD.replace(EXPECTED["actions/checkout"], PRIOR["actions/checkout"], 1))

    def test_reject_old_python_commit(self):
        self.rejected(GOOD.replace(EXPECTED["actions/setup-python"], PRIOR["actions/setup-python"], 1))

    def test_reject_old_uploader_commit(self):
        self.rejected(GOOD.replace(EXPECTED["actions/upload-artifact"], PRIOR["actions/upload-artifact"], 1))

    def test_reject_mutable_major_tags(self):
        for name, tag in (
            ("actions/checkout", "v5"),
            ("actions/setup-python", "v6"),
            ("actions/upload-artifact", "v6"),
        ):
            with self.subTest(name=name):
                self.rejected(GOOD.replace(name + "@" + EXPECTED[name], name + "@" + tag, 1))

    def test_reject_main_branch_ref(self):
        self.rejected(GOOD.replace(EXPECTED["actions/checkout"], "main", 1))

    def test_reject_unknown_action(self):
        self.rejected(GOOD + "      - uses: attacker/build@1234567890123456789012345678901234567890\n")

    def test_reject_extra_known_action(self):
        self.rejected(GOOD + "      - uses: actions/checkout@" + EXPECTED["actions/checkout"] + "\n")

    def test_reject_missing_action(self):
        self.rejected(GOOD.replace("      - uses: actions/setup-python@" + EXPECTED["actions/setup-python"] + "\n", "", 1))

    def test_reject_digest_substitution(self):
        self.rejected(GOOD.replace(EXPECTED["actions/upload-artifact"], "0" * 40, 1))

    def test_r41_policy_accepts_new_uploader(self):
        self.assertEqual(artifacts.verify_upload_policy(self.actual()), 2)

    def test_r41_policy_denies_premium_path(self):
        source = self.actual()
        self.assertIn("            dist/SHA256SUMS.txt", source)
        changed = source.replace("            dist/SHA256SUMS.txt",
                                 "            dist/GrantAuditStudioPro.exe", 1)
        with self.assertRaises(artifacts.ArtifactPolicyError):
            artifacts.verify_upload_policy(changed)

    def test_r41_policy_denies_hidden_export_option(self):
        source = self.actual()
        self.assertIn("          retention-days: 7", source)
        changed = source.replace("          retention-days: 7",
                                 "          include-hidden-files: true\n          retention-days: 7", 1)
        with self.assertRaises(artifacts.ArtifactPolicyError):
            artifacts.verify_upload_policy(changed)

    def test_r57_mandatory_source_gate_accepts_new_actions(self):
        self.assertEqual(provenance.verify_workflow(self.actual()), 2)

    def test_real_workflow_has_exact_six_pins(self):
        source = self.actual()
        self.assertEqual(pins.verify_action_pins(source), 6)
        for name, sha in EXPECTED.items():
            with self.subTest(action=name):
                self.assertEqual(len(re.findall(
                    r"(?m)^\s*-?\s*uses: " + re.escape(name + "@" + sha) + r"(?:\s|$)",
                    source)), 2)

    def test_real_workflow_has_no_old_refs(self):
        source = self.actual()
        for old in PRIOR.values():
            self.assertNotIn(old, source)

    def test_real_workflow_requires_normal_and_optimized_r163(self):
        source = self.actual()
        self.assertEqual(source.count("name: R163 Node24 pinned-action runtime contracts"), 2)
        self.assertEqual(source.count("python products/desktop/scripts/safe_unittest_r163.py"), 2)
        self.assertEqual(source.count("python -OO products/desktop/scripts/safe_unittest_r163.py"), 2)
        self.assertIn('throw "R163 optimized runtime contract failed"', source)

    def test_operating_manual_has_release_hold(self):
        document = MANUAL.read_text(encoding="utf-8")
        self.assertIn("HARD RELEASE HOLD", document)
        self.assertIn("2.327.1", document)
        self.assertIn("Node.js 24", document)
        for sha in EXPECTED.values():
            self.assertIn(sha, document)

    def test_cli_sanitizes_missing_source_path(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            self.assertEqual(pins.main(["/private/customer/ledger-secret.yml"]), 1)
        self.assertNotIn("customer", output.getvalue())
        self.assertNotIn("ledger-secret", output.getvalue())

    def test_cli_success_synthetic(self):
        with tempfile.TemporaryDirectory(prefix="fvs-node24-r163-") as temporary:
            workflow = Path(temporary) / "desktop-build.yml"
            workflow.write_text(GOOD, encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(pins.main([str(workflow)]), 0)
            self.assertIn("NOT a release", output.getvalue())


if __name__ == "__main__":
    unittest.main()
