# R253 — Cross-cluster source variants × 2,000 cited contexts (DRAFT / HARD HOLD)

**Date:** 2026-11-09 PT. **Scope:** Preparedness Issue #136; conversion decision #820; founder charter #818. **Review only. No merge, CMS, public publishing, product activation, analytics installation, email or creator-channel changes.**

## New engineering deliverable

R235 already independently authenticates **244 source inventory rows** and a **32-group shared-URL review queue**. R237 independently extracts **2,000 individual citation occurrences** across the **35-article frozen slate**. Before R253, the two inventories existed separately: source variants could not be browsed in one receipt alongside all the exact article-number/slug/source-ID/citation-ordinal/claim-context evidence they touch.

R253 adds a *deterministic, provenance-preserving join*, not a source merger. Each of the 32 shared-source groups retains its exact URL, all source IDs, branch origins, source-scope variants, verification-date variants and source-evidence SHA-256. Each cited occurrence sharing one of those IDs receives its original article number, author slug, contributor cluster, ordinal, context SHA-256, author-source-use note SHA-256 and context-derived reviewer risk terms. Unmatched source-variant groups are preserved as separate pending workorders, not dismissed or auto-approved. The other cited occurrences remain separately counted and are **not** falsely assumed to belong to a shared group.

All 32 groups retain **PENDING HUMAN SOURCE-SCOPE AND CLAIM REVIEW**. The three original disputed citation occurrences remain separately constrained: **Article #7 / CDC twice; Article #20 / Ready.gov once.** Keyword-derived `HIGH_CONSEQUENCE_REVIEW` is a triage cue, **not a safety verdict**. The word/phrase risk scan does not replace qualified review of every claim.

The R253 code rejects lost/duplicated article and occurrence identities, dropped crosswalk groups, an ID mapping to multiple URLs, altered reader-context checksums, missing source-use note identities, silent human approvals, mutated QD/commerce/release flags, unrepresented original contributor clusters and corpus/count drift.

The existing R220 pipeline now cryptographically pins the R253 module, invokes the join **after independently authenticated R235 and R237 receipts and before any WordPress draft rendering**, requires 35 / 2,000 / 32 / 7 / three-held consistency, and rechecks the R253 Git-blob identity at audit completion. The new read-only script never writes a WordPress draft itself.

## Verification and limits

- Exact committed Git blob for the Python gate: `4456a15606a3787b348cc4d540a2ea40299a0ee5`.
- Exact committed Git blob for its Python tests: `5e1d311c3f1703dd446940338eca8e0ebaa135d3`.
- Locally executed: **74/74 isolated Python unittest methods PASS** (35-article / 2,000-citation synthetic receipts), `python -m py_compile` PASS. GitHub fetch-back independently confirmed both committed blobs match the executed local bytes.
- Static source-document review: actual crosswalk `preparedness/sources/crosswalk.json` blob `d62e493a67dedd23e04cfdf3cce762ef933c6bf9` contains **32** pending groups; IDs clean under safe-slug rule, no group URL duplication or source-ID-to-different-URL conflict; all variants' human link checks are false. This is a source-file inspection, **not the native R235/R237/R253 execution**.
- **New independent authenticated full-body static census (separate from Python execution):** All **35/35** individual original/integrated article HTML bodies were fetched via the connected GitHub API in five seven-article batches; all 35 Git blob identities match R200 originals or the explicitly allowed R219 integration overrides. The full bodies contain **2,000/2,000** syntactically recognized `{{cite:...}}` occurrences. **562 occurrences** have a source ID present in the 32 shared-URL crosswalk groups (56 distinct group source IDs); **1,438** occurrences do not share one of those crosswalk group IDs. This is a **static, source-ID overlap census**, not a 562-claim human verification, full source-use parity run, semantic support check or WordPress verification. Initial all-at-once connector attempt exceeded call limit; smaller batches completed. No article content changed.
- Original branch heads verified **identical via GitHub compare**: start `2122d856`, shelter `5daeaf2d`, food `f911ff7a`, health `d5ef5baf`, hist-field `4e5caf81`, hist-food `67e116e5`, hist-home `7504a5f0`.
- Independent QA PR #157 exact HEAD `7d1ae6b8`: read-only, unmerged. Synthetic-fixture PR #169 exact HEAD `e9cd7766`: read-only, unmerged. Homepage lead PR #1689 exact HEAD `f55c36b6`: read-only, untouched.
- **NOT EXECUTED:** native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, inherited `python -I -m unittest discover -s preparedness/tests -v`, complete authentic R220/R253 pipeline, authentic 41 WordPress exports, end-user/browser printing/network evaluation. The local environment cannot resolve `github.com` for complete clone; a separate bulk GitHub connector read also hit its tool-call limit. Counts refer to inherited pinned receipts unless explicitly inspected. No independent source, medical or QD pass.

## Source and safety workorders still open

1. Article #7: the CDC household-water sentence omits **tap-water heater** versus home-heating-system distinction and **uncontaminated ice** qualification. No automatic copy change.
2. Article #7: upstream creek scenario orders `stop if fuel/chemicals/waste possible` then `collect/clear/boil`, followed by a comparative-boiled-is-safer conclusion. Independent qualified reviewer should assess whether readers could infer that boiling makes **chemically contaminated** creek water usable, and whether a stronger explicit stop condition is needed. This is an editorial safety question, **not an approved treatment protocol**.
3. Article #20: `https://www.ready.gov/plan` language consideration claim remains unverified (fresh 403); no approval.
4. **32 shared-source groups** need real source reading/scope reconciliation; **Tool #104** shorter card, JavaScript-off behavior and privacy wording need independent decision, real browser/printing tests.

No body, metadata, taxonomy, source register, original citation, route or existing safety state changed.

## Conversion-first single provisional route (not approved)

Audience hypothesis: households collecting emergency contacts and family records. **Ungated free landing:** existing `https://finalvestige.com/preparedness/`. A matching **already-published** Grok asset ID/platform post/date/hook/rights/mobile destination is still unknown; TASK-008 research-only coordination, no new creator assignment.

**Optional paid candidate, not approved:** Legacy Triage publicly listed PDF (`https://payhip.com/b/n1RhV`, previously observed $19). A preparedness-fit audit of the *complete* file, rights, handling of sensitive family documents, checkout, payment settlement, delivery, support and refund experience are required before linking or selling it as a Preparedness upsell. No price or checkout is independently revalidated this run. No paid CTA, new offer or retired water freebie.

| Offer → funnel step | Blocker | Change / experiment | PASS/FAIL evidence | Owner |
| --- | --- | --- | --- | --- |
| Verified Grok clip → free public /preparedness/ | No independently verified matching published asset_id/mobile route | TASK-008 existing-asset URL/date/rights audit only | UNVERIFIED | Grok/Praxxis |
| Free guide → source-backed archive guidance | 32 shared-source scope groups, 3 held citation occurrences, native build not run | Use R253 32-group-by-claim reviewer queue; qualified human source/medical review, authentic native build and independent QD | SYNTHETIC TESTED / RELEASE HARD HOLD | Preparedness + independent QA |
| Free guide → practical family card | Tool #104 shorter-card six personal fields, JS-off and privacy copy conflict | Human correction decision and real browser/print/privacy validation | REVIEW ONLY / HARD HOLD | Preparedness Editorial/QA |
| Free guide → optional Legacy Triage PDF | Product suitability, actual rights, delivery and sensitive-data precautions unknown | Commerce completes file/rights/fit QA before any optional price/CTA | NOT APPROVED | Founder/Commerce |
| Optional paid PDF → confirmed revenue | No verified acceptance, completed order, fulfillment/refunds | Authorized merchant evidence and 7/30-day cohort reconciliation | NOT TESTED | Commerce/Analytics |

Measurement only if a real authorized asset becomes available: unique `asset_id`/`utm_campaign` → qualified human landing session → relevant CTA click → independently confirmed lead if applicable → verified paid order/affiliate payout → fees/refunds → **realized net revenue per 1,000 qualified human sessions**. Numerator and denominator unavailable; KPI **NOT COMPUTABLE**. Outbound clicks and leads are NOT sales.

**Status remains BUILT / ISOLATED TESTED / DRAFT / HARD HOLD**, with neither publisher nor commercial authorization.
