#!/usr/bin/env python3
"""Admission bridge for the PRIVATE source-pinned Playground launcher.

Tests actual browser boot and WordPress/Assembler markup. Never writes to
production. A pass from static fixtures/PHP stubs is NOT WordPress acceptance.
WordPress Playground requires JS to boot; no-JS content needs separate
local-WordPress testing. No-JS, Jetpack, Safari and CWV remain release gates.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit
from zipfile import ZipFile

from verify_integrated_playground import CHAPTERS, read_semantics, assert_semantics, verify_image_bytes
from verify_archival_provenance import classify_source, verify_receipt

BLOB = "137c74a476005684a28f5ff9a36e75c6b03268f7"
PARENT = "37bc943c08204867809a0b3c80540fa534fb005f"
ASSEMBLER = "75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f"
ORIGIN = "https://playground.wordpress.net"
PRODUCTION = {"finalvestige.com", "www.finalvestige.com", "vestigefinal-tezws.wpcomstaging.com"}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.scripts = 0
    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.scripts += 1
        if tag == "a":
            href = dict(attrs).get("href", "")
            if href.startswith(ORIGIN + "/#"):
                self.urls.append(href)

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def admit_bundle(path):
    """All claims pinned to the EXACT source and the absence of extra files."""
    with ZipFile(path) as z:
        if set(z.namelist()) != {"blueprint.json", "launch_review.html", "manifest.json"}:
            raise ValueError("Unexpected review archive entries")
        raw = z.read("blueprint.json")
        html = z.read("launch_review.html").decode("utf-8")
        manifest = json.loads(z.read("manifest.json"))
    if git_blob(raw) != BLOB or manifest.get("blob_sha1") != BLOB:
        raise ValueError("Stale or modified Blueprint: not latest pinned candidate")
    digest = hashlib.sha256(raw).hexdigest()
    if manifest.get("blueprint_sha256") != digest or manifest.get("assembler_commit") != ASSEMBLER:
        raise ValueError("Source hash or pinned Assembler mismatch")
    links = Links()
    links.feed(html)
    if links.scripts or len(links.urls) != 1:
        raise ValueError("Unexpected launcher script or number of links")
    parts = urlsplit(links.urls[0])
    if (parts.scheme, parts.netloc, parts.path) != ("https", "playground.wordpress.net", "/"):
        raise ValueError("Unexpected browser origin")
    if base64.b64decode(parts.fragment, validate=True) != raw:
        raise ValueError("Launcher URL fragment not identical to Blueprint bytes")
    bp = json.loads(raw)
    steps = bp.get("steps", [])
    if [x.get("step") for x in steps] != ["installTheme", "mkdir", "writeFile", "runPHP", "runPHP"]:
        raise ValueError("Unapproved WordPress operations in Blueprint")
    php = steps[2].get("data", "")
    if (any(php.count('id="' + x + '"') != 1 for x in CHAPTERS)
        or php.count('class="fv-margin-strip__item"') != 72
        or php.count('href="https://finalvestige.com/focus/"') != 5
        or "NOT LIVE" not in php
        or "fv_ex2_playground_review_only" not in php):
        raise ValueError("Evidence, Focus or review-only safety controls changed")
    return {"git_blob":BLOB, "sha256":digest, "parent":PARENT,
            "chapters":7, "margins":72, "focus_links":5,
            "fragment_length":len(parts.fragment)}, html

def real_wordpress_frame(tab):
    for frame in tab.frames:
        try:
            if frame.evaluate("() => !!document.querySelector('.wp-site-blocks [data-fv-home-flagship]')"):
                return frame
        except Exception:
            pass
    return None

def run(bundle, output, axe_js=None, timeout_ms=120000, chromium=None):
    from playwright.sync_api import sync_playwright
    report = {"scope":"genuine Playground browser launch only",
              "timestamp":datetime.now(timezone.utc).isoformat(),
              "status":"FAIL", "reason":"NOT_STARTED",
              "wordpress":"NOT_VERIFIED", "images":"NOT_VERIFIED", "axe":"NOT_RUN",
              "no_js":"NOT_VERIFIED_IN_JS_POWERED_PLAYGROUND",
              "jetpack":"NOT_TESTED", "lighthouse":"NOT_MEASURED",
              "safari":"NOT_TESTED", "field_cwv":"NOT_MEASURED",
              "sales":"NOT_VERIFIED", "release":"HOLD"}
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        report["source"], launch_html = admit_bundle(bundle)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=chromium or os.environ.get("FV_CHROMIUM", "/usr/bin/chromium"),
                                         headless=True, args=["--no-sandbox"])
            ctx = browser.new_context(viewport={"width":390,"height":667})
            responses = []
            ctx.on("response", lambda x: responses.append(x))
            def read_only(route):
                req = route.request
                host = (urlsplit(req.url).hostname or "").lower()
                if host in PRODUCTION and (req.method.upper() not in ("GET","HEAD") or req.is_navigation_request()):
                    report.setdefault("blocked_production_requests", []).append(req.method+" "+req.url.split("?")[0])
                    route.abort()
                else:
                    route.continue_()
            ctx.route("**/*", read_only)
            controller = ctx.new_page()
            # set_content avoids file:// and HTTP restrictions on isolated CI runners.
            controller.set_content(launch_html, wait_until="load")
            with controller.expect_popup(timeout=10000) as popup:
                controller.get_by_role("link", name="Open isolated Playground review", exact=False).click()
            tab = popup.value
            try:
                tab.wait_for_load_state("domcontentloaded", timeout=min(30000,timeout_ms))
            except Exception as e:
                report["navigation_warning"] = str(e)[:300]
            if not tab.url.startswith(ORIGIN + "/"):
                raise RuntimeError("Official Playground navigation did not load: " + tab.url[:160])
            deadline = time.monotonic() + timeout_ms/1000
            wp = None
            while time.monotonic() < deadline:
                wp = real_wordpress_frame(tab)
                if wp:
                    break
                tab.wait_for_timeout(700)
            if not wp:
                report["frames"] = [f.url[:150] for f in tab.frames]
                raise RuntimeError("Actual WordPress/Assembler document never rendered")
            semantics = read_semantics(wp)
            report["semantics"] = semantics
            failures = assert_semantics(semantics)
            if failures:
                raise RuntimeError("WordPress semantics: "+"; ".join(failures))
            report["wordpress"] = "PASS"
            tab.screenshot(path=str(output.parent/"playground_wordpress_390.png"), full_page=True)
            images = []
            for index, img in enumerate(wp.locator("[data-fv-archive-img]").all()):
                img.scroll_into_view_if_needed(timeout=5000)
                img.evaluate("e => e.loading='eager'")
                tab.wait_for_timeout(850)
                original = img.get_attribute("src") or ""
                src = img.evaluate("e => e.currentSrc || e.src")
                # The browser may select a Jetpack/Photon CDN derivative from srcset.
                # A decodable image is insufficient: bind source, currentSrc,
                # media ID, dimensions, HTTP status and response content-type.
                provenance = classify_source(original, src, index)
                response = next((r for r in responses if r.url == src), None)
                if not response:
                    raise RuntimeError("Missing actual image HTTP response: "+src)
                receipt = verify_image_bytes(response.body(), provenance["format"])
                images.append({"url":src, **verify_receipt(
                    provenance, receipt, response.status,
                    response.headers.get("content-type", ""))})
            report["image_receipts"] = images
            report["first_party_image_transfers"] = (
                "PASS" if len(images) == 2 and all(x["first_party"] for x in images)
                else "NOT_VERIFIED_CDN_SELECTED")
            report["image_provenance"] = "PASS_EXACT_MEDIA_IDS_AND_BYTES"
            report["images"] = "PASS_BYTES_AND_PROVENANCE"
            if not axe_js or not Path(axe_js).is_file():
                raise RuntimeError("Official axe-core library absent; cannot claim WCAG acceptance")
            wp.add_script_tag(path=str(axe_js))
            axe = wp.evaluate("""async()=>{const r=await axe.run(document,{
                runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}
              });return {violations:r.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.length})),
                        incomplete:r.incomplete.length,passes:r.passes.length}}""")
            report["axe"] = axe
            if axe["violations"] or axe["incomplete"]:
                raise RuntimeError("WCAG axe violations or incomplete checks")
            report["status"] = "PARTIAL"
            report["reason"] = ("WordPress/image bytes/axe verified in isolated Playground; "
                "first-party image transfer, no-JS, Safari, CWV, Jetpack and QD remain gated"
                if report["first_party_image_transfers"] != "PASS"
                else "WordPress/first-party image bytes/axe verified; no-JS, Safari, CWV, Jetpack and QD remain gated")
            browser.close()
    except Exception as exc:
        report["status"] = "FAIL"
        report["reason"] = str(exc)[:1000]
    finally:
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--axe-js", type=Path)
    p.add_argument("--chromium")
    p.add_argument("--timeout-ms", type=int, default=120000)
    a=p.parse_args()
    r=run(a.bundle,a.report,a.axe_js,a.timeout_ms,a.chromium)
    print(json.dumps({"status":r["status"],"reason":r["reason"],"report":str(a.report)}))
    sys.exit(0 if r["status"]=="PARTIAL" else 2)
