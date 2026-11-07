# R197 — base-register origin collisions, seven-article source-use custody

**Owner:** Preparedness #136. **Coordinates:** #820 / #818 / Grok–Praxxis TASK-008. **State:** `BUILT / EXACT-CODE SYNTHETICALLY TESTED / DRAFT_HARD_HOLD`. This is not a review sign-off, release authorization, medical/food safety certificate, merchant approval or proof of revenue.

## Authenticated GitHub source observations, 2026-11-07 PT

R196 compared **Historical Field, Food and Home fragments to each other**. It found two same-ID collisions. R197 extends that check to the 34-row **global base register**. This additional source origin matters: the seven historical articles rely on both cluster fragments and the shared base register.

Authenticated reads of the original Git blob IDs (not local native CLI execution) establish the following *subset* census:

- Frozen: base 34 + Historical Field 26 + Historical Food 28 + Historical Home 27 = **115 source rows**. **Six** source IDs occur in more than one origin.
- Observed: base 34 + Historical Field 28 + Historical Food 28 + Historical Home 29 = **119 source rows**. **Seven** source IDs occur in more than one origin.
- Across the seven changed historical articles' metadata, source-use relationships increase **65 frozen → 70 observed**. Of these, **7 frozen → 9 observed source-use relationships** point to IDs with multiple source-record origins. These are metadata relationships, *not citation occurrence counts*, paid outcomes, or the full-archive inventory.
- No seven-article source-use ID was orphaned when the *base* register and the appropriate historical fragment were both considered. Looking at the fragment alone would incorrectly label a number of valid base-backed relationships as orphaned.

**All seven observed shared-origin identifiers require named-origin handling; do not silently collapse them:**

1. `nchfp-home` — global base / Historical Home.
2. `nchfp-jerky` — global base / Historical Food. **New in the observed shared-origin roster**, after the separate historical `hist-food-nchfp-jerky` identifier was replaced; do not equate that replacement with safety or method equivalence.
3. `nps-lewis-clark-salt` — global base / Historical Food.
4. `nps-salt-works` — global base / Historical Food.
5. `loc-pioneer-diaries` — global base / Historical Field / Historical Food.
6. `loc-prairie-traveler` — global base / Historical Field / Historical Food.
7. `nchfp-historical-origins` — global base / Historical Food.

The previous R196 two-ID report was **correct for the three historical fragments alone**; it was not the full cross-origin roster once the global base register was included. Duplicate identifiers can differ in descriptions, review dates, reading scope or bibliographic metadata. A common URL or identical `supports` field does **not** make multiple provenance records editorially interchangeable. Not all differences imply a false source; they demand a human source-scope choice. These source rows' `human_link_check=false` is not replaced by dates in `verified_on`.

## Read-only engineering gate

`preparedness/tools/r197_source_origin_collision_gate.py` binds to the *immutable* R194 docket Git blob, the base register's Git blob, all six frozen/observed historical fragment blobs and all fourteen frozen/observed seven-article metadata positions. Every candidate is re-read by its exact Git blob identity. It rejects a changed record count, missing/duplicate source IDs within one origin, missing source-use provenance, unsafe source shapes, changed pinned article metadata, unexpected collisions, forged human/QD/merchant approvals and substituted objects.

It emits per-version origin-specific workorders and a list of alternative same-ID records with individual record fingerprints. It records a **HARD HOLD even when structural verification succeeds**: CLI exit **2** for `DRAFT_HARD_HOLD`, exit **3** for `INVALID_HARD_HOLD`. It never chooses a canonical source record, aliases historical jerky IDs, writes WordPress, buys/publishes anything, or changes the source register.

This gate is **additive** to R195 complete-body/citation reconciliation, R196 fragment custody, R190 native preflight and independent safety/fixture PRs #157, #169 and #973. It is not a substitute for reviewing the complete 35-article slate, six tools, 41 WordPress-ready draft outputs, all original safety warnings and current regulator advice.

## Verification boundaries

- **96/96 isolated Python unittest methods PASS**, zero skipped; `python -I -m unittest discover -s preparedness/tests -p 'test_r197*.py' -q`.
- `python -I -m py_compile` **PASS**.
- Exact tested local source Git blob: `43a31b025e2cfebc1e6dff0302dee330858ea250`.
- Exact tested local test Git blob: `834d81ca4146c1979d6625810568bbeb74f29a2d`.
- Authenticated GitHub readback of those blobs matches the test environment. The synthetic mutations cover corrupted source-origin/approval/provenance records and non-merging of shared IDs.
- **Authenticated GitHub reads of the original pinned source and article metadata** independently corroborate the stated row counts, conflict IDs, metadata relationship totals and absence of source-use orphans in this seven-article subset.
- **NOT EXECUTED:** original repository `validate.py`, `build.py`, original 36+ suite, authentic R197 `git cat-file` CLI, 41 WordPress-ready exports or browser/print tests. Local `git ls-remote` still cannot resolve `github.com`; a trusted complete checkout is unavailable. Do not report an authentic end-to-end PASS.
- Human food-safety, medical, child-data privacy, citation adjudication, accessibility, offline/print, independent QD and founder production approval remain **PENDING**. All seven historical article edits preserve draft status.

## ONE high-intent audience → ONE optional commercial candidate

**Topic hypothesis:** household document and financial-record continuity during an evacuation. Grok owns any creator production and distribution; do not assume a real published matching asset. Praxxis/TASK-008 owns independent asset-ID/post-URL/rights coordination. Public `/preparedness/` remains an official-resource gateway only. The unpublished comprehensive **Household Emergency Plan** is a *future* ungated educational guide, not a live link.

**Optional paid product candidate:** existing public **Legacy Triage** PDF listing, *not* an authenticated FV-owned/rights-cleared Preparedness SKU. Never activate a paid CTA until seller rights, exact item/price, mobile checkout, access to the delivered PDF, support/refunds, fees, material claims, and household-records buyer fit are documented. The **Family Reunification Card** is a separately held FREE printable with privacy and 11 source decisions pending, not the proposed paid offer. Keep the Seven Day Focus Fieldbook as the sole approved lead magnet. Never revive the retired water freebie.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Legacy Triage → authenticated paid purchase | Merchant identity, rights, product/delivery/terms/fees/refunds unverified | Signed-out mobile checkout/fulfillment and rights audit before founder CTA approval | **HARD HOLD**; no merchant-confirmed order evidence | Founder / Commerce / Claude |
| Grok records-continuity post → free public gateway | No verified matching immutable `asset_id`, live post, permission and campaign link | Reconcile TASK-008, then test allowed `utm_source`, `utm_medium=organic_social`, `utm_campaign`, `utm_content=actual_asset_id` in staged mobile link | **UNVERIFIED**, no attributable qualified-human denominator | Grok / Praxxis |
| Official-source gateway → unpublished Household Emergency Plan | Native render, source/advice check, QD not cleared | Hold draft destination; human claim-and-safety review, source provenance and visible citations before any release | **DRAFT_HARD_HOLD** | Preparedness / Independent QA |
| Free guide → optional Family Reunification Card | Child-data privacy, keyboard/print/offline behavior and 11 source decisions | Synthetic-only 360/390/768/1440px test; block storage/network leaks; independent review | **HARD HOLD** | Preparedness / Site QA |
| Paid order → net realized revenue/1,000 qualified humans | No verified sessions/settled sales, refund/fee records | Reconcile 7/30-day unique creator cohorts through merchant receipts; count signups/clicks separately | **NOT COMPUTABLE** | Commerce / Analytics |

**Draft on-site CTA, NOT DEPLOYED:** “Organize the records and contacts you may need if your household has to relocate. Explore free emergency-planning resources.” Later, any *approved* optional commercial CTA must show the actual product, price, contents, disclosure, refund/delivery details and separate purchase step. No invented urgency or guarantee.

## Release boundary

No source-rebaselining or auto-merge, WordPress/CMS/navigation/homepage/analytics, email/social publishing, merchant/affiliate activation, duplicate measurement scripts, purchases or spending. No invented buyer, lead or performance claims. Cross-reference governing Issues #136 and #820 and charter #818.
