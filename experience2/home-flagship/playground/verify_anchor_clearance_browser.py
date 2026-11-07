#!/usr/bin/env python3
"""Native fragment-link clearance in the exact EX2 Playground Blueprint.
Offline Chromium source test only: NOT WordPress/Assembler, axe, Lighthouse or Jetpack.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

CHAPTERS = ("fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence",
            "fv-hf-inquiry", "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title")
WIDTHS = ((320, 568), (360, 640), (390, 667), (600, 800),
          (768, 900), (1440, 900), (1920, 1080))
FIX_MARKER = "/* FV EX2: accessible native chapter-anchor landing clearance (PR review only) */"

def source(path):
    data = path.read_bytes()
    bp = json.loads(data)
    assert bp["steps"][0]["themeData"]["ref"] == "75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f"
    php = bp["steps"][2]["data"]
    def part(name):
        start = "<<<'FVPG_" + name + "_END'\n"
        end = "\nFVPG_" + name + "_END"
        assert php.count(start) == 1 and php.count(end) == 1
        return php.split(start, 1)[1].split(end, 1)[0]
    css, js, html = (part(x) for x in ("CSS", "JS", "HTML"))
    assert html.count('class="fv-margin-strip__item"') == 72
    assert html.count("https://finalvestige.com/focus/") == 5
    assert html.count("data-fv-archive-img") == 2
    assert all('href="#' + x + '"' in html for x in CHAPTERS)
    return data, css, js, html

def test(blueprint, dest):
    data, css, js, html = source(blueprint)
    assert css.count(FIX_MARKER) == 1
    baseline_css = css.split(FIX_MARKER)[0]
    dest.mkdir(parents=True, exist_ok=True)
    receipts = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path="/usr/bin/chromium",
                                     args=["--no-sandbox"])
        for kind, style in (("before", baseline_css), ("after", css)):
            rows = []
            for width, height in WIDTHS:
                for with_js in (False, True):
                    page = browser.new_page(viewport={"width": width, "height": height},
                                            java_script_enabled=with_js,
                                            reduced_motion="reduce" if with_js else "no-preference")
                    page.route("**/*", lambda route: route.abort())
                    page.set_content('<!doctype html><html lang="en"><head><style>' +
                                     style + '</style></head><body>' + html + '</body></html>')
                    if with_js:
                        page.add_script_tag(content=js)
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                    for chapter in CHAPTERS[1:]:
                        page.evaluate('id => document.querySelector(\`.fv-hf__chapter-nav a[href="#\${id}"]\`).click()', chapter)
                        page.wait_for_timeout(30)
                        dims = page.evaluate('''id => {
                          const r=document.getElementById(id).getBoundingClientRect(),
                                n=document.querySelector(".fv-hf__chapter-nav").getBoundingClientRect();
                          return {y:r.top, navBottom:n.bottom, hash:location.hash,
                                  clearance:r.top-n.bottom};
                        }''', chapter)
                        rows.append(dict(width=width, js=with_js, chapter=chapter,
                                         clearance=round(dims["clearance"], 2),
                                         pass_clearance=(dims["clearance"] >= 12 and
                                                         dims["hash"] == "#" + chapter)))
                    if width == 390 and not with_js:
                        page.evaluate('document.querySelector(".fv-hf__chapter-nav a[href=\'#fv-hf-evidence\']").click()')
                        page.wait_for_timeout(50)
                        page.screenshot(path=str(dest / (kind + "_390x667_evidence.png")))
                    page.close()
            receipts[kind] = {"scenarios": len(rows),
                              "passed": sum(r["pass_clearance"] for r in rows),
                              "failed": sum(not r["pass_clearance"] for r in rows),
                              "min_clearance": min(r["clearance"] for r in rows),
                              "results": rows}
        browser.close()
    result = {"source_git_blob_input_sha256": hashlib.sha256(data).hexdigest(),
              "limits": "Exact HTML/CSS/JS static Chromium only; media intentionally blocked; no WP shell.",
              **receipts}
    (dest / "anchor_clearance_receipt.json").write_text(json.dumps(result, indent=2))
    assert receipts["before"]["failed"] > 0, "negative control failed to reproduce overlap"
    assert receipts["after"]["failed"] == 0, "native chapter target occluded"
    print(json.dumps({key: {k: v for k, v in val.items() if k != "results"} for key, val in receipts.items()}, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--blueprint", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    test(args.blueprint, args.output)
