"""Offline, read-only Focus Fieldbook funnel consistency preflight.

Input is a manually sanitized snapshot of authorized WordPress READ responses.
No network access, WordPress mutations, token handling, or subscriber imports.
This checks CMS configuration, NOT rendered pages or actual email delivery.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

FOCUS_PATH = "/focus/"
RETIRED = {
    "/72-hours-without-the-tap/",
    "/collection/water-resilience-field-manual/",
}


def _as_content(page: dict) -> str:
    content = page.get("content", "")
    if isinstance(content, dict):
        content = content.get("raw", "")
    return content if isinstance(content, str) else ""


def _urls(markup: str) -> set[str]:
    """Collect URLs from serialized Gutenberg attributes and HTML anchors."""
    return set(re.findall(r'\b(?:href|url)=["\']([^"\']+)', markup)) | set(
        re.findall(r'"url"\s*:\s*"([^"]+)"', markup)
    )


def _path(url: str) -> str:
    if not url:
        return ""
    # Accept relative site URLs and absolute HTTPS URLs; do not follow links.
    p = urlparse(url)
    if p.scheme and p.scheme != "https":
        return ""
    return p.path or "/"


def inspect(snapshot: dict) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []

    def add(level: str, code: str, message: str) -> None:
        findings.append({"level": level, "code": code, "message": message})

    pages = snapshot.get("pages", {})
    focus = pages.get("focus", {})
    home = pages.get("home", {})
    dispatch = pages.get("dispatch", {})
    nav = snapshot.get("navigation", {})
    media = snapshot.get("media", {})
    newsletter = snapshot.get("newsletter", {})
    retired = snapshot.get("retired_pages", {})
    evidence = snapshot.get("delivery_evidence", {})
    focus_html = _as_content(focus)
    home_html = _as_content(home)
    dispatch_html = _as_content(dispatch)
    nav_html = _as_content(nav)

    if focus.get("status") != "publish":
        add("P1", "FOCUS_NOT_PUBLISHED", "The Focus landing page is not published in the CMS snapshot.")
    if home.get("status") != "publish":
        add("P1", "HOME_NOT_PUBLISHED", "The homepage is not published in the CMS snapshot.")
    if dispatch.get("status") != "publish":
        add("P1", "DISPATCH_NOT_PUBLISHED", "The Dispatch is not published in the CMS snapshot.")

    if "wp:jetpack/subscriptions" not in focus_html:
        add("P1", "FOCUS_NO_FORM", "Focus page has no serialized Jetpack subscription block.")
    if focus_html.count("wp:jetpack/subscriptions") > 1:
        add("P1", "FOCUS_DUPLICATE_FORM", "Focus page has multiple Jetpack subscription blocks.")
    if "wp:jetpack/subscriptions" not in dispatch_html:
        add("P2", "DISPATCH_NO_FORM", "Dispatch has no Jetpack subscription block.")

    if FOCUS_PATH not in {_path(u) for u in _urls(home_html)}:
        add("P1", "HOME_CTA_MISSING", "Homepage markup contains no link to /focus/.")
    if FOCUS_PATH not in {_path(u) for u in _urls(nav_html)}:
        add("P1", "NAV_CTA_MISSING", "Navigation markup contains no link to /focus/.")

    nav_paths = {_path(u) for u in _urls(nav_html)}
    for retired_path in sorted(RETIRED):
        if retired.get(retired_path) == "draft" and retired_path in nav_paths:
            add("P1", "RETIRED_NAV_LINK", f"Published navigation points at draft page {retired_path}.")

    if not newsletter.get("subscriptions", False):
        add("P1", "SUBSCRIPTIONS_DISABLED", "Newsletter master subscription switch is disabled.")
    welcome = newsletter.get("welcome_message", "")
    pdf_url = media.get("source_url", "")
    if not pdf_url or not pdf_url.lower().endswith(".pdf"):
        add("P1", "PDF_MISSING", "Media snapshot has no PDF source URL.")
    else:
        if media.get("mime_type") != "application/pdf":
            add("P1", "PDF_TYPE", "Media metadata is not application/pdf.")
        if pdf_url not in welcome:
            add("P1", "WELCOME_PDF_MISMATCH", "Welcome email does not contain the designated PDF URL.")
        if pdf_url not in focus_html:
            add("P1", "FOCUS_PDF_MISMATCH", "Focus page does not contain the designated PDF URL.")
    if re.search(r'72 Hours Without the Tap|water.resilience.field.manual', welcome, re.I):
        add("P1", "LEGACY_WELCOME", "Welcome email still promotes a retired water guide.")

    # Source-level behavior observation only, NOT a claim of browser-rendered UX.
    if "if(q&&bad.indexOf(q)<0){show();}" in focus_html:
        add("P2", "QUERY_SUCCESS_HEURISTIC", "Landing-page script may display download success based only on an unverified query parameter; browser-confirm before interpreting this as opt-in proof.")

    for proof in ("public_form_submit", "confirmation_received", "confirmation_clicked", "welcome_received", "public_pdf_download"):
        if evidence.get(proof) is not True:
            add("HOLD", "DELIVERY_NOT_VERIFIED", f"No independent verification for {proof}; the funnel must not be labeled end-to-end passed.")
            break
    if not evidence.get("mobile_rendered"):
        add("INFO", "MOBILE_NOT_VERIFIED", "No actual mobile rendering/keyboard evidence attached to snapshot.")
    return findings


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("snapshot", type=Path, help="Sanitized read-only WordPress snapshot JSON")
    p.add_argument("--strict", action="store_true", help="Exit 1 on any P1 finding, never on HOLD alone")
    args = p.parse_args()
    obj = json.loads(args.snapshot.read_text(encoding="utf-8"))
    findings = inspect(obj)
    for f in findings:
        print(f"{f['level']} {f['code']}: {f['message']}")
    if not findings:
        print("No snapshot-level findings; this DOES NOT prove browser or email delivery.")
    if args.strict and any(f["level"] == "P1" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
