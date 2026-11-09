"""R295: pin desktop GitHub Actions events and permission boundaries."""
from __future__ import annotations

import unittest

from ci_event_permissions_r295 import EventPermissionsError, verify_event_permissions


APPROVED = """name: Desktop suite build (internal)
on:
  pull_request:
    paths:
      - 'products/desktop/**'
      - '.github/workflows/desktop-build.yml'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  source-tests:
    runs-on: ubuntu-24.04
"""


class CIEventPermissionsR295(unittest.TestCase):
    def reject(self, modified: str) -> None:
        with self.assertRaises(EventPermissionsError):
            verify_event_permissions(modified)

    def test_approved_two_event_readonly_policy(self):
        self.assertIsNone(verify_event_permissions(APPROVED))

    def test_whole_line_comments_and_blank_lines_in_preamble(self):
        modified = "# safe comment\n\n" + APPROVED.replace(
            "permissions:\n", "# permissions review note\npermissions:\n")
        self.assertIsNone(verify_event_permissions(modified))

    def test_legacy_permissionless_fixture_rejected(self):
        self.reject(APPROVED.replace("permissions:\n  contents: read\n", ""))

    def test_pull_request_target_rejected(self):
        self.reject(APPROVED.replace("  pull_request:", "  pull_request_target:"))

    def test_push_event_rejected(self):
        self.reject(APPROVED.replace("  pull_request:", "  push:"))

    def test_workflow_run_event_rejected(self):
        self.reject(APPROVED.replace("  workflow_dispatch:", "  workflow_run:"))

    def test_schedule_event_rejected(self):
        self.reject(APPROVED.replace("  workflow_dispatch:", "  schedule:"))

    def test_repository_dispatch_rejected(self):
        self.reject(APPROVED.replace("  workflow_dispatch:", "  repository_dispatch:"))

    def test_extra_event_rejected(self):
        self.reject(APPROVED.replace("  workflow_dispatch:",
                                     "  workflow_dispatch:\n  push:\n    branches: [main]"))

    def test_duplicate_pull_request_event_rejected(self):
        self.reject(APPROVED.replace("  workflow_dispatch:",
                                     "  pull_request:\n  workflow_dispatch:"))

    def test_broader_paths_wildcard_rejected(self):
        self.reject(APPROVED.replace("'products/desktop/**'", "'**'"))

    def test_unreviewed_extra_path_rejected(self):
        self.reject(APPROVED.replace("      - '.github/workflows/desktop-build.yml'",
                                     "      - '.github/workflows/desktop-build.yml'\n      - '**'"))

    def test_missing_workflow_file_path_rejected(self):
        self.reject(APPROVED.replace("      - '.github/workflows/desktop-build.yml'\n", ""))

    def test_paths_filter_removed_rejected(self):
        self.reject(APPROVED.replace("    paths:\n      - 'products/desktop/**'\n"
                                     "      - '.github/workflows/desktop-build.yml'\n", ""))

    def test_event_key_alias_rejected(self):
        self.reject(APPROVED.replace("  pull_request:", "  pull_request: *expanded"))

    def test_flow_mapping_trigger_rejected(self):
        self.reject(APPROVED.replace("  workflow_dispatch:", "  workflow_dispatch: {}"))

    def test_write_token_rejected(self):
        self.reject(APPROVED.replace("  contents: read", "  contents: write"))

    def test_all_write_token_rejected(self):
        self.reject(APPROVED.replace("  contents: read", "  actions: write"))

    def test_id_token_permission_rejected(self):
        self.reject(APPROVED.replace("  contents: read", "  contents: read\n  id-token: write"))

    def test_top_level_write_permission_scalar_rejected(self):
        self.reject(APPROVED.replace("permissions:\n  contents: read", "permissions: write-all"))

    def test_quoted_permissions_key_rejected(self):
        self.reject(APPROVED.replace("permissions:", "'permissions':"))

    def test_spaced_permissions_key_rejected(self):
        self.reject(APPROVED.replace("permissions:", "permissions :"))

    def test_duplicate_permissions_rejected(self):
        self.reject(APPROVED.replace("  contents: read", "  contents: read\npermissions:\n  contents: write"))

    def test_quoted_contents_key_rejected(self):
        self.reject(APPROVED.replace("  contents: read", '  "contents": read'))

    def test_inline_permission_override_rejected(self):
        self.reject(APPROVED.replace("  contents: read", "  contents: read # unreviewed"))

    def test_renamed_workflow_rejected(self):
        self.reject(APPROVED.replace("name: Desktop suite build (internal)", "name: Public release"))

    def test_second_document_rejected(self):
        self.reject(APPROVED.replace("permissions:", "---\npermissions:"))

    def test_duplicated_jobs_boundary_rejected(self):
        self.reject(APPROVED + "\njobs:\n  unreviewed:\n")

    def test_spaced_jobs_boundary_rejected(self):
        self.reject(APPROVED.replace("jobs:\n", "jobs :\n"))

    def test_non_string_and_tabs_rejected(self):
        for source in (None, [], APPROVED.replace("  contents: read", "\tcontents: read"), APPROVED+"\x00"):
            with self.subTest(source=type(source).__name__):
                with self.assertRaises(EventPermissionsError):
                    verify_event_permissions(source)


if __name__ == "__main__":
    unittest.main()
