# EX2 unified flagship — complete-source Chromium visual QA (2026-11-06 PT)

**DRAFT / REVIEW-ONLY / RELEASE HOLD.** This test adds no homepage chapters, styling, tracking, ads, WordPress content, or archive claims. It is stacked on draft PR #1326, head `36888bea912c4dafad16d8dd96b059ff164b6350`. Frozen PR #49 remains at `10495883299d53596992c26a8987f629b2904670`, untouched.

## Exact custody
- Candidate: `experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json`, from #1326 at Git blob **`137c74a476005684a28f5ff9a36e75c6b03268f7`**.
- Candidate file SHA-256: **`10af751569bf11a7fd18003e56cb7ccad9596f59606be9d5fb5d87d95784bb7c`**.
- Committed visual runner: `verify_flagship_fullpage_review.py`, verified against its local Git blob `e9b509e21cbe0d5a3a420a3d50090c06f9ee9a68`.
- Reproduce: `python experience2/home-flagship/playground/verify_flagship_fullpage_review.py --blueprint experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json --out /tmp/fv-ex2-fullpage`.
- Negative control: same command plus `--mutate-scrolling` and a different output folder. **Expected nonzero exit**, reproducing the covered chapter-heading defect. Do not mark a negative-control failure as CI failure.

## Actual Chromium evidence — source-static, not WordPress
- Chromium executed current Blueprint-derived HTML, CSS, JavaScript; **15 scenarios, 105 native chapter-anchor interactions PASS**.
- Viewports: **320×568, 360×640, 390×667, 768×900, 1440×900, 1920×1080**. At 390, also JS disabled, reduced-motion and CSS 200% zoom. At 1440, also CSS 200% zoom. CSS zoom is an approximation, not a certified browser zoom equivalence.
- **Minimum observed chapter-heading clearance 34.7 CSS px**, against 12px minimum; no document-level horizontal overflow in tested scenarios.
- **72/72 Margins fragments, 7/7 chapter links, 5/5 Focus destinations, 2 archival img elements preserved.**
- 390×667 contextual Focus CTA remains ≥44px high and within initial screen in the nonzoomed tested cases. This is layout/visibility evidence, **not sales or signup evidence**.
- **10 first-screen/fullpage screenshots** generated for 320, 390, 768, 1440, 1920 at unenhanced browser-engine scale, useful for founder visual review.
- **Adversarial test fails closed:** removing exact high-specificity anchor clearance reproduces `fv-hf-title` at **−29px** relative to sticky chapter rail at 320px. Native anchor `element.click()` is used, not Playwright `locator.click()`, because the latter pre-scrolls into view and can mask this failure.

## Rights and performance — admission gates, not assumed passes
Existing image references ONLY: Apollo 1 crew NASA S67-19766 media #473 and Franklin Victory Point document/reproduction media #474. Source/caption references are unchanged. The NYPL image #1258 remains excluded pending rights. **Image response bytes, external rights clearance, and first-party load status were not tested here**: the static fixture intentionally aborts all network requests. Do not misrepresent missing image content as a WordPress defect.
No axe-core library was available locally; **WCAG 2.2 AA cannot be certified**. Lighthouse/field CWV, Safari, actual WordPress/Assembler/Jetpack rendering, auth/CSP, site-specific cookies and host redirects remain unverified. No performance numbers are inferred from static rendering. Independent CI and QD remain outstanding.

## Conversion-first interpretation
**Offer:** free 52-page Focus Fieldbook. **Funnel step:** historical evidence exploration → visible contextual Focus action → independently confirmed subscriber → verified paid order. **Blocker addressed by #1326 and tested here:** native chapter navigation hid evidence headings beneath sticky navigation. **Change in this PR:** exact-source fullpage and native-anchor regression test + reproducible founder screenshots. **PASS evidence:** 105 native interactions, first-screen Focus visibility, 72 preserved source fragments, negative mutation rejected. **Owner:** interim homepage engineering / independent Site QA; Claude owns production integration and commercial attribution, Grok/Praxxis acquisition. **Commercial outcome:** zero new verified leads, orders or realized revenue established by this review.

## Release decision
**HOLD:** WordPress.com Personal does not include a staging clone. Run existing #1306 admission harness on a genuinely isolated WordPress Playground/Assembler import; independently inspect real Apollo/Franklin image bytes, axe, keyboard/touch/no-JS, Safari if available, Lighthouse and Jetpack. A Playground clone is not equivalent to WordPress.com infrastructure. **Do not merge, deploy, publish, install, touch production settings, send email, add analytics or spend without exact founder approval.**
