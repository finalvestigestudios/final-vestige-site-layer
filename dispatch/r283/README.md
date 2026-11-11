# Dispatch R283 — single-offer buyer-fit and funnel truth review

**2026-11-11 | UNSENT, NOT ADOPTED, NOT DEPLOYED.** Dispatch owner [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); Mind affiliate owner [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), revenue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Stacked on R282 [#2057](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2057); original six unchanged in [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175). Existing gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), homepage PR #49 frozen.

## Why this is distinct from earlier alternatives

Source-of-truth observation: the live [Focus](https://finalvestige.com/focus/) page visibly offers a direct PDF download along with the subscribe form. A PDF click therefore cannot be counted as provider-confirmed signup, nor as successful welcome delivery. The live [Dispatch](https://finalvestige.com/dispatch/) form uses the same Jetpack newsletter. This is one list, not two audiences. Counts total=3, confirmed=3, unconfirmed=2, WordPress.com followers=3 and email followers=0 are disjoint/overlapping operational views, **not additive** and not actual deliverable recipients. Latest five WordPress post-send records were never_sent_opted_out, not a complete historical email ledger.

The optional Issue 03 editorial cut offers **one blocked guide CTA** and near-CTA disclosure. It does not refer readers back to a lead magnet they already received as an additional marketing action. Seller-described Zen12 12 levels / 48 MP3 files is distinguished from research on meditation generally; no specific effectiveness parity or improvement promised. Sources: [seller checkout](https://zen12.com/getstarted), [NIH NCCIH evidence review](https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety), [public Inspire3 partner page](https://affiliates.inspire3.com/). The public affiliate page is **not publisher-specific acceptance, email rights or an earning URL**. No current campaign price or purported seller countdown is used.

Files: issue03_review.md, issue03_plain.txt, reviewer_preview.html, claims_and_gates.json, funnel_truth_table.md, test_r283.py. No sendable output, subscriber data or merchant earning links. The static HTML only previews review text; it is NOT actual Jetpack MIME or preview. Text preheader not proven to be configurable in WordPress.

## Priority matrix — OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer/funnel | Blocker | Proposed review-only experiment | Today | Owner |
| --- | --- | --- | --- | --- |
| Zen12 → buyer guide | No publisher email permission, earning URL or live vetted guide | Require merchant owner attestation, authorized guide, specific sales terms | HOLD_MERCHANT | Mind #171 |
| Focus → eligible subscriber | Direct PDF click ≠ confirmation; provider category counters conflict | Dedup 1 authenticated provider transition across two pages | Eligible audience UNKNOWN | Focus/Claude #129 |
| Dispatch → inbox | Postal address, unsubscribe function, actual rendered MIME unverified | No-send WordPress editor preview, then separately authorized recipient test | NOT TESTED | Dispatch #174 |
| Grok → Focus | Actual asset ID and verified human sessions missing | Existing source/campaign contract only; no duplicate script | Incomplete attribution | Grok/Praxxis/Claude #820 |
| Merchant → realized net | No authenticated settled orders, refunds or fees | Merchant statement reconciliation | Not computable | Commerce #820 |

**Release:** ALL SIX = HOLD_UNSENT. COMMERCIAL 03 & 05 = HOLD_MERCHANT. R283 copy NOT_ADOPTED. No real sends, test emails, publishing, settings changes, list contact/import/export, merchant links or spending. Founder approval of exact creative, audience, send schedule, commercial permissions and legally verified footer required. Business postal for Final Vestige is NOT the UK address in Inspire3's merchant website. For primary-purpose legal review use [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business); for native non-sending preview method use [WordPress email appearance](https://wordpress.com/support/newsletter/email-appearance/).
