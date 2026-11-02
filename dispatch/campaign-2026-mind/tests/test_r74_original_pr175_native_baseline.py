"""Independently execute PR #175's six native Python tests against its exact pinned Git tree.

The canonical PR #175 contents are reconstructed from git objects, never copied from
the current stacked branch. This is intentionally an offline CI-only baseline.
It is neither a newsletter-send test nor an endorsement of the original claims.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ORIGINAL_HEAD = "d57ccdba3aee8f065e143e101c2945f4f3d01647"
ROOT = Path(__file__).resolve().parents[3]
PREFIX = "dispatch/campaign-2026-mind/"
FILES = [
    "manifest.json",
    "tests/test_campaign.py",
    "issues/01-the-mind-is-not-a-camera.md",
    "issues/02-before-hypnosis-had-a-name.md",
    "issues/03-the-twelve-minute-question.md",
    "issues/04-the-hatch-and-the-spark.md",
    "issues/05-before-you-press-play.md",
    "issues/06-the-evidence-log.md",
]

class OriginalPR175IndependentSuite(unittest.TestCase):
    def test_exact_original_PR_head_runs_all_six_python_tests(self):
        # Explicitly fail if the pinned original tree is unavailable: a silent
        # skip would falsely imply independent verification.
        t = subprocess.run(
            ["git", "cat-file", "-t", ORIGINAL_HEAD],
            cwd=ROOT, capture_output=True, timeout=10, check=True,
        )
        self.assertEqual(t.stdout.strip(), b"commit")
        with tempfile.TemporaryDirectory(prefix="fv-pr175-pinned-") as temp:
            home = Path(temp)
            for relative in FILES:
                original = subprocess.run(
                    ["git", "show", ORIGINAL_HEAD + ":" + PREFIX + relative],
                    cwd=ROOT, capture_output=True, timeout=10, check=True,
                ).stdout
                dest = home / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(original)
            execution = subprocess.run(
                [sys.executable, "-I", "-m", "unittest", "discover",
                 "-s", str(home / "tests"), "-v"],
                cwd=home, capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(execution.returncode, 0,
                             "Pinned original PR #175 native suite must pass")
            self.assertIn("Ran 6 tests", execution.stderr)
            self.assertIn("OK", execution.stderr)

if __name__ == "__main__":
    unittest.main()
