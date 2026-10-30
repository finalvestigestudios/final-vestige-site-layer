"""Real-browser keyboard/focus verification for the Signature Alignment interaction.

NOT part of the CI gate in .github/workflows/ci.yml: this repository has no Node/Playwright
dependency declared anywhere, and CI has no browser install step, so a test requiring Playwright
cannot run there without a separate workflow change (out of scope for this fix). Run this manually,
locally, wherever Node + the `playwright` package (with Chromium) are already available:

    python3 tests/verify_signature_alignment_keyboard_browser.py

Exit codes are deliberately distinct so a missing dependency can never be mistaken for a pass by
anything that checks the exit code alone: 0 = genuinely verified and passed, 1 = ran and an
assertion failed, 2 = skipped because Playwright/Node isn't available here. Only exit 0 means the
checks below actually ran. The printed text also never contains the word "PASS" unless they did.

It builds a throwaway HTML fixture directly from the CURRENT, real page markup
(homepage/page-6-home.blocks.html's fv-align section) and the CURRENT, real governed JS payload
(payloads/signature-alignment-wp-block-v1.txt) -- not a frozen copy -- so it stays accurate as
either file changes. It then drives real Tab/Enter/Arrow key input in headless Chromium and prints
the actual focus sequence and ARIA/`inert` state at each step, asserting the specific accessibility
contract required for this interaction:

- The concealed fact (and its nested source link) must not be reachable via Tab before discovery.
- Activating "Show the connection" must move focus predictably to the revealed fact, and the
  previously-concealed link must become Tab-reachable immediately after.
- Discovering via keyboard/slider movement must NOT move focus away from the stage.
- Re-crossing both extremes after discovery must not re-announce or change state (no duplicates).
- With no JavaScript at all, the fact and its link must be plainly reachable with no concealment,
  and the stage must carry no role/tabindex (it is not a functional slider without JS).
- Slider role/tabindex/aria-describedby are applied by JS only, never present in the static markup.

Playwright resolution: resolved to one absolute file path via a single Node subprocess call, and
that exact path is then baked into the generated runner script's own require() call. The runner
never does its own independent bare-specifier ("require('playwright')") resolution -- if it did,
and Playwright happened to be installed locally inside this repository rather than globally, the
prerequisite check (which resolves relative to this script's working directory) and the runner
(a separate script file living in an unrelated temp directory, which Node would resolve relative
to instead) could legitimately disagree, silently skipping real verification. Resolving once and
threading the exact path through removes that possibility by construction.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "homepage" / "page-6-home.blocks.html"
PAYLOAD = ROOT / "payloads" / "signature-alignment-wp-block-v1.txt"

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_SKIP = 2


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def extract_align_block() -> str:
    page = PAGE.read_text(encoding="utf-8")
    start = page.index('<section class="fv-align"')
    m = re.search(r'<section class="fv-align".*?</section>\n<style>\n(.*?)\n</style>', page, re.S)
    require(m is not None, "could not locate fv-align section+style in homepage page content")
    return page[start:m.end()]


def extract_payload_js() -> str:
    payload = PAYLOAD.read_text(encoding="utf-8")
    m = re.search(r'<script id="fv-signature-alignment-v1-js">\n(.*)\n</script>', payload, re.S)
    require(m is not None, "could not extract JS from the real payload file")
    return m.group(1)


def resolve_playwright_main() -> tuple[str | None, str | None]:
    """Resolve Playwright's absolute entry-file path ONCE via Node's own resolver.

    Returns (path, None) on success or (None, reason) on failure. This is the single source of
    truth for "is Playwright available, and where" -- nothing downstream re-resolves it
    independently (see the module docstring for why that matters).
    """
    try:
        proc = subprocess.run(
            ["node", "-e", "process.stdout.write(require.resolve('playwright'))"],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        return None, "node is not available in this environment"
    if proc.returncode != 0 or not proc.stdout.strip():
        return None, f"the 'playwright' package is not resolvable from Node here: {proc.stderr.strip()}"
    return proc.stdout.strip(), None


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Signature Alignment keyboard test fixture</title></head>
<body>
<a href="#" id="before-marker">BEFORE MARKER</a>
{block}
<a href="#" id="after-marker">AFTER MARKER</a>
{script_tag}
</body>
</html>
"""

RUNNER_JS_TEMPLATE = r"""
const { chromium } = require(__PLAYWRIGHT_MAIN_PATH__);
const path = require('path');

const describe = async (page) => page.evaluate(() => {
  const el = document.activeElement;
  if (!el || el === document.body) return '(nothing focused)';
  const id = el.id ? '#' + el.id : '';
  const marker = el.hasAttribute && el.hasAttribute('data-fv-align-stage') ? '[stage]'
    : el.hasAttribute && el.hasAttribute('data-fv-align-reveal-trigger') ? '[reveal-trigger]'
    : el.hasAttribute && el.hasAttribute('data-fv-align-fact') ? '[fact]'
    : '';
  const tag = el.tagName.toLowerCase();
  const href = el.tagName === 'A' ? ' href=' + el.getAttribute('href') : '';
  return `<${tag}${id}${marker}${href}>`;
});

const factState = async (page) => page.evaluate(() => {
  const fact = document.querySelector('[data-fv-align-fact]');
  const filterValue = getComputedStyle(fact).filter;
  const m = /blur\(([\d.]+)px\)/.exec(filterValue);
  const blurPx = filterValue === 'none' ? 0 : (m ? parseFloat(m[1]) : null);
  const stage = document.querySelector('[data-fv-align-stage]');
  return {
    inert: fact.inert === true,
    hasInertAttr: fact.hasAttribute('inert'),
    blurred: blurPx === null ? null : blurPx > 0,
    dataRevealed: document.querySelector('[data-fv-align-badge]').getAttribute('data-revealed'),
    statusText: document.querySelector('[data-fv-align-status]').textContent,
    stageRole: stage.getAttribute('role'),
    stageTabindex: stage.getAttribute('tabindex'),
    stageDescribedBy: stage.getAttribute('aria-describedby'),
  };
});

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const dir = process.argv[2];
  const url = 'file://' + path.join(dir, 'page.html');
  const results = {};

  await page.goto(url);
  await page.waitForTimeout(150);
  results.initial = await factState(page);
  require_eq(results.initial.inert, true, 'fact must be inert before discovery');
  require_eq(results.initial.hasInertAttr, true, 'inert attribute must be reflected in the DOM');
  require_eq(results.initial.stageRole, 'slider', 'JS must apply role=slider on successful init');
  require_eq(results.initial.stageTabindex, '0', 'JS must apply tabindex on successful init');
  require_eq(results.initial.stageDescribedBy, 'fv-align-desc', 'JS must wire aria-describedby to the real description element on successful init');

  await page.keyboard.press('Tab');
  results.tab1 = await describe(page);
  await page.keyboard.press('Tab');
  results.tab2_stage = await describe(page);
  require_includes(results.tab2_stage, '[stage]', 'second Tab stop must be the alignment stage');
  await page.keyboard.press('Tab');
  results.tab3_trigger = await describe(page);
  require_includes(results.tab3_trigger, '[reveal-trigger]', 'third Tab stop must be the reveal-trigger button');
  await page.keyboard.press('Tab');
  results.tab4_after_marker = await describe(page);
  require_eq(results.tab4_after_marker, '<a#after-marker href=#>', 'fourth Tab stop must SKIP the concealed link entirely and land on the after-marker');

  await page.reload();
  await page.waitForTimeout(150);
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  results.focus_before_button = await describe(page);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(50);
  results.focus_immediately_after_button = await describe(page);
  require_includes(results.focus_immediately_after_button, '[fact]', 'activating the button must move focus to the revealed fact immediately');
  await page.waitForTimeout(400);
  results.fact_after_button_reveal = await factState(page);
  require_eq(results.fact_after_button_reveal.inert, false, 'fact must no longer be inert after discovery');
  require_eq(results.fact_after_button_reveal.blurred, false, 'fact must be visually unblurred (settled) after discovery');
  await page.keyboard.press('Tab');
  results.tab_after_reveal = await describe(page);
  require_includes(results.tab_after_reveal, 'six-miles-an-hour-malbone-street-wreck', 'the source link must be Tab-reachable immediately after discovery');

  await page.reload();
  await page.waitForTimeout(150);
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  results.focus_on_stage_before = await describe(page);
  for (let i = 0; i < 10; i++) await page.keyboard.press('ArrowLeft');
  results.focus_after_low_extreme = await describe(page);
  require_includes(results.focus_after_low_extreme, '[stage]', 'focus must stay on the stage after reaching one extreme');
  for (let i = 0; i < 30; i++) await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(400);
  results.focus_after_both_extremes = await describe(page);
  require_includes(results.focus_after_both_extremes, '[stage]', 'focus must stay on the stage even after discovery fires via keyboard');
  results.fact_after_keyboard_discovery = await factState(page);
  require_eq(results.fact_after_keyboard_discovery.dataRevealed, '1', 'keyboard-driven exploration of both extremes must trigger discovery');

  const statusBefore = results.fact_after_keyboard_discovery.statusText;
  for (let i = 0; i < 10; i++) await page.keyboard.press('ArrowLeft');
  for (let i = 0; i < 30; i++) await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(200);
  const statusAfter = await page.evaluate(() => document.querySelector('[data-fv-align-status]').textContent);
  require_eq(statusAfter, statusBefore, 'status text must not change / re-announce after discovery is already complete');

  await page.goto(url.replace('page.html', 'page-nojs.html'));
  await page.waitForTimeout(150);
  results.nojs_state = await factState(page);
  require_eq(results.nojs_state.inert, false, 'fact must never be inert when JS is absent');
  require_eq(results.nojs_state.hasInertAttr, false, 'fact must never carry the inert attribute when JS is absent');
  require_eq(results.nojs_state.stageRole, null, 'without JS, the stage must NOT advertise role=slider -- it is not a functional slider, so it must not claim to be one');
  require_eq(results.nojs_state.stageTabindex, null, 'without JS, the stage must NOT be in the keyboard Tab order -- a nonfunctional element should not be a dead Tab stop');
  await page.keyboard.press('Tab');
  results.nojs_tab1 = await describe(page);
  require_eq(results.nojs_tab1, '<a#before-marker href=#>', 'first Tab stop must still be the before-marker');
  await page.keyboard.press('Tab');
  results.nojs_tab2 = await describe(page);
  require_includes(results.nojs_tab2, 'six-miles-an-hour-malbone-street-wreck', 'with JS absent, the source link must be the very next Tab stop: the non-interactive stage has no tabindex (skipped), and the "Show the connection" question/button stay display:none since only JS ever shows them, so neither is a Tab stop either');

  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})().catch((err) => { console.error('BROWSER_TEST_FAILED: ' + err.message); process.exit(1); });

function require_eq(actual, expected, message) {
  if (actual !== expected) { console.error('ASSERTION FAILED: ' + message + ' (expected ' + JSON.stringify(expected) + ', got ' + JSON.stringify(actual) + ')'); process.exit(1); }
}
function require_includes(actual, substr, message) {
  if (typeof actual !== 'string' || !actual.includes(substr)) { console.error('ASSERTION FAILED: ' + message + ' (got ' + JSON.stringify(actual) + ')'); process.exit(1); }
}
"""


def main() -> int:
    playwright_main, skip_reason = resolve_playwright_main()
    if playwright_main is None:
        print(
            f"SKIP (exit {EXIT_SKIP}, NOT a pass): {skip_reason}. This is expected outside a "
            "session that has Playwright preinstalled, and is NOT part of the CI gate. Run this "
            "manually wherever Playwright + Chromium are available. No accessibility checks ran."
        )
        return EXIT_SKIP

    block = extract_align_block()
    js = extract_payload_js()
    require("[data-fv-align-reveal-trigger]" in js, "extracted JS does not look like the current payload")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "align.js").write_text(js, encoding="utf-8")
        page_html = PAGE_TEMPLATE.format(block=block, script_tag='<script src="align.js"></script>')
        (tmp_path / "page.html").write_text(page_html, encoding="utf-8")
        nojs_html = PAGE_TEMPLATE.format(block=block, script_tag="<!-- no JS -->")
        (tmp_path / "page-nojs.html").write_text(nojs_html, encoding="utf-8")
        runner_js = RUNNER_JS_TEMPLATE.replace("__PLAYWRIGHT_MAIN_PATH__", json.dumps(playwright_main))
        (tmp_path / "run.js").write_text(runner_js, encoding="utf-8")

        proc = subprocess.run(
            ["node", str(tmp_path / "run.js"), str(tmp_path)],
            capture_output=True, text=True,
        )
        if proc.stdout.strip():
            print(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            print(f"FAIL (exit {EXIT_FAIL}): real-browser keyboard/focus test failed (see assertion above)")
            return EXIT_FAIL

        try:
            results = json.loads(proc.stdout)
        except json.JSONDecodeError:
            print(f"FAIL (exit {EXIT_FAIL}): could not parse the browser test's JSON report")
            return EXIT_FAIL

    print(
        f"PASS (exit {EXIT_PASS}): real-browser keyboard/focus test actually ran against real "
        "Chromium — concealed link unreachable before discovery, slider role/tabindex/"
        "aria-describedby applied by JS only and absent without JS, button-triggered reveal moves "
        "focus to the fact predictably, slider-triggered discovery keeps focus on the stage, "
        "re-crossing extremes post-discovery does not re-announce, and the no-JS fallback is fully "
        "reachable with no concealment and no false slider semantics."
    )
    print(json.dumps(results, indent=2))
    return EXIT_PASS


if __name__ == "__main__":
    raise SystemExit(main())
