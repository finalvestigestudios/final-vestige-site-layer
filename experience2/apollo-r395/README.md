# Apollo Experience 2.0 / R395 — opt-in STAGING prepaint and 400%-text CSS acceptance

**DRAFT. No WordPress installation, production activation, settings/post write, paid service, merge or deployment.** Separate from frozen homepage PR #49, Research Desk PR #158 and Grok/Praxxis TASK-008. Stack only on R394. Coordination: #150, #820, charter #818.

## Why

R394 reproduced **8px of horizontal overflow** at 320px with root font at 400%, and prepared a visually acceptable CSS correction. That candidate was applied *after* rendering in its fixture, and R394 also observed **0.16 cumulative layout shift in a synthetic late-stylesheet test**. The corrected CSS must be ordered in the document's first CSS render, not injected after initial paint. It must also be available when gallery shortcode content is nested in a reusable WordPress block, where R384's original conditional stylesheet enqueue may miss the shortcode.

R395 does not change the approved R384 base stylesheet, edit R384 code or enable staging automatically. Instead, it makes the R394 candidate a SHA-pinned, separately enqueued **screen-only, pre-head staging stylesheet**, guarded by all conditions below. It can be reviewed and installed explicitly in an **approved staging build** after QD authorization.

## Implementation and safety contract

- `staging-prepaint.php`: *standalone, unactivated source* for an opt-in staging WordPress loader. Requires `FV_R395_APOLLO_QA_ENABLE === true`, `wp_get_environment_type() === 'staging'`, the exact `apollo-1-evidence-atlas` page, existing R384 source-custody approval, reviewed R384 CSS SHA-256 and reviewed R395 CSS SHA-256. Any guard failing -> enqueue nothing. Registers no shortcodes, event handlers, metrics, URLs or data writes.
- `assets/mobile-fit.css`: byte-for-byte R394 corrective CSS candidate; same SHA. Readability/width changes only. No font-size reduction, hidden source content, invented map or tracking.
- Original R384 handle is reused and R395 style depends on it. `wp_enqueue_scripts` priority **99** means both styles are queued before WordPress `wp_head` (assuming the standard WP lifecycle). Installed staging must verify actual order; do not claim browser HTTP/CSP delivery from local stubs.
- No other hostname or page is approved, including production. Enabling the constant alone on production must never allow CSS to load, and no code in this PR sets the flag.

## What passed in this run

- PHP 4/4 default-disabled + 16/16 explicitly opted-in staging-stub assertions; PHP lint clean. Correct source checksums, original stylesheet handle/dependency, wrong environment/page, source custody unavailable, missing/mismatched CSS all tested. **These are WP function stubs, not installed WordPress tests.**
- Chromium/Playwright **136/136** local fixture assertions across **11 contexts, width 320–1920px**, including no-JS, touch, Enter-operated native disclosures, reduced-motion, forced colors and 400% root font at 320 and 390. Zero horizontal overflow in all 11. The precise R393 PHP-generated fixture, R392/393/394 source-custody validators and exact R384 CSS hash were reused.
- Local parser-initial styles reported **CLS 0 in all 10 JS contexts**; observed fixture LCP **72–152ms** (no-JS LCP not observed). The independent late-style comparison reproduced 8px -> 0px overflow but **did not reproduce the prior 0.16 CLS** in this run (late CLS 0). This supports only the local test, **not any production LCP/CLS or assertion that staging CSS is delivered before paint**.
- Four reproducible screenshots: standard mobile, desktop, no-JS, and 400%-text mobile. ZIP with a fixed timestamp and stable input ordering; per-file SHA-256 manifest; byte-identical double build.
- Genuine reviewed axe-core, hosted CI on exact PR head, independent NVDA/VoiceOver, native browser zoom (root font scaling ≠ native 400% zoom), actual HTTPS/CSP, installed Assembler/WordPress and merchant/lead attribution were **NOT TESTED**.

## Reproduce from stacked checkout

```sh
php -l experience2/apollo-r395/staging-prepaint.php
php experience2/apollo-r395/qa/php_contract.php
php -d auto_prepend_file="$PWD/experience2/apollo-r395/qa/enable.php" experience2/apollo-r395/qa/php_contract.php
python experience2/apollo-r395/qa/browser.py
python experience2/apollo-r395/qa/package.py
```

`qa/browser.py` requires local Playwright with installed Chromium (`/usr/bin/chromium` in this run) and the immutable R384/R377/R393/R394 fixtures/files in the stacked checkout. It uses `page.set_content`, not actual HTTP navigation; the latter is blocked in the execution environment. All hashes are validated before browser test execution.

The loader source is not sufficient to claim WordPress integration. A separate QD-approved staging review must preserve the expected relative R384/R395 install paths and explicitly enable the flag only there, verify real HTTP stylesheet hashes and source custody, cache/Assembler/shortcode lifecycle, redirects, browser CSP, network guard, genuine axe, screen readers, print, native zoom, and exact-HEAD CI; independently approve any rollout. **PRODUCTION HARD HOLD**.

## Evidence and rights

There are **six documentary questions but only two NASA-hosted underlying publications**. Primary 1967 Apollo 204 Review Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA's February 14, 2018 historical retrospective of deliberate testing *after* the 1967 tragedy: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ . NASA media/use guidance: https://www.nasa.gov/nasa-brand-center/images-and-media/ . This sprint reproduces no NASA photography or logos. No inferred geospatial link or invented Evidence Atlas pin is made. The Review Board did not conclusively establish a unique original ignition initiator; later deliberately ignited tests are never treated as observations of the original fire.

## Conversion-first pathway and release gate

**Single high-intent audience:** history/science educators investigating Apollo 1 with Grok's documentary, if Grok authorizes that topic and publishes with immutable `asset_id` and permitted UTM link placement. **One truthful immediate CTA:** original full *free* [Apollo 1 investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) after inspectable NASA evidence. An Apollo classroom evidence kit is only a **B2B product hypothesis**, not verified as an existing payable, rights-cleared SKU. Do not insert checkout, new email signup, misleading offer or NASA endorsement into this source gallery. Founder/Claude commerce must independently verify one **currently sellable** FV product, licensing, exact checkout, delivered order, fees/refunds *before* an educational product CTA is proposed.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Existing rights-cleared FV product (not yet identified) | human visit -> paid order | seller SKU, checkout/delivery, copyright/returns unknown | Merchant/owner read-only inventory and actual non-spending acceptance test before a price/CTA | **HOLD**, no confirmed paid sale or revenue | Founder / Claude Commerce |
| Grok Apollo long-form (not confirmed published) | `asset_id` + UTM -> qualified landing | exact approved asset, permitted social link and bot-screened sessions unknown | one controlled post-to-Evidence Gallery attribution proposal; no posting/scripts | **UNVERIFIED** visits | Grok / Praxxis / Claude |
| NASA Evidence Gallery | source proof -> free article | narrow-view 400%-text overflow and postpaint CSS risk | R395 pre-head reviewed scoped CSS, keyboard/no-JS checks | **LOCAL PASS**, installed staging unknown | Apollo QA / QD |
| Paid order -> realized net | verified order minus refunds, fees | merchant confirmations and cohorts unavailable | 7/30-day consent-respecting qualified-session cohort design in #820 (no duplicate script) | **NOT COMPUTABLE** net per 1000 qualified humans | Claude Analytics / Commerce |

No email subscriber, affiliate click, checkout start, site view or social impression is called a paid sale. Founder retains release, paid services and posting authority. No project or WordPress production write happened.
