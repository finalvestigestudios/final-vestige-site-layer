# R427 · Reviewed-source custody integration — STAGING ONLY

This is a deliberately small integration layer, **not** another authored copy of NASA evidence or a replacement for the flagship / Research Desk / WordPress. It loads the **actual byte-verified R426 component** and stylesheet from a separately reviewed checkout, adds a clearly differentiated custody banner, and preserves exactly one free-investigation CTA *per instance* from the original. All six EvidencePlates, their six native SourceDrawers, chronology rail, NASA records and original source boundaries come from R426 itself. This prevents the otherwise common failure of testing an unrelated synthetic fixture and calling it integration acceptance.

## Activation and source custody

Not installed or enabled by this PR. Following founder and QD approval *on staging only*, explicitly define `FV_R427_ENABLED=true`, `FV_R427_STAGING_PAGE_ID=<integer approved staging page ID>`, and `FV_R427_UPSTREAM_ROOT=<absolute local path to independently reviewed R426 directory>`. Invocation: `[fv_apollo_source_chain_r427]`. WordPress must report `wp_get_environment_type() === 'staging'`, `is_singular()`, and exact page ID. Default output is a safe link to the existing free investigation. No live WordPress settings, content, cache or user data are modified. Do not activate alongside an already loaded unknown version of `fv_r426_render` (the adapter deliberately rejects ambiguous ownership).

Pinned Git blobs at R426 commit `ef58ae3ab68ff7b3e319ee23f65636b45e9cfa43`:

- `staging-source-comparison.php`: `36ecba01c84d13bf2546d0bd650e9f95ac50d7d9`
- `assets/source-comparison.css`: `e76decc769e811a59f71c1cf459478d747676eb3`

The **only executable dependencies** are these reviewed files. Any missing, changed or symlinked file leads to the safe fallback, not partial evidence. External photo catalogue records are outbound NASA links, **not reused media**. Rights to reuse the actual photo bytes are not asserted. No speculative geo pins/edges, NASA endorsement, analytics scripts, paid CTA, forms or remote calls.

## Reproducible local testing

From `/mnt/data/apollo_r427/` (or equivalent) materialize R426 at `checkout_r426/experience2/apollo-r426/`. The checkout must contain exactly the reviewed source bytes, fetched independently from GitHub if necessary. Run `php -l .../staging-source-chain.php`, `python -m pytest -q experience2/apollo-r427/qa/test_contract.py`, and `python experience2/apollo-r427/qa/browser_qa.py` with `/usr/bin/chromium`. The test fixture renders **real pinned R426 PHP output**, not a substitute six-card mock. Browser screenshots cover 320–1920px and keyboard, touch, disabled JavaScript, reduced motion, forced colors and print. It is still offline `page.set_content`, not a genuine URL navigation or installed WordPress environment.

## Explicit release HOLD

No real WordPress staging installation, HTTP navigation (sandbox browser blocks `page.goto`), NASA asset delivery, independent screen-reader testing, genuine axe-core, navigated LCP/CLS, INP/p75 CWV, exact-head hosted CI or QD approval. The separate R417 four-file source/archive discrepancy remains unresolved. None are converted into passing results by this integration. **Do not merge or deploy.**

## Offer-to-revenue hypothesis

High-intent history educator arriving from a Grok-approved Apollo long-form asset (immutable `asset_id`, tagged platform UTMs once approved) → evidence-first R427 comparison / source custody → **one original free Apollo investigation link** → separately approved rights-cleared educator casefile product *only after* verified sellable SKU, checkout and fulfillment. This commit provides no merchant integration. CTA clicks, signups or pageviews are **not paid orders**. Commercial KPI `1000 * verified net revenue / qualified human sessions` remains **not computable** without permissioned campaign attribution, merchant-confirmed paid order settlements/refunds/fees and 7/30-day cohorts. Grok owns creative/distribution, Praxxis external review, Claude engineering/analytics, Founder release and spending approvals.

NASA source reports: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ ; media guidance https://www.nasa.gov/nasa-brand-center/images-and-media/ . [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Homepage frozen PR #49, original Research Desk PR #158 and Grok/Praxxis TASK-008 unchanged.
