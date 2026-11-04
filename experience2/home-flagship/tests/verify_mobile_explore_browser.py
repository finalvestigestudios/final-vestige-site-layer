#!/usr/bin/env python3
"""Non-production, exact-source mobile primary navigation admission.

Run from any directory:
 python -I experience2/home-flagship/tests/verify_mobile_explore_browser.py --out /tmp/ex2-mobile-menu
Requires local playwright + Chromium. Never writes WordPress. This is FILE://
source QA, not Assembler staging, field CWV, whole-document WCAG or QD approval.
"""
import argparse
import json
import hashlib
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parents[1]
WIDTHS = (320, 360, 390, 420, 600, 768, 920, 921, 1440)
LINKS = (
    ("Investigations", "https://finalvestige.com/blog/"),
    ("Public Record", "https://finalvestige.com/accountability/"),
    ("Library", "https://finalvestige.com/free-resources/"),
)


def assert_source_contract(html, css):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    masthead = soup.select_one(".fv-hf__masthead")
    assert masthead is not None
    details = masthead.select("details.fv-hf__mobile-explore")
    assert len(details) == 1 and not details[0].has_attr("open")
    summary = details[0].find("summary", recursive=False)
    assert summary and "Explore" in summary.get_text(" ", strip=True)
    desktop = masthead.select_one("nav.fv-hf__nav")
    mobile = details[0].select_one("nav.fv-hf__mobile-explore-links")
    assert desktop and mobile
    for nav in (desktop, mobile):
        found = [(a.get_text(" ", strip=True), a.get("href"))
                 for a in nav.find_all("a")]
        assert found == list(LINKS), f"Navigation route mismatch: {found!r}"
    assert masthead.select_one(".fv-hf__mast-cta")["href"] == "https://finalvestige.com/focus/"
    assert len(soup.select(".fv-hf__chapter-nav a")) == 7
    assert "aria-label=\"Primary site destinations\"" in html
    assert ".fv-hf .fv-hf__mobile-explore" in css
    assert "@media (max-width: 920px)" in css
    assert "@media (forced-colors: active)" in css


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("/tmp/ex2-mobile-explore"))
    p.add_argument("--chromium", default="/usr/bin/chromium")
    args = p.parse_args()
    from playwright.sync_api import sync_playwright

    html_path = HERE / "index.html"
    css_path = HERE / "flagship.css"
    html, css = html_path.read_text(), css_path.read_text()
    assert_source_contract(html, css)
    args.out.mkdir(parents=True, exist_ok=True)
    results, failures = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=args.chromium,
                                     args=["--no-sandbox"])
        try:
            for width in WIDTHS:
                context = browser.new_context(viewport={"width": width, "height": 900},
                                              java_script_enabled=False,
                                              reduced_motion="reduce")
                page = context.new_page()
                # Local only: external media links cannot bias this contract.
                page.route("https://**/*", lambda route: route.abort())
                page.route("http://**/*", lambda route: route.abort())
                row = {"width": width, "status": "FAIL"}
                try:
                    page.goto(html_path.as_uri(), wait_until="load", timeout=30000)
                    assert page.locator(".fv-hf__mobile-explore").count() == 1
                    is_mobile = width <= 920
                    visible_mobile = page.locator(".fv-hf__mobile-explore").is_visible()
                    visible_desktop = page.locator(".fv-hf__nav").is_visible()
                    assert visible_mobile == is_mobile, "Mobile menu breakpoint mismatch"
                    assert visible_desktop != is_mobile, "Desktop links not correctly hidden/shown"
                    mast = page.locator(".fv-hf__masthead")
                    metrics = mast.evaluate("""el => ({
                        left:el.getBoundingClientRect().left,
                        right:el.getBoundingClientRect().right,
                        width:el.getBoundingClientRect().width,
                        scroll:document.documentElement.scrollWidth,
                        viewport:innerWidth
                    })""")
                    assert metrics["scroll"] <= width + 1, "Horizontal document overflow"
                    cta = page.locator(".fv-hf__mast-cta")
                    assert cta.is_visible(), "Focus destination hidden"
                    assert cta.get_attribute("href") == "https://finalvestige.com/focus/"
                    if is_mobile:
                        summary = page.locator(".fv-hf__mobile-explore summary")
                        rect = summary.bounding_box()
                        assert rect and rect["width"] >= 44 and rect["height"] >= 44, "Small menu target"
                        assert rect["x"] >= -1 and rect["x"] + rect["width"] <= width + 1, "Menu button offscreen"
                        # Native details behavior with JavaScript intentionally disabled.
                        assert not page.locator(".fv-hf__mobile-explore").evaluate("(d)=>d.open")
                        summary.focus()
                        assert summary.evaluate("(e)=>document.activeElement===e"), "Summary not focusable"
                        page.keyboard.press("Enter")
                        assert page.locator(".fv-hf__mobile-explore").evaluate("(d)=>d.open"), "Enter did not open"
                        for label, href in LINKS:
                            anchor = page.locator(".fv-hf__mobile-explore-links a", has_text=label)
                            assert anchor.is_visible() and anchor.get_attribute("href") == href
                            box = anchor.bounding_box()
                            assert box and box["height"] >= 44 and box["width"] >= 44, label+" touch target"
                        page.keyboard.press("Tab")
                        first = page.locator(".fv-hf__mobile-explore-links a").first
                        assert first.evaluate("(e)=>document.activeElement===e"), "Tab did not reach first route"
                        summary.focus()
                        page.keyboard.press("Enter")
                        assert not page.locator(".fv-hf__mobile-explore").evaluate("(d)=>d.open"), "Enter did not close"
                        assert not first.is_visible(), "Closed menu still visible"
                    if width in (320, 390, 768, 921, 1440):
                        page.screenshot(path=str(args.out / f"mobile-explore-{width}.png"),
                                        animations="disabled", full_page=False)
                    row.update({"status": "PASS", "masthead": metrics,
                                "mobile_nav_visible": visible_mobile,
                                "desktop_nav_visible": visible_desktop})
                except Exception as exc:
                    row["error"] = str(exc)
                    failures.append(row.copy())
                finally:
                    results.append(row)
                    context.close()
        finally:
            browser.close()
    receipt = {"source_sha256": {
                   "index.html": hashlib.sha256(html.encode()).hexdigest(),
                   "flagship.css": hashlib.sha256(css.encode()).hexdigest()},
               "kind": "exact-source FILE URL; NOT WordPress/Assembler staging",
               "javascript": False, "reduced_motion": True, "results": results,
               "failures": failures}
    (args.out / "mobile-explore-receipt.json").write_text(json.dumps(receipt, indent=2))
    print(json.dumps({"passing": len(results) - len(failures),
                      "total": len(results), "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
