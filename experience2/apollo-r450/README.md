# Apollo R450 — text-only source receipt and educator trust bridge

**DRAFT / NOT LIVE / NOT FOR INSTALLATION.** Parent [Apollo #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), commerce [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), founder charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). This isolated folder is stacked on R449 draft #2974; it makes no changes to homepage PR #49, original Research Desk #158, Claude's production/analytics code, or Grok/Praxxis Drive TASK-008.

## What this adds to the actual R449 prototype

A separate opt-in staging-only shortcode `[fv_apollo_source_receipt_r450]` renders the R449 integrated NASA evidence journey *once*, then a compact `<details>` with a 4-record original source-and-inference receipt. Each citation comes **directly from R448's integrity-pinned manifest**, including the honest publication/event-date distinction and *what the cited source does NOT establish*. One optional browser-triggered plain-text download copies the visible original lesson/source notes to the educator's device. No extra investigation CTA, signup, tracking pixel, data transmission, image, inferred map, paid link, account, payment, license claim or NASA endorsement.

**Staging installation proposal only:** site engineering must independently verify exact inherited paths and plugin-URL resolution. Require existing `FV_R449_ENABLE_STAGING=true`, `FV_R449_STAGING_PAGE_ID=<same integer>` plus `FV_R450_ENABLE_STAGING=true`, `FV_R450_STAGING_PAGE_ID=<same integer>`, an actual nonproduction WordPress `staging` environment, and the matching opt-in page. R450's adapter must be explicitly reviewed/loaded; no code is installed by a GitHub PR. If any source, CSS or JavaScript SHA changes, the component displays **one free fallback article link**, rather than potentially compromised content. This is a conservative integrity gate, not a claim that upstream historical interpretation is approved.

The `<details>` disclosure is keyboard/touch native and works when JS is disabled. Four source cards, limitations, links and rights state are visible upon expansion without scripts. Text export is optional enhancement, not a lead or event. The free investigation remains accessible; an instructor may print without downloading or disclosing personal information. Styling scoped to `.fv-r450`, reduced motion and forced colors handled.

## Execute independently

```bash
php -l experience2/apollo-r450/receipt.php
python experience2/apollo-r450/qa/test_contract.py
python experience2/apollo-r450/qa/browser_qa.py
python experience2/apollo-r450/qa/staging_gate.py  # expected HOLD_NOT_RUN (2) without approved HTTPS origin + reviewed axe
```

Local test: PHP-rendered *actual inherited source* loaded by `page.set_content` into Chromium. **NOT WordPress staging.** SHA source-mutation tests use disposable copies and do not modify parent code. Screenshots and `QA/{CONTRACT,BROWSER}.json` are generated locally. Real browser navigation in this runtime returns `ERR_BLOCKED_BY_ADMINISTRATOR`, even for local data URLs; genuine axe-core, navigated LCP/CLS, field INP/p75, real WordPress asset URLs and independent screen-reader QA were **NOT RUN**. The optional network gate requires a specifically approved HTTPS **staging** origin and independently SHA-pinned genuine axe file, refuses off-origin/non-GET requests, and cannot claim a passed staging result unless all cases run.

## Historic source provenance and commercial limits

- [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): the most probable initiator was an electrical arc; **no single ignition source conclusively identified**. Accident Jan 27, 1967 is distinct from report publication.
- [NASA 2018 flammability retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/): later testing of redesigned spacecraft, not an observed 1967 initial spark.
- [NASA Apollo 1 gallery](https://www.nasa.gov/gallery/apollo-1/): 1966 crew preparation caption, not fire footage.
- [NASA Jan 2017 exhibit announcement](https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/): contemporary memorial, not primary instrumentation; unresolved old R447 photographic catalogue ID is **not** certified by this release.
- [NASA media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/): no borrowed photographs or implied endorsement; license/photo-specific clearance required before commercial repackaging.

**Single conversion hypothesis:** an authentic Grok Apollo long-form video (verified immutable asset_id and permitted mobile destination **not currently available**) → freely readable evidence + original classroom exercise → optional text-only source receipt → **one existing free full investigation CTA** → **future** original teacher-ready paid evidence kit *only after* seller identity, exact SKU, rights, checkout, delivery, payment/refunds and founder approval. The receipt download is neither a lead nor a sale. Net revenue per 1,000 qualified-human sessions is **NOT COMPUTABLE** until Claude/Commerce can document verified human 7/30-day cohorts and merchant settlement less refunds/fees.

**Release blockers:** R417 source reconciliation, published Atlas editorial status, verified photo rights, approved nonproduction staging, genuine axe + screen reader + LCP/CLS/INP, exact-head CI, independent QD, founder product/rights/commercial decision. No WP/site write, merge, deployment, Grok queue edits, social post, email, affiliate activation, new measurement script, merchant change or spending.
