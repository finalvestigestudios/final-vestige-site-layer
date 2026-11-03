"""Fail closed on mutable GitHub Actions tags in the six-app INTERNAL CI.

These SHA-1 Git object IDs are immutable action source references, NOT signatures,
malware clearance, or approval to distribute an executable. Verify upgrades
against upstream actions and the repository's independent QD workflow.
This narrow fixed-workflow gate is not a general YAML security scanner.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re
import sys

MAX_WORKFLOW_BYTES = 128 * 1024
APPROVED = {
    "actions/checkout": "08c6903cd8c0fde910a37f88322edcfb5dd907a8",  # v5.0.0 · node24
    "actions/setup-python": "e797f83bcb11b83ae66e0230d6156d7c80228e7c",  # v6.0.0 · node24
    "actions/upload-artifact": "b7c566a772e6b6bfb58ed0dc250532a479d7789f",  # v6.0.0 · node24
}
EXPECTED_COUNTS = {name: 2 for name in APPROVED}
USES = re.compile(r"^\s*(?:-\s*)?uses:\s*(.*?)\s*$")


class ActionPinError(ValueError):
    """Unknown, ambiguous or mutable action could execute in trusted CI."""


def verify_action_pins(source: str) -> int:
    """Require exactly six immutable action calls, with no unknown actions."""
    if (type(source) is not str or "\x00" in source or "\t" in source
            or len(source.encode("utf-8")) > MAX_WORKFLOW_BYTES):
        raise ActionPinError("Invalid desktop workflow")
    counts: Counter[str] = Counter()
    for line in source.splitlines():
        if line.lstrip().startswith("#"):
            continue
        match = USES.match(line)
        if match is None:
            continue
        value = match.group(1).split(" #", 1)[0].strip()
        if value.count("@") != 1:
            raise ActionPinError("Noncanonical GitHub Actions source")
        name, ref = value.split("@", 1)
        if name not in APPROVED or ref != APPROVED[name]:
            raise ActionPinError("Unapproved or mutable GitHub Actions source")
        counts[name] += 1
    if dict(counts) != EXPECTED_COUNTS:
        raise ActionPinError("Missing or duplicated GitHub Actions step")
    return sum(counts.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.workflow.stat().st_size > MAX_WORKFLOW_BYTES:
            raise ActionPinError("Workflow exceeds size limit")
        validated = verify_action_pins(args.workflow.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ActionPinError):
        print("HOLD: immutable six-app CI action custody unavailable", file=sys.stderr)
        return 1
    print(f"PASS: {validated} pinned GitHub Actions steps; NOT a release or QD approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
