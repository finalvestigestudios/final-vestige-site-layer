"""R159 independent native SpendMap CSV export schema.

A source-bound verifier must not attest an unreviewed extra report column
(e.g. a fabricated payment-approved column) or ambiguous/reordered headers.
This contract is deliberately not imported from engine.spend_map: unexpected
changes to the generator's schema need an explicit human-reviewed update.
"""
from __future__ import annotations

COLUMNS = (
    "vendor_key", "month", "category", "amount", "flag",
    "vendor_month_total", "baseline_median", "history_months",
    "category_history_months", "category_baseline_median", "category_review_flag",
    "gross_charges", "gross_credits", "credit_offset_review",
    "vendor_month_evidence_rows", "vendor_month_evidence_count",
    "vendor_month_evidence_omitted", "vendor_month_evidence_sha256",
    "vendor_month_gross_charges", "vendor_month_gross_credits",
    "vendor_month_offset_review", "source_rows", "source_vendor_labels",
    "vendor_label_variants", "source_sha256",
)

# Parsed CSV records do not capture blank rows, alternate quoting or endings.
# Reproduce the deterministic native wire format independently of the engine.
import csv
import hashlib


class NativeSpendCsvDigest:
    """Bounded streaming UTF-8 BOM / csv.DictWriter CRLF byte-identity check."""

    def __init__(self):
        self._hash = hashlib.sha256()
        self._hash.update(b"\xef\xbb\xbf")
        self.byte_length = 3
        self._writer = csv.DictWriter(self, fieldnames=COLUMNS, lineterminator="\r\n")
        self._writer.writeheader()

    def write(self, text):
        if type(text) is not str:
            raise ValueError("Invalid native SpendMap CSV cell")
        data = text.encode("utf-8")
        self._hash.update(data)
        self.byte_length += len(data)
        return len(text)

    def add_row(self, row):
        self._writer.writerow(row)

    def matches(self, source_bytes):
        return (self.byte_length == len(source_bytes)
                and self._hash.digest() == hashlib.sha256(source_bytes).digest())
