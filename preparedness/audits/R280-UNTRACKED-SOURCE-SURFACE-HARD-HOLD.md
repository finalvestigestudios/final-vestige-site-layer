# R280 — Additional Preparedness source-surface custody (DRAFT / HARD HOLD)

**Scope:** Issue #136; conversion cross-reference #820. Isolated continuation from R279 exact SHA `1c1fde5dada4ff3e5b155f6ffbc9e23e043d4b68`. No production site, WordPress, social, merchant, email, analytics, or paid-service writes.

## Reproduced gap and safe repair

R279 authenticated **96 historical source file identities** and checked for new manuscript candidates only at the first article/tool directory level. It did not reject a newly introduced file `sources/fragments/undocumented.json`. Local synthetic demonstration: using the original committed R279 source and existing synthetic 96-file fixture, inserting that unregistered JSON fragment still returned `DRAFT_HARD_HOLD` without flagging the untracked source. That is not a publication approval, but a source provenance blind spot for future importers.

R280 revises **only** the existing R279 gate and adds a standalone adversarial regression file. The new traversal fails closed on source-like additions with extensions `json/jsonl/yaml/yml/csv/tsv` anywhere inside `sources/fragments`, including nested and case-variant names; rejects fragment symlink indirection; and recursively detects nested, case-variant and symlinked article/tool body/metadata candidates. Markdown audit notes remain permitted. Original corpus, citation URLs, 8 source-origin bytes, source crosswalk, docket, 35 article bodies/metas, 6 tools, and R220 exporter are **unchanged**.

## Executed scope versus prohibited claims

- Before patch: prior R279 tests **68/68 PASS** (original R279 archive version); the added-fragment gap was independently reproduced.
- After patch: **95/95 isolated Python regression tests PASS**, combining 68 inherited + 27 new source-surface tests. Python compilation **PASS**. Exact modified gate and new test Git blob SHA identities independently checked against local execution copies.
- **NOT EXECUTED:** complete authentic local repository checkout, R279/R280 against the actual full tree, native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, complete inherited repository regression suite, or all 41 genuine draft exports. Local github.com DNS fails; GitHub connector supports source writes but is not a local checkout. GitHub Actions outcome is not asserted.
- This new gate is a **standalone review-only preflight**; not secretly wired into R220, whose original SHA is protected by the historical 96-file manifest. A passing synthetic test does **not** mean a release gate or QD PASSED.

## Exact independent coordination (Nov 10 PT)

Seven actual Claude contributor refs checked against **R200 true frozen heads** (start `2122d856`, shelter `5daeaf2d`, food `f911ff7a`, health `d5ef5baf`, hist-field `4e5caf81`, hist-food `67e116e5`, hist-home `7504a5f0`): **7/7 identical, no ahead/behind commits**. Original contributor manuscripts are not automatically merged.

Independent QA **PR #157** current head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` OPEN/DRAFT; synthetic QA **PR #169** current head `e9cd7766dac59d47ab467d8945269b9146c2aef5` OPEN/DRAFT, existing fixture source-directory mutation concern remains with its owner; homepage lead **PR #1689** head `f55c36b6598eec558dd8bb24e4c8988becc51be0` OPEN/DRAFT. None were modified.

## Remaining hard holds

17 historical R200-to-integrated article differences, 14 changed bodies, 12 metadata, six shorter HTML bytes need substantive reading-depth/citation/safety review; **32 shared-source URL groups** and **15 repeated IDs** remain unresolved; three CDC/Ready.gov uses held; Article #7 contamination claims need qualified review, Article #15/Tool #104 child-information privacy, printing and accessibility need review. No publication, QD, medical or privacy approval.

## Conversion-first handoff: ONE audience and ONE provisional existing offer

High-intent households researching **emergency contacts and family reunification** → existing public free `/preparedness/` entry (held drafts not linked) → relevant optional resource only after independent review → **Legacy Triage** existing PDF **provisional only** (rights, suitability, sellable state, refund terms, fulfillment and founder approval NOT VERIFIED). Do not create checkout links, release any contact card, reintroduce retired water freebies, or retask Grok.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Free archive → evidence trust | Untracked source fragments could evade R279 extra-file inventory | R280 recursive fragment + manuscript source closure | 95 synthetic tests PASS; native corpus NOT RUN | Preparedness integration |
| Free guide → printable resource | Child privacy, accessibility and qualified safety not cleared | Independent physical, privacy and source review | HARD HOLD | Preparedness QA |
| Grok social → free landing | No verified matching published `asset_id`/mobile URL | TASK-008 owner confirms actual posting, rights, UTM destination | NOT VERIFIED | Grok/Praxxis |
| Free guide → Legacy Triage | Product rights, practical fit, purchase and delivery unverified | Full PDF/merchant evidence audit; founder approval | NOT APPROVED; no CTA | Founder/Commerce |
| Purchase → net revenue | Merchant-confirmed orders and attribution unavailable | 7/30-day cohorts: paid orders, fees, refunds and qualified-human sessions | KPI NOT COMPUTABLE (not zero) | Analytics/Commerce |

**Release state: DRAFT / HARD HOLD / UNMERGED.**