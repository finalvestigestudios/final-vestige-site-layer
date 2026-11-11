# R292 — CSS comment/escape citation provenance hold (UNAPPROVED)

Date: 2026-11-11 PT. Own lane: Preparedness Archive integration and source/citation safety gates, Issue #136. Business cross-reference #820 / charter #818.

**DRAFT / HARD HOLD. DO NOT MERGE, PUBLISH, REWRITE ORIGINALS, OR CLAIM QD/SAFETY APPROVAL.**

## Exact dependency / scope
Stacked from draft R291 PR #2044, exact base commit `7e7ee36cea0931a7989406cc024999ac7a661afb`. Changes exactly three Preparedness-only paths: inherited source-level claim-context gate, synthetic regression test, this audit. The original 35 articles, six tools, source fragments/register, metadata, source URLs, citation IDs, historical evidence lock, WordPress exporter, canonical paths, safety states, and commercial offers are not altered.

## Reproduced failing source integrity case
Prior R291 source validator counted `<p><span style="display:/**/none">{{cite:a}}</span></p>` as a reader-visible source citation because inherited R288 tests only recognized contiguous `display:none` and R291's `style_flags` did not inspect comment-obscured display/visibility property/value pairs. Similarly `visibility:/**/hidden`, `content-visibility:/**/hidden`, `di\\73play:/**/none` and `display:n\\6f ne` could be counted or pollute nearby claim context. These are isolated synthetic examples, not observed production abuse or a browser rendering proof.

## Bounded correction
- Decode conservative CSS ASCII escape sequences **before** comment removal, preserving escape boundaries; recognize obvious `display:none`, `visibility:hidden|collapse`, `content-visibility:hidden`, including `!important`, CSS comments, and supported escape spellings.
- Reject hidden literal source markers, exclude matching hidden sibling prose from claim digests/excerpts and add the inherited `excluded-nonreader-sibling-context` flag.
- If dynamic CSS visibility uses `var()` or `env()`, flag `dynamic-css-visibility-unverified` for human review; citation ancestors carrying class/id selectors receive `external-css-visibility-unverified`. These flags are **not** evidence of visibility or a QD judgment.
- Retain source byte identity, literal span matching, parent R288 custody and all publication/medical/privacy holds.

## Exact local test receipts
- Newly created `test_r292_css_comment_escape_hold.py`: **102/102 PASS**.
- Unmodified inherited R288 (56), R289 (68), R290 (51), R291 (74): **249/249 PASS**.
- Mixed exact-source R288–R292: **351/351 PASS**, 0 failures, 0 skips (synthetic only).
- Python compilation PASS; no source-tree-writing fixtures.
- Python gate on the *incomplete* local partial checkout returned `INVALID_HARD_HOLD`, exit 3, with `R288 parent missing`; flags publication_authorized, independent_qd_pass, medical_safety_verified, privacy_approved all false. Do not conflate this with an authentic archive execution.
- Git blob of corrected validator: `8184a0ac79d8350d04a597d891fa57695516f7c6`. New test blob: `cc613c04239aad2e29e5559146a52f8b36bc9605`.

**NOT EXECUTED:** full authenticated checkout; native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, complete current-head integration tests, 41 authentic WordPress draft exports, browser/screen reader/print check, source-scope/qualified privacy/medical review. Container cannot resolve github.com/api.github.com, and mounted evidence contains only partial source/test files.

## Coordination and unresolved holds
All seven frozen Claude contributor refs compared with their R200 baselines on Nov 11: each **identical, 0 ahead / 0 behind**. Independent draft QA #157 exact HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic QA #169 exact HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` (separate actual-source-writing fixture remains QA-owned); homepage lead #1689 exact HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`. None modified.
21 historical article lineage discrepancies (four triple-different #27/#32/#33/#34), 32 shared URL groups, 15 repeated source-ID groups, three contested CDC/Ready.gov occurrences, Article #7 chemical-contamination advice, and Article #15 / canonical Tool #104 privacy/no-JS/print concerns remain unresolved. Editorial independently reported a Tool #104 minimal-print disclosure-versus-JS mismatch; do not call that qualified verification or modify the editorial owner's draft. NO QD PASS.

## Conversion-first restriction (no activation)
**ONE audience:** households organizing emergency contact and family reunification plans. **Authentic existing free landing:** https://finalvestige.com/preparedness/ (currently public official-source resource archive, not the held 35-article slate). **One paid candidate:** $19 Payhip Legacy Triage page https://payhip.com/b/n1RhV, presented under **Vested Wisdom** (not independently demonstrated to be FV-owned/licensed); financial/end-of-life organizational PDF may not fit school pickup/reunification intent. Rights, seller identity, buyer intent, availability/checkout completion, fulfillment, refunds and privacy remain unverified. No paid CTA, no held child card, no retired water freebies.

Offer → funnel step → blocker → change/experiment → evidence → owner:
1. Free guide → reader trust → CSS-obscured citations → R292 source-level gate → 351 synthetic local PASS; authentic full-tree UNRUN → Preparedness Integration.
2. Existing Grok post → free Preparedness landing → no authenticated matching live family-contact asset `asset_id`, post rights or mobile destination → TASK-008 owner validates existing post, not new content → NO VERIFIED MATCH → Grok/Praxxis.
3. Free guide → optional practical tool → Tool #104 child-information/privacy/print/no-JS mismatch → independent qualified and browser review → HARD HOLD → Preparedness editorial/QA.
4. Free guide → proposed paid pack → Legacy Triage seller rights and audience/merchant delivery unverified → audit product PDF/license/checkout mobile and refunds **without purchasing or altering offers** → NOT APPROVED → Founder/Commerce.
5. Attributed customer journey → settled paid revenue → no verified orders/fees/refunds or qualified-human session denominator → implement only accepted existing privacy-respecting event mapping after consent/approval → NET REVENUE PER 1,000 QUALIFIED HUMAN SESSIONS **NOT COMPUTABLE** (not zero) → Commerce/Analytics.

7/30-day attribution requires `utm_source`, `utm_medium`, `utm_campaign`, `utm_content=asset_id`; distinct landing, CTA, confirmed lead, verified order/merchant affiliate paid conversion, refund/fee states. Clicks, signups, impressions and checkout starts are never sales. No new measurement scripts, social posts, queue edits, WordPress/CMS/navigation, product, affiliate, email or spending actions.
