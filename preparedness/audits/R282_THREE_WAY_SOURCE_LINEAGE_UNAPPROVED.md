# R282 — Three-way historical source-evidence lineage crosswalk (UNAPPROVED)

**Scope:** Preparedness Archive source/citation integrity only; #136 and #820. **DRAFT / HARD HOLD / NO MERGE / NO PUBLISH**. Parent is R281 draft commit `898ee601c8648c7bb1a7b26738a488f042c39a44`. This work does not alter 35 manuscripts, six integrated tools, existing canonical routes, sources, WordPress or any live configuration.

## Newly authenticated finding

R281 pins `sources/article-evidence-lock.json` but does not explicitly reconcile that older source lock against both the R200 frozen Claude originals and the R276 integrated slate. Those three source witnesses do **not** always describe the same historical bytes or attribution. Treating any of them as a universally interchangeable canonical source would conceal review-required differences.

R282 compares independently Git-pinned R200 (blob `5822f9dfde21d1f3bdfc26658769d852c639438c`), R276 (blob `b8c7c6df0dca62b04b01abc5671b7083ad9cb61e`) and the historical evidence lock (blob `2dc41fccad6f1272f0a9d9585b6c10c760dcb08c`). It emits 35 source-specific records with per-body/per-metadata Git OIDs, byte counts, canonical route, original cluster, historical lock origin and **explicit nonapproval**.

## Exact three-way findings

| Measure | Authenticated source records |
|---|---:|
| Original article identities and canonical routes | 35 / 35 |
| Historical evidence-lock records | 36 (35 articles + one historical water-planner tool) |
| R200 ↔ R276 article differences | 17 |
| R200 ↔ historical-lock article differences | 9 |
| Historical-lock ↔ R276 article differences | 15 |
| Changed R200 ↔ R276 bodies / metadata | 14 / 12 |
| Changed R200 ↔ historical-lock bodies / metadata | 7 / 8 |
| Historical origin labels that differ from R200 | 6 |
| Unique articles requiring human three-way lineage review | 21 |
| Bodies that differ across **all three** historical snapshots | 4 |
| Metadata records that differ across **all three** snapshots | 1 |

The four all-distinct bodies are **#27 root-cellars-cool-storage, #32 navigation-before-gps, #33 sanitation-before-germ-theory, #34 pioneer-supply-chains-failed**. Attributions for six articles (3, 4, 5, 6, 7, 21) are labelled `base` in the older lock but `start` in R200; that is a historical provenance difference requiring context, **not proof of unauthorized copying or revision**. The lock's `water-planner` is historical source context, **not an authorized current freebie or commercial offer**. The previously documented six bodies shorter in bytes remain #24, #25, #27, #32, #33, #34.

## Mechanical safety-gate implementation

- `tools/r282_evidence_lineage_hold.py` independently pins all four Git blob identities, performs strict JSON parsing, refuses symlinked or missing custody inputs and regenerates the entire deterministic docket from the three frozen records.
- Detects missing/duplicated article identifiers and URLs, incorrect integrated roles, missing historical lock records, changed OIDs/byte lengths, altered dispute counts and changes to mandatory release holds.
- The script returns `DRAFT_HARD_HOLD` only for mechanically aligned, independently verified source witnesses; returns `INVALID_HARD_HOLD` otherwise. CLI exits **2** for mechanical hold and **3** for invalid; **neither exit code authorizes publication**.
- `tests/test_r282_evidence_lineage_hold.py` contains 56 isolated synthetic Python tests, including adversarial mutation, route, citation-hold, historical-origin, symlink and CLI failure assertions. Local combined R279–R282 suite: **202/202 PASS**; Python compilation **PASS**. Local source/test byte identities checked against exact committed Git blobs.

## Explicit limitations / release restrictions

The genuine full-tree native Python validation/build, inherited repository test suite, R282 validator execution against the complete authenticated checkout and 41 WordPress draft exports remain **NOT EXECUTED**: local GitHub DNS access fails, and the isolated evidence package is not a full clone. Python test results do not substitute for authoritative editorial, source or medical review. All 32 shared-URL groups, 15 duplicate-ID groups, three disputed CDC/Ready.gov occurrences, Article #7 contamination guidance, and Article #15/Tool #104 child-information privacy/accessibility issues remain **UNRESOLVED**. No independent QD PASS or approval.

Independent QA PR #157 (head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`) and fixture QA PR #169 (head `e9cd7766dac59d47ab467d8945269b9146c2aef5`) were inspected read-only; PR #169 retains a test that writes a fixture under the actual sources directory. Homepage lead PR #1689 (head `f55c36b6598eec558dd8bb24e4c8988becc51be0`) was not modified. All seven actual Claude branch refs compared **identical** to the correct R200 frozen SHA baseline in this run (zero ahead/behind, zero changed files).

## Conversion-first acceptance (research-only; Issue #820)

**Audience:** households planning emergency contact and family reunification. **Free:** only the already public `https://finalvestige.com/preparedness/`, contingent on verified Grok published asset_id, rights, date and signed-out mobile link. **Optional practical resource:** draft/held pending qualified child-information privacy, print/accessibility and safety review. **Provisional paid candidate:** existing Legacy Triage PDF, **NOT an approved Preparedness upsell**, rights, offer fit, merchant availability, checkout, delivery and refunds unverified. No retired water freebie and no paid CTA. Track creator asset_id → qualified-human sessions → landing/CTA → verified lead where consented → independently confirmed orders → fees/refunds → 7/30-day net revenue per 1,000 qualified-human sessions. KPI is **NOT COMPUTABLE**, not zero; no asserted paid conversions.

**Ownership:** Preparedness integration owns source crosswalk and draft-only tests; qualified reviewers own safety/privacy decisions; Grok/Praxxis own creator asset inventory and QA under TASK-008; Claude owns production site/analytics; Founder owns any commercial or release approval. No CMS/social/merchant/affiliate/email/analytics/spending activity occurred.
