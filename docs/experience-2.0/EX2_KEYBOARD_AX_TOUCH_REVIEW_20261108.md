# EX2 — Independent pinned-PHP keyboard, accessibility-tree and touch acceptance (2026-11-08)

**Status: TESTED IN ISOLATION / RELEASE HOLD. No production WordPress changes.**

## Exact custody
- Parent draft PR #1562 commit: `2743136a65d2b47034e5abf6854abab098fb9875`
- New test: `experience2/review/verify_keyboard_ax_exact.py`
- Protected PHP renderer SHA-256: `7fe27aecc6f5f2b8033ab826dcb5146b6e31ae4dbcaf2a7825859b48dc5b51ee`.
- Rendered HTML SHA-256: `f3c3416a531dd88e84d900c4f972a71035a158e8e947848f5e49b15db13ac749`.
- Chromium: **144.0.7559.96**. PHP via sibling PR #1562 WordPress-function *stubs*; NOT WordPress core.

## What is newly verified
The *actual pinned PHP renderer* was executed; its generated HTML/CSS/JS was loaded in Chromium. New tests check that seven chapter links transfer keyboard focus and scroll to visible, correct targets at 320/390/768/1440 px in both enhanced/no-JS states; all exposed link/button controls have accessible names in the Chrome Accessibility tree; motion preferences are honored in the test environment; all 72 Margins records and two appropriately labeled authentic archival image elements survive; the Focus Fieldbook link remains; the three evidence controls respond both to Enter and to touchscreen tap; 200% CSS zoom shows no document overflow or visible interactive target below 24px.

**New independent test: 131/131 PASS.** Three deliberately sabotaged contracts (removed Focus link, broken chapter anchor, stripped Apollo alt) were all rejected. Screenshots and structured logs are included in the private founder evidence archive, not checked into public GitHub. The previous PR #1562's 55 checks remain a separate earlier run, not 186 independent results on this exact new HEAD.

## Scope / limits, rigorously retained
- No WordPress core, Assembler theme, hosted Jetpack form or merchant checkout ran.
- **axe-core unavailable:** Chrome accessibility tree checks do **not** qualify WCAG 2.2 AA. Focus visibility/target dimensions are only limited automated checks. No assistive-technology/manual accessibility acceptance.
- Network archival-image requests were blocked; **zero actual image bytes are certified.** WP metadata identifies Apollo #473 as 78,346 bytes, Franklin #474 as 466,043 bytes; NYPL #1258 as 5,553,669 bytes; none equals verified transfer size.
- CSS `zoom:2` is *not actual browser zoom* and is not represented as such.
- Lighthouse/CWV and commercial conversion have **not** been measured; a simulated CTA activation is not a subscribed lead or paid purchase.
- Live Page 6 already contains seven chapters and an additional NYPL map; the protected staging renderer excludes that NYPL image. The private candidate cannot silently replace the live source.
- WordPress.com Personal has no native staging clone; free isolated Playground/local WordPress remains the staging plan. No subscriber/database/private content transfer.
- The source integrity gate, release hold and frozen PR #49 remain intact.

## Commercial acceptance
**Offer:** Existing free Seven Day Focus Fieldbook.  
**Funnel step:** historical evidence → contextual Focus CTA → native Jetpack confirmed lead → independently verified paid order.  
**Blocker:** no integrated WordPress/Jetpack confirmation; PDF may be downloaded independently of signup; user-visible download-ready state can be query-spoofed (separate correction PR #1451).  
**Change:** release-gated keyboard/touch/accessible CTA route test rather than another visual chapter or tracking system.  
**Pass/fail:** offline keyboard/touch/semantic subset PASS; actual signup, merchant revenue and independent accessibility acceptance HOLD.  
**Owner:** interim homepage engineer / Site QA, with Claude owning production attribution/Jetpack, Grok owning acquisition, founder owning release.

## Reproduction
From a checkout containing PR #1562 and this branch (with a locally controlled private PR #1515 bundle):
```sh
python experience2/review/verify_keyboard_ax_exact.py \
  --bundle /private/fv-ex2-official-playground-web-review.zip \
  --out /tmp/fv-ex2-keyboard-ax
```
Requires PHP CLI, Python Playwright and locally installed Chromium. Never install or activate preview files in production.

## Release decision
**HOLD** pending real isolated WordPress/Assembler rendering, actual archival image transfer checks, axe + manual WCAG 2.2 AA, real Lighthouse/CWV, Jetpack confirmation, rights derivative mapping, exact-head CI/QD and founder visual/release approval. Do not merge/deploy or modify live WordPress.
