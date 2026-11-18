# R463 — full 35-article citation/source-use integrity (2026-11-18 PT)

**Draft / HARD HOLD. Issue #136; conversion governance #820; charter #818. Preparedness-only, read-only.**
Parent R462 draft PR #3015, HEAD `edda6a3529b430a47ceee395742044a2b3c49bc4`.
This is a provenance / structural review and NOT a semantic source-claim review, qualified emergency/food/medical review, QD pass, native-build pass or publishing approval.

## Exact authenticated inputs and read-only observations

- Original R460 nine-origin snapshot Git blob `056d14cd97d29b843d52912383c237b9122e73ef`.
- Exact R462 shared-URL crosswalk Git blob `d62e493a67dedd23e04cfdf3cce762ef933c6bf9`.
- At PR-branch HEAD, Git tree verified **70/70 original article body/metadata Git blobs** against R460 and **8/8 original source-file Git blobs** against R462; no original article/source files edited.
- Independent GitHub content reads covered **all 35 article bodies and 35 metadata files**: **2,000 literal `{{cite:id}}` occurrences**, **385 article-to-source-use memberships**, and **0 orphaned citation IDs / 0 unused `source_use` IDs** across these authored pairs. These 2,000 literal tokens and 385 article/source memberships are different units from the older 280-occurrence historical audit and the 244 original raw source records; do not conflate the denominators.
- All 35 authored metadata files still say `status.publish=draft`. The original `safety_review.state` records are 29 pending, 4 not-required, 2 approved (historically recorded, NOT qualified QD approval for the full slate).
- 32 original shared-URL source-reading-scope groups remain pending human review. Five semantic source disputes, nine unselected original manuscript/source forks, 17 R461 divergent articles and four changed source-fragment groups remain independently unresolved.

## New additive enforcement

`preparedness/tools/r463_article_citation_use_custody.py` reads original body + metadata from frozen Git blob pins; rejects duplicate JSON keys, missing/symlinked files, altered body/meta or source registers, missing source-use notes, malformed citations, silently dropped/retargeted article citation IDs, unresolved sources outside an article's own origin or the base, publication-state changes and unsupported safety states. It reports own-origin vs base fallback and source-ID cross-origin URL discrepancies without coalescing them. Reuses R462 exact shared-URL reviewer custody and retains all eight source file origins; no source is rewritten. The **CLI always exits 2 (HARD HOLD)**, even if structural custody succeeds.

## Test and release boundary

- Exact Git-blob-matching local Python compilation and **69/69 R463 isolated synthetic tests PASS**, including 61 explicitly named adversarial mutation tests. Tool Git blob `ef45e3e29a37a86368b7d95786ef7e3fc4f6b671`; test Git blob `5d7d75b52e08900e635b3c4f6ec9c217b61ccf2d`.
- Complete original native `validate.py`, `build.py`, entire test suite, real 35-article WordPress/private-preview exports and R463 native CLI against full authenticated checkout: **NOT EXECUTED**; this run's container lacks the complete source checkout. R463 native CLI returned `exit 2` with missing R460 snapshot; that is a failure/HOLD, **not** a structural native PASS.
- R462 59 tests last run were on a local equivalent prototype, not exact committed suite. Do not upgrade that evidence.
- QA #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and food fixture #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` inspected, both draft/unmerged. Dependent repair #2205 HEAD `bbcf1859768624c611df4abadc564c18247cf32a` draft/unmerged. Independent editorial #2789 HEAD `b80643c09a2d0784b662883e7ed43d8fc27bdbff`, home Apollo #3012 HEAD `31d64399726302375a7669817417983e174268eb`; untouched.
- Seven original Claude refs plus two Shelter descendants rechecked at frozen R460 heads (see Issue #136 receipt).

## Conversion-first owner matrix (NO paid CTA)

| OFFER / FUNNEL STEP | BLOCKER | CHANGE OR EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| One *actually payable*, FV-owned, rights-cleared Preparedness pack → merchant-confirmed order | No qualifying merchant SKU, ownership, delivery/refund and settlement evidence | Founder/Commerce must authenticate a **real** existing SKU and licensed delivery before any relevant optional paid pack CTA | **HOLD / not authenticated** | Founder + Commerce |
| Real Grok on-topic family-contact asset → **free** published Preparedness official planning page | No verified already-published matching asset ID, timestamp, rights or permitted mobile click path | Praxxis independently match one real published on-topic asset and permitted destination; Grok retains posting control | **UNMATCHED** | Grok/Praxxis |
| Source-backed free agency checklist → optional Tool #104 (unpublished) | Article #15 and Tool #104 child-privacy/911 wording, live link accessibility, print and qualified safety reviews | Separate contextual free CTA only after exact official link/mobile proof; Tool #102 remains distinct | **HARD HOLD** | Preparedness/QD |
| Qualified-human sessions → relevant CTA → confirmed lead → merchant-paid order → refunds/fees → realized net revenue | No verified full-funnel attribution and merchant settlement | Reuse Claude's authorized consent-safe measurement; 7/30 day cohorts and tiny-sample caveats, no duplicate scripts | **NOT COMPUTABLE** | Claude/Commerce |

Public /preparedness/ explicitly promises free ungated official guidance. No paid commercial claims, hypothetical offer activation, retired water freebies, false conversions, CMS writes, social publishing, newsletter, analytics deployment, spending, merge or QD PASS.