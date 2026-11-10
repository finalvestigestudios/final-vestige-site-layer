# EX2 Page 6 — Assembler first-screen conversion and duplicate-navigation containment

**DRAFT / release HOLD / no WordPress writes.** Stacked on exact parent PR #1873, commit `4a9bad9c5fbc3950d31902772e91cc7ce89e60b2`. Frozen PR #49 must not change. This is a **scoped offline Gutenberg composer change**, not a public page or theme patch.

## Confirmed design/UX risk

Page 6 already has its WordPress/Assembler theme header and a native Focus Fieldbook destination outside the replaceable seven-chapter Custom HTML block. The standalone EX2 candidate adds a **second masthead with duplicate branding, navigation, mobile menu and Focus CTA**, preceded by a developer "DESIGN STUDY" note. Reusing this structure unmodified in WordPress consumes scarce mobile first-screen space and creates two site navigations. This is a source-grounded integration concern, **not** a verified WordPress-hosted regression.

## Change made in this isolated branch

- Preserve **all seven chapters**, the original Franklin evidence folio/museum link, all six CSS and four JS source files and all **three** art directions, with original Git blob pins unchanged.
- In the offline `stage_payload` composer **only**, require exactly one known source `<header class="fv-hf__masthead">` and exactly one known, permitted original Focus anchor. Fail closed if missing or changed.
- Remove this duplicate source masthead from the **WordPress-integrated payload only**, retaining the theme's own navigation. Move that same original Focus anchor (unmodified URL) into a slim, accessible `Free reader resource` rail. Preserve the original independent native `/focus/` CTA outside the replaceable Gutenberg block.
- Apply strictly scoped `fv-hf--wp-integrated` CSS. De-emphasize the redundant developer "not live" note while keeping the keyboard-operable three-direction preview disclosure. The standalone art study is unaffected.
- Keep the current no-JS skip links, chapter navigation, case evidence and Focus rail visible with no enhancement.
- No affiliate link, tracking event, UTM, product claim, analytics script, paid service, permission or public navigation adjustment.

## Measured, reproducible offline QA (NOT WordPress)

The synthetic comparison used **the 11 pinned EX2 source files**, Python `stage_payload` before/after, an explicitly mocked 74px "Assembler" header and Playwright/Chromium via `/usr/bin/chromium`. Tests used a network-aborted `page.set_content` document (actual archival images intentionally unavailable). Source-equivalent local composer regression tests: **22/22 PASS**, including new route/rail and custody assertions. Browser checks: **15/15 post-change synthetic scenarios PASS** at 320/390/768/1440/1920 CSS pixels, JS-on/off at 100%, and a CSS `zoom:2` reflow simulation. These are NOT actual browser UI 200% zoom, axe, real image transfers or hosted WordPress behavior.

| CSS viewport | Headline y before | After | Reduction | After Focus link y |
| --- | ---: | ---: | ---: | ---: |
| 320px | 492px | 401px | 91px | 146px |
| 390px | 443px | 371px | 72px | 146px |
| 768px | 383px | 351px | 32px | 145px |
| 1440px | 482px | 450px | 32px | 145px |
| 1920px | 482px | 450px | 32px | 145px |

CSS-zoom:2 simulated reflow (not browser zoom) reduced headline y **286px at 320**, **298px at 390**, **227px at 768**, **64px at 1440 and 1920**. Every tested post-change scenario had document scrollWidth equal to its CSS viewport; CTA computed rectangle was at least 44px high; 7 chapter IDs, the source link, and 3 art-direction options were retained. No JS page errors in the synthetic fixture.

**Hypothesis:** A single masthead and an immediately visible, contextual Fieldbook link may reduce first-screen friction for qualified readers and improve navigation to the real Focus funnel. **No production A/B test, subscriber, confirmed order or net-revenue outcome** has been observed. Keep the editorial evidence action prominent and the actual Jetpack form untouched.

## Repeatable checks

```bash
python -m unittest discover -s tests/experience-2 -p 'test_page6_scoped_composer.py' -v
python -m unittest discover -s tests/experience-2 -p 'test_page6_assembler_first_screen.py' -v
```

Both commands require a **complete exact Git checkout** including `experience2/home-flagship/`; do not substitute a synthetic fixture for source custody. Source-pinned browser QA remains in the parent stack. The synthetic browser comparison and screenshots live in the founder's QA package, not the public repository.

## Acceptance / release gates

1. Get a real isolated **WordPress + Assembler** runtime using public content only. WordPress.com Personal cannot create a native staging clone; private Playground/local WordPress is acceptable for developer QA but **not equivalent to the production host**. No subscriber, private database or secret exports.
2. Confirm no duplicate theme header and exact Gutenberg-block swap while **all 72 Margins items, native Jetpack subscription block and original outside `/focus/` CTA** remain visible and functional. Verify the free Fieldbook destination and independently confirm signup only with separately approved safe test consent.
3. Run real Chromium, axe-core and WCAG 2.2 AA (including manual keyboard/touch, screen reader and 200% browser zoom) at 320/360/390/768/1440/1920; no-JS, reduced motion, CSP/nonce and Safari where available.
4. Confirm actual, successful first-party transfers and rights for Apollo 473, Franklin 474 and NYPL 1258, not media metadata alone; measure Lighthouse/CWV from real runtime without inventing numbers.
5. Founder compares the three existing art directions and grants explicit release approval; independently obtain exact-HEAD CI and QD PASS. **Do not install, merge, deploy, publish, modify live WordPress or spend until approved.**

**Ownership:** interim ChatGPT homepage engineering owns the isolated composer; Claude owns production integration/attribution; Grok and Praxxis own social campaign assets. No new instrumentation introduced.
