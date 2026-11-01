#!/usr/bin/env python3
"""Offline, read-only comparator of WP canonical URL and Jetpack backup activity URL.

Consumes a sanitized local JSON snapshot, makes no HTTP/API calls, changes no files,
checks only domain/scheme metadata, and never claims a restore defect from metadata.
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlsplit


def _url(value):
    if not isinstance(value, str):
        raise ValueError("URL must be a string")
    u = urlsplit(value.strip())
    if (u.scheme not in {"http", "https"} or not u.hostname or u.username
            or u.password or u.query or u.fragment or u.path not in ("", "/")):
        raise ValueError("Expected an HTTP(S) root URL without credentials, query, or fragment")
    try:
        port = u.port
    except ValueError as exc:
        raise ValueError("Invalid URL port") from exc
    host = u.hostname.casefold().rstrip(".")
    return {"scheme": u.scheme, "host": host, "port": port}


def _canonical(snapshot):
    settings = snapshot.get("settings", {})
    general = settings.get("general", settings)
    if not isinstance(general, dict):
        raise ValueError("Expected settings.general mapping")
    h, s = _url(general.get("home")), _url(general.get("siteurl"))
    if h != s:
        return None, "CANONICAL_SETTINGS_DISAGREE"
    return h, None


def check(snapshot):
    """Return a compact, evidence-limited verdict; do not echo complete input."""
    if not isinstance(snapshot, dict):
        raise ValueError("Expected object snapshot")
    canonical, problem = _canonical(snapshot)
    if problem:
        return {"classification": "REVIEW", "reason": problem, "examined_backups": 0}
    activity = snapshot.get("activity", {})
    if not isinstance(activity, dict):
        raise ValueError("Expected activity mapping")
    rows = activity.get("activities", [])
    if not isinstance(rows, list):
        raise ValueError("Expected activity.activities list")
    matches = mismatched_scheme = mismatched_host = malformed = 0
    examples = []
    for row in rows[:100]:
        if not isinstance(row, dict):
            malformed += 1
            continue
        backup_info = (row.get("object") or {}).get("backup_info") or {}
        raw = backup_info.get("backup_stats")
        if raw is None:
            continue
        try:
            stats = json.loads(raw) if isinstance(raw, str) else raw
            if not isinstance(stats, dict):
                raise ValueError("Expected backup stats mapping")
            b = _url(stats.get("site_url"))
        except (TypeError, ValueError, json.JSONDecodeError):
            malformed += 1
            continue
        matches += 1
        if (b["host"], b["port"]) != (canonical["host"], canonical["port"]):
            mismatched_host += 1
            label = "backup_host_or_port_differs"
        elif b["scheme"] != canonical["scheme"]:
            mismatched_scheme += 1
            label = "backup_scheme_differs"
        else:
            label = "matches"
        if len(examples) < 7:
            examples.append({"date": row.get("date"), "result": label,
                             "backup_scheme": b["scheme"]})
    if matches == 0:
        status, reason = "INSUFFICIENT_DATA", "No parsable backup metadata"
    elif mismatched_host:
        status, reason = "REVIEW", "Backup hostname/port differs from current site settings"
    elif mismatched_scheme:
        status, reason = "REVIEW", "Backup scheme metadata differs from current site settings"
    elif malformed:
        status, reason = "REVIEW", "Some backup metadata malformed or unparseable"
    else:
        status, reason = "MATCH", "Observed backup metadata matches current site settings"
    return {"classification": status, "reason": reason,
            "canonical_scheme": canonical["scheme"],
            "examined_backups": matches, "scheme_mismatches": mismatched_scheme,
            "host_or_port_mismatches": mismatched_host, "malformed": malformed,
            "samples": examples,
            "interpretation": "Metadata comparison only: not a restore, SSL, uptime, or frontend test."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", help="Path to sanitized JSON snapshot, or '-' for stdin")
    args = parser.parse_args(argv)
    try:
        if args.snapshot == "-":
            obj = json.load(sys.stdin)
        else:
            with open(args.snapshot, encoding="utf-8") as fp:
                obj = json.load(fp)
        result = check(obj)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"classification": "INVALID_INPUT", "error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
