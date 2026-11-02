#!/usr/bin/env python3
"""Real keyboard, touch, reflow, CDP pinch zoom and reduced-motion controls in WordPress.

This is an exact-source, private localhost-only Playwright check, NOT manual WCAG
2.2 AA, assistive-technology, browser UI zoom, WP.com-host or field-CWV
certification. Private WordPress nonce, cookies, URLs and LHR are never exported.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
VERIFIER = HERE.parent / "release-candidate" / "verify_exact_staging.py"
PAGE = "http://127.0.0.1:9400/?pagename=fv-ex2-playground-review"
CHAPTERS = ("fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence", "fv-hf-inquiry",
            "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title")
PROFILES = (("reflow_320", 320, False), ("reflow_640", 640, False),
            ("keyboard_390", 390, False), ("touch_390", 390, True),
            ("pinch_200_390", 390, True))


def exact_checkout(repo: Path, expected: str) -> None:
    actual = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"],
                                     text=True).strip()
    if len(expected) != 40 or actual != expected:
        raise ValueError("EXACT_SOURCE_HEAD_MISMATCH")
    for file in (Path(__file__), HERE / "test_private_usability.py", VERIFIER):
        if file.is_symlink() or not file.is_file():
            raise ValueError("QA_FILE_NOT_REGULAR")
        relative = file.resolve().relative_to(repo)
        committed = subprocess.check_output(
            ["git", "-C", str(repo), "show", expected + ":" + relative.as_posix()])
        if file.read_bytes() != committed:
            raise ValueError("QA_SOURCE_NOT_EXACT_COMMIT")


def load_verifier():
    spec = importlib.util.spec_from_file_location("fv_usability_guard", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(VERIFIER.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(VERIFIER.parent))
    return module


def grade(checks: dict[str, bool], profiles: tuple = PROFILES) -> list[str]:
    if not checks or any(type(value) is not bool for value in checks.values()):
        return ["MISSING_OR_NONBOOLEAN_CHECK"]
    expected = {"reflow_320:real_wordpress", "reflow_320:no_root_overflow",
                "reflow_320:primary_nav_fully_visible",
                "reflow_320:seven_chapters", "reflow_320:reduced_motion",
                "reflow_640:real_wordpress", "reflow_640:no_root_overflow",
                "reflow_640:seven_chapters", "reflow_640:primary_nav_fully_visible",
                "reflow_640:reduced_motion",
                "keyboard_390:real_wordpress", "keyboard_390:focus_visible",
                "keyboard_390:case_enter", "keyboard_390:case_space",
                "keyboard_390:chronicle_enter", "keyboard_390:native_details_keyboard",
                "keyboard_390:reduced_motion", "touch_390:real_wordpress",
                "touch_390:case_tap", "touch_390:chronicle_tap",
                "touch_390:reduced_motion",
                "pinch_200_390:real_wordpress", "pinch_200_390:reduced_motion",
                "pinch_200_390:visual_viewport_2x",
                "pinch_200_390:seven_chapters",
                "pinch_200_390:case_tap_at_2x",
                "pinch_200_390:text_200_percent_no_root_overflow"}
    missing = sorted(expected.difference(checks))
    failures = sorted(key for key, ok in checks.items() if not ok)
    return ["MISSING_" + key.replace(":", "_") for key in missing] + [
        "FAIL_" + key.replace(":", "_") for key in failures]


def run(repo: Path, expected: str, storage_state: Path, out: Path) -> dict:
    if not storage_state.is_file() or storage_state.is_symlink():
        raise ValueError("PRIVATE_AUTH_SESSION_MISSING")
    exact_checkout(repo, expected)
    verifier = load_verifier()
    verifier.check_url(PAGE, "127.0.0.1")
    from playwright.sync_api import sync_playwright
    checks: dict[str, bool] = {}
    def mark(profile: str, name: str, ok: bool) -> None:
        checks[profile + ":" + name] = bool(ok)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for profile, width, touch in PROFILES:
                context = browser.new_context(
                    storage_state=str(storage_state), viewport={"width": width, "height": 844},
                    is_mobile=touch, has_touch=touch, reduced_motion="reduce",
                    service_workers="block")
                try:
                    parent = context.new_page()
                    parent.goto(PAGE, wait_until="domcontentloaded", timeout=30000)
                    iframe = parent.locator(
                        'iframe[title="Final Vestige Experience 2.0, unpublished editorial preview"]')
                    iframe.wait_for(state="attached", timeout=16000)
                    if set((iframe.get_attribute("sandbox") or "").split()) != {
                        "allow-scripts", "allow-popups"}:
                        raise ValueError("WORDPRESS_PRIVATE_IFRAME_SANDBOX_CHANGED")
                    url = verifier.check_private_render_url(iframe.get_attribute("src"), PAGE)
                    page = context.new_page()
                    response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    root = page.locator("[data-fv-home-flagship]")
                    root.wait_for(state="visible", timeout=16000)
                    actual_sha = hashlib.sha256(
                        (repo / "experience2/home-flagship/index.html").read_bytes()).hexdigest()
                    mark(profile, "real_wordpress",
                         response is not None and response.status == 200
                         and response.headers.get("x-fv-ex2-index-sha256") == actual_sha)
                    mark(profile, "reduced_motion", bool(page.evaluate(
                        "matchMedia('(prefers-reduced-motion: reduce)').matches")))
                    if profile == "reflow_320":
                        mark(profile, "seven_chapters", all(
                            page.locator("#" + chapter).count() == 1 for chapter in CHAPTERS))
                        mark(profile, "no_root_overflow", bool(page.evaluate(
                            "document.documentElement.scrollWidth <= window.innerWidth + 1 && window.innerWidth === 320")))
                        # Distinct from the intentionally scrollable chapter rail:
                        # at 320px the three primary top-level destinations
                        # must all remain readable without hidden horizontal scroll.
                        mark(profile, "primary_nav_fully_visible", bool(page.evaluate("""() => {
                            const nav = document.querySelector('.fv-hf__nav');
                            if (!nav) return false;
                            const links = [...nav.querySelectorAll('a')];
                            return links.length === 3 &&
                                   nav.scrollWidth <= nav.clientWidth + 1 &&
                                   links.every(a => {
                                       const box = a.getBoundingClientRect();
                                       return box.left >= 0 && box.right <= innerWidth - 4;
                                   });
                        }""")))
                        page.evaluate("window.scrollTo(0, 0)")
                        page.screenshot(path=str(out / "usability-320-first-screen.png"),
                                        full_page=False, timeout=15000)
                    if profile == "reflow_640":
                        # Equivalent *CSS layout width* to a 1280px desktop
                        # viewport at 200% browser zoom; this does not claim
                        # that Chrome's browser UI zoom control was exercised.
                        mark(profile, "seven_chapters", all(
                            page.locator("#" + chapter).count() == 1 for chapter in CHAPTERS))
                        mark(profile, "no_root_overflow", bool(page.evaluate(
                            "document.documentElement.scrollWidth <= innerWidth + 1 && innerWidth === 640")))
                        mark(profile, "primary_nav_fully_visible", bool(page.evaluate("""() => {
                            const nav = document.querySelector('.fv-hf__nav');
                            if (!nav) return false;
                            const links = [...nav.querySelectorAll('a')];
                            return links.length === 3 &&
                              nav.scrollWidth <= nav.clientWidth + 1 &&
                              links.every(a => {
                                const b = a.getBoundingClientRect();
                                return b.left >= 0 && b.right <= innerWidth - 4;
                              });
                        }""")))
                        page.evaluate("window.scrollTo(0, 0)")
                        page.screenshot(path=str(out / "usability-640-200-percent-reflow-equivalent.png"),
                                        full_page=False, timeout=15000)
                    if profile == "pinch_200_390":
                        # A real CDP visual-viewport pinch zoom, not simulated
                        # desktop UI zoom. Underlying CSS layout width remains
                        # 390px; visual viewport must shrink to ~195 CSS px.
                        # Position the case at a deterministic y-coordinate
                        # before enlarging the visual viewport. Playwright's
                        # Locator.tap auto-scroll can target a hidden element
                        # under CDP page-scale; native touchscreen injection
                        # at a DOM-verified visible point avoids that harness
                        # artifact while still testing a genuine touch event.
                        case = page.locator('[data-fv-case-button="malbone"]')
                        case.wait_for(state="visible", timeout=8000)
                        case.evaluate("e => {e.scrollIntoView({block:'start'});window.scrollBy(0,-72)}")
                        session = context.new_cdp_session(page)
                        session.send("Emulation.setPageScaleFactor", {"pageScaleFactor": 2})
                        page.wait_for_timeout(120)
                        mark(profile, "visual_viewport_2x", bool(page.evaluate("""() =>
                            Math.abs(visualViewport.scale - 2) <= 0.05 &&
                            visualViewport.width >= 185 && visualViewport.width <= 205 &&
                            innerWidth === 390
                        """)))
                        mark(profile, "seven_chapters", all(
                            page.locator("#" + chapter).count() == 1 for chapter in CHAPTERS))
                        point = case.evaluate("""e => {
                            const b = e.getBoundingClientRect(), v = visualViewport;
                            const x = Math.max(b.left + 16, v.offsetLeft + 8);
                            const y = Math.max(b.top + 16, v.offsetTop + 8);
                            if (x >= Math.min(b.right - 4, v.offsetLeft + v.width - 6) ||
                                y >= Math.min(b.bottom - 4, v.offsetTop + v.height - 6) ||
                                !document.elementFromPoint(x, y)?.closest(
                                  '[data-fv-case-button="malbone"]')) return null;
                            return {x, y};
                        }""")
                        if point is not None:
                            page.touchscreen.tap(point["x"], point["y"])
                        mark(profile, "case_tap_at_2x", bool(
                            point is not None and case.get_attribute("aria-pressed") == "true" and
                            page.locator('[data-fv-case="malbone"]').is_visible()))
                        page.evaluate("window.scrollTo(0, 0)")
                        page.screenshot(path=str(out / "usability-390-cdp-pinch-200.png"),
                                        full_page=False, timeout=15000)
                        # The second independent scaling challenge is 200%
                        # root-text magnification. It is not a system browser
                        # font setting and cannot replace manual WCAG review.
                        page.evaluate("document.documentElement.style.fontSize='200%'")
                        page.wait_for_timeout(120)
                        mark(profile, "text_200_percent_no_root_overflow", bool(page.evaluate("""() =>
                            parseFloat(getComputedStyle(document.documentElement).fontSize) >= 31 &&
                            document.documentElement.scrollWidth <= innerWidth + 1
                        """)))
                        page.evaluate("window.scrollTo(0, 0)")
                        page.screenshot(path=str(out / "usability-390-200-percent-root-text.png"),
                                        full_page=False, timeout=15000)
                    if profile == "keyboard_390":
                        case = page.locator('[data-fv-case-button="malbone"]')
                        case.wait_for(state="visible", timeout=8000)
                        page.keyboard.press("Tab")
                        case.focus()
                        visible = case.evaluate("""e => {
                            const s = getComputedStyle(e);
                            return e.matches(':focus-visible') &&
                                   s.outlineStyle !== 'none' &&
                                   parseFloat(s.outlineWidth) >= 2;
                        }""")
                        mark(profile, "focus_visible", bool(visible))
                        page.screenshot(path=str(out / "usability-390-keyboard-focus.png"),
                                        full_page=False, timeout=15000)
                        page.keyboard.press("Enter")
                        mark(profile, "case_enter", case.get_attribute("aria-pressed") == "true"
                             and page.locator('[data-fv-case="malbone"]').is_visible())
                        franklin = page.locator('[data-fv-case-button="franklin"]')
                        franklin.focus()
                        page.keyboard.press("Space")
                        mark(profile, "case_space",
                             franklin.get_attribute("aria-pressed") == "true")
                        lens = page.locator('[data-fv-chronicle-view="original"]')
                        lens.wait_for(state="visible", timeout=7000)
                        lens.focus()
                        page.keyboard.press("Enter")
                        mark(profile, "chronicle_enter",
                             lens.get_attribute("aria-pressed") == "true")
                        summary = page.locator(".fv-hf__chronicle-interpretation details summary").first
                        summary.focus()
                        page.keyboard.press("Enter")
                        opened = summary.evaluate("e => e.parentElement.hasAttribute('open')")
                        page.keyboard.press("Space")
                        closed = not summary.evaluate(
                            "e => e.parentElement.hasAttribute('open')")
                        mark(profile, "native_details_keyboard", bool(opened and closed))
                    if profile == "touch_390":
                        case = page.locator('[data-fv-case-button="malbone"]')
                        case.wait_for(state="visible", timeout=8000)
                        case.tap(timeout=7000)
                        mark(profile, "case_tap",
                             case.get_attribute("aria-pressed") == "true"
                             and page.locator('[data-fv-case="malbone"]').is_visible())
                        addition = page.locator('[data-fv-chronicle-view="addition"]')
                        addition.wait_for(state="visible", timeout=7000)
                        addition.tap(timeout=7000)
                        mark(profile, "chronicle_tap",
                             addition.get_attribute("aria-pressed") == "true")
                        page.evaluate("window.scrollTo(0,0)")
                        page.screenshot(path=str(out / "usability-390-touch-first-screen.png"),
                                        full_page=False, timeout=15000)
                finally:
                    context.close()
        finally:
            browser.close()
    failures = grade(checks)
    return {"status": "ISOLATED_WORDPRESS_KEYBOARD_TOUCH_REFLOW_PASS_NOT_WCAG_CERTIFIED"
                      if not failures else "ISOLATED_USABILITY_HOLD",
            "exact_source_commit": expected,
            "target": "NONPRODUCTION_AUTHENTICATED_WORDPRESS_ASSEMBLER",
            "checks": checks, "failure_codes": failures,
            "manual_browser_200_percent_zoom": "NOT_TESTED",
            "cdp_visual_viewport_pinch_200_percent": "AUTOMATED_TESTED",
            "reflow_200_percent_equivalent_1280px": "AUTOMATED_TESTED",
            "root_text_magnification_200_percent": "AUTOMATED_TESTED",
            "screen_reader_and_manual_AT": "NOT_TESTED",
            "real_world_mobile_touch_device": "NOT_TESTED",
            "wpcom_host_compatibility": "NOT_ESTABLISHED",
            "production_writes": False, "release": "HOLD"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--expected-head", required=True)
    ap.add_argument("--storage-state", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    report = {"status": "ISOLATED_USABILITY_HOLD",
              "failure_codes": ["NOT_EXECUTED"], "production_writes": False, "release": "HOLD"}
    try:
        out = args.out.resolve(strict=False)
        repo = args.repo.resolve(strict=True)
        if repo in out.parents or repo == out or args.storage_state.resolve() == out:
            raise ValueError("OUTPUT_MUST_BE_OUTSIDE_REPO_AND_AUTH_SESSION")
        out.mkdir(parents=True, exist_ok=True)
        report = run(repo, args.expected_head, args.storage_state, out)
    except Exception as exc:
        report["failure_codes"] = ["USABILITY_" + type(exc).__name__.upper()]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "PRIVATE_USABILITY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "failures": report["failure_codes"],
                      "release": "HOLD"}))
    return 0 if report["status"].endswith("PASS_NOT_WCAG_CERTIFIED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
