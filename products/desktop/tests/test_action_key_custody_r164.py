"""R164 synthetic YAML-action-key camouflage tests. No customer data or releases."""
from __future__ import annotations

import unittest

from ci_action_key_guard_r164 import ActionKeyError, verify_action_key_shape

SHA = "08c6903cd8c0fde910a37f88322edcfb5dd907a8"
GOOD = ("name: Desktop internal CI\n"
        "jobs:\n"
        "  source-tests:\n"
        "    steps:\n"
        f"      - uses: actions/checkout@{SHA} # pinned\n"
        f"      - uses: actions/setup-python@{SHA}\n"
        f"      - name: Source evidence\n        uses: actions/upload-artifact@{SHA}\n"
        "  windows-build:\n"
        "    steps:\n"
        f"      - uses: actions/checkout@{SHA}\n"
        f"      - uses: actions/setup-python@{SHA}\n"
        f"      - name: Windows evidence\n        uses: actions/upload-artifact@{SHA}\n")


class ActionKeyCustodyR164(unittest.TestCase):
    def reject(self, source: str) -> None:
        with self.assertRaises(ActionKeyError):
            verify_action_key_shape(source)

    def test_six_canonical_keys_accepted(self):
        self.assertEqual(verify_action_key_shape(GOOD), 6)

    def test_approved_comment_suffix_accepted(self):
        self.assertEqual(verify_action_key_shape(GOOD + "      # uses: fake@v1\n"), 6)

    def test_unquoted_key_space_before_colon_rejected(self):
        self.reject(GOOD + "      - uses : attacker/code@v1\n")

    def test_single_quoted_key_rejected(self):
        self.reject(GOOD + "      - 'uses': attacker/code@v1\n")

    def test_double_quoted_key_rejected(self):
        self.reject(GOOD + '      - "uses": attacker/code@v1\n')

    def test_inline_map_rejected(self):
        self.reject(GOOD + "      - {uses: attacker/code@v1}\n")

    def test_inline_quoted_map_rejected(self):
        self.reject(GOOD + '      - {"uses": attacker/code@v1}\n')

    def test_unicode_escape_key_rejected(self):
        self.reject(GOOD + '      - "u\\u0073es": attacker/code@v1\n')

    def test_hex_escape_key_rejected(self):
        self.reject(GOOD + '      - "u\\x73es": attacker/code@v1\n')

    def test_long_unicode_escape_key_rejected(self):
        self.reject(GOOD + '      - "u\\U00000073es": attacker/code@v1\n')

    def test_explicit_yaml_key_rejected(self):
        self.reject(GOOD + "      ? uses\n      : attacker/code@v1\n")

    def test_merge_mapping_rejected(self):
        self.reject(GOOD + "      - <<: *untrusted\n")

    def test_missing_key_rejected(self):
        self.reject(GOOD.replace(f"      - uses: actions/checkout@{SHA}\n", "", 1))

    def test_duplicate_known_key_rejected(self):
        self.reject(GOOD + f"      - uses: actions/checkout@{SHA}\n")

    def test_unexpected_indent_rejected(self):
        self.reject(GOOD.replace(f"      - uses: actions/checkout@{SHA}",
                                 f"        - uses: actions/checkout@{SHA}", 1))

    def test_unexpected_top_level_key_rejected(self):
        self.reject(GOOD.replace(f"      - uses: actions/checkout@{SHA}",
                                 f"uses: actions/checkout@{SHA}", 1))

    def test_shell_script_camouflage_rejected(self):
        self.reject(GOOD + '          echo "uses: attacker/code@v1"\n')

    def test_embedded_nested_value_key_rejected(self):
        self.reject(GOOD + "        env: {uses: attacker/code@v1}\n")

    def test_null_and_tab_rejected(self):
        for text in (GOOD + "\x00", GOOD + "\t"):
            with self.subTest(suffix=repr(text[-1])):
                self.reject(text)

    def test_non_string_rejected(self):
        for value in (None, b"uses: unsafe", 5):
            with self.subTest(value=type(value).__name__):
                self.reject(value)

    def test_oversized_input_rejected(self):
        self.reject(GOOD + "#" * (128 * 1024))


if __name__ == "__main__":
    unittest.main()
