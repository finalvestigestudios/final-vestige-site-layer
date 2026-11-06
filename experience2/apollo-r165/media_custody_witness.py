"""Apollo archival-gallery selected-media custody witness; READ ONLY.

Browser captures actual currentSrc + response bytes (including WordPress i0.wp.com
srcset rewrites), not just DOM img.src/naturalWidth. Strict release HOLD unless
all evidence and photo controls pass. Never labels this commercial rights clearance.

Run: python media_custody_witness.py --url https://staging.example/... --out evidence
--fixture option is for offline tests ONLY and can NEVER return a release PASS.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

NASA_RECORDS = (
    "https://www.nasa.gov/image-detail/amf-s66-58038/",
    "https://www.nasa.gov/image-detail/amf-s67-15717/",
    "https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129",
)
WIDTHS = (320, 360, 390, 768, 1440, 1920)
MIN_BYTES = 512  # nontrivial transfer guard, not an image-quality/rights judgment
MIN_DIMENSION = 33


def safe_url(url):
    """Do not retain visitor query strings, UTM or tokens in evidence artifacts."""
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}" if p.scheme in ("http", "https") else "NON_HTTP_SOURCE"


def selected_host_allowed(url, site_host):
    host = (urlparse(url).hostname or "").lower()
    return host in {site_host.lower(), "i0.wp.com", "i1.wp.com", "i2.wp.com"}


def witness(url, out, fixture=None, intercept=None, widths=WIDTHS):
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http") or not parsed.hostname:
        raise ValueError("Provide one explicit HTTP(S) installed-page URL")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    is_fixture = fixture is not None
    result = {
        "mode": "CONTROLLED_FIXTURE_NOT_INSTALLED_WORDPRESS" if is_fixture else "READ_ONLY_INSTALLED_PAGE",
        "page": safe_url(url), "release_qualified": False,
        "rights": "NOT_CLEARED_FOR_PAID_PRODUCT_OR_ADVERTISING",
        "source_records": list(NASA_RECORDS), "widths": {},
        "limitations": ["Laboratory image-response evidence is not visitor CWV, field acceptance, or NASA commercial permission."],
    }
    html = Path(fixture).read_text(encoding="utf-8") if is_fixture else None
    if is_fixture:
        result["fixture_sha256"] = hashlib.sha256(html.encode()).hexdigest()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"),
            headless=True, args=["--no-sandbox"],
        )
        for width in widths:
            context = browser.new_context(viewport={"width": width, "height": 900}, device_scale_factor=2 if width <= 390 else 1, reduced_motion="reduce")
            if intercept is not None:
                # Permitted for offline synthetic tests only. In real mode no routes installed.
                if not is_fixture:
                    raise ValueError("Intercept forbidden for installed-page acceptance")
                context.route("**/*", intercept)
            page = context.new_page()
            responses = {}
            failures = []
            page.on("response", lambda r: responses.__setitem__(r.url, r))
            page.on("requestfailed", lambda r: failures.append(safe_url(r.url)))
            row = {"checks": {}, "images": [], "failed_requests": [], "errors": []}
            try:
                if is_fixture:
                    page.set_content(html, wait_until="domcontentloaded")
                    row["http_status"] = "FIXTURE_ONLY"
                else:
                    response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    row["http_status"] = response.status if response else None
                gallery = page.locator('[data-fvx-chrono-gallery]')
                buttons = gallery.locator('.fvx-archive-choice button')
                imgs = gallery.locator('figure[data-fvx-chrono-photo] img')
                links = gallery.locator('figcaption a[href]')
                row["checks"]["one_gallery"] = gallery.count() == 1
                row["checks"]["three_photos"] = imgs.count() == 3
                row["checks"]["exact_nasa_sources"] = (
                    links.count() == 3 and tuple(links.evaluate_all('(a)=>a.map(x=>x.href)')) == NASA_RECORDS
                )
                row["checks"]["independent_photo_controls"] = buttons.count() == 3
                row["checks"]["no_horizontal_overflow"] = page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                for i in range(min(imgs.count(), 3)):
                    if buttons.count() == 3:
                        buttons.nth(i).click()
                    imgs.nth(i).scroll_into_view_if_needed(timeout=4000)
                    # Captures real currentSrc choice after sizes/srcset negotiation.
                    imgs.nth(i).evaluate("(img) => img.decode().catch(() => null)")
                    image = imgs.nth(i).evaluate('''img => ({src: img.src, currentSrc: img.currentSrc,
                        srcset: img.srcset, sizes: img.sizes, complete: img.complete,
                        naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
                        alt: img.getAttribute('alt')})''')
                    current = image["currentSrc"]
                    response = responses.get(current)
                    body_size = None
                    body_sha = None
                    content_type = None
                    status = None
                    if response:
                        status = response.status
                        content_type = (response.headers.get("content-type") or "").split(";")[0].lower()
                        try:
                            data = response.body()
                            body_size = len(data)
                            body_sha = hashlib.sha256(data).hexdigest()
                        except Exception:
                            pass
                    checks = {
                        "decoded": image["complete"] and image["naturalWidth"] >= MIN_DIMENSION and image["naturalHeight"] >= MIN_DIMENSION,
                        "selected_host_allowed": selected_host_allowed(current, parsed.hostname),
                        "response_2xx": status is not None and 200 <= status < 300,
                        "response_image_mime": content_type is not None and content_type.startswith("image/"),
                        "nontrivial_response_bytes": body_size is not None and body_size >= MIN_BYTES,
                        "descriptive_alt": bool(image["alt"] and len(image["alt"].strip()) >= 25),
                    }
                    row["images"].append({
                        "photo_index": i, "src": safe_url(image["src"]), "currentSrc": safe_url(current),
                        "srcset_selected": bool(image["srcset"] and current != image["src"]),
                        "current_src_host": urlparse(current).hostname, "natural_width": image["naturalWidth"],
                        "natural_height": image["naturalHeight"], "http_status": status,
                        "content_type": content_type, "transferred_bytes": body_size,
                        "sha256_response_body": body_sha, "checks": checks,
                    })
                    row["checks"][f"photo_{i}_verified_selected_response"] = all(checks.values())
                if buttons.count() == 3:
                    buttons.nth(0).click()
                row["failed_requests"] = sorted(set(failures))[:20]
                screenshot = out / f"selected-media-{width}.png"
                page.screenshot(path=str(screenshot), full_page=True, animations="disabled")
                row["screenshot_sha256"] = hashlib.sha256(screenshot.read_bytes()).hexdigest()
            except Exception as exc:
                row["errors"].append(type(exc).__name__)
                row["checks"]["navigation_and_inspection"] = False
            result["widths"][str(width)] = row
            context.close()
        browser.close()
    checks = [value for row in result["widths"].values() for value in row["checks"].values()]
    result["passed_checks"] = sum(bool(x) for x in checks)
    result["total_checks"] = len(checks)
    result["result"] = "LAB_MEDIA_GATE_PASS_ONLY" if checks and all(checks) else "HOLD_MEDIA_GATE_FAIL"
    if is_fixture:
        result["result"] = "HOLD_OFFLINE_FIXTURE_ONLY" if all(checks) else "HOLD_OFFLINE_FIXTURE_FAIL"
    # Always hold release: performance, axe, 200-400% zoom, WP staging, editorial QA
    # and founder signoff are independent gates, not granted by an image transfer.
    (out / "media_custody.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--fixture", type=Path, help="OFFLINE fixture only; NEVER installed-page proof")
    args = ap.parse_args()
    r = witness(args.url, args.out, args.fixture)
    print(json.dumps({"result": r["result"], "checks": f"{r['passed_checks']}/{r['total_checks']}", "out": str(args.out)}))
    raise SystemExit(0 if r["result"] == "LAB_MEDIA_GATE_PASS_ONLY" else 2)
