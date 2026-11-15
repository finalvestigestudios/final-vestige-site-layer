"""Offline Jetpack backup-warning classifier; never certifies restore readiness.

Input is a sanitized JSON object with a ``logs`` list from a *read-only*
Jetpack Backup logs query. Never store raw site logs or subscriber data in Git.
The tool has no network, credentials, or WordPress interaction.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ENCODING = re.compile(
    r"connection encoding and table charset mismatch.*?table charset:\s*`?([\w-]+)`?"
    r"\s*,\s*connection charset:\s*`?([\w-]+)`?",
    re.IGNORECASE,
)


def audit(snapshot: object) -> dict:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("logs"), list):
        return {"status": "UNKNOWN", "reason": "Missing structured backup logs; no approval"}
    warnings = 0
    affected_jobs: set[str] = set()
    kinds: set[str] = set()
    for entry in snapshot["logs"]:
        if not isinstance(entry, dict) or entry.get("severity") not in {"warn", "warning", "error"}:
            continue
        if entry.get("feature") not in {"vaultpress-backup", "jetpack-backup"}:
            continue
        msg = entry.get("message")
        if not isinstance(msg, str):
            continue
        match = ENCODING.search(msg)
        if not match or match.group(1).lower() == match.group(2).lower():
            continue
        warnings += 1
        if entry.get("client_id") is not None:
            affected_jobs.add(str(entry["client_id"]))
        kinds.add(f"{match.group(2).lower()}_to_{match.group(1).lower()}")
    if warnings:
        return {
            "status": "RESTORE_FIDELITY_REVIEW",
            "warning_events": warnings,
            "distinct_jobs_with_warning": len(affected_jobs),
            "charset_pairs": sorted(kinds),
            "meaning": "Potential encoding mismatch; not proof of corrupted backups",
            "next_step": "Owner-approved isolated restore and byte/Unicode comparison; no production restore",
        }
    return {
        "status": "NO_MATCH_IN_SUPPLIED_LOGS",
        "warning_events": 0,
        "meaning": "A bounded log sample is not proof of a good backup or successful restore",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("snapshot", type=Path, help="Sanitized read-only Jetpack backup log JSON")
    args = ap.parse_args()
    result = audit(json.loads(args.snapshot.read_text(encoding="utf-8")))
    print(json.dumps(result, sort_keys=True))
    return {"NO_MATCH_IN_SUPPLIED_LOGS": 0, "RESTORE_FIDELITY_REVIEW": 1, "UNKNOWN": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
