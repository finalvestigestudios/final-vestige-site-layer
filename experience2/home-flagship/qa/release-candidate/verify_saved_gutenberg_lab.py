#!/usr/bin/env python3
"""Real CDP lab metrics from the SAVED native Gutenberg front end.

This is deliberately distinct from Lighthouse on the private iframe and from
public WordPress.com or real-user Core Web Vitals. Localhost only; never export
a preview URL, storage state, WordPress admin cookie, HTML or browser trace.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from verify_saved_frontend_admission import CHAPTERS, validate_saved_preview

PERF_INIT = r"""(() => {
  window.__fvSavedNativeLab = { lcp: null, cls: 0 };
  try {
    new PerformanceObserver(list => {
      for (const e of list.getEntries()) {
        const el = e.element || null;
        // Strictly redacted element metadata; never export text, URLs or DOM.
        const id = el && typeof el.id === 'string' && /^fv-hf-[a-z0-9-]{1,70}$/.test(el.id)
          ? el.id : null;
        window.__fvSavedNativeLab.lcp = {
          time: e.startTime,
          tag: el && typeof el.tagName === 'string'
            ? el.tagName.toLowerCase().slice(0, 24) : null,
          id: id,
          size: typeof e.size === 'number' ? e.size : null,
          resourceBacked: Boolean(e.url)
        };
      }
    }).observe({type: 'largest-contentful-paint', buffered: true});
    new PerformanceObserver(list => {
      for (const e of list.getEntries())
        if (!e.hadRecentInput) window.__fvSavedNativeLab.cls += e.value;
    }).observe({type: 'layout-shift', buffered: true});
  } catch (_) { window.__fvSavedNativeLab.instrumentationFailed = true; }
})();"""

# Two real cold-cache, CDP-throttled mobile runs and a desktop comparison.
PROFILES = (
    ("mobile_390_trial_1", 390, 4, True),
    ("mobile_390_trial_2", 390, 4, True),
    ("desktop_1440", 1440, 1, False),
)


def sample_issues(data: dict, width: int) -> list[str]:
    """Reject missing/fabricated measurements; flag slow samples separately."""
    issues = []
    if data.get("http_status") != 200 or data.get("chapters") != 7:
        issues.append("NOT_SAVED_SEVEN_CHAPTER_FRONTEND")
    if data.get("viewport") != width:
        issues.append("INCORRECT_VIEWPORT")
    if data.get("instrumentation_failed") is not False:
        issues.append("PERFORMANCE_OBSERVER_NOT_ACTIVE")
    for field in ("lcp_ms", "cls"):
        value = data.get(field)
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            issues.append(field.upper() + "_NOT_MEASURED")
    if isinstance(data.get("lcp_ms"), (int, float)) and data["lcp_ms"] == 0:
        issues.append("LCP_ZERO_NOT_MEANINGFUL")
    return issues


def run_saved_native_lab(page, page_id: int, out: Path, exact_sha: str) -> dict:
    """Reload the real saved page; measure LCP/CLS under exact CDP conditions."""
    if not isinstance(exact_sha, str) or len(exact_sha) != 40 or any(
            c not in "0123456789abcdef" for c in exact_sha):
        raise ValueError("EXACT_SOURCE_SHA_REQUIRED")
    preview_url = page.url
    validate_saved_preview(preview_url, page_id)
    if page.locator("[data-fv-home-flagship]").count() != 1:
        raise ValueError("SAVED_GUTENBERG_ROOT_REQUIRED")
    page.add_init_script(script=PERF_INIT)
    session = page.context.new_cdp_session(page)
    samples = []
    original_viewport = page.viewport_size
    try:
        session.send("Network.enable")
        session.send("Network.setCacheDisabled", {"cacheDisabled": True})
        for label, width, cpu, throttled in PROFILES:
            page.set_viewport_size({"width": width, "height": 900})
            session.send("Emulation.setCPUThrottlingRate", {"rate": cpu})
            session.send("Network.emulateNetworkConditions", {
                "offline": False,
                "latency": 150 if throttled else 0,
                "downloadThroughput": 200000 if throttled else -1,
                "uploadThroughput": 93750 if throttled else -1,
                "connectionType": "cellular4g" if throttled else "wifi",
            })
            response = page.reload(wait_until="load", timeout=60000)
            validate_saved_preview(page.url, page_id)
            page.locator("[data-fv-home-flagship]").wait_for(state="visible",
                                                              timeout=20000)
            page.wait_for_timeout(2000)
            raw = page.evaluate("""() => {
              const p = window.__fvSavedNativeLab;
              const nav = performance.getEntriesByType('navigation')[0];
              const fcp = performance.getEntriesByName('first-contentful-paint')[0];
              return {
                viewport: innerWidth,
                lcp: p && p.lcp && p.lcp.time, cls: p && p.cls,
                lcpTag: p && p.lcp && p.lcp.tag,
                lcpId: p && p.lcp && p.lcp.id,
                lcpSize: p && p.lcp && p.lcp.size,
                lcpResourceBacked: p && p.lcp && p.lcp.resourceBacked,
                instrumentationFailed: !p || !!p.instrumentationFailed,
                responseMs: nav && nav.responseStart,
                responseEndMs: nav && nav.responseEnd,
                domContentLoadedMs: nav && nav.domContentLoadedEventEnd,
                loadEndMs: nav && nav.loadEventEnd,
                fcpMs: fcp && fcp.startTime
              };
            }""")
            sample = {
                "profile": label, "viewport": raw["viewport"],
                "http_status": response.status if response else 0,
                "chapters": sum(page.locator("#" + chapter).count() == 1
                                for chapter in CHAPTERS),
                "cpu_slowdown_x": cpu,
                "network": "150ms_RTT_1.6Mbps" if throttled else "unthrottled",
                "cache": "disabled",
                "lcp_ms": round(raw["lcp"], 1) if type(raw["lcp"]) in (int, float) else None,
                "cls": round(raw["cls"], 5) if type(raw["cls"]) in (int, float) else None,
                "response_start_ms": (round(raw["responseMs"], 1)
                                      if type(raw["responseMs"]) in (int, float) else None),
                "instrumentation_failed": bool(raw["instrumentationFailed"]),
                "lcp_element": {
                    "tag": raw["lcpTag"],
                    "id": raw["lcpId"],
                    "size": raw["lcpSize"],
                    "resource_backed": bool(raw["lcpResourceBacked"]),
                },
                "page_timing_ms": {
                    "fcp": round(raw["fcpMs"], 1)
                           if type(raw["fcpMs"]) in (int, float) else None,
                    "response_end": round(raw["responseEndMs"], 1)
                                    if type(raw["responseEndMs"]) in (int, float) else None,
                    "dom_content_loaded": round(raw["domContentLoadedMs"], 1)
                                          if type(raw["domContentLoadedMs"]) in (int, float) else None,
                    "load_end": round(raw["loadEndMs"], 1)
                                if type(raw["loadEndMs"]) in (int, float) else None,
                },
            }
            sample["failure_codes"] = sample_issues(sample, width)
            sample["lab_good_lcp"] = (sample["lcp_ms"] is not None
                                      and sample["lcp_ms"] <= 2500)
            sample["lab_good_cls"] = (sample["cls"] is not None
                                      and sample["cls"] <= 0.1)
            samples.append(sample)
    finally:
        try:
            session.send("Emulation.setCPUThrottlingRate", {"rate": 1})
            session.send("Network.emulateNetworkConditions", {
                "offline": False, "latency": 0,
                "downloadThroughput": -1, "uploadThroughput": -1,
            })
            session.send("Network.setCacheDisabled", {"cacheDisabled": False})
            session.detach()
        finally:
            if original_viewport:
                page.set_viewport_size(original_viewport)
    failures = sorted({issue for sample in samples
                       for issue in sample["failure_codes"]})
    budget_misses = [
        sample["profile"] + ":" + metric.upper()
        for sample in samples
        for metric in ("lcp", "cls")
        if not sample["lab_good_" + metric]
    ]
    report = {
        "status": ("SAVED_NATIVE_CDP_INVALID_RELEASE_HOLD" if failures else
                   "SAVED_NATIVE_CDP_BUDGET_MISS_RELEASE_HOLD" if budget_misses else
                   "SAVED_NATIVE_CDP_MEASURED_RELEASE_HOLD"),
        "native_lab_budget_gate": ("FAIL" if budget_misses else "PASS_LAB_ONLY"),
        "release_gate": "HOLD",
        "lab_budget_misses": budget_misses,
        "source_sha": exact_sha,
        "environment": "LOCAL_WORDPRESS_SAVED_GUTENBERG_AUTHENTICATED",
        "fixture": "SYNTHETIC_PROTECTED_BLOCK_PLACEHOLDERS",
        "test": "Real Chromium CDP, not Lighthouse or browser UI zoom",
        "hosted_wordpress_com": "NOT_TESTED",
        "field_cwv_p75": "NOT_MEASURED",
        "production_writes": False,
        "samples": samples,
        "failure_codes": failures,
        "any_lab_budget_missed": bool(budget_misses),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "GUTENBERG_SAVED_NATIVE_CDP_LAB.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        raise ValueError("SAVED_NATIVE_CDP_INSTRUMENTATION_HOLD:" + ",".join(failures))
    return report
