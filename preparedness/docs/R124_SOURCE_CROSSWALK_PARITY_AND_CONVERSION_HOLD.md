# R124 — Frozen candidate shared-URL crosswalk parity (DRAFT / HOLD)

**Preparedness-only engineering lane:** Issue #136. Business conversion charter #818 / attribution issue #820.  
**Date:** 2026-11-04. **Candidate source snapshot:** PR #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706`.  
**Branch:** `review/preparedness-r124-source-crosswalk-parity-hold-20261104` stacked on R123 `9c26fe8d44b1947a1133f3dbea313b9c294d96a1`.  
**Release state:** **HOLD** — do not merge, publish, change WP/navigation/CMS, send email, activate analytics/merchant links, claim independent QD PASS or claim emergency advice is medically safe.

## Change implemented

Reconstructed `preparedness/sources/crosswalk.json` against all **eight actual candidate source files** (base register + 7 cluster fragments), retaining exact variant entries and author-specific `supports` / `notes` text. Existing 2026-10-30 inventory retained under `historical_crosswalk_census_20261030`; original contributor commit references remain historical evidence, not claims of current branch heads. Original articles, metadata, source fragments and 35 routes were **not edited**.

| Inventory | Historic crosswalk | Frozen PR #584 candidate |
|---|---:|---:|
| Source rows | 224 | 244 |
| Distinct exact URLs | 186 | 202 |
| Same-URL source groups | 30 | 32 |
| Source-ID duplication groups | 15 | 15 |
| Human-reviewed shared-URL groups | 0 claimed | **0; all 32 pending** |

Five exact **provenance repair operations** were necessary:

1. `https://ask.fsis.usda.gov/article/How-do-you-keep-food-safe-during-a-power-failure`: add **shelter** variant to the prior base + food record; no shared-scope inference.
2. `https://www.cdc.gov/natural-disasters/response/what-to-do-protect-yourself-during-a-power-outage.html`: add **start** variant to the prior health + shelter record.
3. `https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/emergencies/keep-your-food-safe-during-emergencies`: create previously absent **food + shelter** same-URL pending-review group.
4. `https://www.loc.gov/resource/gdcmassbookdig.prairietravelerh01marc/?st=list`: refresh **hist-field** variant's expanded scoped reading notes without overwriting the frozen historic crosswalk census. This fifth discrepancy was newly identified after the initial R123 four-defect report: source identifiers and group membership were unchanged but recorded source interpretation had changed.
5. `https://www.weather.gov/safety/winter-during`: create previously absent **hist-field + shelter** same-URL pending-review group.

**A common URL is not evidence that two contributors read the same material or support the same claim.** No citation was silently reassigned, no historic source record was removed, and no emergency guidance was certified safe.

## Deterministic gate

`preparedness/tools/r124_source_crosswalk_integrity.py` checks: eight exact Git blob identities and row counts; exact candidate commit; 32 shared-URL groups, 244 source rows and 202 distinct URLs; complete per-group variant identity, ordinal, source-file and entire source-record parity; changed `supports` text; unsafe URLs; duplicate JSON keys; unexpected source-ID/URL changes; duplicate groups; missing variants; historical census custody; and forbidden review/QD/merchant/release approvals. Output stays **HOLD**, even with structural parity. Uses only stdlib and read-only local files.

Run from a trusted full repository checkout:

```sh
python -I preparedness/tools/r124_source_crosswalk_integrity.py --root .
python -I -m unittest discover -s preparedness/tests -p 'test_r124_*.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

### Recorded evidence (do not mislabel)

- **Locally TESTED:** 58 new tests executed in an isolated synthetic filesystem; **57 passed, one full-checkout integration test SKIPPED** because the full source tree could not be mounted. Python compilation passed. Local tested Git blob IDs: validator `3cd729f5ea5ed6c276c04f361ca5e926c8128176`; tests `f4e2ab67af8d9fb018f37c42b871e40edd95a56e`. These match committed Git objects.
- **Independently VERIFIED against immutable GitHub snapshot:** all 8 source files re-read at candidate SHA; **244 rows / 202 URLs / 32 shared-URL groups**; all 32 pending review; exhaustive source-variant and source-file exact-blob comparison yielded **0 discrepancies** on the staged crosswalk. This is a separate JavaScript/connector audit, **not** the local Python gate executed against the full checkout.
- **UNVERIFIED:** `validate.py`, `build.py`, full Python suite, exact-head hosted CI, real WordPress browser QA, claim-level source adjudication, qualified medical/safety review, QD decision. Do not imply any of them passed.

### Live contributor head coordination snapshot (2026-11-04)

The seven main Claude contributor refs currently resolve to:
- food `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- historical-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- historical-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- historical-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`
- shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- start-here `2122d856fce9f64887c16df3d52e64be9f59a55b`

Some contributor heads have advanced relative to the earlier frozen nine-head inventory. R124 validates PR #584's immutable candidate **only** and does **not** pretend to incorporate newer work without separate lossless reconciliation. Main/home PR #49 `10495883299d53596992c26a8987f629b2904670`; flagship #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`. Both untouched.

### Independent QA and fixture coordination

- QA #157 is still draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`: main-breaker drill and refrigerated-medication advisories require qualified reviewer adjudication against PR #584; **no implied medical safety approval**.
- Fixture #169 draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5`: the upgrade test now uses `TemporaryDirectory`, but the separate `test_register_fragments_cannot_duplicate_ids` still writes `_dup_test.json` in the shared source tree. Correct it before integration. No changes made outside Preparedness lane.

## Conversion-first HOLD — offer → funnel → blocker → experiment → evidence → owner

| Offer | Funnel | Blocking condition | Draft experiment / acceptance check | Evidence | Owner |
|---|---|---|---|---|---|
| **No approved paid preparedness SKU yet** | Purchase and delivery | FV ownership, rights, merchant live pricing/checkout/refunds and fulfillment unverified | Inventory actual existing FV Payhip Products 001–015; select one genuine relevant practical pack only after authenticated seller evidence, delivery and safety checks. Do not substitute unrelated public Payhip listings. | **UNVERIFIED** | Growth/Claude merchant lane |
| Original **Household Emergency Plan** guide | Free read | Article unreviewed; 35-route integration, source and emergency-safety reviews incomplete | Preserve ungated evidence-backed guide; satisfy qualified review and nonproduction mobile/browser QA before any publication. | **HOLD** | Preparedness + independent QA |
| Grok household communication/reunification asset | Social → staged free guide | No matched asset ID, live canonical destination or approved creative inventory in TASK-008 | Request Grok/Praxxis to confirm one `asset_id`, platform, allowed link surface, `utm_campaign`, destination and source permissions; no content-posting role takeover. | **UNVERIFIED** | Grok/Praxxis |
| Optional practical pack CTA | Guide → offer → checkout | No verified paid pack or authorized checkout | Draft language for later review only: “Want a printable companion? See the optional planning pack.” **Do not render CTA until rights, product fit, current price, checkout, refunds and accessible delivery pass.** Keep free guidance complete. | **NOT TESTED** | Claude + Site QA |
| Merchant-confirmed sale | Checkout → net revenue | No source-confirmed orders, refunds/fees or qualified human-session denominator | Validate mobile 360/390px and keyboard completion in staging; reconcile authenticated orders and refunds to `asset_id`/UTM under consent; 7/30-day cohorts and tiny-sample warnings. | **N/A** | Growth/merchant QA |

**Primary KPI:** realized net revenue per 1,000 qualified human sessions (**N/A**, denominator and sales evidence absent). A CTA click, email lead, checkout initiation or affiliate outbound click is **not** a paid conversion.

**TASK-008:** https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit ; companion coordination issue #820. No Grok queue changes, posts, email sends, merchant writes, tracking scripts, vendor spending, CMS writes or live deployments.

## Remaining independent HOLD blockers

Full 35-article / seven-cluster latest-head reconciliation; original depth/citation/context and canonical-route checks; human review of all 32 source URL groups including this corrected dossier; outstanding safety/editorial exceptions; five tool readiness checks; independent qualified emergency-guidance review; test fixture isolation; full checkout `validate.py` / `build.py` / 36+ regression tests; browser QA; GitHub mandatory integrity and independent QD on the exact release head. **No claims of QD PASS or publishing eligibility.**
