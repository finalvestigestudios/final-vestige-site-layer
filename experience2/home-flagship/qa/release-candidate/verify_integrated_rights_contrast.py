#!/usr/bin/env python3
"""Anonymous live-host admission for COMBINED unmerged rights + contrast fixes.

GET-only, no WordPress writes or subscriptions. Published page stays unchanged.
Actual isolated WordPress/Assembler and independent release review remain gated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
HOME = HERE.parents[1]
sys.path.insert(0, str(HOME / "rights"))
from verify_hosted_nypl_fallback import (  # noqa: E402
    HOST, URL, NYPL_FILE, NYPL_RECORD, MUTATE, refuse_request,
)

WIDTHS = (320, 390, 768, 1440, 1920)
AXE_WIDTHS = (390, 1440)
CONTRAST_CSS = HOME / "accessibility/margins/margin_strip_contrast_safe.css"


def css_checked(path: Path = CONTRAST_CSS) -> str:
    css = path.read_text(encoding="utf-8")
    required = (
        ".fv-margin-strip--rotator .fv-margin-strip__item",
        "@keyframes fvMarginContrastSafe",
        "visibility: hidden",
        "visibility: visible",
        "animation-timing-function: steps(1, end)",
        "prefers-reduced-motion: reduce",
        "animation: none",
        "filter: none",
    )
    if any(token not in css for token in required):
        raise ValueError("CONTRAST_CANDIDATE_SOURCE_DRIFT")
    if any(x in css.lower() for x in ("@import", "url(", "expression(", "javascript:")):
        raise ValueError("CONTRAST_CANDIDATE_EXTERNAL_OR_EXECUTABLE_CSS")
    return css


def grade(cases: list[dict], css_digest: str) -> dict:
    if len(cases) != len(WIDTHS) or [c.get("width") for c in cases] != list(WIDTHS):
        raise ValueError("MISSING_DUPLICATE_OR_REORDERED_WIDTH")
    if len(css_digest) != 64 or any(ch not in "0123456789abcdef" for ch in css_digest):
        raise ValueError("MISSING_CSS_SOURCE_DIGEST")
    for c in cases:
        q = c.get("nypl", {})
        m = c.get("margins_candidate", {})
        if not (
            c.get("http_status") == 200 and c.get("host") == HOST
            and c.get("chapters") == 7 and c.get("margins") == 72
            and c.get("focus_links", 0) >= 1
            and c.get("nypl_source_links", 0) >= 2
            and c.get("images_before") == 3 and c.get("images_after") == 2
            and c.get("overflow_after") is False
            and c.get("nypl_http_responses") == 0
            and q.get("nypl_file_absent") is True
            and q.get("original_claim_absent") is True
            and q.get("corrected_credit_present") is True
            and q.get("fallback_text_visible") is True
            and q.get("fallback_within_case") is True
            and q.get("frame_label_single_line") is True
            and q.get("frame_date_single_line") is True
            and q.get("source_details_retained") is True
            and m.get("records_total") == 72
            and m.get("visible_count") == 1
            and m.get("visible_index") == 0
            and m.get("visible_opacity") == 1
            and m.get("visible_filter") == "none"
            and m.get("contrast_css_applied") is True
            and c.get("non_get_requests_allowed") == 0
        ):
            raise ValueError(f"INTEGRATED_CANDIDATE_FAIL_WIDTH_{c.get('width')}")
        if c["width"] in AXE_WIDTHS and not (
            c.get("axe_executed") is True
            and c.get("axe_color_contrast_violations") == 0
            and c.get("axe_color_contrast_incomplete") == 0
        ):
            raise ValueError(f"AXE_NOT_VERIFIED_WIDTH_{c['width']}")
        if c["width"] in (390, 1440):
            digest = c.get("candidate_screenshot_sha256", "")
            if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError("SCREENSHOT_CUSTODY_MISSING")
    return {
        "combined_hosted_ephemeral_candidate": "PASS",
        "rights_and_contrast_proposed_simultaneously": True,
        "live_page_modified": False,
        "exact_raw_python_transform_on_export": "NOT_TESTED",
        "actual_wordpress_saved_candidate": "NOT_TESTED",
        "manual_wcag22_aa": "HOLD",
        "nypl_capture_specific_rights": "HOLD",
        "field_core_web_vitals": "NOT_MEASURED",
        "independent_qd": "HOLD",
        "founder_release_authorization": "HOLD",
        "production_release": "HOLD",
    }


MARGIN_PROBE = r"""() => {
  const records = [...document.querySelectorAll('.fv-margin-strip__item')];
  const computed = records.map(el => getComputedStyle(el));
  const visible = computed.map((s,i)=>({s,i})).filter(
    o => o.s.visibility === 'visible' && o.s.display !== 'none');
  const first = visible.length === 1 ? visible[0] : null;
  return {
    records_total: records.length,
    visible_count: visible.length,
    visible_index: first?.i ?? -1,
    visible_opacity: first ? Number(first.s.opacity) : -1,
    visible_filter: first?.s.filter ?? '',
    contrast_css_applied: first?.s.animationName === 'none' &&
      first?.s.visibility === 'visible'
  };
}"""


def capture(out: Path, axe_path: Path) -> tuple[list[dict], str]:
    from playwright.sync_api import sync_playwright
    css = css_checked()
    if not axe_path.is_file() or axe_path.stat().st_size < 100000:
        raise ValueError("PINNED_LOCAL_AXE_CORE_MISSING")
    digest = hashlib.sha256(css.encode("utf-8")).hexdigest()
    cases = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for width in WIDTHS:
                context = browser.new_context(
                    viewport={"width": width, "height": 900},
                    reduced_motion="reduce",
                    service_workers="block", accept_downloads=False,
                )
                blocked = {"nypl": 0, "non_get": 0, "nypl_http_responses": 0}
                def route_guard(route):
                    req = route.request
                    if refuse_request(req.method, req.url):
                        if req.method.upper() != "GET":
                            blocked["non_get"] += 1
                        else:
                            blocked["nypl"] += 1
                        route.abort()
                    else:
                        route.continue_()
                context.route("**/*", route_guard)
                def observe_response(response):
                    if NYPL_FILE.lower() in response.url.lower():
                        blocked["nypl_http_responses"] += 1
                context.on("response", observe_response)
                try:
                    page = context.new_page()
                    response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                    if response is None or urlsplit(page.url).hostname != HOST:
                        raise ValueError("PUBLIC_HOST_DRIFT")
                    page.locator("[data-fv-home-flagship]").wait_for(state="attached", timeout=12000)
                    chapters = page.locator('.fv-hf__chapter-nav a[href^="#"]').count()
                    records = page.locator(".fv-margin-strip__item").count()
                    links = page.locator('a[href*="/focus/"]').count()
                    images_before = page.locator('img[data-fv-archive-img]').count()
                    page.locator('button[data-fv-case-button="malbone"]').click(timeout=12000)
                    case = page.locator('article.fv-hf__case[data-fv-case="malbone"]')
                    case.wait_for(state="visible", timeout=12000)
                    applied_nypl = page.evaluate(MUTATE)
                    page.add_style_tag(content=css)
                    page.wait_for_timeout(100)
                    margins = page.evaluate(MARGIN_PROBE)
                    source_links = page.locator(f'a[href="{NYPL_RECORD}"]').count()
                    images_after = page.locator('img[data-fv-archive-img]').count()
                    overflow = page.evaluate(
                        "() => document.documentElement.scrollWidth > "
                        "document.documentElement.clientWidth + 2"
                    )
                    row = {
                        "width": width, "http_status": response.status,
                        "host": urlsplit(page.url).hostname,
                        "chapters": chapters, "margins": records,
                        "focus_links": links, "nypl_source_links": source_links,
                        "images_before": images_before, "images_after": images_after,
                        "nypl_http_responses": blocked["nypl_http_responses"],
                        "blocked_nypl_requests": blocked["nypl"],
                        "blocked_non_get_requests": blocked["non_get"],
                        "non_get_requests_allowed": 0,
                        "overflow_after": overflow,
                        "nypl": applied_nypl,
                        "margins_candidate": margins,
                    }
                    if width in AXE_WIDTHS:
                        page.add_script_tag(path=str(axe_path))
                        a = page.evaluate("""async () => {
                          if (!window.axe) throw new Error('AXE_NOT_LOADED');
                          const node = document.querySelector('.fv-margin-strip');
                          if (!node) throw new Error('MARGINS_MISSING');
                          const r = await axe.run(node, {runOnly: {type:'rule',
                            values:['color-contrast']}});
                          return {violations:r.violations.length,
                            incomplete:r.incomplete.length};
                        }""")
                        row["axe_executed"] = True
                        row["axe_color_contrast_violations"] = a["violations"]
                        row["axe_color_contrast_incomplete"] = a["incomplete"]
                        page.locator("article.fv-hf__case[data-fv-case='malbone']").scroll_into_view_if_needed()
                        png = page.screenshot(full_page=False, animations="disabled")
                        filename = f"integrated_{width}_case_view_candidate.png"
                        (out / filename).write_bytes(png)
                        row["candidate_screenshot_sha256"] = hashlib.sha256(png).hexdigest()
                    cases.append(row)
                    (out / "partial_cases.json").write_text(
                        json.dumps(cases, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                    print(f"{width}px: status={response.status} source_links={source_links} "
                          f"margins={margins.get('visible_count')} visible; "
                          f"nypl_removed={applied_nypl.get('nypl_file_absent')}",
                          flush=True)
                finally:
                    context.close()
        finally:
            browser.close()
    return cases, digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--axe", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        cases, digest = capture(args.out, args.axe)
        gates = grade(cases, digest)
        receipt = {
            "scope": "ANONYMOUS_PUBLIC_HOST_COMBINED_EPHEMERAL_FIXES",
            "candidate_only_not_published": True,
            "upstream_rights_pr": 786,
            "upstream_contrast_pr": 746,
            "upstream_css_sha256": digest,
            "original_page_6_raw_sha256_at_prior_readback":
                "c9a6cd57582cce2801620381212193d54b9e6446236b24aff1880a12ff1d3b7e",
            "cases": cases, "gates": gates,
        }
        code = 0
    except Exception as e:
        receipt = {"scope": "ANONYMOUS_PUBLIC_HOST_COMBINED_EPHEMERAL_FIXES",
                   "error": f"{type(e).__name__}: {str(e)[:200]}",
                   "production_release": "HOLD"}
        code = 2
    (args.out / "INTEGRATED_HOLD.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt.get("gates", receipt)), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
