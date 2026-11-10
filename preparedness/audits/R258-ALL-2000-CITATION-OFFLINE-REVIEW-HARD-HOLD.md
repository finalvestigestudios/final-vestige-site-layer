# R258 — All 2,000 Source-Claim Excerpts in an Offline, Held Review Surface

**OWNERSHIP:** Preparedness Archive source/citation safety integration only. Issue #136. Business acceptance cross-reference #820 / charter #818. **DRAFT / HARD HOLD.** No CMS, WordPress, navigation, content, email, affiliate, merchant, analytics, social or public release.

## New gap addressed

R254 created 562 human-readable source-group citation workorders plus two separately held Article #7 CDC contexts. R255's inert HTML review displayed those 564 contexts; R257 added the 1,438 remaining citations in an authenticated JSON complement, but did **not** make all 2,000 citations readable together in one review view. This distinction was independently reported in the existing TASK-008 handoff.

R258 supplies a deterministic, **in-memory, offline-only** 35-article HTML reviewer for the full 2,000-citation partition. Every author excerpt and its source-use witness is visible, without truncating the authored reading contexts. Original source URLs are displayed as escaped, unlinked review text; never fetched or presumed equivalent. Every article has ordered citation IDs; the three original disputed citation positions are conspicuously held.

The gate independently rechecks both R254 and R257 canonical SHA-256 receipts, all negative authorization flags, the 32/56 shared-source roster and source-to-citation membership, 562/1,438 nonoverlapping positions, all 35 distinct article slugs and each article's contiguous citation ordinals, the two Article #7 CDC outside-shared disputes and the Article #20 Ready.gov shared dispute. It rejects source IDs silently reassigned to other groups or shared source IDs incorrectly appearing in the complement.

The HTML is generated **only in memory**, escapes every authored excerpt and untrusted source URL, uses a restrictive self-contained CSP and no clickable source links, scripts, remote assets, forms or conversion CTAs. R220 records only counts + HTML digest/byte length, never saves or publishes the HTML.

## Implementation

- `preparedness/tools/r258_complete_offline_claim_review_hold.py` — strict upstream reconciliation and renderer.
- `preparedness/tests/test_r258_complete_offline_claim_review_hold.py` — isolated synthetic fixtures with 75 positive/adversarial tests, including escaped markup injection and fabricated receipt/review status, duplicate URLs, source-ID reassignment, omission, reordering and disputed-source drift.
- `preparedness/tools/r220_full_slate_draft_custody.py` — cryptographic Git-blob pin for R258, invokes R258 immediately after R257 and **before WordPress draft export**; fails closed and rechecks gate identity at the end.

## Executed verification / limitations

- Local Python `python -I -m unittest discover -s preparedness/tests -p 'test_r258*.py' -q`: **75/75 PASS**, isolated synthetic data, not authentic source claims.
- Local `python -m py_compile` on module + tests: **PASS**.
- Original locally executed blob identities verified against GitHub committed blobs: module `3f48d7612986626b4e0faf9dd004e322d6bc7806`; tests `c4836ac1680e686bfbcf406dd37d03f8e3951299`. R220 newly pinned gate and post-audit identity check.
- Current seven contributor branches compared against frozen original R200 SHA set: **7/7 identical** (2026-11-09 PT); QA PR #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic-fixture PR #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5` and homepage lead PR #1689 at `f55c36b6598eec558dd8bb24e4c8988becc51be0` checked, unchanged.
- **NOT EXECUTED:** authentic complete upstream R200→R258 end-to-end integration, native `validate.py` / `build.py` / inherited 36+ tests, actual 41 WordPress-ready artifacts, browser/print QA, source support adjudication, medical safety and independent QD. The container cannot resolve `github.com` for a trusted complete repository checkout. These runs MUST NOT be reported as PASS.

## Editorial release and source blockers

The 32 shared-source groups and every citation remain **unadjudicated**. Article #7 CDC water source scope (including chemical-contamination warnings) and Article #20 Ready.gov reference remain human-review holds. Article #15 / Tool #104 shorter-card personal-information, JavaScript-disabled and printing/disclosure issues remain open. No original articles, metadata, tool code, citations, evidence, routes or safety flags modified.

## Conversion-first, no activation

**Single audience:** households organizing emergency contacts and essential family records. **Proposed ungated free destination:** `https://finalvestige.com/preparedness/` (source/safety release still held). Existing Tool #104 may be an *optional printable companion only after the privacy and behavior gates pass*. **Legacy Triage** remains a provisional existing $19 family-records PDF offer, **NOT an approved Preparedness upsell**: verify complete file, intellectual-property rights, Access Keys/privacy implications, value/fit, founder authorization, merchant checkout/fulfillment/refund before any CTA. A tagged Grok creator asset must first be authenticated via the existing TASK-008 without creating new assignments.

OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER: Legacy Triage → optional free-guide-to-paid-tool bridge → product/rights/privacy and actual creator intent unverified → independent PDF audit and tagged-link mobile QA, then consent-based merchant-side checkout acceptance → **UNTESTED / NOT APPROVED** → Founder/Commerce/Grok/Praxxis. Qualified sessions → confirmed paid order → fees/refunds → realized net revenue per 1,000 qualified human sessions: **NOT COMPUTABLE** without genuine source attribution and merchant orders. No clicks are described as revenue.

**NEXT:** attempt complete native checkout/build/tests, independently adjudicate priority sources, original Tool #104 browser/print behavior, and review commercial authorization. This draft is not an independent safety or QD approval.
