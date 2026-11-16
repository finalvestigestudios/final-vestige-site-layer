# Apollo Experience 2.0 R396 — exact-record staging custody

**BUILT and locally TESTED; not installed on WordPress; not LIVE; no sales VERIFIED.** The R396 candidate is a **separate, default-off staging loader**; it does not edit, replace, activate or auto-merge R395 or any previous branch. Parent R395 draft PR #2683. Frozen homepage PR #49, separate Research Desk PR #158 and Grok/Praxxis TASK-008 are untouched.

## Reproduced QA defect and correction

The R395 WordPress stub test returned a single fake `01-ground-test` record and still passed its `fv_r384_records() !== false` prepaint eligibility test. This is **a weakness in the R395 acceptance guard and stub**, not proof that the actual R384 canonical function has been compromised. R384 separately checks six records and its R377/R381 custodians. R396 independently compares **every gallery-visible field of all six records** against the exact SHA-256-pinned R377 `custody.json`, refuses missing, reordered, substituted, truncated or misleading records, and separately pins both reviewed CSS files. Five questions must cite the original 1967 Apollo 204 Review Board report; the sixth cites the later 2018 NASA historical retrospective. No new NASA media, commercial offer, map pins, tracking, scripts or claims are introduced.

The proposed deployment path is `staging-custody.php`, a **standalone** loader for a future explicitly approved staging install. Required guards: `FV_R396_APOLLO_QA_ENABLE === true`, actual WP environment `staging`, exact `apollo-1-evidence-atlas` slug, real R384 custody function returning the six reviewed records, the pinned ledger and pinned R384/R395 CSS bytes. It enqueues only the existing approved CSS handles (base then mobile-fit); default off. **Do not enable R395 and R396 loaders simultaneously** until a staging integration test proves no duplicate or conflicting enqueues; prefer R396 alone after approval. No WordPress content or settings writes.

## Actual local QA

From an isolated checkout stacked on R395, with PHP, Python Playwright and Chromium installed:

```sh
php -l experience2/apollo-r396/staging-custody.php
php experience2/apollo-r396/qa/php_contract.php
php -d auto_prepend_file="$PWD/experience2/apollo-r396/qa/enable.php" experience2/apollo-r396/qa/php_contract.php
python experience2/apollo-r396/qa/browser.py
python experience2/apollo-r396/qa/package.py
```

- `php_contract.php` executes real PHP with **WordPress stubs**, not WordPress itself. It checks default-off behavior, explicit opt-in, production/wrong-page refusal, exact two-asset dependencies, six-record ledger integrity, changed fields, misclassified 2018 source, and misleading ignition certainty.
- `browser.py` executes Chromium + Playwright on a **PHP-rendered static fixture**, 13 contexts at widths 320–1920px, keyboard and touch native drawers, no-JS, reduced motion, forced colors, 400% root-font stress, print CSS visibility, in-page source navigation and one free CTA. It invokes inherited R393/394 source topology and visibility inspectors. Captures screenshots, fixture-only LCP and CLS (not real Core Web Vitals). `page.set_content()` does **not** prove actual HTTP, CSS waterfall, CSP or WordPress staging behavior.
- The deterministic QA archive has fixed timestamps, sorted entries and per-file SHA-256 manifest. It is not an approved deployable plugin package.
- Genuine axe-core, independent VoiceOver/NVDA, native browser zoom, installed Assembler/WordPress, HTTP/CSP redirect and stylesheet bytes, exact-head hosted CI, QD/founder signoff remain **NOT TESTED**.

## NASA sources, rights and conversion hypothesis

- NASA original 1967 report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- NASA later 2018 account: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/
- NASA media guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/

The Review Board did not conclusively identify a unique ignition spark. Later deliberately ignited tests are not evidence that 102 ignitions occurred during the original event. This component contains **no reproduced NASA images/logos** and implies no NASA endorsement.

**Single intent pathway:** Grok-owned Apollo long-form film (publication and asset ID not yet independently confirmed) → evidence-provenance gallery → existing free [Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → only then a *potential*, independently approved rights-cleared educator evidence kit. Never display a paid CTA for an unverified SKU.

| Offer | Funnel step | Blocker | Change / experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Apollo educator dossier (hypothesis) | qualified reader → paid purchase | No payable rights-cleared SKU, verified delivery, checkout, refunds | Verify product and offer *before* any purchase CTA | HOLD / no attributed paid order | Founder / Claude Commerce |
| Grok Apollo documentary | asset_id/utm_campaign → qualified human landing | Publication, placement, UTMs and bot-filtered sessions unverified | Approved single-asset attribution test, no duplicate scripts | NOT OBSERVABLE | Grok / Praxxis / Claude |
| Apollo evidence gallery | source trust → free investigation | Acceptance guard could be satisfied by one fake record in R395 PHP stub | R396 exact-ledger six-record gate; browser QA | LOCAL PASS; installed staging PENDING | Apollo QA / QD |
| Paid order / affiliate settlement | settlement minus refunds, fees | No confirmed merchant orders or qualified 7/30-day cohorts | Consent-respecting #820 scorecard | Net revenue/1000 qualified sessions NOT COMPUTABLE | Claude / Commerce |

**RELEASE: HARD HOLD.** No merges, WordPress changes, social posts, emails, affiliate activation, new tracking or spending. Coordinate in Issues #150 and #820, charter #818. The independently approved Research Desk and homepage lanes remain untouched.
