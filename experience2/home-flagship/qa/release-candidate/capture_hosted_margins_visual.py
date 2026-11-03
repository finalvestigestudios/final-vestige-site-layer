#!/usr/bin/env python3
"""Anonymous real-host first-screen visual A/B for the existing Margins repair.

This produces founder-review screenshots from the ALREADY PUBLIC homepage,
with unresolved NYPL image requests blocked. Candidate CSS is added to a
disposable Chromium page only. It never changes production WordPress.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

HOST = "finalvestige.com"
URL = "https://finalvestige.com/"
WIDTHS = (320, 390, 1440)
NYPL_PARTS = ("edit-017-v02-nypl-5003296", "nypl-5003296-original")
HERE = Path(__file__).resolve().parent
# Actual structure: release-candidate/ -> qa/ -> home-flagship/ -> accessibility/
CSS_PATH = HERE.parent.parent / "accessibility" / "margins" / "margin_strip_contrast_safe.css"


def denied(method: str, url: str) -> bool:
    if method != "GET" or not isinstance(url, str):
        return True
    parts = urlsplit(url)
    return parts.scheme not in ("https", "http") or any(
        marker in parts.path.lower() for marker in NYPL_PARTS
    )


def valid_css(css: str) -> bool:
    """Allow the exact narrow, local remedy, not remote assets or substitutions."""
    lower = css.lower()
    required = (
        ".fv-margin-strip--rotator .fv-margin-strip__item",
        "animation-name: fvMarginContrastSafe;",
        "@keyframes fvMarginContrastSafe",
        "visibility: hidden;",
        "opacity: 1;",
        "filter: none;",
        "prefers-reduced-motion: reduce",
    )
    blocked = ("@import", "url(", "<", "!important", "expression(", "@font-face")
    return 100 < len(css) < 5000 and all(s in css for s in required) and not any(
        s in lower for s in blocked
    )


def grade(cases: list[dict]) -> dict:
    expected = set(WIDTHS)
    if not isinstance(cases, list) or len(cases) != len(expected) or {
        c.get("width") for c in cases if isinstance(c, dict)
    } != expected:
        raise ValueError("VIEWPORT_MATRIX_MISSING_OR_DUPLICATE")
    good = all(
        c.get("http") == 200
        and c.get("host") == HOST
        and c.get("flagship") is True
        and c.get("margins") == 72
        and c.get("chapters") == 7
        and c.get("focus_links", 0) >= 1
        and c.get("candidate_active") is True
        and c.get("overflow_before") is False
        and c.get("overflow_after") is False
        and c.get("screenshots", {}).keys() == {"before", "after"}
        and all(isinstance(v, str) and len(v) == 64
                and all(x in "0123456789abcdef" for x in v)
                for v in c["screenshots"].values())
        for c in cases
    )
    return {
        "anonymous_visual_capture": "PASS" if good else "FAIL",
        "actual_browser_zoom_certification": "NOT_TESTED",
        "complete_wcag_22_aa": "HOLD",
        "image_rights": "HOLD",
        "independent_qd": "HOLD",
        "publication_authorization": "HOLD",
        "production_release": "HOLD",
    }


def capture(out: Path, css: str) -> list[dict]:
    from playwright.sync_api import sync_playwright

    results = []
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for width in WIDTHS:
                ctx = browser.new_context(
                    viewport={"width": width, "height": 844},
                    reduced_motion="no-preference",
                    service_workers="block",
                    accept_downloads=False,
                )
                denied_counts = {"non_get": 0, "nypl": 0}

                def route_guard(route):
                    req = route.request
                    if denied(req.method, req.url):
                        denied_counts["non_get" if req.method != "GET" else "nypl"] += 1
                        route.abort()
                    else:
                        route.continue_()

                ctx.route("**/*", route_guard)
                page = ctx.new_page()
                try:
                    response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                    if response is None or urlsplit(page.url).hostname != HOST:
                        raise ValueError("UNEXPECTED_REDIRECT_OR_NO_RESPONSE")
                    page.locator("[data-fv-home-flagship]").wait_for(
                        state="attached", timeout=15000)
                    page.wait_for_timeout(350)
                    margins = page.locator(".fv-margin-strip__item").count()
                    chapters = page.locator('.fv-hf__chapter-nav a[href^="#"]').count()
                    focus = page.locator('a[href*="/focus/"]').count()
                    if (margins, chapters) != (72, 7):
                        raise ValueError("SOURCE_MARKERS_DRIFT")
                    before_overflow = page.evaluate(
                        "() => document.documentElement.scrollWidth > "
                        "document.documentElement.clientWidth + 2")
                    before_name = f"live_{width}_before.png"
                    after_name = f"live_{width}_candidate.png"
                    before = page.screenshot(
                        path=str(out / before_name), full_page=False, timeout=20000)
                    page.add_style_tag(content=css)
                    page.wait_for_timeout(200)
                    active = page.evaluate(
                        "() => getComputedStyle(document.querySelector("
                        "'.fv-margin-strip__item')).animationName "
                        "=== 'fvMarginContrastSafe'")
                    after_overflow = page.evaluate(
                        "() => document.documentElement.scrollWidth > "
                        "document.documentElement.clientWidth + 2")
                    after = page.screenshot(
                        path=str(out / after_name), full_page=False, timeout=20000)
                    results.append({
                        "width": width,
                        "host": HOST,
                        "http": response.status,
                        "flagship": True,
                        "margins": margins,
                        "chapters": chapters,
                        "focus_links": focus,
                        "candidate_active": active,
                        "overflow_before": before_overflow,
                        "overflow_after": after_overflow,
                        "blocked_non_get": denied_counts["non_get"],
                        "blocked_nypl": denied_counts["nypl"],
                        "screenshots": {
                            "before": hashlib.sha256(before).hexdigest(),
                            "after": hashlib.sha256(after).hexdigest(),
                        },
                        "filenames": {"before": before_name, "after": after_name},
                    })
                    print(f"checked {width}px: host={response.status}, "
                          f"margins={margins}, chapters={chapters}, "
                          f"candidate={active}, overflow={after_overflow}",
                          flush=True)
                finally:
                    ctx.close()
        finally:
            browser.close()
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("visual_receipt"))
    args = parser.parse_args()
    result_dir = args.output_dir
    result_dir.mkdir(parents=True, exist_ok=True)
    try:
        css = CSS_PATH.read_text(encoding="utf-8")
        if not valid_css(css):
            raise ValueError("CSS_CANDIDATE_MISSING_OR_UNSAFE")
        cases = capture(result_dir, css)
        gates = grade(cases)
        report = {
            "scope": "HOSTED_FIRSTSCREEN_EPHEMERAL_MARGIN_CANDIDATE",
            "css_sha256": hashlib.sha256(css.encode("utf-8")).hexdigest(),
            "cms_writes": False,
            "logged_in": False,
            "nypl_binary_download": False,
            "screenshot_scope": "anonymous public first viewport only",
            "not_a_staging_or_zoom_certification": True,
            "cases": cases,
            "gates": gates,
        }
        result = 0 if gates["anonymous_visual_capture"] == "PASS" else 2
    except Exception as err:
        report = {
            "scope": "HOSTED_FIRSTSCREEN_EPHEMERAL_MARGIN_CANDIDATE",
            "error_type": type(err).__name__,
            "release": "HOLD",
            "cms_writes": False,
        }
        result = 2
    (result_dir / "VISUAL_GATE_HOLD.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report.get("gates", {"visual": "FAIL"})), flush=True)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
