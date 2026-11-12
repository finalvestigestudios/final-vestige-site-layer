#!/usr/bin/env python3
"""Read-only, anonymous source-reader audit for Final Vestige investigation #2151.

This tests public official PDFs separately from the *authenticated* WordPress
preview QA. It CANNOT approve publication or certify that a browser screenshot
contains legible PDF pages; a human must inspect the screenshots.

Dependencies: pip install playwright pymupdf
             python -m playwright install chromium
Run: python inspect_anonymous_pdf_sources_2151.py --out /private/fv-pdf-qa
     (requires a desktop/display for visible PDF viewer inspection)
Optional: --cdp http://127.0.0.1:9222 (existing Chromium, loopback only)
Never put private WordPress previews/cookies in these records.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import fitz
from playwright.sync_api import sync_playwright

# These publicly documented URLs are intentionally not preview/nonced links.
SOURCES = [
    ("usace-2014", "https://www.mvn.usace.army.mil/Portals/56/docs/PAO/Brochures/BCspillwaybooklet.pdf",
     ("Caernarvon", "Bonnet")),
    ("usace-2018", "https://www.mvn.usace.army.mil/Portals/56/docs/Recreation/BCS/Brochures/BC%20spillway%20booklet%20Dec%202018%20.pdf",
     ("Caernarvon", "Bonnet")),
    ("usgs-1994", "https://pubs.usgs.gov/of/1994/0275/report.pdf",
     ("Crevasses", "Davis")),
    ("usgs-2008-combined", "https://pubs.usgs.gov/sir/2008/5164/pdf/sir20085164_AppendixA.pdf",
     ("Arkansas City", "Mississippi")),
    ("usgs-2008-arkansas-city", "https://pubs.usgs.gov/sir/2008/5164/pdf/sir20085164_MississippiRiver.pdf",
     ("Arkansas City", "Chicot")),
]
ALLOWED_HOSTS = {"pubs.usgs.gov", "www.mvn.usace.army.mil"}

def source_check(ctx, source, out: Path, max_bytes: int):
    name, url, expected = source
    row = {
        "id": name, "url": url, "observed_utc": datetime.now(timezone.utc).isoformat(),
        "anonymous_http_status": None, "pdf_header_pass": False,
        "parsed_pdf_pass": False, "page_count": None, "sha256": None,
        "extracted_text_chars": 0, "expected_phrases_found": {},
        "pdf_page_renders": [], "browser_viewer_screenshot": None,
        "browser_navigation_error": None,
        "human_checked_actual_browser_pixels": False,
        "source_release_gate": "NOT_PASSED",
    }
    if urlsplit(url).hostname not in ALLOWED_HOSTS or urlsplit(url).scheme != "https":
        row["error"] = "URL not on the allowlisted government domains"
        return row
    try:
        # Anonymous Playwright context; NO stored state or account login.
        response = ctx.request.get(url, timeout=60000, max_redirects=5)
        row["anonymous_http_status"] = response.status
        row["response_content_type"] = response.headers.get("content-type", "")
        length = response.headers.get("content-length", "")
        if length.isdecimal() and int(length) > max_bytes:
            row["error"] = "PDF larger than configured download ceiling"
            return row
        if response.status != 200:
            row["error"] = f"Anonymous HTTP status {response.status}; not a proof of normal-reader failure"
            return row
        body = response.body()
        if len(body) > max_bytes:
            row["error"] = "Downloaded PDF exceeded configured byte ceiling"
            return row
        if not body.lstrip()[:128].startswith(b"%PDF-"):
            row["error"] = "Response did not contain a PDF header"
            return row
        row["pdf_header_pass"] = True
        row["sha256"] = hashlib.sha256(body).hexdigest()
        row["file_bytes"] = len(body)
        with fitz.open(stream=body, filetype="pdf") as doc:
            row["page_count"] = len(doc)
            row["parsed_pdf_pass"] = bool(len(doc))
            # The two USGS cases may have scanned pages: missing extractable text
            # does NOT imply missing readable content; require human PDF inspection.
            text_parts = []
            for p in doc:
                text_parts.append(p.get_text("text"))
            all_text = "\n".join(text_parts)
            row["extracted_text_chars"] = len(all_text)
            flat = re.sub(r"\s+", " ", all_text).casefold()
            row["expected_phrases_found"] = {
                phrase: phrase.casefold() in flat for phrase in expected
            }
            for index in sorted(set([0, max(0, len(doc) - 1)])):
                if index < len(doc):
                    pix = doc[index].get_pixmap(matrix=fitz.Matrix(1.35, 1.35),
                                               alpha=False)
                    fname = f"{name}-pdf-raster-page-{index + 1}.png"
                    pix.save(out / fname)
                    row["pdf_page_renders"].append(fname)
    except Exception as exc:
        row["error"] = "Document fetch/parse failed: " + type(exc).__name__
        # Do not serialize credentials, cookies, request headers, or arbitrary
        # exception messages that might accidentally include private data.
        return row

    # The next capture is separately made from the real public URL in Chromium.
    # Headless/PDF-plugin limitations may show a blank viewer; screenshots MUST
    # be visually reviewed and are never auto-promoted to a passing result.
    page = ctx.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)
        fname = f"{name}-anonymous-browser.png"
        page.screenshot(path=str(out / fname), animations="disabled",
                        timeout=20000)
        row["browser_viewer_screenshot"] = fname
        row["browser_final_host"] = urlsplit(page.url).hostname
    except Exception as exc:
        row["browser_navigation_error"] = type(exc).__name__
    finally:
        page.close()
    row["interpretation"] = (
        "HTTP PDF byte/parse/page-render checks are separate from anonymous "
        "browser PDF-viewer legibility; reviewer must inspect browser screenshot "
        "and printed source pages before recording an editorial PASS."
    )
    return row

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path,
                        help="Private evidence directory; do not commit screenshots to GitHub")
    parser.add_argument("--cdp", default=None,
                        help="Connect existing local Chromium; only http://127.0.0.1 or localhost")
    parser.add_argument("--max-mb", type=int, default=90)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.cdp and not (
        args.cdp.startswith("http://127.0.0.1:") or
        args.cdp.startswith("http://localhost:")
    ):
        parser.error("CDP must be a loopback-only endpoint")
    with sync_playwright() as pw:
        browser = (pw.chromium.connect_over_cdp(args.cdp) if args.cdp
                   else pw.chromium.launch(headless=False))
        # A fresh ephemeral context is isolated from any logged-in editor session.
        ctx = browser.new_context(accept_downloads=True, service_workers="block")
        try:
            results = [source_check(ctx, source, args.out, args.max_mb * 1024 * 1024)
                       for source in SOURCES]
        finally:
            ctx.close()
            if not args.cdp:
                browser.close()
    result = {
        "investigation": "WordPress draft #2151 — The Levee They Blew on Purpose",
        "source_gate": "HOLD — HUMAN SCREENSHOT AND CLAIM-SCOPED REVIEW REQUIRED",
        "not_a_wordpress_preview_test": True,
        "results": results,
        "instructions": (
            "Inspect each anonymous browser capture for *actual legible PDF page pixels*, "
            "not just a blank viewer or loading spinner; inspect the rendered PDF pages "
            "for context, then cross-check each article claim against the precise "
            "government source. Never treat a crawler 403 or a successful byte fetch "
            "alone as evidence of ordinary-reader availability."
        ),
    }
    target = args.out / "source-readability.json"
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print("Evidence written:", target)
    print("Source pass deliberately withheld; human visual review remains mandatory.")
    for r in results:
        print(r["id"], "status=", r["anonymous_http_status"],
              "pdf=", r["parsed_pdf_pass"],
              "viewer_screenshot=", bool(r["browser_viewer_screenshot"]),
              "gate=", r["source_release_gate"])

if __name__ == "__main__":
    main()
