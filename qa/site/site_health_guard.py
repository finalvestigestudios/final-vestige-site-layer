#!/usr/bin/env python3
"""Read-only production health guard for sanitized WordPress inventory exports.

Input is a locally supplied JSON snapshot; there are no HTTP requests, secrets,
CMS writes, plugin actions, or local persistence. Findings are not 404 claims.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

NAV_LINK = re.compile(r'<!--\s*wp:navigation-link\s+(\{[^\n]*?\})\s*/-->')
TRANSIENT_HINT = re.compile(r'(?:one[- ]shot|predeploy|(?:attach )?probe)', re.I)


def route(url: str, host: str = "finalvestige.com") -> str | None:
    if not isinstance(url, str) or not url.strip():
        return None
    u = urlsplit(url.strip())
    if u.scheme and u.scheme not in ("http", "https"):
        return None
    if u.netloc and u.netloc.lower() not in (host, "www." + host):
        return None
    if not u.netloc and not url.startswith("/"):
        return None
    return u.path.rstrip("/") or "/"


def nav_links(markup: str) -> list[dict]:
    links = []
    for m in NAV_LINK.finditer(markup):
        try:
            block = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(block, dict):
            links.append({"label": block.get("label", ""), "url": block.get("url", "")})
    return links


def check(snapshot: dict) -> dict:
    """Return findings, not actions. Input can contain only harmless metadata."""
    if not isinstance(snapshot, dict):
        raise ValueError("Snapshot must be an object")
    host = snapshot.get("hostname", "finalvestige.com")
    items = snapshot.get("content", [])
    nav = nav_links(snapshot.get("navigation_markup", ""))
    plugins = snapshot.get("plugins", [])
    settings = snapshot.get("settings", {})
    if not isinstance(items, list) or not isinstance(plugins, list):
        raise ValueError("content and plugins must be lists")
    known = {}
    for item in items:
        dest = route(item.get("published_url") or item.get("intended_url") or "", host)
        if dest:
            known[dest] = {"status": item.get("status", "unknown"), "id": item.get("id")}
    findings: list[dict] = []

    def add(severity: str, code: str, **detail) -> None:
        findings.append({"severity": severity, "code": code, **detail})

    for link in nav:
        dest = route(link["url"], host)
        if dest is None:
            continue
        item = known.get(dest)
        if item and item["status"] != "publish":
            add("P1", "navigation-unpublished", label=link["label"],
                path=dest, destination_status=item["status"])
        elif not item and not any(dest == p or dest.startswith(p + "/") for p in snapshot.get("dynamic_prefixes", [])):
            add("REVIEW", "navigation-not-in-inventory", label=link["label"], path=dest)

    for path in snapshot.get("critical_routes", ["/", "/focus", "/dispatch", "/free-resources"]):
        dest = route(path, host)
        if known.get(dest, {}).get("status") != "publish":
            add("P1", "critical-route-not-published-in-snapshot", path=dest)
    if not any(route(link["url"], host) == "/focus" for link in nav):
        add("P1", "focus-navigation-missing")

    for plugin in plugins:
        if plugin.get("status") != "active":
            continue
        label = plugin.get("name", "unknown")
        if plugin.get("update_available") is True:
            add("REVIEW", "plugin-update-available", plugin=label,
                version=plugin.get("version"), new_version=plugin.get("new_version"))
        if TRANSIENT_HINT.search(label) or label in snapshot.get("review_plugin_names", []):
            add("REVIEW", "temporary-sounding-active-plugin", plugin=label)

    site = settings.get("site_info", {})
    reading = settings.get("reading", {})
    privacy = settings.get("privacy", {})
    identity = settings.get("identity", {})
    general = settings.get("general", {})
    if site.get("is_private") is True or privacy.get("blog_public", reading.get("blog_public")) == 0:
        add("P0", "search-visibility-private")
    if identity.get("site_icon") == 0:
        add("REVIEW", "site-icon-unset")
    if identity.get("site_logo") == 0:
        add("REVIEW", "site-logo-unset")
    expected = snapshot.get("expected_brand")
    if expected and general.get("blogname") and general["blogname"].casefold() != expected.casefold():
        add("REVIEW", "site-name-brand-mismatch", configured=general["blogname"], expected=expected)

    return {"hostname": host, "content_items": len(items), "navigation_links": len(nav),
            "active_plugins": sum(p.get("status") == "active" for p in plugins),
            "findings": findings,
            "limitations": [
                "WordPress inventory membership is not an HTTP status, redirect or Google indexing test",
                "Plugin names and pending updates are review flags, not proven vulnerabilities",
                "A site logo may be rendered by the theme even when WP Identity fields are unset",
            ]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="Local sanitized JSON; never stores credentials")
    parser.add_argument("--strict", action="store_true", help="Nonzero exit for P0/P1 findings")
    args = parser.parse_args(argv)
    result = check(json.loads(args.snapshot.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))
    return int(args.strict and any(f["severity"] in ("P0", "P1") for f in result["findings"]))


if __name__ == "__main__":
    raise SystemExit(main())
