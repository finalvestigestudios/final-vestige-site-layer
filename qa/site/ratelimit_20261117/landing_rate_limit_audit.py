"""Offline, read-only assessment of SANITIZED WordPress hosting access-log rows.

Stdlib only. Never contacts the website, writes files, changes rate limits, or
claims that a user-agent identifies an authenticated crawler or real visitor.

Usage: python landing_rate_limit_audit.py < redacted_web_log_response.json
Input: WordPress wpcom_site_logs_list web response, its structuredContent, or
       an array of paginated results. The producer must remove IPs/referers first.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from typing import Any
from urllib.parse import urlsplit

ENTRY = {"/", "/focus/", "/dispatch/", "/collection/"}
DISCOVERY = {"/robots.txt", "/sitemap.xml", "/news-sitemap.xml", "/wp-sitemap.xml"}
SENSITIVE = re.compile(
    r"(?:^|/)(?:\.env|\.git|vendor|node_modules|composer\.(?:json|lock)|"
    r"package\.json|yarn\.lock|config(?:uration)?\.php|appsettings\.json|"
    r"wp-config\.php|dockerfile|auth\.json)(?:/|$)|^/api/(?:config|settings)(?:/|$)",
    re.IGNORECASE,
)
CLAIMED_BOTS = ("googlebot", "bingbot", "perplexitybot", "claudebot", "chatgpt-user", "semrushbot", "gptbot")


def normalize_path(value: str) -> str:
    """Canonicalize only for classification; never follow/alter a URL."""
    if not isinstance(value, str) or not value.startswith("/") or "\x00" in value:
        raise ValueError("Expected sanitized, root-relative request_path")
    path = urlsplit(value).path
    if path != "/":
        path = path.rstrip("/") + ("/" if "." not in path.rsplit("/", 1)[-1] else "")
    return path.lower()


def category(path: str) -> str:
    if SENSITIVE.search(path):
        return "sensitive_probe_pattern"
    if path in DISCOVERY or path.endswith("sitemap.xml"):
        return "discovery"
    if path in ENTRY:
        return "conversion_entry"
    return "other_public_or_unknown"


def ua_claim(user_agent: Any) -> str:
    """An untrusted string claim, NEVER crawler/human authentication."""
    if not isinstance(user_agent, str):
        return "unknown"
    lower = user_agent.lower()
    for term in CLAIMED_BOTS:
        if term in lower:
            return f"claims_{term.replace('-', '_')}"
    return "other_or_unknown"


def pages_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        pages = payload
    elif isinstance(payload, dict):
        pages = [payload]
    else:
        raise ValueError("Expected log-response object or list")
    result = []
    for item in pages:
        if not isinstance(item, dict):
            raise ValueError("Every page must be an object")
        data = item.get("structuredContent", item)
        if not isinstance(data, dict) or data.get("type") != "web" or not isinstance(data.get("entries"), list):
            raise ValueError("Expected web log response with entries array")
        result.append(data)
    return result


def audit(payload: Any) -> dict[str, Any]:
    pages = pages_from_payload(payload)
    cats: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    entry_paths: Counter[str] = Counter()
    discovery_paths: Counter[str] = Counter()
    claims: Counter[str] = Counter()
    examined = 0
    is_complete = True
    windows = []
    declared_totals = []
    sensitive_successes = 0
    for page in pages:
        rows = page["entries"]
        total = page.get("total")
        # A partial listing may never be mistaken for a census.
        if page.get("total_is_lower_bound"):
            is_complete = False
        if isinstance(total, int):
            declared_totals.append(total)
        if page is pages[-1] and page.get("next_cursor"):
            is_complete = False
        windows.append({"start": page.get("window_start"), "end": page.get("window_end")})
        for record in rows:
            if not isinstance(record, dict) or not isinstance(record.get("status"), int):
                raise ValueError("Malformed log entry or status")
            if record.get("request_type") not in {"GET", "HEAD", "POST", "PUT", "DELETE"}:
                raise ValueError("Missing or invalid request method")
            path = normalize_path(record.get("request_path"))
            status = str(record["status"])
            group = category(path)
            examined += 1
            cats[group] += 1
            status_counts[status] += 1
            if group == "sensitive_probe_pattern" and 200 <= record["status"] < 300:
                sensitive_successes += 1
            if status == "429":
                claims[ua_claim(record.get("user_agent"))] += 1
                if group == "conversion_entry":
                    entry_paths[path] += 1
                if group == "discovery":
                    discovery_paths[path] += 1

    if declared_totals and (len(set(declared_totals)) != 1 or declared_totals[0] != examined):
        is_complete = False
    if len({(w["start"], w["end"]) for w in windows}) != 1:
        is_complete = False
    return {
        "schema": "fv_rate_limit_visibility_v1",
        "records_examined": examined,
        "page_count": len(pages),
        "log_enumeration_complete": is_complete,
        "windows": windows,
        "status_counts_in_supplied_sample": dict(sorted(status_counts.items())),
        "path_categories_in_supplied_sample": dict(sorted(cats.items())),
        "rate_limited_conversion_entries": dict(sorted(entry_paths.items())),
        "sensitive_probe_2xx_needing_manual_review": sensitive_successes,
        "rate_limited_discovery_paths": dict(sorted(discovery_paths.items())),
        "unverified_user_agent_claims_on_429": dict(sorted(claims.items())),
        "admission": "REVIEW" if entry_paths or discovery_paths or sensitive_successes else "NO_REVIEW_TRIGGER_IN_SUPPLIED_SAMPLE",
        "not_established": [
            "true visitor identity or failed customer session",
            "crawler authentication, search ranking loss, or cause of throttling",
            "newsletter delivery, checkout success, attributed purchase or realized revenue",
        ],
        "required_follow_up": "Security owner correlates policy decision and request identity; independently test authorized browser paths. No automatic allowlisting or live settings changes.",
    }


def main() -> None:
    payload = json.load(sys.stdin)
    print(json.dumps(audit(payload), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
