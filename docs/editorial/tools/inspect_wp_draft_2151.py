#!/usr/bin/env python3
"""Read-only visual QA for Final Vestige unpublished WordPress investigation #2151.

Requirements: pip install playwright && python -m playwright install chromium
Usage: FV_PREVIEW_URL="<PRIVATE editor preview>" [FV_STORAGE_STATE="/private/auth.json"] \
       python inspect_wp_draft_2151.py --out /private/qa --sha <fresh WP Gutenberg SHA-1>
Preview URLs, authentication states, screenshots, and results must remain private.
No publication, WordPress writes, subscriber notices, or social updates occur.
A successful automated inspection is NOT final editorial authorization to publish.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

TITLE = "The Levee They Blew on Purpose"
# WordPress media IDs are more reliable than exact file basenames: WP may serve
# a srcset-resized image whose currentSrc differs from the Gutenberg src.
MEDIA = {
    "2148": {"stem": "1927-caernarvon-levee-explosion-noaa-archive", "credits": ("NOAA",)},
    "2255": {"stem": "poydras-artificial-crevasse-1927-april30-loc", "credits": ("Library of Congress", "LOC")},
    "2202": {"stem": "emile-riche-1927-flood-claim-lou-block-1939-loc", "credits": ("Library of Congress", "LOC")},
    "2149": {"stem": "mississippi-flood-1927-apr29-national-photo-company", "credits": ("Library of Congress", "LOC", "National Photo Company")},
}
EXPECTED_SOURCES = 39
EXPECTED_EVIDENCE_ROWS = 10
# Content sentinels anchored in the latest authenticated Gutenberg readback.
# These improve confidence that the preview is the current editorial revision,
# but do NOT cryptographically prove the declared --sha or replace a fresh WP read.
REVISION_SENTINELS = (
    "2:17 p.m.", "$1,096,796.53", "Bohemia Spillway", "Acosta v.", "1991",
)

def capture(page, locator, out):
    try:
        if locator.count():
            el = locator.first
            el.scroll_into_view_if_needed(timeout=6000)
            page.wait_for_timeout(250)
            el.screenshot(path=str(out), timeout=7500)
            return out.name
    except Exception:
        pass
    return None

def inspect(page, width, out):
    console_errors, page_errors = [], []
    page.on("console", lambda m: console_errors.append("error") if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append("pageerror"))
    try:
        page.goto(os.environ["FV_PREVIEW_URL"], wait_until="domcontentloaded", timeout=45000)
    except Exception:
        raise RuntimeError("Unable to load authorized draft; preview URL withheld.") from None
    page.wait_for_timeout(1400)
    article = page.locator("article").first
    if not article.count() or TITLE.lower() not in page.locator("h1").first.inner_text(timeout=12000).lower():
        raise RuntimeError("Not the intended post's frontend preview; login/editor screen rejected.")
    if not article.locator("h2#sources").count():
        raise RuntimeError("Sources anchor absent from post: wrong preview or incomplete rendering.")

    page.screenshot(path=str(out / f"{width}-top.png"), animations="disabled")
    pics = article.locator("figure.wp-block-image img")
    photo_results = []
    for i in range(pics.count()):
        el = pics.nth(i)
        try:
            el.scroll_into_view_if_needed(timeout=7000)
            el.evaluate("(img) => img.decode().catch(() => null)")
            info = el.evaluate("""el => ({
              src:el.getAttribute('src')||'', currentSrc:el.currentSrc||el.src,
              alt:el.getAttribute('alt')||'', loaded:el.complete && el.naturalWidth>0,
              width:el.naturalWidth,height:el.naturalHeight,
              wpMediaId:(el.className.match(/wp-image-(\\d+)/)||[])[1]||null})""")
            caption = el.locator("xpath=ancestor::figure[1]/figcaption")
            info["captionText"] = caption.first.inner_text(timeout=3000)[:600] if caption.count() else ""
            photo_results.append(info)
        except Exception:
            photo_results.append({"load_error": True})
    found = {}
    for mid, rec in MEDIA.items():
        matching = [x for x in photo_results if x.get("wpMediaId") == mid or
                    rec["stem"] in x.get("src", "") or rec["stem"] in x.get("currentSrc", "")]
        found[mid] = bool(len(matching) == 1 and matching[0].get("loaded") and
                          matching[0].get("alt") and
                          any(credit.lower() in matching[0].get("captionText", "").lower()
                              for credit in rec["credits"]))
    # The editor sets _jetpack_hide_featured_image=true, but the live template
    # could still duplicate the cover outside the article; check the whole DOM.
    hero_duplicates = page.locator('img[src*="1927-caernarvon-levee-explosion-noa"]').count()
    photo_ok = all(found.values()) and len(photo_results) == 4
    revision_text = article.text_content(timeout=12000) or ""
    revision_sentinels = {token: token in revision_text for token in REVISION_SENTINELS}
    sources = article.locator("h2#sources").first
    source_list = sources.locator("xpath=following-sibling::ul[1]")
    source_count = source_list.locator(":scope > li").count() if source_list.count() else 0
    chart_count = article.locator("figure.fv-evidence-chart").count()
    footer_count = page.locator("footer").count()
    header_count = page.locator("header").count()
    table = page.locator("figure:has(table)").first
    table_stats = None
    if table.count():
        table_stats = table.evaluate("""el => {
          const t=el.querySelector('table'),cs=getComputedStyle(el);
          return {clientWidth:el.clientWidth,scrollWidth:el.scrollWidth,
            overflowX:cs.overflowX,tabindex:el.getAttribute('tabindex'),
            label:el.getAttribute('aria-label'),rows:t?t.rows.length:0};
        }""")
    page_stats = page.evaluate("""() => ({
      viewport:innerWidth, scrollWidth:document.documentElement.scrollWidth,
      headingCount:document.querySelectorAll('article h2').length,
      brokenAnchors:Array.from(document.querySelectorAll('article a[href^="#"]'))
        .filter(a=>a.hash.length>1 && !document.getElementById(decodeURIComponent(a.hash.slice(1)))).length
    })""")
    overflow = max(0, page_stats["scrollWidth"] - page_stats["viewport"])
    checks = {
        "no_page_wide_horizontal_overflow": overflow <= 2,
        "all_four_local_archival_photos_loaded_credited_and_alt": photo_ok,
        "evidence_table_10_rows_including_header": bool(table_stats and table_stats["rows"] == EXPECTED_EVIDENCE_ROWS),
        "source_bibliography_39_entries": source_count == EXPECTED_SOURCES,
        "expected_editorial_revision_markers_present": all(revision_sentinels.values()),
        "original_compensation_figure_present": chart_count == 1,
        "site_header_and_footer_present": bool(header_count and footer_count),
        "no_duplicate_lead_image": hero_duplicates == 1,
        "responsive_table_scrolls_inside_figure": bool(table_stats and (
            width > 500 or (
                table_stats["scrollWidth"] > table_stats["clientWidth"]
                and table_stats["overflowX"] in ("auto", "scroll")
                and table_stats["tabindex"] is not None
                and table_stats["label"]
            )
        )),
        "internal_anchors_resolve": page_stats["brokenAnchors"] == 0,
        "no_uncaught_javascript_errors": not page_errors,
    }
    captures = {"top": f"{width}-top.png"}
    for label, locator in (
        ("hero", page.locator("figure.wp-block-image").first),
        ("final-photo", page.locator("figure.wp-block-image").last),
        ("compensation", page.locator("figure.fv-evidence-chart")),
        ("evidence-table", table),
        ("sources", page.get_by_text("Sources & Further Reading", exact=False).first),
        ("footer", page.locator("footer").last),
    ):
        name = capture(page, locator, out / f"{width}-{label}.png")
        if name:
            captures[label] = name
    return {"viewport": width, "checks": checks, "document": page_stats,
            "overflowPx": overflow, "evidenceTable": table_stats,
            "bibliographyEntryCount": source_count,
            "editorialRevisionSentinels": revision_sentinels,
            "archivalImageChecks": found,
            "archivalImages": photo_results, "featuredImageOccurrences": hero_duplicates,
            "captured": captures, "consoleErrorCount": len(console_errors),
            "uncaughtJsErrorCount": len(page_errors)}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--sha", required=True,
        help="Gutenberg SHA from fresh WP authenticated readback; script does not independently verify it")
    ap.add_argument("--browser-bin", default=os.environ.get("CHROMIUM_PATH"))
    args = ap.parse_args()
    url = os.environ.get("FV_PREVIEW_URL", "")
    if not url or urlsplit(url).scheme != "https" or urlsplit(url).hostname not in (
        "finalvestige.com", "www.finalvestige.com"
    ):
        ap.error("FV_PREVIEW_URL must be an HTTPS editor preview of finalvestige.com (do not publish URL).")
    storage = os.environ.get("FV_STORAGE_STATE")
    if storage and not Path(storage).is_file():
        ap.error("Existing authenticated browser state missing; path withheld.")
    args.out.mkdir(parents=True, exist_ok=True)
    result = {"postId": 2151, "declaredGutenbergSha1": args.sha,
              "hashVerifiedByBrowser": False,
              "releaseGate": "MANUAL_EDITOR_REVIEW_REQUIRED",
              "viewports": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=args.browser_bin or None)
        try:
            for width in (390, 1440):
                ctx = browser.new_context(viewport={"width": width, "height": 900},
                    device_scale_factor=1, storage_state=storage if storage else None)
                try:
                    result["viewports"].append(inspect(ctx.new_page(), width, args.out))
                finally:
                    ctx.close()
        finally:
            browser.close()
    (args.out / "inspection.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("Local screenshots + inspection.json generated for both viewport widths.")
    for item in result["viewports"]:
        print(item["viewport"], item["checks"])
    if not all(all(item["checks"].values()) for item in result["viewports"]):
        print("One or more automated checks FAILED; manual QA and defect resolution required.")
    print("Release status: MANUAL_EDITOR_REVIEW_REQUIRED. No secrets, preview URL or cookies stored.")

if __name__ == "__main__":
    main()
