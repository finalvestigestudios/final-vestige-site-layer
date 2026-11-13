# Apollo R329 — independent reader-to-conversion custody gate (STAGING ONLY)

**Scope:** An executable QA addition to Apollo R328, not another analytics implementation. This branch is stacked on the **R328 branch**, never homepage PR #49, Research Desk PR #158, Grok's TASK-008 queue or a production WordPress branch. Do not merge, activate or publish without the founder's release decision.

## Implemented and actually run

`python experience2/apollo-r329/qa/atlas_release_replay.py`

The exact committed test file has Git blob **`e135e902431c71cc1cd44a191bfc54f5613c371a`**, matched to the independently run local source. It requires PHP, Python Playwright, pypdf, Node and system Chromium at `/usr/bin/chromium`.

The test renders the **existing actual Apollo PHP shortcode via the R320 WordPress lifecycle stub**, imports the reviewed R328 CSS and R323 JavaScript, and executes Chromium in an offline `about:blank` fixture. Results: **14/14** real Chromium responsive/no-JS/400%-text cases at **320–1920px**, **6/6** real trusted-activation campaign scenarios, **20/20 total**; a browser-generated PDF was audited across **48 link annotations**, with zero copied campaign identifiers. Checks also preserve three NASA documentary records, four distinct *contextual only* NASA photo records, exactly one editorial continuation, no fabricated geo or merchant destination, and a source-receipt minimum 40px touch area. Reproducible screenshots and JSON receipts are written to `experience2/apollo-r329/QA/` when executed.

A separate *extended* local gate (included in the evidence bundle, not committed to the branch) passed **14 responsive contexts, eight campaign allow/deny cases, two native keyboard chains, one forced-colors touch disclosure, Chromium CDP accessibility-tree naming of 39 expanded controls, and five destructive controls** (merchant diversion, invented pin, false media clearance, false documentary role, and regression to the old CSS overflow). The local test makes no external HTTP requests. Its synthetic `history.replaceState` query emulates only the campaign value in `location.search`—**not actual platform referral or an installed WordPress HTTP/CSP journey**.

### Read-only real destination evidence

Connected WordPress returned **post 434, published**, with slug `the-hatch-opened-inward-apollo-1` and canonical link `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/` on **2026-11-12 PT**. That establishes a *CMS-published destination*, not an independent remote browser fetch, checkout, paid order or real campaign referral. The browser's native loopback HTTP navigation was explicitly tested but returned `ERR_BLOCKED_BY_ADMINISTRATOR`; do not represent this as an HTTP/CSP pass.

## Source-and-rights contract

Three textual claim sources remain [NASA Apollo 1 mission](https://www.nasa.gov/mission/apollo-1/), [Apollo 204 proceedings](https://www.nasa.gov/history/Apollo204/proceed.html), and [Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). The Board's most-probable electrical initiator is *not* a conclusively located ignition point. NASA photo accession pages are source metadata, **not** independent evidence of fire cause or commercial photo clearance. The prior Research Desk PR #158 labels for S67-15717 and S66-58038 require its owner's editorial classification review. Never invent geo pins, archival joins, rights, NASA endorsement or a gallery image licence.

## ONE conversion hypothesis; not a release authorization

**Intended unlaunched path:** Grok-approved Apollo long-form asset (published URL and immutable `asset_id` **unverified**) → NASA-source-linked Apollo Evidence Atlas → one existing **free** investigation → a *separately approved, genuinely payable, rights-cleared* Apollo classroom evidence kit (offer/checkout **not authenticated**). Keep a potential product recommendation outside historical findings, and never add an unaudited merchant link. The only current action is **Read the free Apollo 1 investigation**.

**Hypothesis:** Evidence transparency and a reliable mobile continuation improve *qualified* consideration of an aligned educational offer. This is untested commercially. Grok owns creative, posting and asset IDs; Praxxis reviews creator evidence; Apollo owns staged reader navigation and accessibility QA; Claude owns instrumentation and authenticated merchant flow; the founder owns production and spending authorization.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Apollo classroom/source kit | Offer → paid checkout | No rights-cleared, accepted payable SKU | Verify inventory, fulfillment, disclosure and merchant confirmation before link | **HOLD** — no confirmed order | Founder / Claude |
| Grok Apollo documentary | Social → Atlas | Published post and immutable asset_id not verified in TASK-008 | Map one existing approved asset to exactly one landing URL | **UNKNOWN** — no attribution asserted | Grok / Praxxis |
| Free investigation | NASA proof → editorial continuation | Campaign policy or 400%-font defect could break continuity | Reproduce approved vs rejected UTM, no-JS link, PDF redaction and source custody | **LOCAL PASS** (20/20 committed test) | Apollo |
| Verified net revenue | Merchant → reconciled 7/30-day cohort | No qualified-human sessions, confirmed paid orders, fees or refunds | Consent-aware reconciliation; do not double count leads, outbound clicks or affiliate taps | **NOT COMPUTABLE** | Claude / Commerce |

**Primary KPI:** `1,000 × realized net revenue / qualified human sessions`, by 7/30-day cohort with denominator, refund/fee reconciliation and tiny-sample warnings; do not report it without verified inputs.

## Explicit remaining release gates

Genuine **axe-core was not executed** (bundle unavailable), nor independent VoiceOver/NVDA, non-Chromium printing, actual installed WordPress/Assembler/CDN, real browser HTTP/CSP, hosted exact-HEAD CI, production LCP/CLS/INP, NASA media-rights/QD/editorial sign-off, a confirmed Grok Apollo post, authentic payable product, or founder approval. **HARD HOLD.** Local fixture LCP/CLS observations are not production Web Vitals; no sales were observed.

Coordination: [Apollo issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [commercial attribution #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818), [Research Desk #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158), [Grok TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit).
