#!/usr/bin/env python3
"""Live anonymous accessibility/interaction lab for the *already published* homepage.

GET-only, browser-local axe-core; no WordPress credentials, clicks on forms, CMS
writes, media archives, screenshots, DOM text, cookies, or visitor data retained.
Axe automation is not a WCAG 2.2 AA certification or independent QD approval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

URL = "https://finalvestige.com/"
WIDTHS = (320, 390, 768, 1440, 1920)
NYPL_MARKERS = ("edit-017-v02-nypl-5003296", "nypl-5003296-original")
AXE_TAGS = ("wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa")


def deny_request(method: str, url: str) -> bool:
    """Deny non-GET and unresolved NYPL photo subrequests even when lazy-loaded."""
    if method != "GET" or not isinstance(url, str):
        return True
    path = urlsplit(url).path.lower()
    return any(marker in path for marker in NYPL_MARKERS)


def compact_axe(results: dict) -> dict:
    """Only rule IDs and counts leave the browser; NEVER HTML or node text."""
    if not isinstance(results, dict):
        raise ValueError("AXE_RESULT_MISSING")
    if not all(isinstance(results.get(key), list)
               for key in ("violations", "incomplete", "passes")):
        raise ValueError("AXE_RESULT_INCOMPLETE")
    violations = []
    for entry in results["violations"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise ValueError("AXE_RULE_INVALID")
        if not isinstance(entry.get("nodes"), list):
            raise ValueError("AXE_NODE_LIST_INVALID")
        violations.append({
            "rule": entry["id"], "impact": entry.get("impact"),
            "affected_elements": len(entry["nodes"]),
        })
    return {
        "violations": sorted(violations, key=lambda item: item["rule"]),
        "violation_rules": len(violations),
        "incomplete_rules": len(results["incomplete"]),
        "passed_rules": len(results["passes"]),
        "wcag_tags": list(AXE_TAGS),
    }


def evaluate(cases: list[dict]) -> dict:
    expected = {f"js_{w}" for w in WIDTHS} | {"nojs_390", "reduced_390"}
    if not isinstance(cases, list) or len(cases) != 7 or {
        item.get("case") for item in cases if isinstance(item, dict)
    } != expected:
        raise ValueError("LIVE_UX_MATRIX_INCOMPLETE")
    basic = all(c.get("http_status") == 200 and c.get("host") == "finalvestige.com"
                and isinstance(c.get("blocked_non_get"), int)
                and c["blocked_non_get"] >= 0 for c in cases)
    interactive = next(c for c in cases if c["case"] == "js_390")
    nojs = next(c for c in cases if c["case"] == "nojs_390")
    reduced = next(c for c in cases if c["case"] == "reduced_390")
    ux_ok = (len(interactive.get("interactions", {})) >= 4
             and all(interactive["interactions"].values())
             and nojs.get("nojs_fallback") is True
             and reduced.get("prefers_reduced_motion") is True
             and all(c.get("document_horizontal_overflow") is False for c in cases))
    axe_cases = [c for c in cases if c.get("axe") is not None]
    axe_available = {c["case"] for c in axe_cases} == {"js_390", "js_1440"}
    axe_clear = axe_available and all(
        c["axe"]["violation_rules"] == 0 for c in axe_cases)
    # "incomplete" always requires manual follow-up; zero violations never certify WCAG.
    return {
        "anonymous_read_only_gate": "PASS" if basic else "FAIL",
        "hosted_interaction_and_reflow_gate": "PASS" if ux_ok else "FAIL",
        "axe_instrumentation_gate": "PASS" if axe_available else "FAIL",
        "axe_automated_violation_gate": "PASS" if axe_clear else "FAIL",
        "manual_accessibility_gate": "HOLD",
        "image_specific_rights_gate": "HOLD",
        "publication_authorization_gate": "HOLD",
        "release_gate": "HOLD",
    }


def run_browser(axe_script: Path) -> list[dict]:
    if not axe_script.is_file() or axe_script.stat().st_size < 10000:
        raise ValueError("AXE_SOURCE_NOT_INSTALLED_OR_EMPTY")
    from playwright.sync_api import sync_playwright

    cases = []
    matrix = [(f"js_{w}", w, True, False) for w in WIDTHS]
    matrix += [("nojs_390", 390, False, False),
               ("reduced_390", 390, True, True)]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for case, width, javascript, reduced in matrix:
                ctx = browser.new_context(
                    viewport={"width": width, "height": 844},
                    java_script_enabled=javascript,
                    reduced_motion="reduce" if reduced else "no-preference",
                    accept_downloads=False, service_workers="block",
                    bypass_csp=True,  # Axe injection only; NOT a hosted CSP test.
                )
                observed = {"blocked_non_get": 0, "blocked_nypl": 0}
                def guard(route):
                    method = route.request.method
                    target = route.request.url
                    if deny_request(method, target):
                        if method != "GET":
                            observed["blocked_non_get"] += 1
                        else:
                            observed["blocked_nypl"] += 1
                        route.abort()
                    else:
                        route.continue_()
                ctx.route("**/*", guard)
                page = ctx.new_page()
                try:
                    response = page.goto(URL, wait_until="domcontentloaded",
                                         timeout=45000)
                    if response is None:
                        raise ValueError("NO_HOST_DOCUMENT_RESPONSE")
                    if urlsplit(page.url).hostname != "finalvestige.com":
                        raise ValueError("UNEXPECTED_HOST_REDIRECT")
                    page.locator("[data-fv-home-flagship]").wait_for(
                        state="attached", timeout=15000)
                    page.wait_for_timeout(400)
                    record = {
                        "case": case, "host": "finalvestige.com",
                        "http_status": response.status,
                        "blocked_non_get": observed["blocked_non_get"],
                        "blocked_nypl": observed["blocked_nypl"],
                        "document_horizontal_overflow": bool(page.evaluate(
                            "() => document.documentElement.scrollWidth > "
                            "document.documentElement.clientWidth + 2")),
                        "interactions": {}, "nojs_fallback": None,
                        "prefers_reduced_motion": None, "axe": None,
                    }
                    if case in ("js_390", "js_1440"):
                        page.add_script_tag(path=str(axe_script))
                        axe_raw = page.evaluate("""async (tags) => {
                            if (!window.axe || typeof window.axe.run !== 'function')
                                throw new Error('AXE_DID_NOT_INITIALIZE');
                            return await window.axe.run(document, {
                                runOnly: {type: 'tag', values: tags}
                            });
                        }""", list(AXE_TAGS))
                        record["axe"] = compact_axe(axe_raw)
                    if case == "js_390":
                        interactions = {}
                        first = page.locator('[data-fv-chronicle-view="original"]')
                        first.click()
                        interactions["chronicle_click"] = (
                            first.get_attribute("aria-pressed") == "true"
                            and page.locator(".fv-hf__chronicle").get_attribute(
                                "data-fv-chronicle-mode") == "original")
                        first.focus()
                        page.keyboard.press("ArrowRight")
                        interactions["chronicle_keyboard"] = (
                            page.locator('[data-fv-chronicle-view="addition"]').get_attribute(
                                "aria-pressed") == "true")
                        page.locator('[data-fv-case-button="franklin"]').click()
                        interactions["case_switch"] = (
                            page.locator('[data-fv-case-button="franklin"]').get_attribute(
                                "aria-pressed") == "true"
                            and page.locator('[data-fv-case="franklin"]').is_visible()
                            and not page.locator('[data-fv-case="apollo"]').is_visible())
                        page.locator('[data-fv-observer-switch="b"]').click()
                        interactions["observer_switch"] = (
                            page.locator('[data-fv-observer-switch="b"]').get_attribute(
                                "aria-pressed") == "true"
                            and page.locator('[data-fv-observer-frame="b"]').is_visible()
                            and not page.locator('[data-fv-observer-frame="a"]').is_visible())
                        page.locator('.fv-hf__chapter-nav a[href="#fv-hf-method-title"]').click()
                        interactions["chapter_anchor"] = (
                            urlsplit(page.url).fragment == "fv-hf-method-title")
                        record["interactions"] = interactions
                    if case == "nojs_390":
                        # Intrinsic page meaning must remain visible without page JS.
                        base = (not page.locator("[data-fv-case-buttons]").is_visible()
                                and page.locator('[data-fv-case="apollo"]').is_visible()
                                and page.locator('[data-fv-case="franklin"]').is_visible()
                                and page.locator('[data-fv-case="malbone"]').is_visible()
                                and not page.locator("[data-fv-observer-controls]").is_visible()
                                and page.locator('[data-fv-observer-frame="a"]').is_visible()
                                and page.locator('[data-fv-observer-frame="b"]').is_visible())
                        native = page.locator("#fv-hf-observer-answer summary")
                        native.focus()
                        page.keyboard.press("Enter")
                        record["nojs_fallback"] = (
                            base and page.locator("#fv-hf-observer-answer").get_attribute(
                                "open") is not None)
                    if case == "reduced_390":
                        record["prefers_reduced_motion"] = bool(page.evaluate(
                            "() => matchMedia('(prefers-reduced-motion: reduce)').matches"))
                    cases.append(record)
                finally:
                    ctx.close()
        finally:
            browser.close()
    return cases


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--axe-source", required=True)
    cli.add_argument("--output", default="HOSTED_WCAG_INTERACTIONS_HOLD.json")
    args = cli.parse_args()
    output = Path(args.output)
    try:
        cases = run_browser(Path(args.axe_source))
        report = {
            "scope": "ANONYMOUS_HOSTED_CHROMIUM_A11Y_INTERACTIONS",
            "axe_dependency": "axe-core@4.10.3 locally injected for audit only",
            "csp_note": "CSP bypass used solely to inject offline axe instrumentation",
            "not_field_cwv_or_manual_wcag_2_2_aa": True,
            "cms_writes": False, "page_html_retained": False,
            "screenshot_or_archive_binaries_retained": False,
            "cases": cases, "gates": evaluate(cases),
        }
        code = 0
    except Exception as exc:
        report = {
            "scope": "ANONYMOUS_HOSTED_CHROMIUM_A11Y_INTERACTIONS",
            "error_type": type(exc).__name__, "instrumentation_gate": "FAIL",
            "cms_writes": False, "release_gate": "HOLD",
        }
        code = 2
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    # Safe public-CI log summary: rule names/counts, not page text or selectors.
    summary = {"gates": report.get("gates", {"instrumentation_gate": "FAIL"}),
               "cases": [{"case": c["case"], "blocked_non_get": c["blocked_non_get"],
                          "blocked_nypl": c["blocked_nypl"],
                          "overflow": c["document_horizontal_overflow"],
                          "interactions": c["interactions"],
                          "axe": c["axe"]} for c in report.get("cases", [])]}
    print(json.dumps(summary, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
