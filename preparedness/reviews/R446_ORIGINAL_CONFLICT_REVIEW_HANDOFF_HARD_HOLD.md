# R446 — Original 35-article qualified-adjudication queue and exact source/fork custody

**2026-11-17 PT | Preparedness Integration #136 / P0 #820 / Charter #818 | DRAFT / HARD HOLD | no publication permission**

## Engineering lift: materially advance the real source-review blocker

R445 established an exact 203-ID/181-URL crosswalk but left five original source-scope disputes and nine article/metadata/source forks unselected. R446 builds a **concrete immutable-input reviewer packet** from the **authentic** R397 original docket, so independent qualified reviewers can adjudicate the specific full claims, reading depths, literal source URLs, and original variant candidates rather than relying on counts or generic HOLD wording.

- Original immutable source: `preparedness/reviews/r397_original_source_fork_docket.json` at PR #2656 commit `a22c8797da58ecf186f50fcf47063bd195fd3c17`, Git blob `86d22a1d504c93db7689b914e2202a7845b648e2`.
- New review data: `preparedness/reviews/R446_AUTHENTIC_R397_CONFLICT_REVIEW_QUEUE.json`, Git blob `0e655316ced77212abeff77459898253a1e768fd`. Verified exact GitHub readback at commit `bf619b7bdd6f16b8815bd0a3a0bdbe3487ea9ad9`.
- New offline integrity gate: `preparedness/tools/r446_original_review_packet_integrity.py`, readback blob `22fce83083bbb5aa16cef2e0a53438f8b9abe457` at commit `c9b79eb6d3520acc5147afdbf07a61d31efe06ac`.
- New synthetic tests: `preparedness/tests/test_r446_original_review_packet_integrity.py`, readback blob `76cf8c3febcd0baa4de2616d528510642c4f9c99` at commit `d4342a624901dedae4d202756367633386eefd5c`. **67 committed discoverable test methods; exact committed Python execution NOT performed.**
- Independent read-only authenticated original-vs-packet replay: 35 article candidate identities, 203 source IDs, 280 occurrences, 181 exact literal URLs, 17 reviewed exact shared URL groups, **five full claim/scope variant pairs**, nine unselected file forks, nine contributor pins: **ZERO relationship mismatches** (not a safety PASS).
- Original branches freshly compared to R397 full SHAs: all 9 **identical, 0 ahead / 0 behind**. Original seven Claude cluster branches and two Shelter follow-ups untouched.
- Existing independent QD #157, synthetic fixture #169, dependent #2205, homepage #1689 and concurrent Article #11 editorial #2789 reviewed by current metadata; remain outside this edit lane.
- Local standalone companion `r446_original_adjudication_queue.py` built separately and its **61/61 synthetic Python tests PASS**, compilation PASS. This is *not* direct execution of the new GitHub-integrity module; source/test readbacks alone are not runtime proof.
- **Native full 35-body validate.py/build.py, 70 genuine WP/private-preview HTML exports, actual style/browser checks and independent qualified QD/medical/food/fire/emergency/child privacy review NOT DONE** because the authenticated full checkout/export evidence is not present locally. All original disputed decisions stay `HUMAN_REVIEW_REQUIRED`, not automatically selected.
- Hosted GitHub CI status for this exact final HEAD to be inspected separately. No CI PASS is claimed until genuine executed steps and logs are available.

## Named reviewer work queue (all unapproved)

1. `fsis-power-failure` — authenticate FSIS page's timing assumptions, temperature bounds and context; qualified food reviewer.
2. `loc-pioneer-diaries` — separate LOC collection catalogue metadata from unread original diary entries; qualified historian.
3. `loc-prairie-traveler` — reconcile original scan/OCR/page-level read depth against any third-party transcription; qualified historian.
4. `nchfp-home` — homepage hub vs tested process; never promote a homepage alone into a specific recipe or safety protocol; qualified food preservation reviewer.
5. `nchfp-jerky` — reconcile agency/species/drying, heat treatment, parasite and revision-specific bounds before any consumer safety prose; qualified food reviewer.
6. Nine genuine forks retained separately, covering family communication, home fire escape, outage heat/cold/generators, shelter/evacuation bodies+metadata and Shelter source fragment: **no manuscript selection**.
7. Seventeen exact shared-URL source-ID groups retained for a separate duplication/claim-scope reviewer decision, **no automatic merging of source identities**.

## Execution instruction for authenticated full checkout

```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r446_original_review_packet_integrity.py --original /path/to/authentic/r397_original_source_fork_docket.json --packet preparedness/reviews/R446_AUTHENTIC_R397_CONFLICT_REVIEW_QUEUE.json --observed-heads /path/to/captured_current_nine_head_shas.json
```

**R446 gate returns code 2 / DRAFT_HARD_HOLD even on a structurally consistent packet, by design.** Reviewer packets do not authorize publication, resolve medical advice, or approve a product.

## Conversion-first acceptance — strict owner boundary

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| ONE currently owned FV Preparedness pack → payable checkout → delivery → confirmed net order | No authenticated rights-cleared seller/SKU, payable checkout, fulfillment, refunds, fees or settlement | Read-only founder/Commerce inventory; authorize one appropriate product *before* any paid CTA | **HOLD** — not verified purchasable; no net revenue | Founder/Commerce |
| Genuine published family-contact/reunification video → free official Preparedness Archive | Unmatched real Grok `asset_id`, post/date, rights, spoken claims and mobile destination | Praxxis independent verification using existing TASK-008, without new creator requests | **UNMATCHED**, no campaign attributed sessions | Grok/Praxxis |
| Free official household checklist → optional practical downloadable tool | Article #15 emergency accuracy, child privacy/print accessibility, Tool #102/#104 identity and URL/QD approval | One unpublished free CTA concept; preview only, essential emergency resources never gated | **HARD HOLD** | Preparedness/QD |
| qualified human `asset_id`/UTM session → CTA → confirmed lead → independently paid order → net fees/refunds | No merchant settlement, confirmed subscribed cohort or privacy-safe joined 7/30-day denominator | Claude/Commerce read-only measurement contract, no duplicate scripts or consent changes | **NOT COMPUTABLE** net revenue/1,000 qualified humans | Claude/Commerce |

Unpublished candidate: **“Review the official household emergency checklist.”** No retired water offer, speculative SKU, fake urgency, unapproved affiliate link, paid CTA, email/social post, analytics activation, CMS/nav change or spending.

**DRAFT / HARD HOLD. No merge, qualified QD pass, site publication, WordPress writes or commercial release.**