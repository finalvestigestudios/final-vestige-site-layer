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
