#!/usr/bin/env python3
"""Read-only visual QA for Final Vestige unpublished WordPress investigation #2151.

Requirements: pip install playwright && python -m playwright install chromium
Usage: FV_PREVIEW_URL="<PRIVATE editor preview>" [FV_STORAGE_STATE="/private/auth.json"] \
       python inspect_wp_draft_2151.py --out /private/qa --sha <fresh WP Gutenberg SHA-1>
Alternative: use an already authenticated, locally running dedicated Chromium session:
    FV_PREVIEW_URL="<PRIVATE editor preview>" \
       python inspect_wp_draft_2151.py --cdp http://127.0.0.1:9222 --out /private/qa \
       --sha <fresh WP Gutenberg SHA-1>
Start that session with a loopback-only remote debugging port and a separate
private profile; log in there normally. The inspector opens only new QA tabs.
No cookies, preview URLs or editor credentials are serialized to output.
Preview URLs, authentication states, screenshots, and results must remain private.
No publication, WordPress writes, subscriber notices, or social updates occur.
A successful automated inspection is NOT final editorial authorization to publish.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, unquote

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
EXPECTED_SOURCES = 42  # Nov 11 20:42 Pacific: AP/Brownsville Herald added as bibliography item 42.
EXPECTED_EVIDENCE_ROWS = 10
# Content sentinels anchored in the latest authenticated Gutenberg readback.
# These improve confidence that the preview is the current editorial revision,
# but do NOT cryptographically prove the declared --sha or replace a fresh WP read.
REVISION_SENTINELS = (
    "2:17 p.m.", "$1,096,796.53", "Bohemia Spillway", "Acosta v.", "1991", "May 9, 1927", "$3,387,000", "Graham v. Jones",
)
# The Nov 12 07:43 revision corrected the USGS Peak-Flow File precision.
# Earlier fingerprints shared every old sentinel, so they could falsely pass.
# All markers must occur within ONE paragraph, not scattered across the post.
PRECISION_CORRECTION_MARKERS = (
    "Peak-Flow File lists 2,470,000",
    "also discusses 2,472,000",
    "recommends reporting approximately 2.47 million",
    "estimated peak if flow had remained confined",
)

def local_asset_source(url):
    """Only original FV uploads or WordPress's image CDN proxy of those uploads."""
    p = urlsplit(url)
    host = (p.hostname or "").lower()
    path = unquote(p.path)
    if p.scheme != "https":
        return False
    if host in ("finalvestige.com", "www.finalvestige.com"):
        return path.startswith("/wp-content/uploads/")
    if host in ("i0.wp.com", "i1.wp.com", "i2.wp.com"):
        return path.startswith((
            "/finalvestige.com/wp-content/uploads/",
            "/www.finalvestige.com/wp-content/uploads/",
        ))
    return False

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
              visible:el.getBoundingClientRect().width > 40 &&
                el.getBoundingClientRect().height > 20 &&
                getComputedStyle(el).visibility !== "hidden" &&
                getComputedStyle(el).display !== "none",
              wpMediaId:(el.className.match(/wp-image-(\\d+)/)||[])[1]||null})""")
            caption = el.locator("xpath=ancestor::figure[1]/figcaption")
            info["captionText"] = caption.first.inner_text(timeout=3000)[:600] if caption.count() else ""
            info["localSource"] = local_asset_source(info["src"]) and local_asset_source(info["currentSrc"])
            photo_results.append(info)
        except Exception:
            photo_results.append({"load_error": True})
    found = {}
    for mid, rec in MEDIA.items():
        matching = [x for x in photo_results if x.get("wpMediaId") == mid or
                    rec["stem"] in x.get("src", "") or rec["stem"] in x.get("currentSrc", "")]
        found[mid] = bool(len(matching) == 1 and matching[0].get("loaded") and
                          matching[0].get("alt") and matching[0].get("visible") and
                          matching[0].get("localSource") and
                          any(credit.lower() in matching[0].get("captionText", "").lower()
                              for credit in rec["credits"]))
    # The editor sets _jetpack_hide_featured_image=true, but the live template
    # could still duplicate the cover outside the article; check the whole DOM.
    hero_duplicates = page.locator('img[src*="1927-caernarvon-levee-explosion-noa"]').count()
    photo_ok = all(found.values()) and len(photo_results) == 4
    revision_text = article.text_content(timeout=12000) or ""
    revision_sentinels = {token: token in revision_text for token in REVISION_SENTINELS}
    precision_paragraphs = [" ".join(p.split()) for p in article.locator("p").all_text_contents()]
    precision_correction_ok = any(
        all(marker in p for marker in PRECISION_CORRECTION_MARKERS)
        for p in precision_paragraphs
    )
    sources = article.locator("h2#sources").first
    source_list = sources.locator("xpath=following-sibling::ul[1]")
    source_count = source_list.locator(":scope > li").count() if source_list.count() else 0
    chart_count = article.locator("figure.fv-evidence-chart").count()
    # This chronology was added AFTER the original QA inspector was written.
    # Inspect the real production-theme rendering, not merely its Gutenberg source.
    timeline = article.locator("figure.fv-caernarvon-timeline")
    timeline_stats = None
    if timeline.count() == 1:
        timeline.first.scroll_into_view_if_needed(timeout=6000)
        timeline_stats = timeline.first.evaluate("""el => {
          const r=el.getBoundingClientRect(), cards=Array.from(el.querySelectorAll('ol > li'));
          const links=Array.from(el.querySelectorAll('figcaption a[href]'));
          const cap=el.querySelector('figcaption');
          const descriptions=cards.map(c=>c.querySelector('span:last-child')).filter(Boolean);
          const text=el.textContent||'';
          return {
            count:cards.length,
            cardDates:cards.map(c=>(c.querySelector('span')?.textContent||'').trim()),
            creditLinks:links.map(a=>a.getAttribute('href')),
            accessible:el.getAttribute('role')==='group' && !!el.getAttribute('aria-label'),
            caution: text.includes('Neither number is a direct measurement')
              && text.includes('Different methods and reference conditions'),
            stageEstimates: text.includes('½ foot') && text.includes('2 feet'),
            withinViewport:r.left>=-2 && r.right<=innerWidth+2,
            clippedCards:cards.some(c=>{const b=c.getBoundingClientRect();
              return b.left < r.left-2 || b.right > r.right+2
                || c.scrollWidth>c.clientWidth+2;}),
            captionFontPx:cap?parseFloat(getComputedStyle(cap).fontSize):0,
            minDescriptionFontPx:descriptions.length?
              Math.min(...descriptions.map(d=>parseFloat(getComputedStyle(d).fontSize))):0
          };
        }""")
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
        "source_bibliography_42_entries": source_count == EXPECTED_SOURCES,
        "expected_editorial_revision_markers_present": all(revision_sentinels.values()),
        "usgs_2026_11_12_precision_correction_present_in_one_paragraph": precision_correction_ok,
        "original_compensation_figure_present": chart_count == 1,
        "timeline_has_five_chronology_cards_and_four_source_links": bool(
            timeline_stats and timeline_stats["count"] == 5
            and len(timeline_stats["creditLinks"]) == 4
            and timeline_stats["accessible"]),
        "timeline_preserves_estimate_measurement_distinction": bool(
            timeline_stats and timeline_stats["caution"] and timeline_stats["stageEstimates"]),
        "timeline_fits_and_has_readable_mobile_text": bool(
            timeline_stats and timeline_stats["withinViewport"]
            and not timeline_stats["clippedCards"]
            and timeline_stats["captionFontPx"] >= 14
            and timeline_stats["minDescriptionFontPx"] >= 14),
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
        ("original-timeline", timeline),
        ("evidence-table", table),
        ("sources", page.get_by_text("Sources & Further Reading", exact=False).first),
        ("footer", page.locator("footer").last),
    ):
        name = capture(page, locator, out / f"{width}-{label}.png")
        if name:
            captures[label] = name
    return {"viewport": width, "checks": checks, "document": page_stats,
            "overflowPx": overflow, "evidenceTable": table_stats,
            "originalTimeline": timeline_stats,
            "bibliographyEntryCount": source_count,
            "usgsPrecisionCorrectionParagraphPresent": precision_correction_ok,
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
    ap.add_argument("--cdp", metavar="LOCAL_CDP_ENDPOINT",
        help="Attach to an already authenticated Chromium browser using a LOOPBACK-ONLY "
             "CDP endpoint, e.g. http://127.0.0.1:9222; no credentials are exported.")
    args = ap.parse_args()
    url = os.environ.get("FV_PREVIEW_URL", "")
    if not url or urlsplit(url).scheme != "https" or urlsplit(url).hostname not in (
        "finalvestige.com", "www.finalvestige.com"
    ):
        ap.error("FV_PREVIEW_URL must be an HTTPS editor preview of finalvestige.com (do not publish URL).")
    storage = os.environ.get("FV_STORAGE_STATE")
    if storage and not Path(storage).is_file():
        ap.error("Existing authenticated browser state missing; path withheld.")
    if args.cdp:
        from urllib.parse import urlsplit as _urlsplit
        endpoint = _urlsplit(args.cdp)
        if (endpoint.scheme != "http" or endpoint.hostname not in ("127.0.0.1", "localhost")
                or endpoint.username or endpoint.password or endpoint.path not in ("", "/")
                or endpoint.query or endpoint.fragment or not endpoint.port):
            ap.error("--cdp accepts only a plain HTTP loopback host:port (no credentials or paths).")
        if storage:
            ap.error("Use either --cdp with an authenticated browser or FV_STORAGE_STATE, not both.")
    args.out.mkdir(parents=True, exist_ok=True)
    result = {"postId": 2151, "declaredGutenbergSha1": args.sha,
              "captureMode": "attached_authorized_browser" if args.cdp else "isolated_browser",
              "hashVerifiedByBrowser": False,
              "releaseGate": "MANUAL_EDITOR_REVIEW_REQUIRED",
              "viewports": []}
    with sync_playwright() as p:
        if args.cdp:
            # Reuse the authenticated session in an authorized *local* browser.
            # Open and close only our own tabs, without changing its user tabs,
            # profile, persistent cookies or logged-in WordPress session.
            browser = p.chromium.connect_over_cdp(args.cdp, timeout=15000)
            if not browser.contexts:
                raise RuntimeError("Local Chromium has no active browser context.")
            ctx = browser.contexts[0]
            for width in (390, 1440):
                page = ctx.new_page()
                try:
                    page.set_viewport_size({"width": width, "height": 900})
                    result["viewports"].append(inspect(page, width, args.out))
                finally:
                    page.close()
            # Playwright context-manager teardown disconnects from CDP.
            # Do not call browser.close() on a user's running Chromium.
        else:
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
