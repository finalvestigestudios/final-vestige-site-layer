# EX2 P0 — exact WordPress-stage Focus hero admission (2026-11-05)

**Status: DRAFT / RELEASE HOLD.** Head is stacked on draft PR #1082 at `4a4b36f96c84bec60e7f0bae7f387aec783e23b1`, never frozen PR #49. No production writes, merges, plugins, tracking, merchant activation, paid services or emails.

## Source-grounded offer and user path
- Real published WordPress Page 6: published 2026-11-04T14:39:24, 7 named chapter anchors, **72/72 ordered Margins items**, existing 4 /focus/ links and Jetpack block. The revised hero action from PR #1082 **is not live**.
- Published Focus Page 1579 at `https://finalvestige.com/focus/` is a published page with the **free 52-page Seven Day Focus Fieldbook**, native Jetpack subscriptions block and explicit confirmation message. Its mere form existence does not prove successful delivery, confirmed subscriber or attributed paid purchase. Do not submit email in QA.
- Draft flagship exact parent `4a4b36f96c84bec60e7f0bae7f387aec783e23b1` has 2 hero actions, evidence room first, a precise free 52-page Fieldbook destination second, and 5 total source occurrences of the Focus URL. This QA introduces **no** changes to those source assets.
- Source rights check: zero new images, fonts, scripts, merchants or factual claims; candidate contains Apollo and Franklin image exhibits, with the Malbone/NYPL exact capture withheld until verified. Royal Museums Greenwich source link preserved. Existing asset-use review and the historical rights ledger remain required.

## Blocker being closed
The existing exact-source WordPress Playwright admission in `verify_exact_staging.py` only checked **presence** of some /focus/ link. A hidden, off-screen, blocked, 12px-high or wrongly labelled *hero* CTA could still have been approved. This matters directly to visitor conversion and keyboard/mobile acceptance.

## Changes / fail-closed admission
New `focus_cta_admission.py` checks the actual authenticated WordPress renderer at each of the five established widths (360/390/768/1440/1920) and its separate real no-JS 390px run. All nine booleans must pass: exactly two hero actions, evidence remains first, free 52-page offer language, exact existing Focus destination, rendered target >=44x44 CSS px, horizontal containment, appearing within 1.5 viewport heights of initial entry, no obscuring overlay at center, and keyboard focus. Test runs **after** first-screen screenshots so the auto-scroll required for hit-testing cannot corrupt founder visual evidence. It does not click the live destination or submit forms.

The modified exact-head WordPress staging verifier also SHA-attests both newly committed QA files. An uncommitted modified verifier/helper/test fails closed. Source check-ins are not approval to deploy.

## Actual verification — offline, representative fixture
- Native system Chromium / Python Playwright executable: **six no-JS, reduced-motion responsive positives passed** at 320/360/390/768/1440/1920.
- **Nine hostile fixtures rejected**: missing action, wrong URL, misleading paid claim, undersized 12px CTA, hidden CTA, extra competing CTA, inert element, intercepting overlay, and horizontal off-screen placement.
- Before/after **representative fixture only** at 390 and 1440: old 19px second-action height / 6 of 9 admission checks; revised 44px second-action / 9 of 9. These are not live WordPress measurements.
- Local `git hash-object` exact matches GitHub blobs `f8278e76385cd32bd4525dea85a45ec374485e64` (helper) and `e5cec10f07f768b45ba54ba1d440d220704f5687` (real-browser fixture test). Native syntax compiled. The **entire WordPress staging verifier** was updated on GitHub, not executed in a complete repo checkout.
- No staging, live HTTP image, axe/WCAG 2.2 AA, Safari, native desktop 200% zoom, Lighthouse or field CWV acceptance is asserted.

## Required before release
1. Check out exact current candidate SHA including this PR and run `python experience2/home-flagship/qa/release-candidate/test_focus_cta_admission_browser.py` and the repository's existing tests.
2. Use the authorized private **isolated WordPress Playground/Assembler** harness and execute `verify_exact_staging.py` on real authentication, with local axe-core. Never point the verifier at production or publish a private preview bundle as a public asset.
3. Read its per-width `hero_*` checks and `no_javascript.hero_*`, preserve real first-screen screenshots, then verify source/rights parity, full mobile keyboard/touch, no-JS, reduced-motion, actual image transfer, 200% zoom and measured Lighthouse. Playground is not WordPress.com Atomic host or live Jetpack deliverability parity.
4. Founder visual review, QD and runner-backed CI on *this exact commit*. No implementation, branch merge or WordPress production changes until specifically approved.

**Offer → funnel step → blocker → change/experiment → evidence → owner:** Free 52-page Fieldbook → historical-evidence homepage secondary hero action → inaccessible or misleading CTA could falsely pass staging → integrate measured real-browser hero admission → local Chromium 15/15, integrated WordPress run still outstanding → homepage engineering; Claude for campaign attribution and commerce, Grok/Praxxis for acquisition.

**Primary KPI:** realized net revenue per 1,000 qualified human sessions, verified from merchant orders after fees/refunds over 7/30 days. This branch measures only interface release readiness. No confirmed leads/orders or revenue improvement is claimed.
