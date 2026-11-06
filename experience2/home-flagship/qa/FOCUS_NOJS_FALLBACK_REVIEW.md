# EX2 /focus/ non-JavaScript Fieldbook access — REVIEW ONLY
**November 6, 2026 · no WordPress writes · no deployment · no inferred conversions.**

## Why this candidate exists
Read-only WordPress Page 1579 (/focus/), modified `2026-11-05T17:44:02`, currently has a serialized `wp:jetpack/subscriptions` block; its 52-page complete-edition PDF appears in `#fvf-gift[hidden]` and is revealed on a JavaScript-driven successful signup signal. The raw editor source contains no `<noscript>` fallback. The rendered content fragment previously examined in PR #1264 does not prove normal Jetpack operation is broken.

**Offer → funnel → blocker → experiment → evidence → owner:** free Seven Day Focus Fieldbook → homepage contextual CTA /focus/ → no-JS visitor cannot directly access the initially hidden PDF in the raw source → preserve Jetpack signup while exposing a clearly disclosed, usable direct-PDF alternative *only if JS is off* → offline 11/11 Node assertions plus 12/12 native Chromium fixture checks; live WordPress, actual Jetpack signup/delivery, source PDF bytes, WCAG 2.2 AA, and conversions UNVERIFIED → Site QA/Claude review and founder release approval.

## Proposal (no production changes)
`focus_nojs_fallback_block.html` is a Gutenberg Custom HTML block to insert **immediately after** the existing Jetpack subscriptions block. It is visible only without JavaScript, contains a genuine public first-party PDF URL obtained from the current editor source, and explicitly says this route **does not subscribe** the visitor. No signup events or affiliate sales are implied. The fallback is intentionally self-contained, keyboard-focusable and 48px-high in isolation. No new image, copyrighted third-party media, merchant claim, external library, payment step, instrumentation, or SaaS.

`prepare_focus_nojs_fallback.cjs` is an **offline-only** patch generator. It must receive a reviewed, locally supplied exported Page 1579 JSON with exact `id`, `status`, `modified`, and `content`. It rejects changed WordPress modification times, absent/duplicate Jetpack blocks, unrecognized PDF, already-patched page, missing hidden-gift marker, unsafe markup, and source/output overwrite. **It never submits to a CMS.** Later revisions demand a new review; do not force through checks.

Run:
```sh
node --test experience2/home-flagship/qa/test_prepare_focus_nojs_fallback.cjs
python experience2/home-flagship/qa/test_focus_fallback_browser.py
node experience2/home-flagship/qa/prepare_focus_nojs_fallback.cjs /local/read-only-page1579-export.json /local/proposed-page1579-content.html
```

## What was actually measured (local, isolated test)
- Native Node 22.16: **11/11 pass**, one positive insertion and 10 deliberately invalid scenarios rejected.
- Chromium via Python Playwright: **12/12 pass** on a *standalone fixture containing this exact proposed fallback block*, with JS OFF and ON at 320,360,390,768,1440 CSS px plus 1280 px with 200% CSS zoom. The link is visible/focusable at no-JS, absent with JS, touch target >=44px, no observed fixture horizontal overflow. Screenshots `focus_fallback_320_nojs.png` and `focus_fallback_390_nojs.png` produced locally. **Not** a WordPress/Assembler or real Jetpack test.
- Before: raw WordPress editor source has no noscript and PDF in hidden gift. After *proposed*: local output would add a no-JS PDF alternative; **not live**.

## Release gates / privacy / economics
1. WordPress Playground/Assembler import of an isolated, public-content-only copy; verify Gutenberg serialization/sanitization, full-page 320–1920, 200% zoom, actual reduced-motion and keyboard/axe (fail closed).
2. Confirm WordPress native/Jetpack behavior for JS ON and JS OFF, including successful confirmation and welcome delivery **only with founder-approved test signup**; do not silently bypass lead capture in the normal JS path.
3. Verify first-party PDF request 200, genuine transferred bytes, PDF opens, and that the link text is accurate. No claim based only on URL existence.
4. If accessible fallback sacrifices some lead capture for no-JS visitors, quantify it only with consented, verified data; never count raw PDF clicks as leads, purchases or revenue.
5. No CI/QD PASS, no hosted WordPress staging, no Playwright/axe/Lighthouse actual homepage certification, no source image rights changes. Frozen PR #49 and full seven-chapter Blueprint untouched.

**Decision: HOLD.** No production CMS, theme, navigation, signup, marketing, affiliate or analytics changes; no merge/activation/spend. Coordinate with #150, #129, #820; Claude owns production lead capture and attribution.
