# R116 | Original author metadata custody, source-scope integrity and conversion HOLD

**2026-11-04 PT. Issue #136; revenue coordination #820; charter #818.**
**DRAFT/REVIEW ONLY — NOT A PUBLIC RELEASE.** This branch is stacked on exact R115
head `454a87a278543ae837ec651b7ad206b390c52d58`; its claims are
engineering-only. **Do not merge, publish, send, spend, run merchant tests, change
WordPress, add tracking scripts or claim qualified human emergency safety approval.**

## Why this is an integrity gap, not another article

R115 freezes original article **body** Git blob identities and checks a
*35-article aggregate* of historical self-reported safety states and source-use
counts. It does **not** freeze the 35 *metadata* Git blobs. Before R116, an
editor could change an article's original `source_use` explanation, risk caveat,
editorial/reviewer note, or safety metadata while the article body remained
byte-identical. Two per-article safety status swaps could also leave R115's
aggregate status census unchanged. A new body/meta pair outside the original
roster could be imported by the build library while the R115 checker only
loaded the 35 ledger-listed paths.

R116 adds the missing immutable counterpart:

1. `R116_FROZEN_35_METADATA_BLOB_CENSUS.json`: **35 exact metadata Git blob
   OIDs** (and the 35 corresponding article body OIDs cross-checked with R115).
   Evidence was read from GitHub at the exact R115 initial freeze commit
   `8f42bd2d4bd2a5a3a9781b1ac28cd8ec80d25620` on Nov 4 PT. Every original
   metadata blob was separately compared between that commit and the R115 final
   head `454a87a...`; 35/35 matches. No author prose, source URL, private
   visitor data or customer record is copied into the manifest.
2. `r116_frozen_metadata_and_roster_gate.py`: independent, **read-only**
   per-article byte-identity check; refuses all altered metadata, including
   whitespace changes (this is intentionally strict so human reviewers must
   re-baseline a deliberate edit), changed source reading scope, changed
   safety claim, and publication-state drift. Enforces original article reading
   order and exactly paired 35 body and 35 metadata files, rejects extra,
   missing, orphaned or symlinked inputs, duplicate JSON keys, and unmatched
   historical source-use and safety counts. All outputs stay `HOLD`.
3. `test_r116_frozen_metadata_and_roster_gate.py`: **71 locally executed
   synthetic/adversarial unittest cases**, including one altered author-specific
   source-use description for each of 35 original slate positions, a safety
   status swap preserving aggregate counts, extra/absent file pairs, path
   traversal, duplicate JSON keys, unexpected publish/medical/QD state, and
   symlink rejection.
4. `test_r116_actual_checkout_custody.py`: demands this check against actual
   complete source files in any future full Python suite. **Not locally
   executable in the constrained scratch environment**, because a complete
   private checkout is not available. Its eventual CI result must not be
   substituted with a synthetic pass.

`python -I preparedness/tools/r116_frozen_metadata_and_roster_gate.py --repo-root .`
will yield a report with **35 paired files, the original 364 article-scoped
source-use IDs (NOT 364 unique URLs), and historical self-reported safety
state counts** only when the original metadata is byte-identical. A zero exit
code is an inventory check, never a release, medical, article, or source fact
approval. R115 body custody, R114 markup visibility, R111 two-version
provenance, human source-checks and the mandatory integrity pipeline remain
independently required.

## Verified vs outstanding

- **BUILT / exact GitHub:** new frozen census comes from a 70-file original
  GitHub directory inventory (35 metadata + 35 HTML), with original
  body OIDs cross-checked to R115. Metadata OIDs did not change between
  the reference commit and R115 final head.
- **TESTED / synthetic only:** 71 isolated unittest cases and Python
  compilation passed in local scratch; exact Github source/test blob OIDs
  were compared with the tested bytes.
- **NOT VERIFIED:** R116 against an actual complete repository checkout;
  native `validate.py`, offline `build.py`, full 36+/9k suite, the 13-stage
  mandatory pipeline, human link/claims review, clinical emergency guidance
  safety, browser/print QA and independent QD PASS. GitHub Actions
  has recently failed before executing runner steps; do not infer a Python
  outcome from no-step jobs.
- **Release state:** HOLD, `may_publish=false`, `may_merge=false`,
  `independent_QD_PASS=false`. Author safety metadata `approved` is a
  historical self-report and is not independently verified approval.

## Exact contributor/reference coordination (2026-11-04)

Seven current Claude contributor branch heads (read GitHub refs, not stale
saved observations): start
`2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter follow-up
`6a5998ead97eca997e573ce8d3ceacf1c6aabad4`; food
`f911ff7a655de8d81535ea86ec3d65a49ee76648`; health
`d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical food
`67e116e536c7410bed30f8f3b1bb8c166f3c223d`; historical home
`7504a5f099594d635e3dd7332a33a2e1346c43a2`; historical field
`4e5caf812727953aa45e3bda2d382f2c67b6a09c`.

Existing PR #584 RC `ddb3528ba6494dada1fa1c3a142ce746e3a67706`,
independent QA #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`,
fixture QA #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`,
homepage #49 `10495883299d53596992c26a8987f629b2904670`,
flagship #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`.
All remain under other owners. QA #157 modifies the original two Start Here
article bodies and source attribution as a **proposed safety edit**; it may be
incorporated only after human adjudication, with revised frozen lineage, not
an unconditional overwrite. PR #169 still changes one source-upgrade test
to a temp directory but its `test_register_fragments_cannot_duplicate_ids`
still writes `_dup_test.json` into the shared checkout: isolate this too
before approving its merge. R116 does not modify either agent's PR.

The existing 23 changed contributor paths, 30 shared-source URL groups,
15 safety exceptions, 22 editorial decisions and five incomplete tools
remain OPEN. R116 preserves the original 35 article drafts and one complete
tool; it **does not silently accept** any contributor revision.

## #820 conversion-first lane: one high-intent audience, no invented SKU

**One audience/topic:** Grok/Praxxis must verify a real video asset aimed at
households planning out-of-area contact and emergency reunification. Until
TASK-008 supplies immutable `asset_id`, actual publish URL, source rights,
platform and actual website destination, the creative-to-guide match is
**UNOBSERVABLE**. Do not take over Grok's production.

**One free guide:** `household-emergency-plan`, canonical *proposed*
`/preparedness/start-here/household-emergency-plan/`. Original source-backed
draft; 14 author-scoped IDs and 57 citations in the earlier frozen census;
qualified safety review and live page are **not verified**. Safety-critical
guidance remains free after authorization; never gate it behind an email or
payment.

**Optional paid pack:** **NONE VERIFIED** among FV-owned, rights-cleared,
delivered Preparedness SKUs with authenticated merchant ownership,
seller-approved price/terms, testable receipt and refund evidence. Do not
fabricate product, price, checkout URL, `Buy` CTA or acceptance. The
existing Focus Fieldbook is the distinct authorized lead magnet; do not
revive the retired water giveaway or imply a preparedness product is already
for sale.

| Priority / OFFER | FUNNEL STEP | BLOCKER | STAGED CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| P0 / existing Preparedness paid SKU, if any | Offer → paid receipt | No authenticated seller/rights/fulfillment SKU | Read-only seller product inventory and rights review; choose zero if none fits | **FAIL/UNVERIFIED**: no merchant order, fulfilled file, fee/refund or price proof | Growth + Claude; founder approves |
| P0 / free household guide | Social reader → accurate guide | 15 safety exceptions/other editorial review; no live page | Source-claim verification, qualified safety adjudication, responsive preview, R114-R116 gates | **HOLD**: source custody is not medical clearance | Preparedness + independent QA/QD |
| P1 / Grok family-reunification asset | Post/bio link → guide | TASK-008 asset ID, UTM and actual destination missing | Verify published post and nonproduction UTM paths, avoiding caption-link assumptions | **UNOBSERVABLE**: no verified video/route yet | Grok + Praxxis + Claude |
| P1 / staged free-guide CTA | Guide → optional planning pack | No approved/relevant purchasable product or functioning checkout | After seller validation, compare plain-language relevance/disclosures and accessible mobile CTA/checkout | **NOT TESTED**: no merchant sandbox/approval | Claude/Site QA |
| P0 / realized net purchases | Merchant confirmed paid order → 7/30d net | No attributed qualified sessions, order/refund/fees | Join approved privacy-safe asset campaign cohort to merchant records, remove refunds/fees | **N/A** net revenue/1,000 qualified-human sessions | Growth/Claude |

**Noninteractive draft-copy direction only (do not paste live):**
"Make a household contact and reunification plan you can actually practice.
Read the free guide, with sources and limits explained." This copy is
conditional on qualified safety and source approval; **no link goes live now**.
When and only when a real paid pack is verified, stage a clearly separate
optional CTA whose label exactly matches its rights-cleared product, price,
format, delivery, limitations and merchant terms. Emergency instructions must
remain available without buying.

### Funnel acceptance / privacy contract

A campaign test cannot PASS until: authentic asset ID and platform URL
verified by Grok/Praxxis; live target approved and 200/mobile accessible;
caption/pinned Sources comment/profile placement permitted by platform;
no misleading safety or efficacy claims; consent-compatible qualified
human-session detection; distinct relevant CTA clicks; actual confirmed
lead records when applicable; merchant-confirmed unique paid orders,
customers and refund/fee ledger; no duplicate analytics scripts; 7- and
30-day reconciliation; small-sample caveats and unknown attribution
clearly visible. Formula: `1000 × realized_net_revenue /
qualified_human_sessions` only when both numerator and denominator
come from verified compatible cohorts. Views, social likes, CTA taps,
checkout starts, email forms and affiliate outbound clicks are **NOT paid
conversions**.

## Release governance

This private engineering branch may be reviewed, not merged/published.
Require all 7 historical/current contributors, 23 changed paths, 30
author-specific source collisions, 15 safety flags, 22 editorial decisions,
five tools, full mandatory validation/build/tests, human qualified guidance,
browser QA, independent QD on **exact** release head and explicit founder
authorization. No navigation, WordPress/CMS, merchant, analytics, social,
email or spend modifications are made by this lane.
