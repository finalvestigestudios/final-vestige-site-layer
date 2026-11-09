#!/usr/bin/env python3
"""R238: pinned Atlas staging builder + keyboard-focus/browser regression acceptance.

Uses the exact R236 generated-source set. Works without HTTP navigation, which is
blocked in the hosted test environment. Offline browser passes are NOT WP or axe signoff.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

PARENT_MANIFEST = "f9169870eb3c02415feaf70eed9bbefdca5b194c6ddb27a92a0b80102ef1ce95"
PARENT_TEMPLATE = "50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6"
FREE_ARTICLE = "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
WIDTHS = (320, 390, 768, 1440, 1920)
SOURCES = ("Apollo 204 Review Board", "S66-58038", "S67-15717", "S67-21294")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def verify(directory, expected_manifest):
    assert sha(directory / "manifest.json") == expected_manifest, "manifest provenance drift"
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        assert sha(directory / name) == digest, "protected artifact drift: " + name
    assert sha(directory / "templates/atlas-fragment.html") == PARENT_TEMPLATE
    return manifest


def build(parent, patch, out):
    manifest = verify(parent, PARENT_MANIFEST)
    assert not out.exists(), "refuse to overwrite staging output"
    assert patch.read_text().startswith("/* R238"), "unexpected CSS patch"
    shutil.copytree(parent, out)
    css_path = out / "assets/atlas-scoped.css"
    previous_css = manifest["files"]["assets/atlas-scoped.css"]
    css_path.write_bytes(css_path.read_bytes() + b"\n" + patch.read_bytes())
    new_css = sha(css_path)
    php = out / "fv-ex2-apollo-r224.php"
    src = php.read_text(encoding="utf-8")
    assert src.count(previous_css) == 1, "PHP full CSS integrity pin changed"
    assert src.count("'" + previous_css[:12] + "'") == 1, "PHP CSS cache pin changed"
    src = src.replace(previous_css, new_css).replace(previous_css[:12], new_css[:12])
    php.write_text(src, encoding="utf-8")
    manifest["files"]["assets/atlas-scoped.css"] = new_css
    manifest["files"]["fv-ex2-apollo-r224.php"] = sha(php)
    manifest["r238_parent_manifest_sha256"] = PARENT_MANIFEST
    manifest["r238_change"] = "Keyboard-first 44px skip-link and focus-visibility hardening"
    manifest["release"] = "R238_STAGING_HOLD"
    manifest["status"] = "STAGING_HOLD"
    manifest["axe_core"] = "NOT_EXECUTED"
    emit(out / "manifest.json", manifest)
    verify(out, sha(out / "manifest.json"))
    return {"manifest": sha(out / "manifest.json"), "css": new_css, "php": sha(php)}


def static_custody(root):
    manifest = json.loads((root / "manifest.json").read_text())
    for rel, hash_value in manifest["files"].items():
        assert sha(root / rel) == hash_value, rel
    html = (root / "templates/atlas-fragment.html").read_text()
    css = (root / "assets/atlas-scoped.css").read_text()
    assert sha(root / "templates/atlas-fragment.html") == PARENT_TEMPLATE, "NASA template changed"
    assert html.count('href="' + FREE_ARTICLE + '"') == 1, "free article CTA drift"
    assert len(re.findall(r'<a\b[^>]*class="cta"', html)) == 1, "CTA count drift"
    assert 'class="skip" href="#fv-apollo-main"' in html
    assert 'id="fv-apollo-main"' in html and 'tabindex="-1"' in html
    assert set(SOURCES) <= set(re.findall(r'data-fv-plate-source="([^"]+)"', html))
    assert 'rel="sponsored"' not in html and not re.search(r'payhip|awin1|confirmed.?orders|data-latitude|data-longitude', html, re.I)
    assert not re.search(r'<script\b|<iframe\b|\bon(click|load|error)=', html, re.I)
    assert css.count("/* R238") == 1 and "min-block-size: 44px" in css
    return html, css


def focus_state(page):
    return page.evaluate("""() => {
      const e=document.activeElement, c=getComputedStyle(e), r=e.getBoundingClientRect();
      return {tag:e.tagName, id:e.id, href:e.getAttribute('href'),
        text:(e.textContent||'').trim().slice(0,90),
        focus_visible:e.matches(':focus-visible'),
        outline:c.outlineStyle, outline_width:parseFloat(c.outlineWidth),
        width:Math.round(r.width*100)/100, height:Math.round(r.height*100)/100,
        hidden:c.visibility==='hidden'||c.display==='none',
        viewport_overflow:document.documentElement.scrollWidth-innerWidth};
    }""")


def assert_visible_focus(state):
    assert not state["hidden"] and state["focus_visible"], state
    assert state["outline"] not in ("none", "hidden") and state["outline_width"] >= 2.9, state
    assert state["viewport_overflow"] <= 1, state


def run_browser(root, qa_dir):
    html, css = static_custody(root)
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width, initial-scale=1">'
           '<style>' + css + '</style></head><body>' + html + '</body></html>')
    assert not qa_dir.exists(), "refuse to overwrite browser evidence"
    qa_dir.mkdir(parents=True)
    output = []
    performance_samples = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox"])
        for width in (*WIDTHS, 256):
            for js in ((False,) if width == 256 else (False, True)):
                context = browser.new_context(
                    viewport={"width": width, "height": 900}, java_script_enabled=js,
                    is_mobile=width <= 390, has_touch=width <= 390,
                    reduced_motion="reduce", forced_colors="active" if width == 768 else "none")
                page = context.new_page()
                requests = []
                page.on("request", lambda request: requests.append(request.url))
                page.set_content(doc, wait_until="load")
                assert not requests, (width, js, requests)
                assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
                assert page.locator("a.cta").count() == 1
                assert page.locator("a.cta").get_attribute("href") == FREE_ARTICLE
                assert page.locator("details.fv-apollo-source-drawer").count() == 1

                # Walk the mast navigation with real Tab events from a fresh document.
                seq = []
                for i in range(6):
                    page.keyboard.press("Tab")
                    s = focus_state(page)
                    seq.append(s["href"])
                    assert_visible_focus(s)
                assert seq == ["#fv-apollo-main", "#fv-apollo-evidence", "#fv-apollo-chronology",
                               "#fv-apollo-gallery", "#fv-apollo-source-test", "#fv-apollo-reading-bridge"], seq

                # Fresh browser document for skip link: set_content on an already
                # focused page preserves sequential focus state and is NOT a reset.
                page.close()
                page = context.new_page()
                page.on("request", lambda request: requests.append(request.url))
                page.set_content(doc, wait_until="load")
                page.keyboard.press("Tab")
                first = focus_state(page)
                assert first["href"] == "#fv-apollo-main" and first["tag"] == "A", first
                assert first["width"] >= 44 and first["height"] >= 44, first
                assert_visible_focus(first)
                page.keyboard.press("Enter")
                target = focus_state(page)
                assert target["id"] == "fv-apollo-main" and page.evaluate("location.hash") == "#fv-apollo-main", target
                page.keyboard.press("Tab")
                next_one = focus_state(page)
                assert next_one["tag"] == "A" and next_one["href"].startswith("https://www.nasa.gov/"), next_one
                assert_visible_focus(next_one)

                drawer = page.locator("details.fv-apollo-source-drawer")
                drawer.locator("summary").focus()
                assert not drawer.evaluate("el=>el.open")
                page.keyboard.press("Enter")
                assert drawer.evaluate("el=>el.open"), "keyboard cannot open NASA source drawer"
                assert_visible_focus(focus_state(page))
                for source in SOURCES:
                    assert drawer.locator('[data-fv-plate-source="' + source + '"]').count() == 1
                page.keyboard.press("Enter")
                assert not drawer.evaluate("el=>el.open"), "keyboard cannot close source drawer"
                if width <= 390:
                    drawer.locator("summary").tap()
                    assert drawer.evaluate("el=>el.open"), "mobile tap cannot open NASA source drawer"

                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
                assert page.evaluate("document.querySelectorAll('script,iframe,form').length") == 0
                if js:
                    # A fresh, non-interacted document: after keyboard/touch input,
                    # Chromium suppresses LCP reporting. Do not fabricate the value.
                    perf_page = context.new_page()
                    perf_page.set_content(doc, wait_until="load")
                    perf = perf_page.evaluate("""async () => {
                      let l=[],s=[];
                      new PerformanceObserver(x=>x.getEntries().forEach(e=>l.push(e.startTime))).observe({type:'largest-contentful-paint',buffered:true});
                      new PerformanceObserver(x=>x.getEntries().forEach(e=>{if(!e.hadRecentInput)s.push(e.value)})).observe({type:'layout-shift',buffered:true});
                      await new Promise(r=>setTimeout(r,420));
                      return {lcp_ms:l.length?Math.round(Math.max(...l)):null,cls_observed:s.reduce((a,b)=>a+b,0)};
                    }""")
                    assert perf["lcp_ms"] is not None and perf["cls_observed"] <= .1, perf
                    performance_samples[str(width)] = perf
                    perf_page.close()
                page.set_content(doc, wait_until="load")
                page.mouse.move(0, 0)
                page.wait_for_timeout(100)
                path = qa_dir / f"{width}-{'js' if js else 'nojs'}.png"
                page.screenshot(path=str(path), animations="disabled", full_page=True)
                output.append({"width": width, "js": js, "forced_colors": width == 768,
                               "skip": first, "main_after_enter": target["id"],
                               "next_after_main": next_one["href"],
                               "mast_keyboard_sequence": seq, "drawer_keyboard_enter": True,
                               "touch": width <= 390, "offline_fixture_lcp_cls": "SEE_SEPARATE_NONDETERMINISTIC_FILE" if js else None,
                               "screenshot_sha256": sha(path)})
                context.close()
        v = browser.version
        browser.close()
    receipt = {"run": "R238", "browser": v, "contexts": len(output), "results": output,
      "source_manifest_sha256": sha(root / "manifest.json"),
      "source_template_sha256": PARENT_TEMPLATE,
      "quality": "LOCAL_CHROMIUM_PASS_NOT_RELEASE",
      "true_axe_core": "NOT_EXECUTED", "installed_wordpress": "NOT_TESTED",
      "actual_browser_ui_zoom": "NOT_TESTED", "real_http_navigation": "ERR_BLOCKED_BY_ADMINISTRATOR",
      "field_lcp_cls": "NOT_TESTED", "commercial_sales": "NOT_VERIFIED",
      "release": "STAGING_HOLD"}
    emit(qa_dir / "receipt.json", receipt)
    emit(qa_dir / "fixture_performance_not_field.json", {
        "scope": "offline set_content Chromium fixture, not production CWV",
        "samples": performance_samples, "field_metrics": "NOT_MEASURED"})
    return {"receipt_sha256": sha(qa_dir / "receipt.json"), "contexts": len(output),
            "screenshots": {p.name: sha(p) for p in sorted(qa_dir.glob("*.png"))}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--parent", required=True, type=Path)
    p.add_argument("--patch", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--qa", required=True, type=Path)
    args = p.parse_args()
    built = build(args.parent, args.patch, args.output)
    browser = run_browser(args.output, args.qa)
    print(json.dumps({"build": built, "browser": browser, "release": "STAGING_HOLD"}, sort_keys=True))


if __name__ == "__main__":
    main()
