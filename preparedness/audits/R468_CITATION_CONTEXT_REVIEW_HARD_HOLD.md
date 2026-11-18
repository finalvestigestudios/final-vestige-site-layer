# R468 — citation-context witness docket (review only; HARD HOLD)

**Date:** 2026-11-18 PT. **Lane:** Preparedness Archive integration and source/citation safety (#136) only. **Business:** #818/#820. **Parent:** R467 draft PR #3040, exact parent HEAD `ce66362cb748bee2d26bc8aa1bf6f0d139993fbe`.

## New nonduplicative engineering lift
R463 established a 35-article/2,000-citation/385-source-use census. R468 adds the missing **citation-adjacent authored context**: an ordered HTMLParser text-unit docket, one immutable source-ID/literal-URL/cluster-origin/reading-scope witness per citation occurrence, and SHA-256 fingerprints of original complete body and normalized review text. This makes a changed sentence or warning visible to human review **even if all citation IDs/counts remain identical**. Shared URLs stay literal and separate; source-use notes are not deduplicated. The pure comparison function identifies body/context, literal URL, reading scope, and citation-order drift and never chooses a preferred manuscript.

The native reader calls the existing R463 pinned-original gate first and reads only R460 exact-blob-pinned metadata/manuscripts and R462 exact-blob-pinned source registers. Its final JSON is **CITATION_CONTEXT_REVIEW_REQUIRED** (or **CITATION_CONTEXT_FAILURE_HARD_HOLD**). The CLI **always exits 2** and always sets claim support, medical/food/emergency/QD release and publication false. No internet retrieval, scripts, WordPress, API writes or human data. This is a mechanistic context docket, not independent source corroboration, current official URL availability verification, HTML sanitizer, medical safety certification, or native export proof.

## Exact executed local evidence
- Source file: `preparedness/tools/r468_citation_context_docket.py` Git blob `c9b3d9d6e5f144f3747cb22ba75dc3493d8700e3`.
- Test file: `preparedness/tests/test_r468_citation_context_docket.py` Git blob `842f8cf6833a9b0922beaac9ade61740d8dd3097`.
- Both new remote Git blobs were fetched back and **exactly matched** the locally executed Python bytes.
- `python -I -m py_compile`: PASS.
- New isolated adversarial tests: **140/140 PASS**, including 40 unique contextual text mutations, 40 authored reading-scope mutations, 20 missing-source denial cases and 20 non-draft denials.
- Combined local synthetic `python -I -m unittest discover -s preparedness/tests -p 'test_r46*.py' -q`: **624/624 PASS**, using the exact local copies of R463, R465, R466 and R468 files.
- Native `python -I preparedness/tools/r468_citation_context_docket.py --root preparedness`: **exit 2 / HARD HOLD**, missing original authenticated `R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json` in runtime. No full authenticated original 35-article build, WordPress-ready or private preview export executed. No CI PASS claimed.

## Independent coordination
Nine frozen Claude/Shelter contributor branch HEADs were re-compared with the R460 recorded SHAs, all `identical`, zero ahead/behind. Independent QA #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, food fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, repair #2205 `bbcf1859768624c611df4abadc564c18247cf32a` remain open and unmerged. Home/Apollo is a separate owner; Article #11 editorial #2789 is not imported. Five original semantic source disputes, nine unselected manuscript forks, 17 divergent articles and 32 distinct shared-URL source-scope groups all remain HUMAN REVIEW REQUIRED.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER
| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| One FV-owned/licensed Preparedness practical pack (not authenticated) | verified purchase and delivery | rights, existing payable SKU, checkout, fulfillment, refunds and settlement absent | authenticate **existing** authorized SKU before any paid CTA | **HOLD**, no paid product or sale verified | Founder / Commerce |
| Existing free ungated public Archive `https://finalvestige.com/preparedness/` | relevant social visit → free guide | no matched published Grok family-contact/reunification asset_id, actual hook, rights, permitted signed-out mobile URL | Praxxis independently verify one **already published** matching asset then map asset_id/UTM; no new posting assignment | **UNMATCHED**, qualified-human sessions unknown | Grok / Praxxis |
| Original household family-contact guide → optional Tool #104 | free guide → downloadable planning tool | Article #15/Tool #104 medical/emergency, child privacy, accessibility and print QD held | independent qualified safety/source review; preserve Tool #102 identity; no gated free safety help | **HARD HOLD**, no public tool CTA | Preparedness / QD |
| Verified human referrals → lead (if applicable) → merchant-confirmed purchase → net revenue | attribution and 7/30-day cohorts | no actual confirmed orders, fees/refunds, consentful attribution | specify 7/30-day reconciled receipts; do not deploy duplicate analytics scripts | **NOT COMPUTABLE** net revenue / 1,000 qualified sessions | Claude / Commerce |

No retired water freebies, no speculative offers, no affiliate activation, no overclaiming. No merges, publications, site/navigation/CMS edits, social posts, emails, tracking deployment or spending. Founder retains release authority.

**Next gate:** execute R468 in an authenticated full checkout after R463/R462/native validate/build, record 2,000 exact context events and preserve reviewer attention for safety-critical claims before any possible release.
