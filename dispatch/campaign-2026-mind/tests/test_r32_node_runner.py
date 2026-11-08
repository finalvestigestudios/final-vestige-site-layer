"""Run previously unexercised Dispatch audits on actual Node in hosted CI.

Automatically discovered by the existing Python unittest workflow on the exact
PR checkout. No WordPress, SMTP, merchant network, subscribers or publishing.
"""
import pathlib
import re
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Explicit allowlist prevents config-controlled subprocesses/path traversal.
CASES = (
    ("r11_native_delivery_gate", "native-email-contract/source_gate.test.mjs", "node_test"),
    ("r12_merchant_release_gate", "merchant-operations/r12_evidence_gate.test.mjs", "node_test"),
    ("r22_excerpt_model", "jetpack-excerpt-gate-r22/tests/test_excerpt.cjs", "r22"),
    ("r27_delivery_mode", "r27-delivery-mode-proof/tests/test_excerpt_truth.cjs", "r27"),
    ("r28_cross_surface", "r28-cross-surface-integrity/tests/test_audit_surfaces.cjs", "r28"),
    ("r29_native_inbox_contract", "r29-inbox-contract/tests/test_inbox_contract.cjs", "r29"),
    ("r30_excerpt_truth", "r30-excerpt-truth/tests/test_excerpt_truth.cjs", "r30"),
    ("r31_reader_clickpath", "r31-clickpath-audit/tests/test_route_audit.cjs", "r31"),
)

def run_native_case(relative_path, mode):
    """Fail closed on missing Node, script, timeout, exit failure, or missing evidence."""
    node = shutil.which("node")
    if not node:
        raise AssertionError("Node executable unavailable; Actions must set up Node 20")
    target = (ROOT / relative_path).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
        raise AssertionError(f"Missing/unsafe source-controlled audit: {relative_path}")
    args = [node, "--test", str(target)] if mode == "node_test" else [node, str(target)]
    try:
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=55, check=False)
    except subprocess.TimeoutExpired as exc:
        raise AssertionError(f"Native Node audit timed out: {relative_path}") from exc
    output = p.stdout + "\n" + p.stderr
    if p.returncode:
        raise AssertionError(f"Native Node audit FAILED: {relative_path}\n{output[-5000:]}")
    if mode == "node_test":
        if not re.search(r"(?m)^# fail 0\s*$", output):
            raise AssertionError(f"Node TAP did not prove zero failed tests: {relative_path}\n{output[-2500:]}")
    elif mode == "r22":
        if not re.search(r"R22: \d+/\d+ node regression checks passed", output):
            raise AssertionError("R22 success marker absent")
    elif mode == "r27":
        if "R27:" not in output or "PASSED" not in output:
            raise AssertionError("R27 success marker absent")
    elif mode == "r28":
        if "R28 SOURCE SURFACE TESTS:" not in output or "assertions passed" not in output:
            raise AssertionError("R28 success marker absent")
    elif mode == "r29":
        if not re.search(r"PASS \d+ assertions", output):
            raise AssertionError("R29 success marker absent")
    elif mode in ("r30", "r31"):
        if not re.search(r'"(?:status|result)"\s*:\s*"PASS"', output):
            raise AssertionError(f"{mode} success marker absent")
    else:
        raise AssertionError(f"Unknown audit mode: {mode}")
    return output

class NativeNodeSafetySuite(unittest.TestCase):
    def test_native_runner_inventory_cannot_be_empty_or_duplicated(self):
        self.assertEqual(len(CASES), 8)
        self.assertEqual(len({c[0] for c in CASES}), 8)
        self.assertEqual(len({c[1] for c in CASES}), 8)
        self.assertTrue(all(c[1].endswith((".cjs", ".mjs")) for c in CASES))

def _make_test(relative, mode):
    def test(self):
        output = run_native_case(relative, mode)
        self.assertTrue(output.strip(), "No Node evidence output")
    return test

for name, filename, kind in CASES:
    setattr(NativeNodeSafetySuite, "test_" + name, _make_test(filename, kind))

if __name__ == "__main__":
    unittest.main()
