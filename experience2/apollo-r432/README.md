# R432 — Apollo source-custody and rights gate (STAGING ONLY)

**Related**: [Apollo charter #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion measurement #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Stack on R431. This directory does **not** edit homepage PR #49, Research Desk PR #158, Grok's task queue, WordPress content or the commercial checkout.

## New enforcement / actual component

R431 checked the immediate R430 PHP/CSS, but did not pin its **own JavaScript or CSS**; a modified archive script could therefore be served with a previously passing parent-PHP check. R432 closes this custody gap by verifying **seven** exact historical component dependencies **before rendering/enqueueing any of them**: two from R429 (PHP/CSS), two from R430 (PHP/CSS), and three from R431 (PHP/CSS/JS). Traversed symlinks, absent and altered files fail closed to the unchanged free article. No source file is overwritten.

The stage-only shortcode is `[fv_apollo_custody_gate_r432]`. It activates only if `FV_R432_ENABLED === true`, `FV_R432_STAGING_PAGE_ID` is a positive integer and exactly matches a singular page, and `wp_get_environment_type() === 'staging'`. Neither constant is set here. The component preserves **three dated evidence plates, three educator questions, three source-linked notes, one contextual free-article CTA per instance**, with distinct IDs across reusable instances. The new native `details` disclosure links the Review Board and NASA's media-use rules, explicitly separates evidence from permission to commercialize imagery, and states that NASA does not endorse the publisher. No copied media, logo, invented Atlas pins, purchase links, cookies, forms, submissions or tracking.

**Historian/source checks:** Apollo 204 Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; NASA media/rights conditions: https://www.nasa.gov/nasa-brand-center/images-and-media/ . The Board did not conclusively identify a single ignition source. NASA makes many materials available for factual/editorial use, but names, images, identifiers and third-party rights may have additional commercial restrictions; an official archive link is **not** resale permission.

## Reproduce the actual tests

From a checkout containing the stacked R429–R432 directories:

```bash
php -l experience2/apollo-r432/staging-custody-gate.php
python experience2/apollo-r432/qa/test_contract.py
python experience2/apollo-r432/qa/browser_qa.py
python experience2/apollo-r432/qa/package_evidence.py
```

Local Chromium QA loads **real PHP-generated markup** using `page.set_content`, not a WordPress installation. It checks 320, 360, 390, 768, 1024, 1440, 1920 widths, double instances, IDs, documentary dates, consent-free UTM continuity, keyboard and touch disclosure, JS disabled, reduced motion, forced colors, 200% text at 320, print and real browser `.txt` export. The contract tests mutate *temporary clones* of every pinned source and verify deliberate fail-closed behavior. Screenshots, fixture, browser/contract JSON and reproducible deterministic ZIP live in local `QA/` and are not deployment artifacts.

The separate **installed WordPress staging** test can pass only after the founder supplies an approved HTTPS staging hostname and reviewed SHA-256-pinned `axe-core` JavaScript. It uses actual `page.goto` and browser-navigation LCP/CLS, checks no overflow and one real CTA, and fails rather than substituting local HTML. Example:

```bash
python experience2/apollo-r432/qa/staging_acceptance.py \
 --staging-url https://APPROVED-STAGING-HOST/APPROVED-PAGE \
 --approved-host APPROVED-STAGING-HOST \
 --axe-js /path/to/reviewed/axe.min.js --axe-sha256 EXACT_64_HEX \
 --out /tmp/apollo-r432-staging-evidence
```

Local runtime HTTP navigation reported `ERR_BLOCKED_BY_ADMINISTRATOR`, and an approved axe bundle/staging site is not present. **No installed staging, axe, navigated LCP/CLS, field p75, screen-reader certification, or paid conversion claim is made.** Previous R417 four-file reconciliation and QD/CI exact-head review remain separate blockers.

## Strict conversion-first handoff

| Offer | Step | Blocker | Experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Original rights-cleared Apollo educator dossier (candidate, **not verified payable**) | Paid order | SKU/license/checkout/fulfillment unverified | Do not display commercial CTA; validate merchant and rights first | HOLD; no sale | Founder + Claude |
| Grok-approved Apollo film (not proved published) | Qualified audience → landing | asset_id, link inventory, confirmed human sessions missing | Approved `utm_content` only; R429 preserves known, validated tags | Offline link QA only | Grok + Praxxis + Claude |
| Source-backed Evidence Notebook | Research Desk → original free investigation | Broken custody destroys trust | Verify seven parent objects, safely fall back | Contract and offline browser QA | Apollo owner / independent QD |
| Authenticated paid orders | Realized net revenue / 1,000 qualified humans | No merchant sales, refunds/fees or human denominator | Native data reconciliation; 7/30-day cohorts | NOT COMPUTABLE | Claude / commerce |

Never equate outbound click, optional notes export or apparent UTM with a purchase. No commercial offers are inserted into the historic narrative. Nothing in this work authorizes a merge, deployment, new measurement script, posting, email or spending.
