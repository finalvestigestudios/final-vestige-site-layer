"""R293: known desktop CI root YAML shape must not shadow the tested jobs.

This is a lexical fail-closed check, not a YAML parser or permission to
release six Windows executables. Reuses R57's known-good two-job fixture to
exercise the *actual* full source-contract validator and its security imports.
"""
from __future__ import annotations

from pathlib import Path
import unittest

import ci_source_contract as guard
from test_ci_source_contract_r57 import GOOD


class CIRootMappingCustodyR293(unittest.TestCase):
    def reject(self, changed: str) -> None:
        with self.assertRaises(guard.SourceContractError):
            guard.verify_workflow(changed)

    def test_existing_reviewed_two_job_fixture_still_passes(self):
        self.assertEqual(guard.verify_workflow(GOOD), 2)

    def test_comments_and_blank_lines_do_not_change_root_mapping(self):
        self.assertEqual(guard.verify_workflow("# preflight comment\n" + GOOD +
                                               "\n# reviewed trailer\n"), 2)

    def test_preceding_space_before_jobs_key_rejected(self):
        self.reject("jobs :\n  windows-build:\n    runs-on: ubuntu-24.04\n" + GOOD)

    def test_preceding_quoted_jobs_key_rejected(self):
        self.reject('"jobs":\n  windows-build:\n    runs-on: ubuntu-24.04\n' + GOOD)

    def test_following_space_before_jobs_key_rejected(self):
        self.reject(GOOD + "\njobs :\n  windows-build:\n    runs-on: ubuntu-24.04\n")

    def test_following_single_quoted_jobs_key_rejected(self):
        self.reject(GOOD + "\n'jobs':\n  windows-build:\n    runs-on: ubuntu-24.04\n")

    def test_second_yaml_document_rejected(self):
        self.reject(GOOD + "\n---\nname: Unreviewed workflow\n")

    def test_appended_top_level_permissions_rejected(self):
        self.reject(GOOD + "\npermissions:\n  contents: write\n")

    def test_appended_whitespace_variant_permissions_rejected(self):
        self.reject(GOOD + "\npermissions :\n  actions: write\n")

    def test_appended_unreviewed_root_environment_rejected(self):
        self.reject(GOOD + "\nenv:\n  SKIP_TESTS: 1\n")

    def test_replaced_root_event_key_rejected(self):
        self.reject(GOOD.replace("on:\n", "on :\n", 1))

    def test_replaced_workflow_name_requires_review(self):
        self.reject(GOOD.replace("name: Desktop suite build (internal)",
                                 "name: Different workflow", 1))

    def test_checked_out_real_workflow_accepted(self):
        path = Path(__file__).resolve().parents[3] / ".github/workflows/desktop-build.yml"
        if not path.is_file():
            self.skipTest("Full checked-out workflow unavailable")
        self.assertEqual(guard.verify_workflow(path.read_text(encoding="utf-8")), 2)


if __name__ == "__main__":
    unittest.main()
