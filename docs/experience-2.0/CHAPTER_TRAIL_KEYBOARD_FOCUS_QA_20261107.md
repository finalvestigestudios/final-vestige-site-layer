# Experience 2.0 — keyboard visibility correction for the seven-chapter trail

**Review-only / release HOLD.** Source family: draft PR #1500 stacked on #1493. This is a targeted accessibility/conversion correction, **not** an additional chapter, theme change, public WordPress edit, promotion, or analytics installation.

## Source-grounded finding — 7 November 2026

Exact protected private WordPress-review bundle: `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d`. Candidate PHP inside: `91adf4e42a711bf253370a706b29d1428131051333e470af4a841948d1e97b04`.

A real Chromium Tab traversal of the *actual packaged homepage PHP-derived HTML, CSS and JS* found that **some horizontally scrolling chapter anchors received a visible keyboard focus state while their center remained outside the viewport or untargetable**. The defect reproduced at 320, 390 and 768 CSS pixels, with and without JavaScript, and intensified under synthetic 200% CSS zoom. The source already contained `overflow-x:auto`, sticky wayfinding, gradient edge masks and scroll-indication behavior; simple `scroll-margin-inline` and scroll-snap attempts were insufficient.

This is a keyboard-focus visibility defect in the isolated candidate source; **not a tested allegation about the published WordPress homepage**. WCAG 2.2 SC 2.4.11 (focus not obscured) warrants independent integrated review rather than a blanket compliance claim.

## Isolated correction

1. **Enhanced case:** The chapter rail listens to `focusin` on native anchor elements and recenters the newly focused anchor in the *existing* horizontal scroller. Rectangles are converted from visual pixels to CSS scroll units to preserve behavior at 200% zoom. No links are replaced, no interactions are intercepted, and there are no network or analytics calls.
2. **JavaScript-off case:** For widths <=920px, where scroll enhancement is absent, the seven native anchor links wrap into a complete, visible chapter index. Historical content and fragment navigation remain fully readable and actionable without JavaScript.
3. **Source custody:** The patcher requires the exact parent bundle and PHP SHA-256, checks its fixed file inventory and source markers, and emits an explicitly **derived, unapproved** ZIP. It does **not** reuse the original exact-source hash or bypass the old release gate. The current consolidated admission verifier intentionally rejects the derived candidate until a separate source and integration review is approved.

## Local browser evidence

| Test | Original bundle | Derived review source |
|---|---|---|
| Chromium source render configurations | 12 | 12 |
| Responsive widths | 320, 390, 768, 1440, 1920 | Same |
| 200% CSS-zoom stress | 320 and 390, JS enabled | Same |
| Keyboard focus/link visibility failures | **19** | **0** |
| Seven tabbable chapter anchors | Present throughout | Preserved throughout |
| Margins records / Focus destinations | 72 / 5 | 72 / 5 |
| Above-fold Focus CTA at regular zoom | Present in tested widths | Preserved |
| Document overflow / uncaught JS exceptions | None observed | None observed |
| PHP syntax check | PASS | PASS |
| Five separate adversarial patcher unit methods | — | **5 PASS** |
| Old consolidated exact-source gate applied to patched ZIP | — | **FAIL as intended**, exit 2 |
| Real WordPress/Assembler, image transfers, independent axe, Lighthouse/CWV | **Not tested** | **Not tested** |

Total: **24 independent original-versus-derived Chromium configurations**. No browser requests were permitted. Tests do not submit email addresses, click affiliates, contact analytics services or change subscriber records.

Derived review ZIP: `75334d85b187916a21b32d172c2228fe71f50fce2c6ad1a1ce4fd86b71a3db53`; derived PHP: `cab2236dca3bf83a07bac23325425e01ceeee9c832619e62e79812f8dcc275fc`. These are review identities, **not release hashes**.

## How to reproduce (no WordPress writes)

1. Extract the protected nested `fv-ex2-local-cli-preflight-guarded.zip` from PR #1469's evidence archive (original bundle SHA must match).
2. In this directory, run `python apply_ex2_chapter_trail_fix.py --parent /path/to/original.zip --out /tmp/fv-ex2-derived.zip --css chapter-trail-focus-visibility.css --js chapter-trail-focus-visibility.js`.
3. Run `FV_EX2_PROTECTED_PARENT_ZIP=/path/to/original.zip python -m unittest -v test_ex2_chapter_trail_fix.py`.
4. Run `python verify_ex2_chapter_keyboard_browser.py --parent /path/to/original.zip --patched /tmp/fv-ex2-derived.zip --out /tmp/fv-ex2-trail-qa`. Chromium and Python Playwright are required; unavailable dependencies are a blocker, not a pass.
5. Independently inspect 390px screenshots, stage in genuine isolated WordPress/Assembler only after fresh exact-source approval, and re-run normal 320–1920px, keyboard/touch/no-JS/zoom/reduced-motion/axe/media/Lighthouse gates. Maintain the frozen PR #49 and no-CMS-write gate.

## Evidence and commercial impact

**Offer:** The existing free 52-page Focus Fieldbook, not an unverified commercial product. **Funnel step:** chapter exploration → unobstructed contextual Focus CTA → verified subscriber → independently verified paid purchase. **Blocker:** partially offscreen keyboard-focused chapter choices interrupt exploration for some users. **Change:** native focus centering and complete no-JS chapter navigation. **Evidence:** 19 original failures → zero in the derived offline browser study; no confirmed signup or purchase attribution. **Owners:** interim homepage engineering and Site QA review this patch; Claude owns native WordPress integration, Jetpack and commerce attribution; Grok/Praxxis own acquisition.

The seven chapters, Franklin editorial folio, Apollo and Franklin media references, NYPL non-reproduction restriction, 72 Margins entries and five Focus links remain intact. Historical image rights and real transferred bytes remain release gates, not inferred from this patch. No claims about award status, conversions, WP production performance, or host parity are made.

**Next release decision:** HOLD pending new exact-source staging admission, genuine Assembler theme rendering, axe plus manual WCAG review (including 2.4.11), real first-party/CDN image transfers, measured Lighthouse/CWV, functioning Jetpack flow, independent QD/CI and founder visual/release authorization.
