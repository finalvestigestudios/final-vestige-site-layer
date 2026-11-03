#!/usr/bin/env python3
"""Read-only A/B admission of a proposed Margins CSS override on the PUBLIC homepage.

Browser-local style injection is ephemeral, never a WordPress edit or deploy.
No credentials, forms, subscriber data, document HTML, axe nodes, or screenshots
are saved. This audit does NOT establish WCAG 2.2 AA, hosted release permission,
archive-image rights, production performance, or QD approval.
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
from queue import Empty
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

URL = "https://finalvestige.com/"
WIDTHS = (320, 390, 768, 1440, 1920)
PHASES = (0.5, 2.5, 4.5, 5.5, 17.5, 355.5, 359.5, 360.5)
REDUCED_JS = (False, True)
NYPL = ("edit-017-v02-nypl-5003296", "nypl-5003296-original")
HERE = Path(__file__).resolve().parent
CSS = HERE / "margin_strip_contrast_safe.css"


def denied(method: str, url: str) -> bool:
    if method != "GET":
        return True
    if not url.startswith("https://") and not url.startswith("http://"):
        return True
    return any(part in urlsplit(url).path.lower() for part in NYPL)


def valid_candidate(css: str) -> bool:
    """Never inject imports, network resources or arbitrary HTML into the host."""
    low = css.lower()
    return (
        len(css) < 5000
        and all(marker in css for marker in (
            ".fv-margin-strip--rotator .fv-margin-strip__item",
            "animation-name: fvMarginContrastSafe;",
            "visibility: hidden;",
            "opacity: 1;",
            "filter: none;",
            "prefers-reduced-motion: reduce",
        ))
        and not any(bad in low for bad in (
            "@import", "url(", "javascript:", "<", "expression(",
            "content:", "@font-face", "!important"))
    )


def contrast_rgb(fg: list[float], bg: list[float], alpha: float) -> float:
    if (len(fg) != 3 or len(bg) != 3
            or not all(math.isfinite(x) and 0 <= x <= 255 for x in fg + bg)
            or not math.isfinite(alpha) or not 0 <= alpha <= 1):
        raise ValueError("INVALID_COLOR")
    mixed = [a * alpha + (1 - alpha) * b for a, b in zip(fg, bg)]
    def lum(values):
        def channel(n):
            v = n / 255
            return v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
        return sum(a * channel(x) for a, x in zip((.2126, .7152, .0722), values))
    a, b = sorted((lum(mixed), lum(bg)), reverse=True)
    return (a + .05) / (b + .05)


def rgb(s: str) -> list[float]:
    vals = re.findall(r"(?<![a-z])\d+(?:\.\d+)?", s)
    if len(vals) < 3:
        raise ValueError("INVALID_CSS_COLOR")
    return [float(v) for v in vals[:3]]


def evaluate_case(record: dict) -> bool:
    """Fail closed: every phase must show one readable record, with no overflow."""
    if record.get("status") != 200 or record.get("count") != 72:
        return False
    if record.get("flagship") is not True:
        return False
    if record.get("overflow") is True or record.get("blocked_non_get", -1) < 0:
        return False
    if record.get("css_active") is not True or len(record.get("samples", [])) != len(PHASES):
        return False
    for s, phase in zip(record["samples"], PHASES):
        if s.get("phase") != phase or s.get("shown") != [int(phase // 5) % 72]:
            return False
        if not s.get("sharp") or s.get("contrast", 0) < 4.5:
            return False
    if record.get("axe") is not None:
        a = record["axe"]
        if a.get("violation_rules") != 0 or a.get("incomplete_rules", -1) < 0:
            return False
    return True


def sample_style(page, phase: float) -> dict:
    """Return only primitive computed styles; never return actual historical text."""
    page.evaluate("""phase => {
      document.querySelectorAll('.fv-margin-strip__item').forEach((e,i) => {
        e.style.animationDelay = (i * 5 - phase) + 's';
      });
    }""", phase)
    page.wait_for_timeout(95)
    raw = page.evaluate("""() => {
       const items = Array.from(document.querySelectorAll('.fv-margin-strip__item'));
       const holder = document.querySelector('.fv-margin-strip');
       const bg = getComputedStyle(holder).backgroundColor;
       return { bg, entries: items.map((e, i) => {
           const s = getComputedStyle(e);
           return { i, visibility: s.visibility, display: s.display,
                    opacity: Number(s.opacity), filter: s.filter, color: s.color };
       }) };
    }""")
    shown = [s for s in raw["entries"]
             if s["visibility"] == "visible" and s["display"] != "none"
             and s["opacity"] > 0]
    ratios = [contrast_rgb(rgb(s["color"]), rgb(raw["bg"]), s["opacity"])
              for s in shown]
    return {"phase": phase, "shown": [s["i"] for s in shown],
            "contrast": round(min(ratios), 3) if ratios else 0,
            "sharp": all(s["filter"] == "none" and s["opacity"] == 1 for s in shown)}


def axe_strip(page, axe_source: Path) -> dict:
    page.add_script_tag(path=str(axe_source))
    result = page.evaluate("""async () => {
      if (!window.axe || !window.axe.run) throw new Error('AXE_MISSING');
      const r = await window.axe.run(document.querySelector('.fv-margin-strip'), {
        runOnly: {type: 'rule', values: ['color-contrast']}
      });
      return { violations: r.violations.map(x => x.id),
               incomplete: r.incomplete.map(x => x.id),
               passes: r.passes.map(x => x.id) };
    }""")
    return {"violation_rules": len(result["violations"]),
            "incomplete_rules": len(result["incomplete"]),
            "rule_ids": sorted(result["violations"]),
            "contrast_rule_executed": "color-contrast" in
            (result["violations"] + result["incomplete"] + result["passes"])}


def probe(axe_path: Path) -> dict:
    from playwright.sync_api import sync_playwright
    css = CSS.read_text(encoding="utf-8")
    if not valid_candidate(css):
        raise ValueError("CANDIDATE_CSS_REJECTED")
    if not axe_path.is_file() or axe_path.stat().st_size < 10000:
        raise ValueError("AXE_MISSING_FAIL_CLOSED")
    records = []
    auxiliary = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for width in WIDTHS:
                ctx = browser.new_context(
                    viewport={"width": width, "height": 844},
                    reduced_motion="no-preference",
                    java_script_enabled=True, service_workers="block",
                    accept_downloads=False, bypass_csp=True)
                blocked = {"non_get": 0, "nypl": 0}
                def guard(route):
                    if denied(route.request.method, route.request.url):
                        key = "non_get" if route.request.method != "GET" else "nypl"
                        blocked[key] += 1
                        route.abort()
                    else:
                        route.continue_()
                ctx.route("**/*", guard)
                page = ctx.new_page()
                try:
                    response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                    if response is None or urlsplit(page.url).hostname != "finalvestige.com":
                        raise ValueError("UNEXPECTED_HOST_OR_NO_DOCUMENT")
                    page.locator("[data-fv-home-flagship]").wait_for(state="attached", timeout=15000)
                    count = page.locator(".fv-margin-strip__item").count()
                    if count != 72:
                        raise ValueError("SOURCE_RECORD_COUNT_DRIFT")
                    baseline = None
                    if width in (390, 1440):
                        baseline = {"axe": axe_strip(page, axe_path)}
                    # Browser-local overlay, not a WordPress or GitHub deployment.
                    page.add_style_tag(content=css)
                    styles = [sample_style(page, p) for p in PHASES]
                    candidate_axe = None
                    if width in (390, 1440):
                        # Observe a stable fully-visible slot during the axe scan.
                        sample_style(page, 2.5)
                        candidate_axe = axe_strip(page, axe_path)
                    rec = {
                        "width": width, "status": response.status, "count": count,
                        "flagship": page.locator("[data-fv-home-flagship]").count() == 1,
                        "css_active": page.evaluate("""() =>
                          getComputedStyle(document.querySelector('.fv-margin-strip__item'))
                          .animationName === 'fvMarginContrastSafe'"""),
                        "overflow": page.evaluate("""() =>
                          document.documentElement.scrollWidth >
                          document.documentElement.clientWidth + 2"""),
                        "blocked_non_get": blocked["non_get"],
                        "blocked_nypl": blocked["nypl"],
                        "samples": styles, "axe": candidate_axe,
                        "baseline_axe": baseline,
                    }
                    records.append(rec)
                finally:
                    ctx.close()
            # Reduced motion with and without page scripts. Exact public HTML,
            # local CSS only; never run any signup or editorial POST interaction.
            for javascript in REDUCED_JS:
                ctx = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    reduced_motion="reduce", java_script_enabled=javascript,
                    service_workers="block", accept_downloads=False)
                ctx.route("**/*", lambda route: route.continue_()
                          if not denied(route.request.method, route.request.url)
                          else route.abort())
                page = ctx.new_page()
                try:
                    response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                    if response is None or response.status != 200:
                        raise ValueError("REDUCED_MOTION_HOST_FAILED")
                    page.add_style_tag(content=css)
                    states = page.evaluate("""() => [...document.querySelectorAll(
                       '.fv-margin-strip__item')].map((e,i) => {
                          let s=getComputedStyle(e);
                          return {i, display:s.display, visibility:s.visibility};
                       })""")
                    shown = [e["i"] for e in states
                             if e["display"] != "none" and e["visibility"] == "visible"]
                    auxiliary.append({"javascript": javascript,
                                      "shown": shown,
                                      "passed": len(states) == 72 and shown == [0]})
                finally:
                    ctx.close()
        finally:
            browser.close()
    gates = {
        "hosted_in_memory_candidate": "PASS" if all(evaluate_case(r) for r in records)
                                       and all(c["passed"] for c in auxiliary) else "FAIL",
        "contrast_axe_instrumentation": "PASS" if all(
            r["axe"] and r["axe"]["contrast_rule_executed"]
            for r in records if r["width"] in (390, 1440)) else "FAIL",
        "editorial_rights": "HOLD",
        "manual_wcag_22_aa": "HOLD",
        "independent_qd": "HOLD",
        "production_release": "HOLD",
    }
    return {
        "scope": "ANONYMOUS_PUBLIC_WORDPRESS_IN_MEMORY_CSS_AB_COMPARE",
        "hosted": True, "site_modified": False,
        "external_css_published": False, "media_bytes_retained": False,
        "visitor_data_retained": False, "raw_html_retained": False,
        "axe_node_html_retained": False, "csp_test": False,
        "notes": "Public host delivery; local CSS overlay does not test production style deployment.",
        "source_css": str(CSS.name),
        "cases": records, "reduced_motion": auxiliary, "gates": gates,
    }


# Each remote-browser phase runs in its own killable process. The first
# hosted workflow ran over 24 minutes without a receipt before cancellation;
# a Playwright/axe stall must never hide which individual case was reached.
def _bounded_worker(kind: str, value: int | bool, axe_source: str, out) -> None:
    global WIDTHS, REDUCED_JS
    if kind == "width":
        WIDTHS, REDUCED_JS = (int(value),), ()
    elif kind == "reduced":
        WIDTHS, REDUCED_JS = (), (bool(value),)
    else:
        out.put({"error": "UNSUPPORTED_CASE"})
        return
    try:
        r = probe(Path(axe_source))
        out.put({"cases": r["cases"], "reduced_motion": r["reduced_motion"]})
    except BaseException as exc:
        # Never retain page text, URLs, credentials, or exception messages.
        out.put({"error": type(exc).__name__})


def assemble_bounded(cases: list[dict], auxiliary: list[dict], errors: list[dict]) -> dict:
    widths = [r.get("width") for r in cases]
    complete = sorted(widths) == sorted(WIDTHS) and len(cases) == len(WIDTHS)
    motions = sorted((r.get("javascript") for r in auxiliary)) if len(auxiliary) == 2 else []
    motion_ok = motions == [False, True] and all(r.get("passed") is True for r in auxiliary)
    axe_targets = [r.get("axe") for r in cases if r.get("width") in (390, 1440)]
    axe_ok = len(axe_targets) == 2 and all(
        isinstance(a, dict) and a.get("contrast_rule_executed") is True
        and a.get("violation_rules") == 0 for a in axe_targets)
    valid = complete and not errors and motion_ok and all(evaluate_case(r) for r in cases)
    return {
        "scope": "ANONYMOUS_HOSTED_IN_MEMORY_MARGINS_BOUNDED_ADMISSION",
        "hosted": True, "site_modified": False, "external_css_published": False,
        "raw_html_retained": False, "media_bytes_retained": False,
        "visitor_data_retained": False, "axe_node_html_retained": False,
        "completed_cases": len(cases) + len(auxiliary), "expected_cases": len(WIDTHS) + 2,
        "cases": cases, "reduced_motion": auxiliary, "errors": errors,
        "gates": {
            "hosted_in_memory_candidate": "PASS" if valid and axe_ok else "FAIL",
            "contrast_axe_instrumentation": "PASS" if axe_ok else "FAIL",
            "editorial_rights": "HOLD", "manual_wcag_22_aa": "HOLD",
            "independent_qd": "HOLD", "production_release": "HOLD",
        }
    }


def bounded_probe(axe_source: Path, output: Path, case_timeout: int = 90) -> dict:
    if not 15 <= case_timeout <= 120:
        raise ValueError("INVALID_CASE_TIMEOUT")
    if not axe_source.is_file() or axe_source.stat().st_size < 10000:
        raise ValueError("AXE_MISSING_FAIL_CLOSED")
    records: list[dict] = []
    auxiliary: list[dict] = []
    errors: list[dict] = []
    jobs = [("width", n) for n in WIDTHS] + [("reduced", n) for n in REDUCED_JS]
    ctx = mp.get_context("spawn")
    for kind, value in jobs:
        print(f"START CASE {kind}:{value}", flush=True)
        q = ctx.Queue()
        child = ctx.Process(target=_bounded_worker,
                            args=(kind, value, str(axe_source), q), daemon=True)
        try:
            child.start()
            child.join(case_timeout)
            if child.is_alive():
                child.terminate()
                child.join(4)
                if child.is_alive():
                    child.kill()
                    child.join(2)
                errors.append({"case": f"{kind}:{value}", "reason": "CASE_TIMEOUT"})
            else:
                try:
                    observed = q.get(timeout=3)
                except Empty:
                    observed = {"error": "NO_CASE_RECEIPT"}
                if "error" in observed:
                    errors.append({"case": f"{kind}:{value}", "reason": observed["error"]})
                else:
                    records.extend(observed["cases"])
                    auxiliary.extend(observed["reduced_motion"])
        finally:
            q.close()
            q.cancel_join_thread()
        receipt = assemble_bounded(records, auxiliary, errors)
        # Checkpoint *after every case*, including timeouts and exceptions.
        output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\\n",
                          encoding="utf-8")
        print(f"END CASE {kind}:{value}; complete={receipt['completed_cases']}/"
              f"{receipt['expected_cases']}; errors={len(errors)}", flush=True)
    return assemble_bounded(records, auxiliary, errors)


class SourceGuards(unittest.TestCase):
    def test_partial_or_duplicate_bounded_receipts_fail_closed(self):
        r = assemble_bounded([], [], [])
        self.assertEqual(r['gates']['hosted_in_memory_candidate'], 'FAIL')
        self.assertEqual(r['completed_cases'], 0)
        sample = {'width': 390, 'status': 200, 'count': 72}
        r = assemble_bounded([sample, sample], [], [])
        self.assertEqual(r['gates']['hosted_in_memory_candidate'], 'FAIL')
        self.assertEqual(r['gates']['contrast_axe_instrumentation'], 'FAIL')
        self.assertEqual(r['gates']['production_release'], 'HOLD')

    def test_bounded_timeout_validation(self):
        with self.assertRaises(ValueError):
            bounded_probe(Path('/missing/axe.js'), Path('/tmp/none'), case_timeout=121)
        with self.assertRaises(ValueError):
            bounded_probe(Path('/missing/axe.js'), Path('/tmp/none'), case_timeout=14)

    def test_reject_non_get(self):
        self.assertTrue(denied("POST", URL))
        self.assertTrue(denied("DELETE", URL))
        self.assertFalse(denied("GET", URL))

    def test_block_photo_by_exact_path(self):
        self.assertTrue(denied("GET", URL+"wp-content/uploads/edit-017-v02-nypl-5003296.jpg"))
        self.assertFalse(denied("GET", URL+"nypl-record-without-image"))

    def test_validate_candidate(self):
        self.assertTrue(valid_candidate(CSS.read_text(encoding="utf-8")))
        for bad in ("@import url(//x)", "url(https://x)", "<script>", "!important"):
            self.assertFalse(valid_candidate(CSS.read_text()+"\n"+bad))

    def test_source_declares_no_release(self):
        self.assertFalse(evaluate_case({}))
        self.assertLess(contrast_rgb([216, 210, 199], [15, 16, 15], .42), 4.5)
        self.assertGreater(contrast_rgb([216, 210, 199], [15, 16, 15], 1), 7)

    def test_incomplete_record_fails_closed(self):
        rec = {"status": 200, "count": 72, "flagship": True, "overflow": False,
               "blocked_non_get": 0, "css_active": True,
               "samples": [{"phase": t, "shown": [int(t // 5) % 72],
                            "sharp": True, "contrast": 12.0} for t in PHASES]}
        self.assertTrue(evaluate_case(rec))
        for field, wrong in (("count", 71), ("status", 500), ("css_active", False),
                             ("overflow", True), ("blocked_non_get", -1)):
            other = dict(rec)
            other[field] = wrong
            self.assertFalse(evaluate_case(other))
        other = dict(rec)
        other["samples"] = rec["samples"][:-1]
        self.assertFalse(evaluate_case(other))
        other = dict(rec)
        other["axe"] = {"violation_rules": 1, "incomplete_rules": 0}
        self.assertFalse(evaluate_case(other))

    def test_color_validation(self):
        for a in (-.1, 1.1, float("nan")):
            with self.assertRaises(ValueError):
                contrast_rgb([216, 210, 199], [15, 16, 15], a)
        with self.assertRaises(ValueError):
            rgb("transparent")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--axe-source")
    p.add_argument("--output")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--case-timeout", type=int, default=90)
    args = p.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(SourceGuards)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 2
    if not args.axe_source or not args.output:
        p.error("hosted run requires --axe-source and --output")
    try:
        receipt = bounded_probe(Path(args.axe_source), Path(args.output), args.case_timeout)
    except Exception as exc:
        receipt = {"scope": "ANONYMOUS_HOSTED_IN_MEMORY_MARGINS",
                   "status": "INSTRUMENTATION_FAILURE",
                   "failure_type": type(exc).__name__, "site_modified": False,
                   "production_release": "HOLD"}
    Path(args.output).write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt.get("gates", {"instrumentation": "FAIL", "release": "HOLD"})))
    return 0 if receipt.get("gates", {}).get("hosted_in_memory_candidate") == "PASS" \
        and receipt["gates"].get("contrast_axe_instrumentation") == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
