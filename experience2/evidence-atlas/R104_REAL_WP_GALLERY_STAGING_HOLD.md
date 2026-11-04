# Apollo R104 — genuine private WordPress Source Gallery interaction acceptance

**Status: STAGING HOLD / zero production changes.** Issue #150; stacked on draft R103 PR #859 (not homepage PR #49 or Research Desk PR #158).

## Purpose

R103 added mobile scrolling and native fragment jumps to two-source comparison. R103's dedicated Chromium test used `page.set_content`; the inherited genuine WordPress test exercised 70 responsive configurations plus R102 interactions but did not directly verify the R103 horizontal-scroll, jump, or reset behaviors through actual WordPress HTTP. R104 closes this evidence gap *without modifying the public research data or deployment*.

## Implementation

- `tests/browser_real_wp_gallery_r104.py` opens seven-view R99/R103 private-plugin gallery through real WordPress `template_redirect` and authenticated administrator session; URL is **hard-restricted** to `http://127.0.0.1:8955/` or `http://localhost:8955/`.
- Exercises 320, 390, 768, 1440 and 1920px with JavaScript on/off, touch on mobile, reduced motion, forced colors at 320, 6 NASA custody anchors, private cache/robots/CSP headers, absence of photos and map data, 6 complete no-JS cards, and document overflow.
- With JS: selects two actual records; checks both custody columns, all six enhanced native comparison links, #comparison URL fragment navigation, touch interaction, keyboard-scrollable horizontal comparison, a prohibited third selection with an announcement, reset and focus return. All normal test contexts enforce delivered CSP.
- At 390 and 1440px, separately runs axe-core on a **selected comparison state** using a diagnostic-only CSP bypass to load axe; does not change shipped CSP.
- Records six fresh-navigation LCP/CLS laboratory samples (3 at 390px, 3 at 1440px), retaining unchanged LCP <=2500ms and CLS <=0.1 test budgets. These are disposable WordPress-core laboratory metrics, **not** hosted WordPress.com, Assembler, or field Core Web Vitals. Samples distinguish variance instead of quietly accepting a single retry.
- Writes checksum-receipted 320/390/1440 screenshots, a 390 no-JS screenshot, and a printed research PDF that must preserve original NASA identifiers and six rights holds. Tests do not download any NASA photos.
- Extends existing `.github/workflows/ex2-apollo-r103-actual-wordpress.yml` to exercise R104 against its already-created genuine disposable WordPress installation. No duplicated WordPress provisioning job or additional paid service.

## Inputs and historical boundaries

Derived from the exact R103 branch of draft PR #859, which itself is stacked on R102 through the R99 SHA-pinned plugin. R103 sealed receipt remains authoritative for the private package; R104 adds QA code and workflow only and does **not** change pinned review HTML, CSS, JS, PHP, source rights, NASA claims or custody hashes.

Research content remains six sourced NASA records / **zero photographs cleared** / zero photographs embedded / zero geolocated pins / zero invented edges. Proposed portrait association `S67-19766` and day remain provisional. A source URL is not a license.

## Acceptance and release gates

Do not claim pass until the exact-head GitHub Actions job completes and its artifact includes `R104_REAL_WP_GALLERY_QA.json`, screenshot hashes, PDF hash, 10 interaction cases, 2 zero-violation axe scans, and six recorded LCP/CLS samples. If any threshold fails, retain the failure as a finding and do not relax the gate.

The new tests do not replace independent author/editor/anonymous security verification, hosted WordPress.com + actual Assembler tests, manual NVDA/VoiceOver + physical-device/zoom, historical/editorial/rights review, field CWV, QD review or founder publishing approval.

**No merge, publish, install to hosted CMS, WordPress content/settings writes, homepage edits, NASA photo embeds, speculative geography, or paid services authorized.**
