"""R72 fail-closed, privacy-safe case ledger for genuine Apollo WordPress QA.

Every case is recorded at the exact completed milestone; a truncated or
failing browser run can never be represented as a 14/14 admission. No live
WordPress URLs, cookies, auth state, NASA text, CLI output, screenshots or
exception strings are accepted by this format.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
MILESTONES = (
    "STARTED", "HTTP_200", "SOURCE_CUSTODY", "NETWORK_CLEAN",
    "INTERACTION", "AXE", "LAB_METRICS", "PRINT",
    "NO_JS_CONTENT", "PASSED",
)
FAILURE_CLASSES = (
    "ASSERTION", "BROWSER", "NETWORK", "READINESS",
    "PERFORMANCE", "ACCESSIBILITY", "UNKNOWN",
)


class CaseLedger:
    """Atomic immutable-shape progress receipt, with fail-closed admission."""

    def __init__(self, destination: Path):
        self.destination = Path(destination)
        if self.destination.name != "R72_CASE_LEDGER.json":
            raise ValueError("UNEXPECTED_LEDGER_DESTINATION")
        self.expected = [(w, js) for w in WIDTHS for js in (False, True)]
        self.cases = []
        self.active = None
        self.failure = None
        self._save()

    def _save(self):
        complete = len(self.cases) == len(self.expected) and all(
            x["milestone"] == "PASSED" for x in self.cases
        ) and self.failure is None
        payload = {
            "schema": "fv.apollo.r72.case-ledger.v1",
            "release": "STAGING_HOLD",
            "environment": "LOCAL_WORDPRESS_PLAYGROUND_ONLY",
            "total_expected": 14,
            "completed": sum(x["milestone"] == "PASSED" for x in self.cases),
            "all_cases_accepted": complete,
            "production_wordpress_written": False,
            "axe_verified_all_required": False,  # separate axe receipt is required
            "field_cwv_verified": False,
            "cases": self.cases,
            "failure_class": self.failure,
        }
        self.destination.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.destination.with_name(self.destination.name + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        os.replace(tmp, self.destination)

    def begin(self, width: int, javascript: bool):
        if self.active is not None or self.failure is not None:
            raise ValueError("CASE_NOT_CLOSED")
        if type(width) is not int or type(javascript) is not bool:
            raise ValueError("INVALID_CASE_TYPES")
        if len(self.cases) >= len(self.expected) or (width, javascript) != self.expected[len(self.cases)]:
            raise ValueError("UNEXPECTED_CASE_ORDER")
        self.active = len(self.cases)
        self.cases.append({"width": width, "javascript": javascript, "milestone": "STARTED"})
        self._save()

    def advance(self, milestone: str):
        if self.active is None or self.failure is not None:
            raise ValueError("NO_ACTIVE_CASE")
        if milestone not in MILESTONES or milestone in ("STARTED", "PASSED"):
            raise ValueError("UNEXPECTED_MILESTONE")
        row = self.cases[self.active]
        if MILESTONES.index(milestone) <= MILESTONES.index(row["milestone"]):
            raise ValueError("MILESTONE_NOT_MONOTONIC")
        if not row["javascript"] and milestone in ("INTERACTION", "AXE", "LAB_METRICS", "PRINT"):
            raise ValueError("JAVASCRIPT_ONLY_MILESTONE")
        if row["javascript"] and milestone == "NO_JS_CONTENT":
            raise ValueError("WRONG_JAVASCRIPT_MODE")
        row["milestone"] = milestone
        self._save()

    def pass_case(self):
        if self.active is None or self.failure is not None:
            raise ValueError("NO_ACTIVE_CASE")
        row = self.cases[self.active]
        required = "PRINT" if row["javascript"] else "NO_JS_CONTENT"
        if row["milestone"] != required:
            raise ValueError("INCOMPLETE_CASE")
        row["milestone"] = "PASSED"
        self.active = None
        self._save()

    def hold(self, failure_class: str = "UNKNOWN"):
        if failure_class not in FAILURE_CLASSES:
            failure_class = "UNKNOWN"
        self.failure = failure_class
        self._save()

    def require_complete(self):
        receipt = json.loads(self.destination.read_text())
        if not receipt["all_cases_accepted"]:
            raise AssertionError("R72_INCOMPLETE_WORDPRESS_BROWSER_GATE")
        return receipt
