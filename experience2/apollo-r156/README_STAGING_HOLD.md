# Apollo R156 — Source provenance repair + exact-review Chromium QA (STAGING HOLD)

Independent implementation for Issues #150, #820 and charter #818. Built on R155 without editing PR #158, frozen homepage PR #49, any active Claude branch, WordPress, social accounts or merchant settings.

## Source integrity repair

The original six-record Research Desk pairs real NASA archive photo URLs with technical findings, sometimes implying the photographs prove pressure, ignition or instrumentation. This review copy:
- Removes an unsupported claim that NASA's linked crew portrait displays catalog ID S67-19766.
- Distinguishes **contextual NASA image** links from **NASA evidence-document** links in every record.
- Provides six plain-HTML source custody notes describing the pictured event/date and exactly what the image does **not** establish.
- Explicitly identifies the October 18, 1966 altitude training photo as distinct from the January 27, 1967 fire chronology and the January 24, 2017 museum photos as retrospective.
- Preserves six findings, six limitations, twelve NASA links, all native details expanders, and the single existing "Read original investigation" CTA. No new pins, speculative sources, checkout links or image hosting.
- Provides a machine-readable provenance/rights manifest and accessibility styling for touch, high-contrast and reduced-motion settings.

Exact original PR #158 HTML Git blob: `403d128c57b9bc82dac7c619651689070edef86c`.
Exact staged corrected HTML Git blob: `47424544ce344a3a1a364dfd27a78675c33935a5`.
Corrected HTML SHA-256: `7aea496f2a88a7d1eec8bb12e0161d6b34fdfe1797822f6fda333463a7f85ee4`.
Original PR158 CSS and R153 compatibility JS/CSS reused unchanged for testing.

NASA primary support: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
Individual image URLs and exact dates: see `provenance_manifest.json`.
NASA advertising/rights guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ .
**Rights gate**: No NASA photographs cleared for FV commercial promotion or paid-product packaging. No NASA endorsement implied.

## Read-only reproduction

From the repository root after checking out this branch (Python Playwright + local Chromium; no external navigation):

```bash
python experience2/apollo-r156/test_reviewed_source_browser.py \
 --source experience2/apollo-r156/ledger_source_custody_review.html \
 --original experience2/research-desk/templates/ledger.html \
 --css experience2/apollo-r156/source_custody_review.css \
 --orig-css experience2/research-desk/assets/source-ledger.css \
 --compat-css experience2/apollo-r154/r153_source_ledger_compat.css \
 --compat-js experience2/apollo-r154/r153_source_ledger_compat.js \
 --out /tmp/fv-apollo-r156-qa-1
```

Repeat with a new output path and compare the `SHA256SUMS` files. To run a WCAG audit, supply a locally reviewed version of axe-core with `--axe /path/to/axe.min.js`. No externally loaded runtime scripts or duplicate analytics are used.

## Test scope and evidence

- Local **independent broader test** of this exact corrected HTML SHA-256: **162/162 real Chromium checks PASS**, 320/360/390/768/1440/1920 pixels, with JavaScript-disabled content, search/reset, keyboard Escape/focus, external fragment, touch, reduced motion, source custody and horizontal-overflow checks. Two runs yielded identical six PNG SHA-256s. That broader local runner is supplied in the R156 evidence bundle; it is not the same file as this shorter source-controlled smoke runner.
- Source-controlled runner: **COMMITTED; exact-head execution pending**. Do not present the 162 broader assertions as results of the committed smoke runner.
- Native adversarial local build checks: **12/12 PASS** (separate supporting evidence; generated review original confirmed by source blob).
- **axe-core NOT EXECUTED**: locally reviewed axe script unavailable; Chromium AX inspection in R155 does not replace axe.
- **Actual WordPress staging/Assembler/Jetpack/caching NOT TESTED**; **production LCP/CLS/INP NOT MEASURED**; hosted CI and manual screen-reader acceptance pending.
- Zero purchase, qualified Grok session or realized Apollo revenue claims. The educator casefile is a demand hypothesis, not a verified Payhip product.

## Conversion-first release table

| Offer -> funnel step | Blocker | Proposed change | Test evidence | Owner |
| --- | --- | --- | --- | --- |
| Classroom evidence dossier -> paid purchase | No verified rights-cleared sellable SKU, functioning checkout or post-refund net | Audit existing Payhip products, rights, fulfillment | NOT VERIFIED | Claude/Growth + founder |
| Grok historical long-form -> Research Desk | Apollo asset ID / published URL / qualified UTM traffic unverified | Preserve creator attribution contract; coordinate TASK-008 | NO CONFIRMED ATTRIBUTION | Grok/Praxxis/Claude |
| Research Desk -> evidence trust -> investigation | Photo misrepresented as proof | R156 six source-custody notes and correction | BUILT; exact-html offline Chromium 162/162 | Apollo |
| Investigation -> contextual next action | No approved matching offer | Keep existing investigation CTA only | BUILT; browser source reviewed | Apollo/Claude |
| Confirmed orders -> realized revenue/1000 qualified sessions | No merchant-confirmed order/refund/fees, human-session denominator | Apply #820 seven/thirty-day cohorts; do not treat clicks or signups as sales | NOT COMPUTABLE | Claude/Analytics |

## Release decision

**STAGING HOLD; unmerged draft only.** Before release: editorial NASA provenance approval, photograph-specific rights review where used in products, WordPress staging integration including shortcode asset lifecycle, real axe-core + manual accessibility, visual QA with site fonts/image delivery, real network performance and CI on exact head, QD review and founder authorization. Never merge or deploy from this document.
