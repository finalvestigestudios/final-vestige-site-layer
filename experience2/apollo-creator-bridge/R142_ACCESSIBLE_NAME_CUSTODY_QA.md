# Apollo R142 — Accessible-name and raw-text custody (isolated staging)

**Governance:** Experience 2.0 issue #150, conversion issue #820 and founder charter #818. **Release: STAGING_HOLD.** Stacked only on R141 draft PR #1099. Do not change homepage PR #49, Research Desk PR #158, Grok's queue, WordPress, merchant, analytics, or production settings.

## Reproduced source-gate defects

The R141 Node validator returned SOURCE_LINK_CONTINUITY_ONLY for five invalid primary CTA source patterns before this patch:

1. Anchor whose only label was hidden from assistive technology in an aria-hidden descendant.
2. Anchor whose only label was in an HTML hidden descendant.
3. Anchor containing a nondecorative image alt text that changes its computed accessible name.
4. Fake anchor written inside a textarea element (parsed as text by browsers).
5. Fake anchor written inside title content.

R142 closes those false positives. It also conservatively blocks accessibility-name ambiguity from labelled descendants, SVG, ambiguous images, aria-labelledby, role changes, form-option containers, collapsed details and unclosed/ambiguous HTML. HTML-only source gates cannot resolve external CSS, JavaScript mutation, redirects, rendered accessible names or actual focus order; these require browser acceptance. The link remains a provisional source finding, never an accessibility certification.

## Implementation and regression

- Modified the R141 custody parser in the R142-only branch, not in R141's existing PR.
- Added test_r142_accessible_name_gate.cjs with adversarial and benign source tests; retained all R141 regression coverage.
- Added r142_browser_fixtures.py: real Chromium, offline synthetic HTML fixtures using Playwright page.set_content (not remote navigation). Six no-JavaScript responsive widths (320/360/390/768/1440/1920) test keyboard Tab focus, >=2px focus ring, reduced motion, no overflow and screenshots. Six adversarial DOM cases test accessible reader role/name. Emits screenshot checksums and a JSON receipt.
- Local reproduction: **49/49** native Node tests across R141+R142, **12/12** Chromium synthetic DOM fixtures. These are local results, not actual-page or hosted CI qualification.
- Reader CTA destination remains the actual published Atlas-to-investigation URL. No worksheet fragment, unverified product link, NASA imagery, map pins, sales/UTM tracking or extra CTA added.

## Reproduce

Run on a checkout of this branch:

    node --test experience2/apollo-creator-bridge/test_r141_dom_custody_gate.cjs experience2/apollo-creator-bridge/test_r142_accessible_name_gate.cjs

    python experience2/apollo-creator-bridge/r142_browser_fixtures.py --out /tmp/apollo-r142-fixtures

Browser runner requires Python Playwright and Chromium and emits only fixture screenshots. No site network access required.

## Conversion bridge and owner gates

**Audience hypothesis:** middle-school social-studies educators consuming Grok's Apollo 1 long-form/Shorts (published creator asset URL and asset_id remain unverified).

**Published Atlas:** https://finalvestige.com/apollo-1-evidence-atlas/ . **Single existing relevant action:** Read the full investigation -> https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . This is evidence reading, not a paid sale or confirmed lead.

**Commercial offer hypothesis:** rights-cleared Apollo educator dossier — NOT CURRENTLY VERIFIED AS SALEABLE. No merchant SKU, Payhip ownership, price, terms, licensed media, refund handling, purchaser or order is verified. Do not add checkout CTA before Claude/Growth independently verifies a currently saleable offer and founder approves. No unrelated commerce in historical narrative.

**Measurement:** Grok supplies real asset_id/UTM per TASK-008; Claude/Growth validates qualified human sessions -> CTA -> approved offer -> merchant-confirmed paid orders -> net after fees/refunds, with 7/30 day cohorts and small-sample warnings. Do not infer sales from clicks or introduce duplicate analytics scripts.

## Remaining blockers / release decision

- Actual Apollo/WordPress-stage 320–1920 Playwright navigation, axe-core, LCP/CLS, real-page screenshots, computed accessible names, keyboard/screen-reader/touch and WCAG 2.2 AA: NOT COMPLETED (prior Chromium navigation returned ERR_BLOCKED_BY_ADMINISTRATOR).
- Individual NASA photographs, commercial-use/likeness/endorsement assessment, provenance custody: NOT APPROVED. NASA source URLs are not reuse certificates.
- WordPress/Assembler shortcode lifecycle and HTML parity: NOT TESTED.
- Exact-head hosted CI and independent QD: NOT VERIFIED.
- Matched rights-cleared sellable product, published Grok asset, qualified sessions and revenue: NOT VERIFIED.
- Founder production-release approval: NOT GIVEN.

**No WordPress edits, merges, deployment, social posting, emails, tracking, merchant writes or spending.**
