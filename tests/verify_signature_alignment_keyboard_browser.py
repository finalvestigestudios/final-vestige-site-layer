"""Real-browser keyboard/focus verification for the Signature Alignment interaction.

NOT part of the CI gate in .github/workflows/ci.yml: this repository has no Node/Playwright
dependency declared anywhere, and CI has no browser install step, so a test requiring Playwright
cannot run there without a separate workflow change (out of scope for this fix). Run this manually,
locally, wherever Node + the `playwright` package (with Chromium) are already available:

    python3 tests/verify_signature_alignment_keyboard_browser.py

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
- With no JavaScript at all, the fact and its link must be plainly reachable with no concealment.
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

RUNNER_JS = r"""
const { chromium } = require('playwright');
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
  return {
    inert: fact.inert === true,
    hasInertAttr: fact.hasAttribute('inert'),
    blurred: blurPx === null ? null : blurPx > 0,
    dataRevealed: document.querySelector('[data-fv-align-badge]').getAttribute('data-revealed'),
    statusText: document.querySelector('[data-fv-align-status]').textContent,
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
  results.nojs_inert_attr = await page.evaluate(() => document.querySelector('[data-fv-align-fact]').hasAttribute('inert'));
  require_eq(results.nojs_inert_attr, false, 'fact must never be inert when JS is absent');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  results.nojs_tab3 = await describe(page);
  require_includes(results.nojs_tab3, 'six-miles-an-hour-malbone-street-wreck', 'with JS absent, the source link must be directly Tab-reachable (no concealment is possible without JS)');

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
    try:
        resolved = subprocess.run(
            ["node", "-e", "console.log(require.resolve('playwright'))"],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        print("SKIP: node is not available in this environment; cannot run the real-browser check.")
        return 0
    if resolved.returncode != 0:
        print(
            "SKIP: the 'playwright' package is not resolvable from Node in this environment "
            "(this is expected outside a session that has it preinstalled, and is NOT part of "
            "the CI gate). Run this manually wherever Playwright + Chromium are available.\n"
            f"node stderr: {resolved.stderr.strip()}"
        )
        return 0

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
        (tmp_path / "run.js").write_text(RUNNER_JS, encoding="utf-8")

        proc = subprocess.run(
            ["node", str(tmp_path / "run.js"), str(tmp_path)],
            capture_output=True, text=True,
        )
        print(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            raise SystemExit("FAIL: real-browser keyboard/focus test failed (see assertion above)")

        try:
            results = json.loads(proc.stdout)
        except json.JSONDecodeError:
            raise SystemExit("FAIL: could not parse the browser test's JSON report")

    print(
        "PASS: real-browser keyboard/focus test — concealed link unreachable before discovery, "
        "button-triggered reveal moves focus to the fact predictably, slider-triggered discovery "
        "keeps focus on the stage, re-crossing extremes post-discovery does not re-announce, and "
        "the no-JS fallback is fully reachable with no concealment."
    )
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
