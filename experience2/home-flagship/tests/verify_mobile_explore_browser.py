#!/usr/bin/env python3
"""Non-production, exact-source mobile primary navigation admission.

Run from any directory:
 python -I experience2/home-flagship/tests/verify_mobile_explore_browser.py --out /tmp/ex2-mobile-menu
Requires local playwright + Chromium. Never writes WordPress. This is inlined exact
source QA, not Assembler staging, field CWV, whole-document WCAG or QD approval.
"""
import argparse
import json
import hashlib
from pathlib import Path
import re

HERE = Path(__file__).resolve().parents[1]
WIDTHS = (320, 360, 390, 420, 600, 768, 920, 921, 1440)
LINKS = (
    ("Investigations", "https://finalvestige.com/blog/"),
    ("Public Record", "https://finalvestige.com/accountability/"),
    ("Library", "https://finalvestige.com/free-resources/"),
)


def assert_source_contract(html, css):
    mast = re.search(r'<header class="fv-hf__masthead">(.*?)</header>', html, re.S)
    assert mast, "Missing flagship masthead"
    header = mast.group(1)
    details = re.search(r'<details class="fv-hf__mobile-explore">(.*?)</details>', header, re.S)
    assert details, "Native closed-by-default details disclosure missing"
    assert "<summary>Explore " in details.group(1), "Missing native summary"
    for selector, fragment in (
        ("desktop", re.search(r'<nav class="fv-hf__nav"[^>]*>(.*?)</nav>', header, re.S)),
        ("mobile", re.search(r'<nav class="fv-hf__mobile-explore-links"[^>]*>(.*?)</nav>',
                             details.group(1), re.S)),
    ):
        assert fragment, f"Missing {selector} primary routes"
        found = [(re.sub(r'<[^>]*>', '', name).strip(), href)
                 for href, name in re.findall(r'<a href="([^"]+)">(.+?)</a>',
                                              fragment.group(1), re.S)]
        assert found == list(LINKS), f"{selector} routes changed: {found!r}"
    assert re.search(r'class="fv-hf__mast-cta" href="https://finalvestige.com/focus/"', header)
    chapter = re.search(r'<nav class="fv-hf__chapter-nav"[^>]*>(.*?)</nav>', html, re.S)
    assert chapter and len(re.findall(r'<a href="#fv-hf-', chapter.group(1))) == 7
    assert 'aria-label="Primary site destinations"' in html
    assert ".fv-hf .fv-hf__mobile-explore" in css
    assert "@media (max-width: 920px)" in css
    assert "@media (forced-colors: active)" in css


def inline_local_styles(html):
    # Browser sandbox may block file:// navigation. Inlining the actual six
    # checked-out stylesheets is deterministic and requires no HTTP server.
    stylesheet_names = (
        "flagship.css", "chronicle.css", "chronicle-lens.css",
        "inquiry.css", "observer-lab.css", "reading-trail.css",
    )
    found = []
    def replace(m):
        name = m.group(1)
        assert name in stylesheet_names, f"Unapproved stylesheet {name!r}"
        found.append(name)
        return "<style>\n" + (HERE / name).read_text() + "\n</style>"
    rendered = re.sub(r'<link rel="stylesheet" href="\./([^"]+)">', replace, html)
    assert tuple(found) == stylesheet_names, f"Stylesheet order changed: {found}"
    return rendered


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
    render_html = inline_local_styles(html)
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
                    page.set_content(render_html, wait_until="domcontentloaded", timeout=30000)
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
                        # Even with the menu open, the free Focus CTA must remain hittable.
                        assert cta.evaluate("""e => {
                            const r=e.getBoundingClientRect();
                            const hit=document.elementFromPoint((r.left+r.right)/2,(r.top+r.bottom)/2);
                            return hit===e || e.contains(hit);
                        }"""), "Mobile menu overlays the Focus CTA"
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
