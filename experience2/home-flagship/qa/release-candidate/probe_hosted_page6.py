#!/usr/bin/env python3
"""Anonymous, GET-only hosted homepage observation; NEVER a release approval.

No WordPress authentication or content mutation. Does not persist HTML, screenshots,
user records, browser cookies, image bytes, URL query strings or subscriber data.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit

HOST = "https://finalvestige.com/"
CHAPTER_TARGETS = (
    "fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence", "fv-hf-inquiry",
    "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title",
)
WIDTHS = (320, 390, 768, 1440, 1920)
NYPL_BINARY_MARKERS = ("edit-017-v02-nypl-5003296", "nypl-5003296-original")


def internal_focus_link(href: str) -> bool:
    """Only the actual site's Focus route qualifies; external lookalikes do not."""
    if not isinstance(href, str):
        return False
    dest = urlsplit(urljoin(HOST, href))
    return dest.scheme == "https" and dest.hostname == "finalvestige.com" and dest.path.rstrip("/") == "/focus"


class PublicHomeParser(HTMLParser):
    """DOM-shaped facts only; no article text is retained in the report."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.chapter_hrefs: set[str] = set()
        self.margin_index: set[str] = set()
        self.margin_count = 0
        self.focus_count = 0
        self.jetpack_marker = False
        self.flagship = False
        self.binary_nypl_evidence: list[str] = []
        self.image_identities: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        ident = a.get("id")
        if ident:
            self.ids.add(ident)
        if "data-fv-home-flagship" in a:
            self.flagship = True
        if "fv-margin-strip__item" in classes and tag == "span":
            self.margin_count += 1
            if (a.get("style") or "").startswith("--i:"):
                self.margin_index.add(a["style"])
        if tag == "a":
            href = a.get("href") or ""
            if href.startswith("#fv-hf-"):
                self.chapter_hrefs.add(href[1:])
            if internal_focus_link(href):
                self.focus_count += 1
        if "wp-block-jetpack-subscriptions" in classes or "jetpack-subscriptions" in classes:
            self.jetpack_marker = True
        if tag == "form" and any(p in (a.get("action") or "").lower()
                                 for p in ("subscribe.wordpress.com", "jetpack_subscriptions")):
            self.jetpack_marker = True
        # Inspect binary image delivery vectors only, not NYPL catalog/citation links.
        if tag in ("img", "source"):
            for key in ("src", "srcset", "data-src", "data-srcset"):
                value = (a.get(key) or "").lower()
                if any(marker in value for marker in NYPL_BINARY_MARKERS):
                    self.binary_nypl_evidence.append(f"{tag}.{key}")
                if "s67-19766" in value:
                    self.image_identities.add("apollo")
                if "franklinexpeditionnote" in value:
                    self.image_identities.add("franklin")


def inspect_public_html(html: str) -> dict:
    if not isinstance(html, str) or not html or len(html) < 400:
        raise ValueError("HOST_HTML_INVALID")
    p = PublicHomeParser()
    p.feed(html)
    missing = [x for x in CHAPTER_TARGETS if x not in p.ids or x not in p.chapter_hrefs]
    structural = {
        "flagship_present": p.flagship,
        "chapter_targets_and_links": len(CHAPTER_TARGETS) - len(missing),
        "chapter_names_missing": missing,
        "margins_count": p.margin_count,
        "margin_unique_indices": len(p.margin_index),
        "focus_links": p.focus_count,
        "jetpack_markup_detected": p.jetpack_marker,
        "apollo_franklin_binary_markers": sorted(p.image_identities),
    }
    structural["protected_content_ok"] = (
        p.flagship and not missing and p.margin_count == 72
        and len(p.margin_index) == 72 and p.focus_count >= 2
        and p.jetpack_marker and p.image_identities == {"apollo", "franklin"}
    )
    return {
        "structural": structural,
        "nypl_binary_embedded": bool(p.binary_nypl_evidence),
        "nypl_vectors": sorted(set(p.binary_nypl_evidence)),
        "html_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
    }


def evaluate_receipts(receipts: list[dict]) -> dict:
    if len(receipts) != 6 or {r.get("test_case") for r in receipts} != {
        f"js_{width}" for width in WIDTHS
    } | {"nojs_390"}:
        raise ValueError("HOST_BROWSER_MATRIX_INCOMPLETE")
    all_ok = all(
        r.get("http_status") == 200 and r.get("protected_content_ok") is True
        and r.get("host") == "finalvestige.com"
        for r in receipts
    )
    image_rights_hold = any(r.get("nypl_binary_embedded") for r in receipts)
    probe390 = next(r for r in receipts if r["test_case"] == "js_390")
    media = probe390.get("first_party_media")
    media_ok = isinstance(media, dict) and set(media) == {"apollo", "franklin"} and all(
        x.get("status") == "PASS" for x in media.values())
    return {
        "structural_gate": "PASS" if all_ok else "FAIL",
        "first_party_archive_binary_gate": "PASS" if media_ok else "FAIL",
        "nypl_image_specific_rights_gate": "HOLD_REPRODUCTION_PRESENT" if image_rights_hold
        else "HOLD_NEEDS_EDITORIAL_APPROVAL",
        "release_gate": "HOLD",
    }


def first_party_media_url(src: str, expected_filename: str) -> bool:
    """Never fetch a third-party URL or the unresolved NYPL reproduction."""
    if not isinstance(src, str) or not isinstance(expected_filename, str):
        return False
    p = urlsplit(src)
    return (p.scheme == "https" and p.hostname == "finalvestige.com"
            and p.username is None and p.password is None
            and p.path.startswith("/wp-content/uploads/")
            and p.path.endswith("/" + expected_filename)
            and not p.query and not p.fragment)


def inspect_first_party_media(context, page) -> dict:
    """Retrieve approved originals anonymously into memory; never persist bytes."""
    files = {"apollo": "s67-19766.webp", "franklin": "Franklinexpeditionnote.jpg"}
    found = {}
    for name, filename in files.items():
        selector = '[data-fv-case="' + name + '"] img[data-fv-archive-img]'
        loc = page.locator(selector)
        if loc.count() != 1:
            found[name] = {"status": "MISSING_IMAGE_NODE"}
            continue
        src = loc.get_attribute("src") or ""
        if not first_party_media_url(src, filename):
            found[name] = {"status": "UNAPPROVED_IMAGE_ORIGIN"}
            continue
        resp = context.request.get(src, timeout=30000)
        binary = resp.body()  # Memory only; never written, logged or screenshotted.
        mime = resp.headers.get("content-type", "").split(";", 1)[0]
        verified = resp.status == 200 and mime.startswith("image/") and len(binary) >= 10000
        found[name] = {"status": "PASS" if verified else "TRANSFER_FAILED",
                       "http_status": resp.status, "media_type": mime,
                       "bytes_received": len(binary),
                       "sha256": hashlib.sha256(binary).hexdigest()}
    return found


def run_browser() -> dict:
    # Playwright is deliberately loaded only during hosted read-only observations.
    from playwright.sync_api import sync_playwright

    results: list[dict] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for width, js in [(w, True) for w in WIDTHS] + [(390, False)]:
                ctx = browser.new_context(viewport={"width": width, "height": 844},
                                          java_script_enabled=js,
                                          service_workers="block", accept_downloads=False)
                page = ctx.new_page()
                # No account cookies are loaded; prevent even incidental POST requests.
                page.route("**/*", lambda route: route.continue_()
                           if route.request.method == "GET" else route.abort())
                try:
                    response = page.goto(HOST, wait_until="domcontentloaded", timeout=45000)
                    if response is None:
                        raise ValueError("HOST_DOCUMENT_RESPONSE_MISSING")
                    if urlsplit(page.url).hostname != "finalvestige.com":
                        raise ValueError("HOST_REDIRECT_OUTSIDE_ALLOWED_ORIGIN")
                    # Allow normal source-side enhancement without scrolling into third-party media.
                    page.wait_for_timeout(650)
                    snapshot = inspect_public_html(page.content())
                    structures = snapshot["structural"]
                    # One real first-party binary fetch per approved historical image.
                    # Do not request or preserve the unresolved NYPL reproduction.
                    media = inspect_first_party_media(ctx, page) if (width == 390 and js) else None
                    results.append({
                        "test_case": f"{'js' if js else 'nojs'}_{width}",
                        "host": "finalvestige.com",
                        "http_status": response.status,
                        "html_sha256": snapshot["html_sha256"],
                        "protected_content_ok": structures["protected_content_ok"],
                        "protected_content": structures,
                        "nypl_binary_embedded": snapshot["nypl_binary_embedded"],
                        "nypl_vectors": snapshot["nypl_vectors"],
                        "anonymous_context": True,
                        "non_get_requests_allowed": False,
                        "first_party_media": media,
                    })
                finally:
                    ctx.close()
        finally:
            browser.close()
    gates = evaluate_receipts(results)
    return {
        "scope": "ANONYMOUS_HOSTED_GET_ONLY_PLAYWRIGHT",
        "source_note": "PUBLIC_HOST_RENDER_NOT_AUTHENTICATED_RAW_GUTENBERG",
        "does_not_establish": ["copyright_permission", "publication_authorization", "WCAG_2.2_AA",
                               "field_CWV_p75", "Safari_or_physical_device_support", "Jetpack_submission"],
        "cms_writes": False, "screenshot_or_image_bytes_retained": False,
        "source_html_retained": False, "cases": results, "gates": gates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="HOSTED_PAGE6_ANONYMOUS_AUDIT.json")
    args = parser.parse_args()
    out = Path(args.output)
    try:
        report = run_browser()
    except Exception as exc:
        report = {"scope": "ANONYMOUS_HOSTED_GET_ONLY_PLAYWRIGHT",
                  "status": "INSTRUMENTATION_FAILURE", "failure_type": type(exc).__name__,
                  "release_gate": "HOLD", "cms_writes": False}
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("HOSTED AUDIT INSTRUMENTATION FAILURE: " + type(exc).__name__)
        return 2
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["gates"], sort_keys=True))
    return 0 if (report["gates"]["structural_gate"] == "PASS" and
                 report["gates"]["first_party_archive_binary_gate"] == "PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
