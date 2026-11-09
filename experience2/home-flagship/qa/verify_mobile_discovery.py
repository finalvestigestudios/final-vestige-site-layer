#!/usr/bin/env python3
"""EX2 native mobile-navigation admission for the real candidate source.

Browser mode renders the exact checkout's masthead with exact flagship.css,
not a full WordPress page. No claim of hosted staging, axe or field CWV.
No network, analytics calls or subscriber actions are performed.
"""
import argparse
import json
import re
from pathlib import Path

ROUTES = {
    "Investigations": "https://finalvestige.com/blog/",
    "Public Record": "https://finalvestige.com/accountability/",
    "Library": "https://finalvestige.com/free-resources/",
}
FOCUS = "https://finalvestige.com/focus/"


def source_check(html, css):
    match = re.search(r'<header class="fv-hf__masthead">([\s\S]*?)</header>', html)
    assert match, "Candidate header not found"
    header = match.group(0)
    assert header.count('<details class="fv-hf__mobile-menu">') == 1
    assert '<summary>Explore site <span aria-hidden="true">' in header
    assert header.count('class="fv-hf__nav"') == 1
    nav = re.search(r'<nav class="fv-hf__mobile-links"[\s\S]*?</nav>', header)
    assert nav, "Missing no-JS mobile navigation landmark"
    for title, href in ROUTES.items():
        assert f'href="{href}"' in nav.group(0) and title in nav.group(0), title
    assert header.count(f'href="{FOCUS}"') == 1, "Focus CTA missing or duplicated"
    assert re.search(r'\.fv-hf__mobile-menu\s*\{\s*display\s*:\s*none', css), "Desktop concealment missing"
    assert re.search(r'@media\s*\(max-width:\s*920px\)[\s\S]*?\.fv-hf__mobile-menu\s*\{\s*display\s*:\s*block', css), "No mobile breakpoint"
    assert re.search(r'\.fv-hf__mobile-links a\s*\{[^}]*min-height\s*:\s*44px', css), "Tap target rule missing"
    assert 'fv-hf-evidence' in html and 'fv-hf-chronicle' in html and 'fv-hf-observer' in html
    assert 'data-fv-archive-img' in html and 'data-fv-direction-choice' in html
    return header


def browser_check(header, css, out=None):
    from playwright.sync_api import sync_playwright
    observations = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, executable_path="/usr/bin/chromium",
            args=["--no-sandbox"])
        for width in (320, 390, 560, 768, 920, 921, 1440, 1920):
            for js in (False, True):
                ctx = browser.new_context(
                    viewport={"width": width, "height": 820},
                    java_script_enabled=js, reduced_motion="reduce")
                page = ctx.new_page()
                page.set_content(
                    '<!doctype html><html><head><meta name="viewport" '
                    'content="width=device-width,initial-scale=1"><style>'
                    + css + '</style></head><body><div class="fv-hf">'
                    '<div class="fv-hf__canvas">' + header +
                    '</div></div></body></html>')
                mobile = width <= 920
                menu = page.locator("details.fv-hf__mobile-menu")
                assert menu.is_visible() == mobile, ("mobile menu", width, js)
                assert page.locator(".fv-hf__nav").is_visible() != mobile
                cta = page.locator(".fv-hf__mast-cta")
                assert cta.is_visible() and cta.get_attribute("href") == FOCUS
                if mobile:
                    summary = menu.locator("summary")
                    assert summary.bounding_box()["height"] >= 44
                    summary.focus()
                    page.keyboard.press("Enter")
                    assert menu.get_attribute("open") is not None
                    region = menu.locator(".fv-hf__mobile-links")
                    assert region.is_visible()
                    for title, route in ROUTES.items():
                        link = region.get_by_role("link", name=title)
                        assert link.is_visible() and link.get_attribute("href") == route
                        assert link.bounding_box()["height"] >= 44
                    # Commercial CTA remains actionable even while the native
                    # menu is open: fail if the dropdown covers its hit target.
                    panel_box, cta_box = region.bounding_box(), cta.bounding_box()
                    overlap = (min(panel_box["x"] + panel_box["width"],
                                   cta_box["x"] + cta_box["width"]) >
                               max(panel_box["x"], cta_box["x"]) and
                               min(panel_box["y"] + panel_box["height"],
                                   cta_box["y"] + cta_box["height"]) >
                               max(panel_box["y"], cta_box["y"]))
                    assert not overlap, ("menu obscures Focus", width, js)
                    cta.click(trial=True)
                    summary.focus()
                    page.keyboard.press("Enter")
                    assert menu.get_attribute("open") is None
                extent = page.evaluate(
                    '({scroll: document.documentElement.scrollWidth, '
                    'viewport: window.innerWidth})')
                assert extent["scroll"] <= extent["viewport"] + 1, (
                    "horizontal overflow", width, js, extent)
                if out and not js and width in (320, 390, 768, 1440):
                    page.screenshot(
                        path=str(out / f"mobile_header_{width}_nojs.png"),
                        full_page=True)
                observations.append({
                    "width": width, "js": js,
                    "mobile_menu": "PASS" if mobile else "HIDDEN",
                    "focus_cta": "VISIBLE", "overflow": "NONE",
                    "native_keyboard": "PASS" if mobile else "n/a"})
                ctx.close()
        browser.close()
    return observations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", default="experience2/home-flagship/index.html")
    parser.add_argument("--css", default="experience2/home-flagship/flagship.css")
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args()
    html, css = Path(args.html).read_text(), Path(args.css).read_text()
    header = source_check(html, css)
    result = {"source": "PASS", "browser": "NOT RUN",
              "scope": "actual candidate masthead only, not WordPress"}
    if args.browser:
        out = Path(args.out) if args.out else None
        if out:
            out.mkdir(parents=True, exist_ok=True)
        result["browser"] = browser_check(header, css, out)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
