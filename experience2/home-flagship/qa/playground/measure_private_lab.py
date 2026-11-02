#!/usr/bin/env python3
"""Measured, private, CDP-throttled Chromium lab for the release-canonical 7-chapter WordPress renderer.

Only localhost WordPress Playground. This is NOT Lighthouse, WordPress.com host parity,
field p75 CWV, mobile INP, a WCAG certificate, or approval to deploy.
Never serialize renderer nonces, cookies, URLs, response bodies or private browser state.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
VERIFIER = HERE.parent / "release-candidate" / "verify_exact_staging.py"
PAGE = "http://127.0.0.1:9400/?pagename=fv-ex2-playground-review"
PROFILES = (("mobile_390_4x_cpu_slow4g", 390, 4, 2),
            ("desktop_1440_unthrottled", 1440, 1, 1))


def grade(sample: dict) -> list[str]:
    """Fail closed on absent metrics, wrong render, or measured lab budget overrun."""
    issues = []
    if sample.get("http_status") != 200 or sample.get("chapter_count") != 7:
        issues.append("NOT_CANONICAL_RENDER")
    for key, maximum in (("lcp_ms", 2500), ("cls", 0.1)):
        val = sample.get(key)
        if type(val) not in (int, float) or not math.isfinite(val) or val < 0:
            issues.append(key.upper() + "_NOT_MEASURED")
        elif val > maximum:
            issues.append(key.upper() + "_LAB_BUDGET_EXCEEDED")
    if sample.get("viewport") not in (390, 1440):
        issues.append("UNEXPECTED_VIEWPORT")
    return issues


def exact_checkout(repo: Path, expected: str) -> None:
    actual = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if len(expected) != 40 or actual != expected:
        raise ValueError("EXACT_SOURCE_HEAD_MISMATCH")
    for path in (Path(__file__), VERIFIER, HERE / "test_measure_private_lab.py"):
        relative = path.resolve().relative_to(repo)
        stored = subprocess.check_output(["git", "-C", str(repo), "show",
                                          expected + ":" + relative.as_posix()])
        if stored != path.read_bytes() or path.is_symlink():
            raise ValueError("STAGING_QA_CODE_NOT_EXACT_COMMIT")


def load_verifier():
    spec = importlib.util.spec_from_file_location("fv_exact_staging", VERIFIER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def measure(repo: Path, expected: str, storage_state: Path) -> dict:
    if not storage_state.is_file():
        raise ValueError("MISSING_PRIVATE_BROWSER_SESSION")
    exact_checkout(repo, expected)
    verifier = load_verifier()
    verifier.check_url(PAGE, "127.0.0.1")
    from playwright.sync_api import sync_playwright
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            # Discover the nonce only from the authorized WordPress shortcode.
            # NEVER log, return, store or attach that renderer URL.
            discover = browser.new_context(storage_state=str(storage_state), service_workers="block")
            page = discover.new_page()
            page.goto(PAGE, wait_until="domcontentloaded", timeout=30000)
            iframe = page.locator('iframe[title="Final Vestige Experience 2.0, unpublished editorial preview"]')
            iframe.wait_for(state="attached", timeout=16000)
            if set((iframe.get_attribute("sandbox") or "").split()) != {"allow-scripts", "allow-popups"}:
                raise ValueError("PREVIEW_SANDBOX_CONTRACT_CHANGED")
            private_url = verifier.check_private_render_url(iframe.get_attribute("src"), PAGE)
            discover.close()
            # Isolated clean Chromium contexts, fresh cache disabled; neither
            # the WordPress editor layout nor a static HTML file is measured.
            for label, width, cpu, repetitions in PROFILES:
                for trial in range(1, repetitions + 1):
                    ctx = browser.new_context(storage_state=str(storage_state),
                                              viewport={"width": width, "height": 844},
                                              reduced_motion="reduce", service_workers="block")
                    ctx.add_init_script(verifier.PERF_INIT)
                    pg = ctx.new_page()
                    cdp = ctx.new_cdp_session(pg)
                    cdp.send("Network.enable")
                    cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
                    cdp.send("Emulation.setCPUThrottlingRate", {"rate": cpu})
                    if cpu == 4:
                        cdp.send("Network.emulateNetworkConditions", {
                            "offline": False, "latency": 150,
                            "downloadThroughput": 200000, "uploadThroughput": 93750,
                            "connectionType": "cellular4g"})
                    try:
                        response = pg.goto(private_url, wait_until="load", timeout=45000)
                        pg.locator("[data-fv-home-flagship]").wait_for(state="attached", timeout=12000)
                        pg.wait_for_timeout(4000)
                        raw = pg.evaluate("""() => {
                          const nav = performance.getEntriesByType('navigation')[0];
                          const lab = window.__fvLab || {};
                          return {innerWidth, chapterCount: document.querySelectorAll(
                            '[data-fv-home-flagship] [id^="fv-hf-chapter-"]').length,
                            lcp:lab.lcp ? lab.lcp.startTime : null,
                            cls:lab.cls == null ? null : lab.cls,
                            responseStart:nav ? nav.responseStart : null,
                            dcl:nav ? nav.domContentLoadedEventEnd : null};
                        }""")
                        # CHAPTERS uses canonical explicit IDs: do not silently
                        # confuse an alternate chapter naming convention with 7.
                        chapter_count = sum(pg.locator("#" + ident).count() == 1
                                            for ident in verifier.CHAPTERS)
                        sample = {
                            "profile":label,"trial":trial,"viewport":raw["innerWidth"],
                            "http_status":response.status if response else 0,
                            "chapter_count":chapter_count,
                            "cpu_slowdown_x":cpu,"network":("150ms_RTT_1.6Mbps" if cpu==4 else "unthrottled"),
                            "lcp_ms":round(raw["lcp"],1) if isinstance(raw["lcp"],(int,float)) else None,
                            "cls":round(raw["cls"],5) if isinstance(raw["cls"],(int,float)) else None,
                            "navigation_response_ms":round(raw["responseStart"],1) if isinstance(raw["responseStart"],(int,float)) else None,
                            "dom_content_loaded_ms":round(raw["dcl"],1) if isinstance(raw["dcl"],(int,float)) else None,
                        }
                        sample["failure_codes"] = grade(sample)
                    except Exception as exc:
                        # Exception CLASS only: Playwright messages can contain
                        # the nonce-bearing AJAX URL. Never serialize raw exception messages.
                        sample = {"profile":label,"trial":trial,"viewport":width,
                                  "http_status":0,"chapter_count":0,
                                  "lcp_ms":None,"cls":None,
                                  "failure_codes":["BROWSER_"+type(exc).__name__.upper()]}
                    results.append(sample)
                    ctx.close()
        finally:
            browser.close()
    failures = sorted({code for sample in results for code in sample["failure_codes"]})
    return {
        "status":"LAB_RECORDED_RELEASE_HOLD" if not failures else "LAB_FAILED_RELEASE_HOLD",
        "source_head":expected,
        "environment":"LOCAL_WORDPRESS_PLAYGROUND_AUTHENTICATED_RENDERER",
        "throttling":"Chromium CDP, not Lighthouse simulated throttling",
        "release":"HOLD; no hosted WordPress.com parity, manual AT, or field CWV",
        "field_cwv":"NOT_MEASURED","lighthouse":"NOT_RUN","inp":"NOT_MEASURED",
        "real_user_p75":"NOT_MEASURED","production_writes":False,
        "results":results,"failure_codes":failures,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--expected-head",required=True)
    p.add_argument("--storage-state",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report = {"status":"LAB_BLOCKED_RELEASE_HOLD","failure_codes":["NOT_EXECUTED"],
              "field_cwv":"NOT_MEASURED","lighthouse":"NOT_RUN","production_writes":False}
    try:
        report = measure(args.repo.resolve(strict=True),args.expected_head,args.storage_state)
    except Exception as exc:
        report["failure_codes"]=["LAB_"+type(exc).__name__.upper()]
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"THROTTLED_CHROMIUM_LAB.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"failures":report["failure_codes"],
                      "release":"HOLD"}))
    return 0 if report["status"]=="LAB_RECORDED_RELEASE_HOLD" else 2


if __name__=="__main__":
    raise SystemExit(main())
