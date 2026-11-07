# R198 — Article-scoped source origin admission and 7/30-day conversion HOLD

**Owner:** Preparedness Archive Issue #136. **Related:** commercial Issue #820, charter #818, Grok/Praxxis TASK-008. **State:** BUILT / EXACT-CODE SYNTHETICALLY TESTED / DRAFT_HARD_HOLD. Nothing here authorizes safety, QD, sale or publication.

## Genuine integration defect fixed in draft

R197 correctly enumerates all global-base and historical-cluster records sharing a source ID, but its source-use resolution treats all four origins as globally eligible. A Historical Field article could therefore pass R197's existence test using an ID found **only in the unrelated Historical Food or Home register**. A source that merely exists somewhere in the combined repository is not sufficient proof that its claim-support provenance belongs to the article's cluster.

R198 adds `preparedness/tools/r198_source_scope_gate.py` as an additive, read-only second-stage admission gate. It authenticates the **exact R197 validator Git blob** `43a31b025e2cfebc1e6dff0302dee330858ea250` before importing it. Production execution must obtain source records from R197's original pinned immutable Git objects. It rejects article source-use IDs backed only by another historical cluster. A shared ID is eligible only through the global **base** source register or the article's **own** historical cluster. All other matching origins are preserved in a human-review workorder; none is silently resolved or collapsed.

The gate also checks all fourteen frozen/observed metadata positions for exactly seven original articles, unique source-use IDs, sorted nonempty origin lists, pending review states, and immutable non-approval controls. On a trusted original checkout it requires R197's observed subset census: **115 frozen / 119 revised source rows; 65 / 70 source-use relationships; 7 / 9 ambiguous source-use relationships; six / seven cross-origin collision IDs.** These are article metadata relationships, **not** the 315/334 body-citation occurrence count, and do not measure the full 35-article archive. R194–R197 safeguards remain additive and separate from independent PRs #157, #169 and #973.

## Tests and reproducibility

- New Python exact-code synthetic test suite: **162/162 PASS** using `python -I -m unittest discover -s preparedness/tests -p 'test_r198*.py' -v` in an isolated test-only copy.
- `python -I -m py_compile` **PASS** for the new source and test files.
- Exact local/remote Git source blob: `77ca95b4140721a30370b7e851522bc0c85ef2aa`; exact local/remote test blob: `3c3353598dfb9932c9afa776fc98439836404a0c`.
- The tests include 140 per-article/per-version negative mutations, 14 false-header/approval mutations, source-origin leakage, same-ID ambiguity with other-cluster alternatives, R197 producer-mutation refusal, deterministic workorders and census refusal. No original content modified.
- **NOT EXECUTED**: authentic original 35-article + six-tool validate/build, complete original test suite, the R198 `git cat-file` CLI against source blobs, all 41 WordPress draft exports, or real browser/safety/citation/QD reviews. Complete local checkout blocked by `github.com` DNS resolution; hosted CI not established. Exit code **2 = verified structural DRAFT_HARD_HOLD**, **3 = INVALID_HARD_HOLD**; neither is publication approval.

On an authenticated full repository clone that contains the historical blob objects, run:

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r198_source_scope_gate.py --repo . --report /tmp/fv-r198-origin-scope.json
```

Expected last command return code 2 on structural custody with continued DRAFT_HARD_HOLD. The reviewer must inspect the report and separately adjudicate claims, sources, safety and citations.

## Contributor custody and release

Fresh current heads on 2026-11-07 UTC (read-only):
- `claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`
- `claude/prep-food-ccdc55` `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- `claude/prep-health-837444` `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- `claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- `claude/prep-hist-field-9db767` `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- `claude/prep-hist-food-b81f19` `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- `claude/prep-hist-home-0e0e38` `7504a5f099594d635e3dd7332a33a2e1346c43a2`

Independent safety #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; follow-up #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`. All remain draft/unmerged. Home leads PR #1443/#1451 identified as independent Focus funnel release holds; no changes.

All original 35 articles and six tools remain under independent safety/source/QD review, and 41 draft WordPress destinations remain unreleased. No navigation/CMS/WordPress, scripts/analytics, emails, merchant, affiliates, social, spending, production or source register changes.

## Single source-grounded commercial hypothesis and acceptance

**Audience:** households protecting identity, financial/insurance and contact records before an evacuation. **Free information:** currently public Preparedness resource gateway; Household Emergency Plan is an UNPUBLISHED candidate free guide, not a live URL. **Optional paid candidate:** existing public Legacy Triage PDF listing only after exact publisher ownership/permissions, contents, current price, safe claims, checkout/delivery, refund/support and payment reconciliation are independently authenticated. Family Reunification Card stays a held **free** printable, not the paid product. Sole existing approved email freebie remains Seven Day Focus Fieldbook; no retired water offer.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Legacy Triage → paid sale | Rights, inventory, live checkout, delivery, refunds and customer relevance not verified | Read-only rights/product audit, then founder-approved synthetic/nonfinancial checkout QA | **HARD HOLD**; no paid-order proof | Founder / Commerce / Claude |
| Grok records-focused post → Preparedness gateway | No authenticated matching publish URL/asset_id/click placement | Reconcile existing TASK-008 without changing Grok queue; test permitted asset-specific UTMs only after approval | **UNVERIFIED**; attribution absent | Grok / Praxxis |
| Public gateway → authentic source-backed Household Emergency Plan | Full native source/safety/QD not cleared | Independent citations and advice review, 360/390/768/1440 mobile stage | **DRAFT_HARD_HOLD**, not a public link | Preparedness / QA |
| Free guide → optional printable Family Card | Child-data privacy, source review, network-offline/printing checks outstanding | Staged synthetic-data acceptance with no persistent sensitive storage | **HARD HOLD** | Preparedness / Site QA |
| Verified settled purchases → net revenue per 1,000 qualified human sessions | No merchant-confirmed orders, attribution, refunds, fees, denominator | Reconcile 7/30-day cohorts; distinguish outbound clicks, leads, checkout starts, paid sales | **NOT COMPUTABLE** | Commerce / Analytics |

**Draft CTA, NOT LIVE:** “Keep important household documents and contacts organized before an interruption. Explore the free emergency-planning resources.” Keep any future paid CTA separate, accurately priced, disclosed and optional, with approved merchant/delivery details. No invented product launches, buyer counts or conversion results.