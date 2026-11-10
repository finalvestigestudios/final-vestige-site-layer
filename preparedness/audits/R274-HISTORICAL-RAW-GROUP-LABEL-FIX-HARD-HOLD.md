# R274 — source-review alias lookup corrected without rewriting historical URLs

**Status:** DRAFT / HARD HOLD / UNMERGED. **Scope:** Preparedness Issue #136; business coordination #820 / #818. **Date:** November 10, 2026.

## Confirmed inherited control defect

Independent Praxxis review of R272 observed that `inspect()` treated the archived group label as if it had to equal the terminal-slash-stripped review alias. The frozen historical crosswalk contains five group labels ending in a path slash, for example NCHFP ground/chopped meat, LOC item 2002564479, USFA high-rise guidance and weather.gov/nwr. The control therefore returns `INVALID_HARD_HOLD` on authentic source data, even though the rows and identities reconcile. R273 depends on that gate and is likewise blocked by the incorrect comparison.

## Correction, not approval

R274 separates `group["url"]` (the original, untouched raw label) from `review_key = alias(group["url"])` (an internal lookup only). Membership, collisions and identity comparisons use `review_key`; the original raw group label, `canonical_url`, every unmerged source URL, date, supports/notes field, claim scope, article and citation remain unchanged. The group label is required to equal the most frequently occurring exact raw URL among its original members; a deterministic lexical tie break preserves the crosswalk's original jerky label. That strict rule matched **all 32 authenticated historical group labels**. Invented group labels or fake reviewer/approval states remain rejected.

The new R272 Python gate is Git blob `13f9e06da710c500c4dc45dd013133d46e5d87ab`, replacing `97cacd40b2a4324696f746798b472251a42a53b6`. The R273 docket gate source SHA is re-pinned to `1ff75d8cb329cdfa027c6bbc8a6cc96aef276875`; R220 pre-export/post-audit pin constants are updated, preserving all original corpus pin identities. Neither the original 143KB docket nor original crosswalk or eight source files changes.

## Bounded verification — never claim native release

An independent read through the connected repository inspected **all eight original source blobs**, each matched its pinned SHA. An independent JavaScript provenance comparison reconciled all **244 source records, 202 exact URLs, 201 terminal-slash review aliases, 32 shared-URL groups, 15 duplicate-ID groups, one raw slash variant and 36 origin assignments**, with **zero lost/altered group members**. It separately confirmed the raw-label rule against every group; this is not a native Python audit of the original corpus.

Offline Python **73/73 isolated tests passed** against exact locally reconstructed production R272 and R273 code (matching their committed Git blobs): 50 inherited R273 tests from prior exact committed evidence, plus 23 local R274 adversarial tests. Python compilation passed. The newly committed R274 test file is additional source-bound regression coverage, **not yet executed against its exact Git blob** in the unavailable full checkout. Full original-data `python -I preparedness/tools/validate.py`, `build.py`, inherited suite and all 41 intended WordPress draft exports **NOT RUN**. Local shell GitHub DNS resolution still fails. Never report independent QD or publication PASS.

## Newly confirmed branch drift / integration governance

The frozen R200 SHA snapshots and their original source blobs remain pinned. Comparing live Claude branch refs now reveals **2/7 identical** (start and shelter) and **five not identical**: food diverged (ahead 1, behind 1); hist-food ahead 1; health ahead 1; hist-home ahead 2; hist-field ahead 1. The changed source/content branches MUST NOT be silently brought into the frozen 35-article slate. Triage each exact diff with its owner and independent QA before incorporating new reading claims. Keep frozen R200 identities while the differences are reviewed. This comparison does not mean their new content is wrong; it means it is not yet reconciled and source-pinned.

Independent QD PR #157 remains draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. Fixture QA PR #169 remains draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5` with a source-directory mutation case requiring the independent QA owner's review. Home lead PR #1689 remains draft at `f55c36b6598eec558dd8bb24e4c8988becc51be0`. No cross-ownership edits.

## Unchanged hard holds and commercial separation

All 32 URL/15 ID groups remain unadjudicated; Article #7's two CDC occurrences, Article #20's Ready.gov occurrence and chemical-contamination advice remain pending qualified source/safety review. Tool #104, Article #15 and the proposed wallet card require child-information privacy, accessibility and physical printing approval. No independent QD PASS, medical-safety or privacy certification.

Existing `https://finalvestige.com/preparedness/` is free; do not route to unreleased manuscripts/card. Grok/Praxxis TASK-008 owners must authenticate ONE already published family-communication/reunification asset_id, posting URL, rights and native-mobile destination or record **NO VERIFIED MATCH**. The existing Legacy Triage PDF is merely a provisional paid candidate, not an authorized Preparedness upsell until complete rights, privacy, delivery, checkout/refund/fee and founder review. Paid orders, qualified attribution and realized net revenue per 1,000 human sessions remain **NOT COMPUTABLE**, not zero. No WordPress/CMS, navigation, publication, social post, analytics, affiliate, merchant, email or spending change.

**Next:** exact full-checkout Python validate/build/inherited tests/41 export parity; independent review of five moving Claude branches; human source and safety adjudication; independently verify rights and paid delivery before any commercial CTA.
