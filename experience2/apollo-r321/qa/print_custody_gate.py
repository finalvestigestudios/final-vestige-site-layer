#!/usr/bin/env python3
"""R321 checked-in acceptance gate: offline Chromium print/zoom/source custody.

This is NOT real WordPress, native HTTP, genuine axe-core, or production CWV.
Requires PHP CLI, system Chromium, Python playwright + pypdf.
"""
import hashlib
import io
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PHP = ROOT / "apollo-r281/apollo-source-experience.php"
CSS = ROOT / "apollo-r281/assets/apollo-source-experience.css"
JS = ROOT / "apollo-r281/assets/apollo-cache-continuation.js"
STUB = ROOT / "apollo-r320/qa/wp_late_shortcodes.php"
EXPECTED = ["Custodian: NASA", "Record type:", "January 27", "January 28",
            "January 31", "February 3", "Source relationship:",
            "S67-21294", "KSC-20170124-PH_KLS01_0090",
            "https://www.nasa.gov/history/Apollo204/proceed.html"]

def blob(b):
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def html(n=1, css=None):
    raw = subprocess.check_output(
        ["php", str(STUB), "late-dynamic", str(n)], text=True
    ).split("<!--R320_QUEUE:")[0]
    if css is None:
        css = CSS.read_text()
    return raw.replace("</head>", "<style>" + css + "</style></head>")

def pdf_text(page):
    return "\n".join(p.extract_text() or "" for p in
                     PdfReader(io.BytesIO(page.pdf(format="A4", print_background=True))).pages)

def run():
    subprocess.run(["php", "-l", str(PHP)], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["node", "--check", str(JS)], check=True, stdout=subprocess.DEVNULL)
    assert blob(PHP.read_bytes()) == "6eae2c74eaf9d38745462b446185132023cc5d0e"
    assert blob(CSS.read_bytes()) == "b71505d6ee462148e19594cab46a47a0fae90eaf"
    assert blob(JS.read_bytes()) == "a3c858b51005495ebebb326086badc155c1b7e5a"
    assert ("r321-" + hashlib.sha256(CSS.read_bytes()).hexdigest()[:12]) in PHP.read_text()
    count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        try:
            for width in (320, 360, 390, 768, 1024, 1440, 1920):
                for mode in ("nojs", "text200", "text400", "forced"):
                    ctx = browser.new_context(
                        viewport={"width": width, "height": 900},
                        java_script_enabled=(mode != "nojs"),
                        forced_colors="active" if mode == "forced" else "none",
                        reduced_motion="reduce",
                        has_touch=width <= 390
                    )
                    page = ctx.new_page()
                    mark = "" if mode not in ("text200", "text400") else (
                        "<style>html{font-size:" + ("32" if mode == "text200" else "64") +
                        "px!important}</style>"
                    )
                    page.set_content(html(2).replace("</head>", mark + "</head>"))
                    assert page.locator("section.fv-r281").count() == 2
                    assert page.locator("[data-fv-media-record]").count() == 8
                    assert page.locator("a[data-fv-cta]").count() == 2
                    assert page.locator("img,canvas,iframe,video,[data-latitude],[data-longitude]").count() == 0
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                    ids = page.locator("[id]").evaluate_all("(els)=>els.map(el=>el.id)")
                    assert len(ids) == len(set(ids))
                    first = page.locator(".fv-r281__source-jump a").first
                    first.click()
                    target = page.locator(page.evaluate("location.hash"))
                    assert target.count() == 1 and target.is_visible()
                    assert target.evaluate("(e)=>e===document.activeElement")
                    count += 1
                    ctx.close()
            for width in (390, 1440):
                ctx = browser.new_context(viewport={"width": width, "height": 900},
                                          java_script_enabled=False)
                page = ctx.new_page()
                page.set_content(html())
                assert page.locator("section.fv-r281 details[open]").count() == 0
                page.emulate_media(media="print")
                text = pdf_text(page)
                assert all(required in text for required in EXPECTED)
                assert "Inspect the source and custody record" not in text
                ctx.close()
            original = CSS.read_text().split("\n/* R321 print:", 1)[0]
            assert hashlib.sha256(original.encode()).hexdigest() == (
                "0c31dbffe1a78500c10f08806d76eb5399be93207eef1fed4c1bb6de7d8d17e9"
            )
            ctx = browser.new_context(java_script_enabled=False)
            page = ctx.new_page()
            page.set_content(html(1, original))
            page.emulate_media(media="print")
            old_text = pdf_text(page)
            assert "Inspect the source and custody record" in old_text
            assert "Custodian: NASA" in old_text
            ctx.close()
        finally:
            browser.close()
    print(f"R321 PASS: {count} Chromium contexts; 2 real print PDFs; R320 negative control")

if __name__ == "__main__":
    run()
