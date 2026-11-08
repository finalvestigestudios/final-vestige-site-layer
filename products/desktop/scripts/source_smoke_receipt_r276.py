"""Validate the exact six-app source-smoke records in private build evidence.

This is source-only provenance: a passing record is never proof of a Windows
executable, a compliance determination, QD approval or release authorization.
"""
from __future__ import annotations

EXPECTED = (
    ("LedgerDiffLite", "ledger"),
    ("InvoiceTwinScout", "invoices"),
    ("SpendMapLite", "spend"),
    ("PolicyDeltaDesk", "policy"),
    ("GrantAuditStudioPro", "grants"),
    ("ProcureGuardStudioPro", "procurement"),
)
MAX_SYNTHETIC_OUTPUTS = 10000


def valid_source_smoke_records(records: object) -> bool:
    """Require one canonical successful source smoke for each expected engine.

    Reject booleans masquerading as counts, unexpected/private fields, absent
    results, reordered/duplicated products and impossible/oversized counts.
    The runner must separately bind this receipt to tested source bytes.
    """
    if type(records) is not list or len(records) != len(EXPECTED):
        return False
    for record, (app, engine) in zip(records, EXPECTED):
        if (type(record) is not dict
                or set(record) != {"app", "engine", "result", "synthetic_output_count"}
                or type(record["app"]) is not str or record["app"] != app
                or type(record["engine"]) is not str or record["engine"] != engine
                or type(record["result"]) is not str or record["result"] != "PASS"
                or type(record["synthetic_output_count"]) is not int
                or not 1 <= record["synthetic_output_count"] <= MAX_SYNTHETIC_OUTPUTS):
            return False
    return True
