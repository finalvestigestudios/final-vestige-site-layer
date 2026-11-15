"""Fail-closed parser for R408's six-app source-smoke child receipt.

The receipt is a source-only diagnostic, never approval to publish executables.
Read bounded bytes from an owner-private file; do not display untrusted child
output, paths, customer labels, or errors to an operator.
"""
from __future__ import annotations

import json

EXPECTED_APPS = ("ledger", "invoices", "spend", "policy", "grants", "procurement")
MAX_RECEIPT_BYTES = 4096
_STATUS_KEYS = frozenset({"app", "normal", "optimized"})
_TOP_KEYS = frozenset({
    "schema", "source_sha256", "evidence", "tests", "passed", "required",
    "release_authorized",
})


class SourceSmokeReceiptError(ValueError):
    """Only fixed, customer-data-free messages are exposed."""


def require_six_app_smokes(raw: bytes) -> int:
    """Prove all twelve actual R408 mode statuses, not only process exit 0.

    This cross-check does not authenticate the child code. Git checkout review,
    independent QD and native Windows release verification remain mandatory.
    """
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_RECEIPT_BYTES:
        raise SourceSmokeReceiptError("Six-app source smoke receipt rejected")
    parse_failed = False
    try:
        item = json.loads(raw)
    except (ValueError, UnicodeError):
        parse_failed = True
    if parse_failed:
        raise SourceSmokeReceiptError("Six-app source smoke receipt rejected")
    if (type(item) is not dict or set(item) != _TOP_KEYS
            or item["schema"] != "fvs-source-smoke-r408-v1"
            or item["evidence"] != "SOURCE_ONLY_NOT_WINDOWS_BINARY"
            or item["release_authorized"] is not False
            or type(item["passed"]) is not int or item["passed"] != 12
            or type(item["required"]) is not int or item["required"] != 12
            or type(item["source_sha256"]) is not str
            or len(item["source_sha256"]) != 64
            or not all(c in "0123456789abcdef" for c in item["source_sha256"])
            or type(item["tests"]) is not list or len(item["tests"]) != 6):
        raise SourceSmokeReceiptError("Six-app source smoke receipt rejected")
    for expected, result in zip(EXPECTED_APPS, item["tests"]):
        if (type(result) is not dict or set(result) != _STATUS_KEYS
                or result["app"] != expected or result["normal"] != "pass"
                or result["optimized"] != "pass"):
            raise SourceSmokeReceiptError("Six-app source smoke receipt rejected")
    return 12
