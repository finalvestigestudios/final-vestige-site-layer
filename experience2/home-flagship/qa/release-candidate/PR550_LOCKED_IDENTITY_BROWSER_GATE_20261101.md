# Exact PR #550 browser-gate repair — release HOLD

**Parent candidate:** PR #550 at `6ef459ec76208fc84022328b938d79bf556ac774` (production-rooted, draft). **Isolation:** this companion branch only; no changes to PR #550, PR #49, production WordPress, Apollo, or Mind.

## Confirmed red condition (source-level)

The candidate intentionally removed the three-way art-direction picker and locked the editorial identity. Its `index.html` contains **zero** `data-fv-direction-choice` controls and zero `.fv-hf__studio-controls` elements, while two inherited browser harnesses still attempted to click or assert those retired controls:

- `qa/integration/verify_full_browser.py`: action at former line 107 would target no DOM element at all.
- `qa/release-candidate/verify_csp_exact_browser.py`: positive tests and three negative controls still assumed the obsolete studio UI.

This is a deterministic selector mismatch, **not a measured Chromium failure**, because full exact-checkout Chromium execution is not available in the current tool runtime.

## Repair

- Replaced the defunct art-direction click in the eight-width integrated suite with assertions of the **locked identity** and measured computed/painted Franklin folio geometry, background and both source-derived dates.
- Replaced the retired interaction in the exact-source seven-width CSP suite with a **real keyboard ArrowRight** case transition (Franklin → Malbone), preserving four real interactions: case click, keyboard switch, Chronicle lens switch, Observer switch.
- Replaced obsolete studio-control tests in no-JS, unauthorized-inline-script and bad-nonce negative controls with checks on actual current case buttons and source-visible panels.
- Added six stdlib regression checks to prevent the obsolete selector from quietly returning to these gates.

## Reproduction and remaining gates

Run from exact checkout of **this companion PR's final HEAD**:

```bash
python -m unittest discover -s experience2/home-flagship/tests -p 'test_browser_gate_locked_identity.py' -v
python experience2/home-flagship/qa/integration/verify_full_browser.py --root experience2/home-flagship --out /tmp/fv-home-browser
python experience2/home-flagship/qa/release-candidate/verify_csp_exact_browser.py --root experience2/home-flagship --expected-head "$(git rev-parse HEAD)" --output /tmp/fv-home-csp --chromium /usr/bin/chromium
```

The full browser gates should be run with Playwright installed, and **results must be recorded from an exact checkout**; no claim of passing seven/eight widths is made here. The CSP harness exercises a meta policy in a synthetic DOM, not a true HTTP CSP header or the WordPress/Assembler/Jetpack release environment. The standalone design itself lacks the 72 Margins entries and Jetpack block and **must never overwrite WordPress page ID 6**. Media loading/rights, exact WordPress render, Lighthouse/CWV, manual assistive-tech testing, independent QD/CI and founder release signoff remain unverified. All release gates remain HOLD.
