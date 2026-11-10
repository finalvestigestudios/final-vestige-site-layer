"""R334 fail-closed SHA256SUMS canonical framing; synthetic test evidence only."""
from __future__ import annotations

import unittest

from canonical_inventory_r334 import CanonicalInventoryError, parse_canonical_inventory


NAMES = (
    "LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
    "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe",
)
DIGESTS = tuple(f"{i:064x}".encode("ascii") for i in range(1, 7))


def canonical() -> bytes:
    return b"".join(h + b"  " + name.encode("ascii") + b"\n"
                    for h, name in zip(DIGESTS, NAMES))


class CanonicalManifestR334(unittest.TestCase):
    def check_rejected(self, content):
        with self.assertRaises(CanonicalInventoryError):
            parse_canonical_inventory(content, NAMES)

    def test_exact_six_accepted_with_original_order(self):
        self.assertEqual(
            parse_canonical_inventory(canonical(), NAMES),
            dict(zip(NAMES, (d.decode("ascii") for d in DIGESTS))),
        )

    def test_deterministic_reparse(self):
        self.assertEqual(parse_canonical_inventory(canonical(), NAMES),
                         parse_canonical_inventory(bytes(canonical()), NAMES))

    def test_reversed_lines_rejected(self):
        self.check_rejected(b"".join(reversed(canonical().splitlines(keepends=True))))

    def test_adjacent_rows_swapped_rejected(self):
        rows = canonical().splitlines(keepends=True)
        rows[1], rows[2] = rows[2], rows[1]
        self.check_rejected(b"".join(rows))

    def test_duplicate_name_rejected(self):
        rows = canonical().splitlines(keepends=True)
        rows[5] = DIGESTS[5] + b"  " + NAMES[0].encode("ascii") + b"\n"
        self.check_rejected(b"".join(rows))

    def test_missing_last_line_rejected(self):
        self.check_rejected(b"".join(canonical().splitlines(keepends=True)[:-1]))

    def test_extra_line_rejected(self):
        self.check_rejected(canonical() + canonical().splitlines(keepends=True)[0])

    def test_missing_final_lf_rejected(self):
        self.check_rejected(canonical()[:-1])

    def test_crlf_rejected(self):
        self.check_rejected(canonical().replace(b"\n", b"\r\n"))

    def test_bare_cr_rejected(self):
        self.check_rejected(canonical().replace(b"\n", b"\r"))

    def test_trailing_blank_line_rejected(self):
        self.check_rejected(canonical() + b"\n")

    def test_bom_rejected(self):
        self.check_rejected(b"\xef\xbb\xbf" + canonical())

    def test_non_ascii_rejected(self):
        self.check_rejected(canonical().replace(b"0", b"\xff", 1))

    def test_uppercase_digest_rejected(self):
        self.check_rejected(b"A" + canonical()[1:])

    def test_non_hex_digest_rejected(self):
        self.check_rejected(b"g" + canonical()[1:])

    def test_one_space_separator_rejected(self):
        self.check_rejected(canonical().replace(b"  ", b" ", 1))

    def test_three_space_separator_rejected(self):
        self.check_rejected(canonical().replace(b"  ", b"   ", 1))

    def test_wrong_filename_case_rejected(self):
        self.check_rejected(canonical().replace(b"LedgerDiffLite", b"ledgerDiffLite", 1))

    def test_space_padded_filename_rejected(self):
        self.check_rejected(canonical().replace(b"LedgerDiffLite.exe", b"LedgerDiffLite.exe ", 1))

    def test_embedded_null_rejected(self):
        self.check_rejected(canonical().replace(b"L", b"\x00", 1))

    def test_unsupported_input_types_rejected(self):
        for obj in ("ascii", bytearray(canonical()), memoryview(canonical()), None):
            with self.subTest(value=type(obj).__name__):
                self.check_rejected(obj)

    def test_duplicate_expected_names_rejected(self):
        with self.assertRaises(CanonicalInventoryError):
            parse_canonical_inventory(canonical(), NAMES[:5] + (NAMES[0],))

    def test_non_ascii_expected_name_rejected(self):
        with self.assertRaises(CanonicalInventoryError):
            parse_canonical_inventory(canonical(), ("café.exe",))

    def test_invalid_expected_extension_rejected(self):
        with self.assertRaises(CanonicalInventoryError):
            parse_canonical_inventory(canonical(), ("bad.dll",))

    def test_no_implicit_newline_normalization(self):
        self.check_rejected(canonical().replace(b"\n", b"\x0b"))


if __name__ == "__main__":
    unittest.main()
