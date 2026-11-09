"""R294: prevent duplicate/alternate job YAML keys shadowing source gates."""
from __future__ import annotations

import unittest

from ci_job_mapping_r294 import JobMappingError, verify_job_mapping


SOURCE = [
    "  source-tests:",
    "    runs-on: ubuntu-24.04",
    "    timeout-minutes: 20",
    "    env:",
    "      PYTHONPATH: products/desktop",
    "    steps:",
    "      - uses: actions/checkout@pinned",
    "      - name: Validate",
    "        run: |",
    "          echo reviewed",
]
WINDOWS = [
    "  windows-build:",
    "    runs-on: windows-latest",
    "    timeout-minutes: 45",
    "    steps:",
    "      - name: Build",
    "        run: echo candidate",
]


class CIJobMappingR294(unittest.TestCase):
    def reject(self, name: str, lines: list[str]) -> None:
        with self.assertRaises(JobMappingError):
            verify_job_mapping(name, lines)

    def test_current_source_shape_accepted(self):
        self.assertIsNone(verify_job_mapping("source-tests", SOURCE))

    def test_current_windows_shape_accepted(self):
        self.assertIsNone(verify_job_mapping("windows-build", WINDOWS))

    def test_r57_source_fixture_accepted(self):
        self.assertIsNone(verify_job_mapping("source-tests", [SOURCE[0], SOURCE[1], "    steps:"]))

    def test_r57_windows_fixture_accepted(self):
        self.assertIsNone(verify_job_mapping("windows-build", [WINDOWS[0], WINDOWS[1], "    steps:"]))

    def test_blank_lines_and_comments_accepted(self):
        lines = SOURCE[:2] + ["", "    # reviewer note", "        # nested note"] + SOURCE[2:]
        self.assertIsNone(verify_job_mapping("source-tests", lines))

    def test_duplicate_steps_after_reviewed_steps_rejected(self):
        self.reject("windows-build", WINDOWS + ["    steps:", "      - run: echo bypass"])

    def test_duplicate_steps_before_reviewed_steps_rejected(self):
        self.reject("source-tests", SOURCE[:5] + ["    steps:"] + SOURCE[5:])

    def test_duplicate_runner_rejected(self):
        self.reject("windows-build", WINDOWS + ["    runs-on: ubuntu-latest"])

    def test_alternate_whitespace_steps_key_rejected(self):
        self.reject("source-tests", SOURCE + ["    steps :", "      - run: echo bypass"])

    def test_quoted_steps_key_rejected(self):
        self.reject("windows-build", WINDOWS + ['    "steps":', '      - run: echo bypass'])

    def test_single_quoted_runner_key_rejected(self):
        self.reject("source-tests", SOURCE + ["    'runs-on': ubuntu-latest"])

    def test_job_level_merge_alias_rejected(self):
        self.reject("windows-build", WINDOWS[:3] + ["    <<: *unreviewed"] + WINDOWS[3:])

    def test_job_level_conditional_rejected(self):
        self.reject("windows-build", WINDOWS[:3] + ["    if: ${{ true }}"] + WINDOWS[3:])

    def test_job_level_permissions_rejected(self):
        self.reject("source-tests", SOURCE[:5] + ["    permissions:", "      contents: write"] + SOURCE[5:])

    def test_job_level_strategy_rejected(self):
        self.reject("windows-build", WINDOWS[:3] + ["    strategy:", "      fail-fast: false"] + WINDOWS[3:])

    def test_windows_env_requires_review(self):
        self.reject("windows-build", WINDOWS[:3] + ["    env:", "      SKIP: 1"] + WINDOWS[3:])

    def test_timeout_override_requires_review(self):
        self.reject("windows-build", [x.replace("timeout-minutes: 45", "timeout-minutes: 1") for x in WINDOWS])

    def test_job_key_order_change_requires_review(self):
        self.reject("source-tests", [SOURCE[0], SOURCE[1], "    steps:", "    timeout-minutes: 20", "    env:"])

    def test_embedded_steps_map_requires_review(self):
        self.reject("windows-build", [WINDOWS[0], WINDOWS[1], "    steps: *replacement"])

    def test_unknown_job_name_rejected(self):
        self.reject("replacement", ["  replacement:", "    runs-on: ubuntu-24.04", "    steps:"])

    def test_wrong_job_heading_rejected(self):
        self.reject("windows-build", ["  other:"] + WINDOWS[1:])

    def test_non_list_input_rejected(self):
        with self.assertRaises(JobMappingError):
            verify_job_mapping("windows-build", tuple(WINDOWS))

    def test_non_string_line_rejected(self):
        self.reject("windows-build", WINDOWS + [None])


if __name__ == "__main__":
    unittest.main()
