#!/usr/bin/env python3
"""Offline audit of subscriber cadence copy. No network, no WordPress writes.

The tool reports copy inconsistency for editorial review, not an actual
sending-frequency failure. Its snapshot contains only de-identified copy.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FIXED = re.compile(r"\b(?:one|1)\s+emails?\s+(?:a|per)\s+week\b|\b(?:once\s+a\s+week|weekly|every\s+week)\b", re.I)
EVENT = re.compile(r"\b(?:when\s+(?:we|there(?:'s| is)|a|new)|as\s+we)\b.{0,100}\b(?:publish|publishing|new|investigation|find|archive)\b|\bwhen\s+we\s+publish\b", re.I | re.S)
TEXT_FIELDS = ("home_visible", "dispatch_visible", "dispatch_seo", "welcome_message")


def classify(text):
    if not isinstance(text, str):
        return "missing"
    text = re.sub(r"<[^>]+>", " ", text).strip()
    if not text:
        return "missing"
    fixed, event = bool(FIXED.search(text)), bool(EVENT.search(text))
    if fixed and event:
        return "mixed"
    if fixed:
        return "fixed_weekly"
    if event:
        return "event_driven"
    return "unspecified"


def evaluate(snapshot):
    if not isinstance(snapshot, dict):
        raise ValueError("Snapshot must be a JSON object")
    fields = {key: classify(snapshot.get(key)) for key in TEXT_FIELDS}
    fixed = [k for k, v in fields.items() if v in ("fixed_weekly", "mixed")]
    event = [k for k, v in fields.items() if v in ("event_driven", "mixed")]
    # None of this proves cadence, list eligibility, or email delivery.
    if not any(v not in ("missing", "unspecified") for v in fields.values()):
        status, reason = "INCONCLUSIVE", "No explicit cadence promise available to compare."
    elif fixed and event:
        status, reason = "REVIEW_CADENCE", "Fixed weekly and publish-driven promises coexist across subscriber surfaces."
    elif fixed and snapshot.get("email_new_posts_by_default") is False:
        status, reason = "REVIEW_UNVERIFIED_WEEKLY", "Weekly promise exists; automatic new-post emailing is disabled (manual weekly sends may still occur)."
    else:
        status, reason = "NO_CONFLICT_DETECTED", "No conflicting cadence promises detected in the supplied copy."
    return {
        "status": status,
        "reason": reason,
        "surface_classification": fields,
        "fixed_weekly_surfaces": fixed,
        "publish_driven_surfaces": event,
        "wordpress_write_performed": False,
        "email_delivery_verified": False,
        "browser_copy_verified": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True, help="Local sanitized JSON snapshot; never credentials or emails")
    args = parser.parse_args(argv)
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = evaluate(snapshot)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as e:
        print(json.dumps({"status": "ERROR", "error": str(e), "wordpress_write_performed": False}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
