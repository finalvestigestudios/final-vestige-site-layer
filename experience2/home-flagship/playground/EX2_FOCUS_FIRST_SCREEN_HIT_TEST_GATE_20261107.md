# EX2 — first-screen Focus action hit-test receipt (REVIEW ONLY)

**Release HOLD.** Parent: PR #1372 at `c2544b8407bc612b758d780c0036aad428961fed`. Frozen PR #49 and WordPress production untouched.

The previous private WordPress Playground receipt measured five Focus links and their dimensions but could miss an invisible or obstructing overlay covering the conversion action. This extends the *isolated, local-only* reviewer to sample the true first-screen scroll position, run `elementFromPoint` hit tests on each Focus link, record its bounds and visibility, and restore the reviewer's scroll position. It does not follow links, submit forms, send telemetry or authorize release.

New fail-closed signals: `NO_USABLE_FIRST_SCREEN_FOCUS_ACTION` (no hit-testable action at least 44 CSS px tall on the sampled first screen) and `FOCUS_FIRST_SCREEN_POINTER_OCCLUDED` (an in-view Focus action is covered or blocked). Individual observations are recorded in `first_screen_focus_hit_tests`. This is a narrow DOM pointer test, **not** keyboard, touch, usability, verified lead, WCAG or commerce testing.

**Offline test evidence:** PHP 8.4 lint PASS; 17/17 local Python/Chromium test methods PASS. Baseline 320, 360, 390, 768, 1440px fixture layouts each expose a 44px usable Focus action. Negative controls reject full-screen popup, fixed top banner and invisible mobile masthead action. Existing false-image-load guard still holds because external images are intentionally blocked. These fixtures are NOT WordPress staging. Original reviewer tests remain, the five-step canonical Blueprint is unchanged, and source-only build pin now references the new exact review plugin sha256 `a58e144fd8e9e584681b7edceb667a4a5b0ca303e49b6902299b941d0a95a9fc`.

**Archival/rights:** Apollo 1 NASA S67-19766 #473 and Franklin Victory Point #474 (1869 print of 1847/1848 note) stay exactly as supplied. Rights-pending NYPL #1258 remains excluded from the unpublished candidate. No additional images, historical assertions or affiliate offers.

**Commercial hypothesis:** Historical homepage → visible free 52-page Focus Fieldbook action → independently confirmed lead → independently verified sale/net revenue. Obstructed touch actions are a testable barrier to lead capture. **No subscriptions, paid orders or revenue were verified** by this work. No changes to the published page, checkout, Jetpack, merchant links or tracking.

**Outstanding independent gates:** genuine isolated WordPress Playground + Assembler import, real archival-image response bytes and hashes, axe WCAG 2.2 AA, keyboard/touch/no-JS tests, Lighthouse/mobile CWV, WordPress.com-hosting differences, Jetpack confirmation, independent CI/QD and founder release authorization. WordPress.com Personal plan has no native staging clone; no paid upgrade proposed.

Owners: homepage engineering and independent Site QA; Claude handles attribution/checkout, Grok/Praxxis the social acquisition and content distribution. No merge/deploy/production writes permitted.
