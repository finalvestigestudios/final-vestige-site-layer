"""Regression guards for runner-context validation and bounded cleanup.

No WordPress, network, credentials or third-party dependencies. This test
specifically prevents the GH workflow from failing before a runner is assigned.
"""
from pathlib import Path
import re
import unittest

WORKFLOW = Path(__file__).resolve().parents[4] / ".github/workflows/ex2-assembler-front-render-HOLD.yml"
# parents[4] is the repository root for .../experience2/home-flagship/qa/release-candidate
# Test the actual tracked workflow, not a copy supplied by a caller.

def validate(text):
    errors = []
    before_steps = text.split("    steps:", 1)[0]
    if "    steps:" not in text:
        errors.append("missing steps")
    if re.search(r"(?m)^    env:\s*$", before_steps):
        errors.append("job-level env")
    if "${{ runner." in before_steps:
        errors.append("runner context before assignment")
    if "${{ runner.temp }}" in text:
        errors.append("runner temp expression")
    if "${{ github.ref }}" not in text:
        errors.append("missing cancel-safe concurrency")
    for name in ("FV_THEME_PARENT", "FV_SCREEN_DIR", "FV_CANDIDATE", "FV_MANIFEST"):
        marker = f"printf '{name}=%s\\n' \"$RUNNER_TEMP/"
        if marker not in text:
            errors.append("missing safe runner-path initialization " + name)
        if f'test "${name}" = "$RUNNER_TEMP/' not in text:
            errors.append("missing anchored cleanup " + name)
    if '>> "$GITHUB_ENV"' not in text:
        errors.append("missing cross-step environment delivery")
    if "if: ${{ always() && env.FV_SCREEN_DIR != '' }}" not in text:
        errors.append("unguarded screenshot artifact")
    if "if: ${{ always() && env.FV_THEME_PARENT != '' }}" not in text:
        errors.append("unguarded cleanup step")
    if 'rm -rf -- "$FV_CANDIDATE"' not in text:
        errors.append("missing cleanup")
    if "persist-credentials: false" not in text:
        errors.append("checkout token persistence")
    # Official archive is verified as assembler-wpcom/; safe rebasing must
    # prevent both archive traversal and silent wrong-theme activation.
    if "parts[0]!='assembler-wpcom'" not in text:
        errors.append("official theme ZIP root mismatch")
    if "dest.is_relative_to(target_root)" not in text:
        errors.append("theme escape validation missing")
    if "Duplicate theme ZIP path" not in text or "Theme symlink/special file denied" not in text:
        errors.append("theme ZIP structural validation missing")
    if "z.extractall(" in text:
        errors.append("raw ZIP extraction prohibited")
    if "--assembler-dir" not in text or "Gutenberg" not in text:
        errors.append("missing nonproduction admission gate")
    return errors

class WorkflowRuntimePathsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = WORKFLOW.read_text(encoding="utf-8")

    def test_actual_source_validates(self):
        self.assertEqual(validate(self.original), [])

    def test_runner_context_in_job_env_fails(self):
        t = self.original.replace("    steps:", "    env:\n      F: ${{ runner.temp }}\n    steps:", 1)
        self.assertTrue(validate(t))

    def test_missing_path_init_fails(self):
        self.assertTrue(validate(self.original.replace("FV_MANIFEST=%s", "FV_MANIFES=%s")))

    def test_doubled_shell_newline_fails(self):
        self.assertTrue(validate(self.original.replace("FV_SCREEN_DIR=%s\\n", "FV_SCREEN_DIR=%s\\\\n")))

    def test_unanchored_delete_fails(self):
        self.assertTrue(validate(self.original.replace('test "$FV_SCREEN_DIR" = "$RUNNER_TEMP/', 'echo "$FV_SCREEN_DIR" = "$RUNNER_TEMP/')))

    def test_unguarded_artifact_fails(self):
        self.assertTrue(validate(self.original.replace("if: ${{ always() && env.FV_SCREEN_DIR != '' }}", "if: always()")))

    def test_unguarded_teardown_fails(self):
        self.assertTrue(validate(self.original.replace("if: ${{ always() && env.FV_THEME_PARENT != '' }}", "if: always()")))

    def test_no_checkout_token_persistence(self):
        self.assertTrue(validate(self.original.replace("persist-credentials: false", "persist-credentials: true")))

    def test_missing_github_env_fails(self):
        self.assertTrue(validate(self.original.replace('>> "$GITHUB_ENV"', '>> "$RUNNER_TEMP/unused"')))

    def test_theme_archive_prefix_must_match_observed_official_zip(self):
        self.assertTrue(validate(self.original.replace("parts[0]!='assembler-wpcom'", "parts[0]!='assembler'")))

    def test_theme_rebase_cannot_use_raw_extractall(self):
        self.assertTrue(validate(self.original.replace("shutil.copyfileobj(src,dst,1024*1024)", "z.extractall(root)")))

    def test_theme_path_escape_check_is_mandatory(self):
        self.assertTrue(validate(self.original.replace("dest.is_relative_to(target_root)", "True")))

if __name__ == "__main__":
    unittest.main()
