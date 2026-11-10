#!/usr/bin/env python3
"""R250: exact R238 Apollo Atlas source custody + actual offline Chromium QA.

Use --atlas on a locally unpacked, SHA-verified R238 artifact from the prior
Apollo staging review. No installed WordPress, live HTTP, axe, screen-reader,
merchant acceptance, NASA promotional-media rights, or field CWV claimed.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

MANIFEST_SHA256 = "f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68"
ORIGINAL = "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
NASA = ("Apollo 204 Review Board", "S66-58038", "S67-15717", "S67-21294")
WIDTHS = (320, 390, 768, 1440, 1920)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def custody(html):
    soup = BeautifulSoup(html, "html.parser")
    names = [x["data-fv-plate-source"] for x in soup.select("[data-fv-plate-source]")]
    assert len(names) == 4 and sorted(names) == sorted(NASA), "unreviewed source identity"
    assert len(soup.select("a.cta")) == 1, "unexpected purchase or duplicate CTA"
    assert soup.select_one("a.cta")["href"] == ORIGINAL, "free CTA destination changed"
    assert len(soup.select('a[href="' + ORIGINAL + '"]')) == 1
    nasa_urls = soup.select('.fv-apollo-print-custody a[href^="https://www.nasa.gov/"]')
    assert len(nasa_urls) >= 8, "missing archival URLs"
    assert not soup.select("script,svg,img,video,canvas,iframe,[data-latitude],[data-longitude]")
    assert not re.search("(?i)payhip|checkout|awin1|mini museum|<script", html)
    chronology = [x["datetime"] for x in soup.select("#fv-apollo-chronology ol time[datetime]")]
    assert len(chronology) >= 5 and chronology == sorted(chronology)
    ids = [x["id"] for x in soup.select("[id]")]
    assert len(ids) == len(set(ids)), "duplicate DOM IDs"
    for a in soup.select('a[href^="#"]'):
        assert soup.find(id=a["href"][1:]), "dead internal source link"
    assert "not conclusively identified" in soup.get_text(" ", strip=True).lower(), "ignition uncertainty removed"
    return {"plates": len(names), "print_nasa_urls": len(nasa_urls), "chronology": chronology}


def mutations(html):
    variants = {
        "source_identity": html.replace('data-fv-plate-source="Apollo 204 Review Board"', 'data-fv-plate-source="unreviewed"', 1),
        "fabricated_pin": html.replace("<article", '<article data-latitude="28.5"', 1),
        "unapproved_checkout": html.replace("</article>", '<a href="https://payhip.com/checkout">Buy</a></article>', 1),
        "duplicate_cta": html.replace("</article>", '<a class="cta" href="' + ORIGINAL + '">Read</a></article>', 1),
        "missing_print_custody": html.replace("fv-apollo-print-custody", "lost-custody", 1),
        "injected_script": html.replace("</article>", "<script>alert(1)</script></article>", 1),
        "invalid_chronology": html.replace('datetime="1967-01-27"', 'datetime="2099-01-27"', 1),
    }
    rejected = []
    for key, modified in variants.items():
        try:
            custody(modified)
        except AssertionError:
            rejected.append(key)
    assert len(rejected) == len(variants), "negative control unexpectedly accepted"
    return rejected


def load(root):
    assert digest((root / "manifest.json").read_bytes()) == MANIFEST_SHA256
    manifest = json.loads((root / "manifest.json").read_text())
    assert manifest["status"] == "STAGING_HOLD" and manifest["not_live"]
    for path, expected in manifest["files"].items():
        assert digest((root / path).read_bytes()) == expected, "protected file drift: " + path
    cmd = ["php", str(root / "wp-render-shim-r224.php"), str((root / "fv-ex2-apollo-r224.php").resolve())]
    modes = {}
    for mode in ("normal", "late", "printed"):
        modes[mode] = json.loads(subprocess.run(cmd + [mode], capture_output=True, text=True,
                                                check=True, timeout=20).stdout)
    assert modes["normal"]["html"] == (root / "templates/atlas-fragment.html").read_text()
    assert modes["normal"]["css"] == "enqueued" and not modes["normal"]["fallback"]
    assert modes["late"]["fallback"] and ORIGINAL in modes["late"]["html"]
    assert modes["printed"]["html"] == modes["normal"]["html"]
    return modes["normal"]["html"], (root / "assets/atlas-scoped.css").read_text()


def run(root, out):
    html, css = load(root)
    structure = custody(html)
    rejected = mutations(html)
    out.mkdir(parents=True, exist_ok=False)
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           '<style>' + css + '</style></head><body style="margin:0">' + html + '</body></html>')
    cases, timing = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE", "/usr/bin/chromium"),
                                     args=["--no-sandbox", "--disable-dev-shm-usage"])
        for width in WIDTHS:
            for js in (False, True):
                label = str(width) + ("-js" if js else "-nojs")
                context = browser.new_context(viewport={"width": width, "height": 900},
                                              java_script_enabled=js, is_mobile=width <= 390,
                                              has_touch=width <= 390, reduced_motion="reduce")
                page = context.new_page()
                requests = []
                page.on("request", lambda request: requests.append(request.url))
                page.set_content(doc, wait_until="load")
                assert not requests and not page.evaluate("document.documentElement.scrollWidth>innerWidth+1"), label
                if js:
                    page.evaluate("""() => {window.__apollo_perf={lcp:[],cls:[]};
                      new PerformanceObserver(l=>window.__apollo_perf.lcp.push(...l.getEntries().map(e=>e.startTime))).observe({type:'largest-contentful-paint',buffered:true});
                      new PerformanceObserver(l=>window.__apollo_perf.cls.push(...l.getEntries().filter(e=>!e.hadRecentInput).map(e=>e.value))).observe({type:'layout-shift',buffered:true});
                    }""")
                assert page.locator(".fv-apollo-atlas a.cta").count() == 1
                assert page.locator(".fv-apollo-atlas a.cta").get_attribute("href") == ORIGINAL
                assert page.locator(".fv-apollo-print-custody").is_hidden()
                if width == 1440:
                    page.keyboard.press("Tab")
                    assert page.locator(".fv-apollo-atlas .skip").evaluate("(e)=>document.activeElement===e")
                    page.keyboard.press("Enter")
                    assert page.evaluate("location.hash") == "#fv-apollo-main"
                summary = page.locator("details.fv-apollo-source-drawer>summary")
                if width <= 390:
                    summary.tap()
                else:
                    summary.focus()
                    page.keyboard.press("Enter")
                assert page.locator("details.fv-apollo-source-drawer").evaluate("(e)=>e.open")
                page.locator("details").evaluate_all("(xs)=>xs.forEach(e=>e.open=true)")
                ax_nodes = context.new_cdp_session(page).send("Accessibility.getFullAXTree")["nodes"]
                link_names = [x.get("name", {}).get("value", "") for x in ax_nodes
                              if not x.get("ignored") and x.get("role", {}).get("value") == "link"]
                assert link_names and all(x.strip() for x in link_names), label + " unnamed link"
                for source in NASA:
                    assert any(source in link for link in link_names), label + " inaccessible NASA action: " + source
                page.emulate_media(media="print")
                assert page.locator(".fv-apollo-print-custody").is_visible()
                urls = page.locator(".fv-apollo-print-custody a").all_text_contents()
                assert len(urls) >= 8 and all(u.startswith("https://www.nasa.gov/") for u in urls)
                page.emulate_media(media="screen")
                page.locator("details").evaluate_all("(xs)=>xs.forEach(e=>e.open=false)")
                page.mouse.move(0, 0)
                page.evaluate("document.activeElement?.blur()")
                page.evaluate("document.body.style.zoom='200%'")
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth+1"), label + " CSS zoom"
                page.evaluate("document.body.style.zoom='100%'")
                page.wait_for_timeout(120)
                image = out / (label + ".png")
                page.screenshot(path=str(image), full_page=True, animations="disabled")
                cases.append({"case": label, "ax_links": len(link_names), "print_urls": len(urls),
                              "css_zoom_200": "PASS (approximation)", "image_sha256": digest(image.read_bytes())})
                if js:
                    page.wait_for_timeout(350)
                    timing.append({"case": label, "offline_observers": page.evaluate("window.__apollo_perf"),
                                   "meaning": "local synthetic navigation, NOT production CWV"})
                context.close()
        version = browser.version
        browser.close()
    receipt = {"test": "R250 EXACT Apollo R238 source + original PHP shim",
               "browser": version, "manifest_sha256": MANIFEST_SHA256, "structure": structure,
               "negative_controls_rejected": rejected, "cases": cases,
               "status": "STAGING_HOLD", "axe_core": "NOT_RUN", "installed_wordpress": "NOT_TESTED",
               "http_csp": "NOT_TESTED", "real_browser_zoom": "NOT_TESTED",
               "media_rights": "NOT_CLEARED", "paid_revenue": "NOT_COMPUTABLE"}
    (out / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    (out / "local-performance-not-field-cwv.json").write_text(json.dumps(timing, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "contexts": len(cases), "mutations": len(rejected),
                      "browser": version, "receipt_sha256": digest((out / "receipt.json").read_bytes())}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--atlas", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    run(args.atlas, args.out)
