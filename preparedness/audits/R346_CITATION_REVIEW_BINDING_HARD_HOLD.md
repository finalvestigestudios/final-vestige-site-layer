# R346 — Preparedness disputed-source decision binding — DRAFT / HARD HOLD

**Scope:** Issue #136 only; business source-of-truth #820 and charter #818. No public or source changes. The branch is stacked on unmerged R345 (#2365, `d34f2637d37f8ccf2382ca4cacf49ba4d8b1e1a8`). All new paths are additive under `preparedness/`. This gate supplies a *review-proposal preflight*, not approvals, evidence verification, a WordPress export, or a commercial conversion.

## Exact predecessor and threat model

R345 freezes original R344 source fragments and exposes quarantined citations associated with four competing verified source identities: `fsis-power-failure`, `nchfp-home`, `loc-prairie-traveler`, `loc-pioneer-diaries`. R345 original Python source blob SHA is `9712a220212508f832fb05083c7a3a03e84412e4`; R346 native execution rejects its replacement or absence. There are twelve metadata `source_use` dependencies across ten private drafts from the preceding R345 observation; these are **not** a substitute for the paragraph-level citation-ticket set until the native R343/R345 audit completes.

A source adjudicator could accidentally or maliciously pair a source variant with **stale** article text, reassign one ticket to a different source, omit a ticket, accept a fabricated source file, confuse two variant records, inject false `QD_PASS` or approved claim states, or present an unauthenticated reviewer name as proof. R346 conservatively validates **all four** expected source IDs against their **two original source-file paths** each, distinct 64-hex source-record SHA-256s, source packet SHA-256, every exact ticket ID and its claim fingerprint, affected document identity, zero duplicated tickets across packet/source boundaries, and an explicit unapproved disposition. It rejects unknown or additional approval-like fields, missing or altered tickets, changed packet fingerprints, duplicate packets/proposals, unsafe rationale control bytes, and non-frozen input.

**Even four correctly formed proposals yield `PROPOSALS_STILL_UNREVIEWED_HARD_HOLD`**. The tool does not authenticate humans or source link checks, inspect primary documents, decide semantic claim support, choose a verified source winner, or set QD or publication states. Every output has `may_publish=false`, `may_merge=false`, human review/medical safety/merchant evidence false. It does not write to disk, the source tree, WordPress, analytics, the funnel, or users.

## Reproducible tests / exact identities

- `preparedness/tools/r346_source_claim_decision_binding_hold.py`: committed Git blob `ffa0e61d36d954d6e67bc66dadab590d7cd99cc9`.
- `preparedness/tests/test_r346_source_claim_decision_binding_hold.py`: committed Git blob `83464596b88ac89fe53775c7a1dc086063b002b0`.
- Local Python execution: **76/76 new** and **240/240 combined R344/R345/R346 isolated** tests PASS, Python bytecode compilation PASS. Executed R346 code/test bytes **match their exact committed Git blobs**. The 164 inherited R344/R345 tests are an offline local reconstruction, not a native checkout certification.
- Missing-complete-checkout native negative control: `INVALID_HARD_HOLD`, refuses all approvals. The nine original Claude/Shelter heads were independently re-compared to their pinned SHAs (`identical`, ahead 0/behind 0). Home lead PR #1689, independent QA #157, food fixture #169 and its unmerged dependent correction #2205 were inspected; no external owner branch modified.
- **NOT EXECUTED:** genuine repository `validate.py` / `build.py`, original 50 WordPress + 50 preview rendered exports, browser/mobile/print safety, CI, qualified human emergency/medical/privacy/source review and QD.

## Existing holds preserved

1. Fifteen contributor editorial/source conflicts remain separate and unresolved; 35 original article bodies and six tool bodies remain draft/private without source or URL changes.
2. Original seventeen Article #15 / Tool #104 emergency/child-privacy claim review obligations remain; separately identified animal-access, FEMA source age and airplane-mode/WEA issues remain for qualified review. Tool #102 (plan) is distinct from Tool #104 (wallet card).
3. QA #157 includes draft wording and tests not applied to the canonical integrated corpus. QA #169 still contains an original canonical-source-writing synthetic duplicate fixture; #2205 is a separate unmerged fix. Never treat passing synthetic tests as safety clearance.
4. No `human_link_check=true` source proof or independently adjudicated source-to-claim support has been produced by this gate. No private tool can be advertised.

## Conversion-first funnel and acceptance (no new merchant, post or tracker)

| Offer | Funnel step | Blocker | Safe change / experiment | Evidence / owner |
|---|---|---|---|---|
| ONE existing FV-owned Preparedness practical pack, **not authenticated** | Actual payable checkout → fulfilled digital file → settled paid order | Seller ownership, rights/license, SKU, genuine checkout, mobile delivery, refund/fees and merchant reconciliation absent | Founder/Commerce to privately verify an existing suitable SKU before any paid CTA | **HOLD, no verified sale** / Founder-Commerce |
| Existing free official-agency `/preparedness/` archive | Reader discovers relevant family-contact guide/tool | Detailed Article #15 / Tool #104 are unreleased; safety and source holds | Draft CTA **“Start With Trusted Preparedness Resources”** to existing free archive only, with 360/390/768/1440px, keyboard, consent, official-link, disabled-tool and no false-paywall checks | **NOT DEPLOYED, no validated mobile click path** / Preparedness-QD + Claude site |
| ONE genuinely already-published on-topic Grok family-contact asset | Unique `asset_id`, permitted platform URL → qualified landing | No independently authenticated matching social asset, placement or clickthrough | Praxxis checks real source post, timestamp, exact topic, `asset_id`, permitted mobile destination in TASK-008; Grok retains content and posting | **UNVERIFIED** / Grok-Praxxis |
| Qualified sessions → relevant CTA → confirmed lead → merchant-verified order → net revenue | 7/30-day deduped cohort | No actual unique qualified-human denominator, attributed confirmed lead, paid order, fees/refunds/settled affiliate amount | Claude/Commerce reconciles existing approved measurement tools, no new trackers | **NOT COMPUTABLE: net realized revenue per 1,000 qualified humans** / Claude-Commerce |

**No retired water offer, false urgency or order/conversion claim, unapproved product CTA, CMS/navigation/social/email/analytics/affiliate change, public publication, spending, merge or release.** Human safety clearance and founder release must remain separate gates.
