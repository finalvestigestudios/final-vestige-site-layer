# R391 — Frozen WordPress/private-preview evidence attestation
2026-11-15 PT · Issue #136 · Conversion coordination #820 · Founder charter #818.

**DRAFT / HARD HOLD / PRIVATE REVIEW ONLY.** No merge, publishing, navigation, WordPress/CMS, live tracking, affiliate, email, creator queue, product, or QD approvals.

## Material integration defect addressed
R390 validates all 50+ export pairs but R386 article-content parity, R387 claim/citation anchors and R390 all-export safety run as separate filesystem reads. A parallel export write or an output swap between those three independent checks can cause each to report on **different file bytes**, then R389 combine those reports. This is a time-of-check/time-of-use evidence-custody gap, not a demonstrated production incident.

R391 takes no-follow, file-descriptor-relative pre/post SHA-256 snapshots of the exact same WordPress/private-preview directories around all three audits, records inode/device/size/mtime/ctime/link counts, rejects symlinks, hardlinks, unexpected files, empty files, oversize files, mid-read mutations, directory-entry races, missing pairs, and 35-article taxonomy drift. It then binds every R390 per-file SHA and byte count to the pre/post snapshot; changed outputs return INVALID_HARD_HOLD. A clean synthetic case only yields FROZEN_EXPORT_REVIEW_HARD_HOLD, **not** QD PASS or permission to publish.

## Source and branch custody
Stacked on R390 draft PR #2623 exact parent HEAD `dfd01e2da6892a761227dab39f7d860eb23aaad7` (R389 draft #2618 HEAD `e0288b230d3c7621020b4ae47d96febb233eaa3e`). Changes are only new R391 Python validator, new adversarial test file, one bounded edit to R389 native entrypoint, and this review. Neither original articles, sources, URLs, manuscript versions nor safety states are rewritten.

2026-11-15 read-only nine exact original ref comparisons were identical, 0 ahead/behind:
- Start `2122d856fce9f64887c16df3d52e64be9f59a55b`, Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`, Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`.
- Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`, Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`, Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.
- Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, continuation `ac8625faf30dd5538fadc31e06cb5a2cea1defae`, evidence `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`.

Independent QA draft #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, dependent fix #2205 `bbcf1859768624c611df4abadc564c18247cf32a`, home lead #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0` were inspected, not modified.

## Execution and release
- **57/57 new R391 synthetic tests PASS; 962/962 currently available R381–R389 + R391 local assembled Python tests PASS.** Includes file-swap, same-size replacement, write-and-restore, mutation during validators, malformed/missing reports, source review flags, 50-pair consistency and no-follow filesystem adversaries. Python compile PASS.
- Exact new committed R391 Python blob `9f86329fe80ac636a7a1d0a40258f3f395f84956` and test blob `6ac2dbf75f6f20d5bc2fa0467894038ac64ca0d7` matched locally executed files (no trailing newline). Native integration patched R389 blob `02d62cef698b89e9da2547d612d7065ea73f14cb`.
- Earlier R390's 101 tests are not part of this local assembly; no claim they were rerun this iteration.
- Full native authenticated Git checkout, real validate.py/build.py, authentic 50+ WordPress/private-preview exports and hosted CI PASS **NOT VERIFIED**. Local GitHub DNS unavailable. Native R391 direct CLI deliberately returns exit **2** with INVALID_HARD_HOLD. No qualified food/water/emergency/child privacy/source/QD approval.

## One-offer conversion-first release review
**OFFER**: ONE truly FV-owned, rights-cleared Preparedness digital toolkit (not yet authenticated) → **FUNNEL STEP**: verified checkout/paid order → **BLOCKER**: no confirmed purchasable deliverable FV SKU, lawful rights/refund/merchant receipts → **CHANGE**: founder/Commerce verify an actual listing, rights, test fulfillment/refunds and source-safe product claims before adding any paid CTA → **EVIDENCE**: HOLD, none verified → **OWNER**: Founder/Commerce.
**FREE PATH**: one independently confirmed already-published rights-cleared Grok family-contact/reunification asset with real asset_id and hook → existing free https://finalvestige.com/preparedness/ → **BLOCKER**: matching published asset, UTM, mobile destination unverified → **CHANGE**: Praxxis validates TASK-008, no queue or post changes → **OWNER** Grok/Praxxis.
**OPTIONAL TOOL**: private #104 family reunification card → printable CTA → **BLOCKER**: child/privacy/print/emergency approval missing → HOLD → **OWNER** Preparedness/QD.
**REVENUE KPI**: qualified-human asset_id sessions → CTA → confirmed leads → independently paid orders → refunds/fees → net revenue per 1,000 eligible sessions (7/30d) = NOT COMPUTABLE; merchant and cohort evidence missing → **OWNER** Claude/Commerce.

Remain **DRAFT / HARD HOLD** pending 5 source-evidence conflicts, 9 Shelter object forks, source-reading Article #7 and Article #11, Tool #104 human review, complete native validation, authentic private builds, and founder release approval.
