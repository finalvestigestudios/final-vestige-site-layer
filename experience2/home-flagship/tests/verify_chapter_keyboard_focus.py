#!/usr/bin/env python3
"""EX2 candidate: keyboard fragment focus at every chapter; never WordPress certification.

Usage: python -I experience2/home-flagship/tests/verify_chapter_keyboard_focus.py
Optional: --smoke runs 7-target synthetic positive/negative fixtures without repo CSS.
Runs with browser JavaScript disabled and all external network requests rejected.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

TARGETS = (
    "fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence",
    "fv-hf-inquiry", "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title",
)
VIEWPORTS = ((390, 844), (720, 450), (1440, 900))
CSS_LINK = re.compile(r'<link\s+rel="stylesheet"\s+href="\./([a-z0-9._-]+\.css)"\s*/?>', re.I)


def exact_source(root):
    original = (root / "index.html").read_text(encoding="utf-8")
    nav = re.search(r'<nav class="fv-hf__chapter-nav"[^>]*>(.*?)</nav>', original, re.S)
    assert nav, "missing chapter navigation"
    found = re.findall(r'<a\s+href="#([^"]+)"', nav.group(1))
    assert tuple(found) == TARGETS, f"chapter order differs: {found!r}"
    assert '<a class="fv-hf__skip" href="#fv-hf-evidence">' in original, "skip link missing"
    for ident in TARGETS:
        tags = re.findall(r'<(?:h1|h2|section)\b[^>]*\bid="' + re.escape(ident) + r'"[^>]*>', original)
        assert len(tags) == 1, f"expected exactly one semantic destination for {ident}"
        assert re.search(r'\btabindex="-1"', tags[0]), f"fragment target not programmatically focusable: {ident}"
    styles = []
    names = []

    def inline(match):
        name = match.group(1)
        assert name not in names, "duplicate stylesheet"
        names.append(name)
        data = (root / name).read_text(encoding="utf-8")
        assert "</style" not in data.lower(), f"unsafe style terminator: {name}"
        styles.append(hashlib.sha256(data.encode()).hexdigest())
        return '<style data-source-css="' + name + '">\n' + data + '\n</style>'

    html = CSS_LINK.sub(inline, original)
    assert len(names) == 6, f"expected six source stylesheets, got {names}"
    return html, {"html_sha256": hashlib.sha256(original.encode()).hexdigest(),
                  "css_names": names, "css_sha256": styles}


def smoke_html(focusable):
    nav = "".join(f'<a href="#{ident}">Chapter {n + 1}</a>'
                  for n, ident in enumerate(TARGETS))
    content = ""
    for n, ident in enumerate(TARGETS):
        tag = "h1" if n == 0 else "h2" if n in (4, 6) else "section"
        focus = ' tabindex="-1"' if focusable else ""
        content += f'<{tag} id="{ident}"{focus} style="min-height:600px">'
        content += f'Chapter {n + 1} <a href="/proof-{n}">View source</a></{tag}>'
    css = '[tabindex="-1"]:focus-visible{outline:3px solid #f6cc86;outline-offset:-3px}'
    return ('<!doctype html><html lang="en"><head><style>' + css +
            '</style></head><body><nav class="fv-hf__chapter-nav">' + nav +
            '</nav><a class="fv-hf__skip" href="#fv-hf-evidence">Skip to evidence</a>' +
            '<main>' + content + '</main></body></html>')


def run(proposed_html, out, smoke=False):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        executable = os.getenv("FV_EX2_CHROMIUM") or shutil.which("chromium") or shutil.which("google-chrome")
        browser = p.chromium.launch(headless=True, executable_path=executable or None,
                                    args=["--no-sandbox"])
        try:
            cases = [("after" if smoke else "exact-source", proposed_html)]
            if smoke:
                cases.insert(0, ("before", smoke_html(False)))
            for label, html in cases:
                for width, height in VIEWPORTS:
                    page = browser.new_page(
                        viewport={"width": width, "height": height},
                        java_script_enabled=False, reduced_motion="reduce")
                    blocked = []
                    page.route("**/*", lambda route: (blocked.append(route.request.url), route.abort()))
                    try:
                        page.set_content(html, wait_until="domcontentloaded")
                        for ident in TARGETS:
                            anchor = page.locator('.fv-hf__chapter-nav a[href="#' + ident + '"]')
                            anchor.focus()
                            page.keyboard.press("Enter")
                            measured = page.evaluate("""() => {
                              const target = document.getElementById(location.hash.slice(1));
                              const active = document.activeElement;
                              const outline = getComputedStyle(active).outlineStyle;
                              return {hash: location.hash, focused: active?.id || "",
                                      outline: outline, targetExists: !!target};
                            }""")
                            passed = (measured["hash"] == "#" + ident and
                                      measured["focused"] == ident and
                                      measured["targetExists"] and
                                      measured["outline"] not in ("none", "hidden"))
                            rows.append({"case": label, "width": width, "height": height,
                                         "target": ident, "pass": bool(passed), "observed": measured})
                        if width == 390 and label != "before":
                            page.screenshot(path=str(out / "ex2-chapter-focus-390.png"),
                                            animations="disabled", full_page=False)
                    finally:
                        page.close()
        finally:
            browser.close()
    good = [r for r in rows if r["case"] != "before"]
    bad = [r for r in rows if r["case"] == "before"]
    passed = all(r["pass"] for r in good) and (not bad or not any(r["pass"] for r in bad))
    receipt = {"classification": "SYNTHETIC_BROWSER_NEGATIVE_CONTROL" if smoke
               else "SOURCE_EXACT_STANDALONE_BROWSER_NOT_WORDPRESS",
               "browser_js_enabled": False, "network_blocked": True,
               "width_height": VIEWPORTS, "total_expected": len(good),
               "positive_passed": sum(r["pass"] for r in good),
               "negative_rejected": sum(not r["pass"] for r in bad), "passed": passed,
               "checks": rows}
    (out / "chapter-focus-receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"{receipt['classification']}: {receipt['positive_passed']}/{len(good)} positive"
          + (f", {receipt['negative_rejected']}/{len(bad)} negative rejected" if smoke else ""))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, default=Path("/tmp/fv-ex2-chapter-focus"))
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.smoke:
        return run(smoke_html(True), args.out, smoke=True)
    html, manifest = exact_source(args.root)
    status = run(html, args.out)
    receipt_path = args.out / "chapter-focus-receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["source_manifest"] = manifest
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
