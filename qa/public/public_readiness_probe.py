#!/usr/bin/env python3
"""Bounded, first-party-only, public GET smoke checks; no subscriptions or writes."""
from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = "https://finalvestige.com"
PDF = "/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"
ROUTES = (
    ("homepage", "/", "html", b"final vestige"),
    ("focus", "/focus/", "html", b"focus fieldbook"),
    ("dispatch", "/dispatch/", "html", b"the dispatch"),
    ("fieldbook_pdf", PDF, "pdf", None),
)
LEGACY_ROUTES = (
    ("old_water_planner", "/72-hours-without-the-tap/"),
    ("old_water_manual", "/collection/water-resilience-field-manual/"),
)
HTML_LIMIT = 262144
PDF_LIMIT = 1048576


def first_party(url: str) -> bool:
    parts = urlparse(url)
    return parts.scheme == "https" and parts.hostname in ("finalvestige.com", "www.finalvestige.com") and not parts.username and not parts.password


class FirstPartyRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if not first_party(newurl):
            raise URLError("redirect left permitted HTTPS host")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


class NoFollowRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def probe(name: str, path: str, kind: str, marker: bytes | None = None, opener=None) -> dict:
    """GET with size cap; never submits a form or logs an email address."""
    url = BASE + path
    result = {"name": name, "url": url, "outcome": "INCONCLUSIVE"}
    if not first_party(url):
        return {**result, "reason": "URL not first-party HTTPS"}
    opener = opener or build_opener(FirstPartyRedirects())
    request = Request(url, headers={"User-Agent": "FinalVestige-QA-read-only/1.0", "Accept": "text/html,application/pdf"}, method="GET")
    try:
        with opener.open(request, timeout=10) as response:
            code = response.getcode()
            final = response.geturl()
            content_type = response.headers.get("Content-Type", "").lower().split(";", 1)[0].strip()
            if not first_party(final):
                return {**result, "reason": "final URL left first-party HTTPS"}
            result.update(status=code, final_url=final, content_type=content_type)
            if code != 200:
                return {**result, "outcome": "FAIL", "reason": "expected HTTP 200"}
            max_bytes = PDF_LIMIT if kind == "pdf" else HTML_LIMIT
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                return {**result, "reason": "response exceeded read limit; not verified"}
            if kind == "pdf":
                if content_type != "application/pdf" or not data.startswith(b"%PDF-"):
                    return {**result, "outcome": "FAIL", "reason": "not a valid PDF response signature/type"}
                if b"%%EOF" not in data[-1024:]:
                    return {**result, "outcome": "FAIL", "reason": "missing PDF EOF marker"}
                if len(data) != 599946:
                    return {**result, "outcome": "FAIL", "reason": "PDF bytes differ from WordPress media ID 1737"}
                return {**result, "outcome": "PASS", "bytes": len(data), "note": "PDF signature, EOF and media length; page count NOT verified"}
            if content_type != "text/html":
                return {**result, "outcome": "FAIL", "reason": "not HTML content type"}
            if b"<html" not in data[:8192].lower():
                return {**result, "outcome": "FAIL", "reason": "HTML document marker missing"}
            if marker and marker not in data.lower():
                return {**result, "outcome": "FAIL", "reason": "expected content text missing from bounded response"}
            return {**result, "outcome": "PASS", "bytes_checked": len(data), "note": "HTTP and HTML source only; NOT browser or form verification"}
    except HTTPError as exc:
        result.update(outcome="FAIL", status=exc.code, reason="HTTP error")
        if 300 <= exc.code < 400 and exc.headers:
            location = urljoin(url, exc.headers.get("Location", ""))
            if first_party(location):
                result["redirect_location"] = location
        return result
    except (URLError, OSError, TimeoutError) as exc:
        # Do not print exception payloads: URLs/tokens from servers may be sensitive.
        return {**result, "reason": "public GET unavailable: " + type(exc).__name__}


def inspect_legacy(name: str, path: str, opener=None) -> dict:
    """One optional GET; classify endpoint without claiming an ideal redirect."""
    result = probe(name, path, "html", opener=opener or build_opener(NoFollowRedirects()))
    result["outcome"] = "OBSERVED" if result.get("status") is not None else "INCONCLUSIVE"
    result["note"] = "Review the old URL for entitlement-preserving 301/410 choice; never redirect water content blindly to Focus."
    return result


def main(argv=None) -> int:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--legacy", action="store_true", help="also classify retired water URLs; no destination policy is assumed")
    opts = args.parse_args(argv)
    checks = [probe(*row) for row in ROUTES]
    if opts.legacy:
        checks.extend(inspect_legacy(*row) for row in LEGACY_ROUTES)
    print(json.dumps({"read_only": True, "checks": checks, "scope": "public GET only; no JavaScript, subscriber verification or email delivery"}, indent=2))
    core = checks[:len(ROUTES)]
    return 1 if any(x["outcome"] == "FAIL" for x in core) else 2 if any(x["outcome"] == "INCONCLUSIVE" for x in core) else 0


if __name__ == "__main__":
    sys.exit(main())
