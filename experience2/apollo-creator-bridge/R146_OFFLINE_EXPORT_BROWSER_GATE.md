# Apollo R146 — Offline-browser acceptance for an actual WordPress export

Status: **BUILT; representative fixture TESTED; real published-page browser acceptance NOT VERIFIED; STAGING HOLD**. Issue #150; conversion coordination #820; charter #818. Isolated from frozen homepage PR #49, Research Desk PR #158, WordPress production and Grok's TASK-008.

## Why

R143–R145 identified the real published Apollo Atlas gallery's selector defect. The live source still has `const photos = $(box, '[data-fvx-chrono-photo]');`, producing a single Element rather than three figures. R145 prepares a one-character repaired, **read-only local preview** with an SHA-256 receipt. Earlier Chromium navigation to live HTTP/file/data URLs returned `ERR_BLOCKED_BY_ADMINISTRATOR`, which blocked real-page acceptance.

R146 makes meaningful progress without bypassing that policy. Its real Chromium runner accepts a **caller-supplied actual WordPress HTML export** and injects the contents into a blank browser via `page.set_content`, with all network requests blocked. It does not navigate to WordPress or activate any service. Run it on the R145 repaired export, not on a synthetic page, to produce actual-export **offline** evidence; do not call that live-page acceptance.

## Command and output

```sh
node experience2/apollo-creator-bridge/r145_review_preview_cli.cjs --input /read-only/wp-atlas-export.html --out /tmp/fv-r145-preview
python experience2/apollo-creator-bridge/r146_offline_browser_acceptance.py --input /tmp/fv-r145-preview/apollo-r145-local-review.html --out /tmp/fv-r146-browser
# Optional local axe script, reviewed and already installed:
#   --axe-js /path/to/axe.min.js
```

Requires Python Playwright and a Chromium binary (`FV_CHROMIUM=/path/to/chromium` when different from `/usr/bin/chromium`). No pip install, network fetch, browser vendor, analytics, or CMS write occurs in the runner. Outputs go in an exclusively new directory, never an existing output location. Reusing an output path fails rather than clobbering evidence or inputs.

Checks at 320, 360, 390, 768, 1440 and 1920px: three figures, a real range input, four chronology positions (0, 6, 11.3, 14.7), exactly one active gallery figure with correct archived-context distinction, absence of page runtime errors and horizontal overflow, keyboard ArrowLeft slider operation, touch at 390px, reduced-motion viewport at 768px, visible contextual disclaimer and screenshots. At 390px with JavaScript disabled it confirms all three records and NASA original-source links remain readable alongside the ordinary **Read the full investigation** anchor. An optional **local** axe-core artifact runs selected WCAG 2.2 AA tags; without it, axe is explicitly `NOT_EXECUTED`.

Screenshot SHA-256 digests and source SHA-256 are recorded. Blocking image/font requests means the PNGs may show broken image placeholders, so they **cannot certify commercial media rendering or visual page quality**. Browser timing in this offline document cannot establish production LCP/CLS or field p75 Core Web Vitals; those explicitly remain unmeasured. No actual social asset, merchant product, signup or order is demonstrated by this runner.

## Test evidence — local representative fixture, not actual website

Python Playwright using real Chromium (headless, network disabled), with `r146_synthetic_fixture.html`: **64/64 checks PASS** on six viewport widths + 390px no-JavaScript. Separate input with the unrepaired selector: **SOURCE_FAIL** (no screenshots generated). Two consecutive runs yielded identical reports and seven identical PNG SHA-256 hashes. This confirms reproducibility **for this fixture/environment only**; it does not prove the real published Apollo page passes. Runner source was also native Python syntax-checked locally. The source-controlled Python file should be independently executed at its exact Git head before production sign-off.

## Current actual-page evidence and blocked acceptance

Read-only WordPress page 2017, last modified **2026-11-04T17:09:24**, still includes the incorrect selector, verified again 2026-11-05. Three archival contextual photographs are present with NASA source links. They are *not* evidence of the seconds shown on the chronology. No photograph-specific commercial product reuse permission is established. No actual-export Playwright screenshots, axe scan or CWV values have yet been produced in this sprint. Acquire an export via the existing authorized WordPress read lane; do not store an unrestricted published snapshot in this PR.

**Release hold:** actual-export offline QA; unrestricted staging browser and axe/performance; asset transport & alt-text manual review; NASA image-specific commercial/endorsement review; WordPress/Assembler integration; editorial and QD reviews; exact-head CI; founder authorization; Claude production engineering. Nothing merged or installed.

## Conversion contract

Proposed source-backed Grok Apollo long-form/Shorts (publication and asset IDs **UNVERIFIED**) → verified published Atlas permalink → existing single **Read the full investigation** action → *hypothesized* classroom-ready teacher dossier only when separately verified rights, SKU, fulfillment and founder approval exist → independently confirmed paid order less fees and refunds. No unreviewed purchase CTA was added. Track qualified-human sessions and confirmed purchases in Issue #820's 7/30-day framework; a link click or screenshot is **not revenue**.
