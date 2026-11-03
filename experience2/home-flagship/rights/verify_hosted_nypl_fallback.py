#!/usr/bin/env python3
"""Read-only, anonymous Chromium visual admission for withholding NYPL capture.

This does NOT edit WordPress. It prevents NYPL image fetches, captures the
already-published Malbone frame, and replays the narrowly reviewed proposed
remediation in browser memory only. The real raw Gutenberg transformer is in
withhold_unverified_nypl_capture.py; this harness does not replace WordPress
staging or prove publication compatibility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

HOST = "finalvestige.com"
URL = "https://finalvestige.com/"
NYPL_FILE = "edit-017-v02-nypl-5003296-original.jpg"
NYPL_RECORD = "https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0"
WIDTHS = (320, 390, 768, 1440, 1920)

# Mutation operates ONLY inside an already-rendered local Chromium document.
# The exact old prose was checked against 2026-11-03 authenticated WordPress
# page-6 readback, sha256 c9a6cd57582cce2801620381212193d54b9e6446236b24aff1880a12ff1d3b7e.
MUTATE = r"""() => {
 const record = 'https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0';
 const name = 'edit-017-v02-nypl-5003296-original.jpg';
 const article = document.querySelector('article.fv-hf__case[data-fv-case="malbone"]');
 if (!article || document.querySelectorAll('article.fv-hf__case[data-fv-case="malbone"]').length !== 1)
   throw new Error('MALBONE_ARTICLE_DRIFT');
 const imgs = [...article.querySelectorAll('img[data-fv-archive-img]')];
 if (imgs.length !== 1 || !imgs[0].getAttribute('src').includes(name)
     || !imgs[0].getAttribute('srcset') || !imgs[0].getAttribute('srcset').includes(name))
   throw new Error('NYPL_IMAGE_DRIFT');
 const paragraphs = [...article.querySelectorAll('.fv-hf__case-source p')];
 const oldCaption = "Image: Brooklyn Rapid Transit system map, 1903; NYPL Digital Collections item 5003296, as published in Final Vestige's Malbone investigation.";
 const oldCredit = "Credit: From The New York Public Library. NYPL believes this item is in the public domain under United States law.";
 const cap = paragraphs.filter(p => p.textContent.trim().startsWith('Image: Brooklyn Rapid Transit system map, 1903;') && p.textContent.includes('NYPL Digital Collections item 5003296') && p.textContent.includes('Malbone investigation.'));
 const cred = paragraphs.filter(p => p.textContent.trim() === oldCredit);
 const frame = article.querySelector('.fv-hf__image-frame span');
 const fallback = article.querySelector('.fv-hf__case-image-fallback');
 if (cap.length !== 1 || cred.length !== 1 || !frame ||
     frame.textContent.trim() !== 'ARCHIVE IMAGE 03 / NYPL 5003296' || !fallback)
   throw new Error('SOURCE_OR_FALLBACK_DRIFT ' + JSON.stringify({
       caption: cap.length, credit: cred.length,
       paragraphs: paragraphs.length, frame: !!frame,
       frame_label: frame?.textContent.trim().slice(0,85) || null,
       fallback: !!fallback,
       actual_p: paragraphs.map(p=>p.textContent.trim().slice(0,115))
     }));
 if (!article.outerHTML.includes(record)) throw new Error('SOURCE_LINK_DRIFT');
 const outerBefore = article.outerHTML;
 imgs[0].remove();
 cap[0].innerHTML = '<strong>Catalog record:</strong> Brooklyn Rapid Transit system map, 1903; NYPL Digital Collections item 5003296. The source is linked, not reproduced here.';
 cred[0].innerHTML = '<strong>Source:</strong> From The New York Public Library; 1903 Brooklyn Rapid Transit system map, catalog item 5003296. <strong>Reuse:</strong> The digital image\'s specific rights status is not verified. The reproduction is withheld pending review.';
 frame.textContent = 'NYPL RECORD 03 / 5003296';
 fallback.style.left = 'clamp(16px, 6%, 72px)';
 fallback.style.right = 'clamp(16px, 6%, 72px)';
 fallback.style.width = 'auto';
 fallback.style.fontSize = 'clamp(17px, 2.4vw, 30px)';
 fallback.style.overflowWrap = 'break-word';
 const outerAfter = article.outerHTML;
 const fallbackRect = fallback.getBoundingClientRect();
 const imageRect = article.querySelector('.fv-hf__case-image').getBoundingClientRect();
 return {
    article_before_chars: outerBefore.length,
    article_after_chars: outerAfter.length,
    image_count_before: 1,
    image_count_after: article.querySelectorAll('img[data-fv-archive-img]').length,
    nypl_file_absent: !outerAfter.includes(name),
    original_claim_absent: !outerAfter.includes('NYPL believes this item is in the public domain'),
    corrected_credit_present: outerAfter.includes('The reproduction is withheld pending review.'),
    catalog_links_in_case: article.querySelectorAll('a[href="' + record + '"]').length,
    fallback_text_visible: getComputedStyle(fallback).display !== 'none' &&
       getComputedStyle(fallback).visibility !== 'hidden' &&
       fallbackRect.width > 0 && fallbackRect.height > 0,
    fallback_within_case: fallbackRect.left >= imageRect.left - 2 &&
      fallbackRect.right <= imageRect.right + 2,
    frame_relabelled: frame.textContent.trim() === 'NYPL RECORD 03 / 5003296',
    source_heading_retained: !!article.querySelector('#fv-hf-malbone-title'),
    source_details_retained: article.querySelectorAll('details summary').length === 1
 };
}"""


def refuse_request(method: str, url: str) -> bool:
    """No server writes; NEVER transfer disputed NYPL image bytes."""
    if method.upper() != "GET":
        return True
    try:
        p = urlsplit(url)
        return p.scheme != "https" or not p.hostname or (
            NYPL_FILE in p.path.lower()
            or "nypl-5003296-original" in p.path.lower()
        )
    except (TypeError, ValueError):
        return True


def grade(cases: list[dict]) -> dict:
    if len(cases) != len(WIDTHS) or {c.get("width") for c in cases} != set(WIDTHS):
        raise ValueError("MISSING_OR_DUPLICATE_WIDTH")
    for c in cases:
        q = c.get("candidate", {})
        shots = c.get("screenshots", {})
        if not (
            c.get("status") == 200
            and c.get("host") == HOST
            and c.get("chapters") == 7
            and c.get("margins") == 72
            and c.get("focus_links", 0) >= 1
            and c.get("catalog_links_after", 0) >= 2
            and c.get("images_before") == 3
            and c.get("images_after") == 2
            and c.get("horizontal_overflow_after") is False
            and q.get("image_count_before") == 1
            and q.get("image_count_after") == 0
            and all(q.get(k) is True for k in (
                "nypl_file_absent", "original_claim_absent",
                "corrected_credit_present", "fallback_text_visible",
                "fallback_within_case", "frame_relabelled",
                "source_heading_retained", "source_details_retained"
            ))
            and q.get("catalog_links_in_case") == 1
            and set(shots) == {"before", "after"}
            and all(isinstance(d, str) and len(d) == 64
                    and all(ch in "0123456789abcdef" for ch in d)
                    for d in shots.values())
        ):
            raise ValueError(f"RELEASE_HOLD_BROWSER_CASE_FAILED_WIDTH_{c.get('width')}")
    return {"read_only_hosted_candidate_visual": "PASS",
            "exact_wordpress_raw_python_transformer_execution": "NOT_TESTED",
            "wordpress_native_staging": "NOT_AVAILABLE_ON_PERSONAL",
            "complete_wcag_22_aa": "HOLD",
            "field_cwv": "NOT_TESTED",
            "nypl_capture_reuse_rights": "HOLD",
            "independent_qd": "HOLD",
            "founder_release_authorization": "HOLD",
            "production_release": "HOLD"}


def capture(output_dir: Path) -> list[dict]:
    from playwright.sync_api import sync_playwright
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for width in WIDTHS:
                context = browser.new_context(
                    viewport={"width": width, "height": 900},
                    reduced_motion="reduce",
                    service_workers="block",
                    accept_downloads=False,
                )
                blocked = {"non_get": 0, "nypl": 0}

                def route_guard(route):
                    req = route.request
                    if refuse_request(req.method, req.url):
                        blocked["non_get" if req.method != "GET" else "nypl"] += 1
                        route.abort()
                    else:
                        route.continue_()

                context.route("**/*", route_guard)
                page = context.new_page()
                try:
                    response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                    if response is None or urlsplit(page.url).hostname != HOST:
                        raise ValueError("UNEXPECTED_HOST")
                    page.locator('[data-fv-home-flagship]').wait_for(
                        state="attached", timeout=12000)
                    chapters = page.locator('.fv-hf__chapter-nav a[href^="#"]').count()
                    margins = page.locator('.fv-margin-strip__item').count()
                    focus = page.locator('a[href*="/focus/"]').count()
                    if (chapters, margins) != (7, 72):
                        raise ValueError("PUBLIC_HOMEPAGE_MARKER_DRIFT")
                    images_before = page.locator('[data-fv-archive-img]').count()
                    if images_before != 3:
                        raise ValueError(f"PUBLIC_ARCHIVE_IMAGE_INVENTORY_DRIFT: observed={images_before}")
                    case_button = page.locator('button[data-fv-case-button="malbone"]')
                    case_button.click(timeout=12000)
                    case = page.locator('article.fv-hf__case[data-fv-case="malbone"]')
                    case.wait_for(state="visible", timeout=12000)
                    case.locator('.fv-hf__case-image').scroll_into_view_if_needed()
                    before_bytes = case.locator('.fv-hf__case-image').screenshot(
                        path=str(output_dir / f"malbone_{width}_before_blocked_nypl.png"),
                        timeout=20000)
                    candidate = page.evaluate(MUTATE)
                    # Article itself is modified ONLY inside this disposable browser page.
                    after_bytes = case.locator('.fv-hf__case-image').screenshot(
                        path=str(output_dir / f"malbone_{width}_candidate_fallback.png"),
                        timeout=20000)
                    after_images = page.locator('[data-fv-archive-img]').count()
                    after_links = page.locator(f'a[href="{NYPL_RECORD}"]').count()
                    overflow = page.evaluate(
                        "() => document.documentElement.scrollWidth > "
                        "document.documentElement.clientWidth + 2"
                    )
                    result = {
                        "width": width, "status": response.status,
                        "host": urlsplit(page.url).hostname,
                        "chapters": chapters, "margins": margins,
                        "focus_links": focus,
                        "catalog_links_after": after_links,
                        "images_before": images_before,
                        "images_after": after_images,
                        "horizontal_overflow_after": overflow,
                        "nypl_bytes_transferred": 0,
                        "blocked_nypl_requests": blocked["nypl"],
                        "blocked_non_get_requests": blocked["non_get"],
                        "candidate": candidate,
                        "screenshots": {
                            "before": hashlib.sha256(before_bytes).hexdigest(),
                            "after": hashlib.sha256(after_bytes).hexdigest(),
                        },
                    }
                    results.append(result)
                    print(f"{width}px: HTTP {response.status}, "
                          f"NYPL blocked={blocked['nypl']}, "
                          f"candidate no NYPL image={candidate['nypl_file_absent']}",
                          flush=True)
                    (output_dir / "partial_cases.json").write_text(
                        json.dumps(results, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
                finally:
                    context.close()
        finally:
            browser.close()
    return results


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, default=Path("nypl_visual_hold"))
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    try:
        cases = capture(args.output_dir)
        gates = grade(cases)
        receipt = {"scope": "PUBLIC_HOST_BROWSER_ONLY_EPHEMERAL_DOM_PATCH",
                   "site": URL,
                   "source_page_id": 6,
                   "source_modified_at_readback": "2026-11-02T17:48:13",
                   "source_raw_sha256_at_readback":
                      "c9a6cd57582cce2801620381212193d54b9e6446236b24aff1880a12ff1d3b7e",
                   "expected_offline_candidate_sha256":
                      "dc2c6ff17639d114794f9c1b78b4a6ab77962ca7129473bef10a5d20a859be19",
                   "authentication": "none",
                   "wordpress_writes": 0,
                   "nypl_image_fetches_allowed": False,
                   "cases": cases,
                   "gates": gates}
        exit_code = 0
    except Exception as e:
        receipt = {"scope": "PUBLIC_HOST_BROWSER_ONLY_EPHEMERAL_DOM_PATCH",
                   "error": f"{type(e).__name__}: {str(e)[:200]}",
                   "wordpress_writes": 0,
                   "release": "HOLD"}
        exit_code = 2
    (args.output_dir / "NYPL_BROWSER_HOLD.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps(receipt.get("gates", {"release": "HOLD"})), flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
