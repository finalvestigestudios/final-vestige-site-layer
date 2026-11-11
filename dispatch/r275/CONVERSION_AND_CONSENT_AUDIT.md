# Dispatch R275 — First-party consent-expectation divergence and commercial release plan
**2026-11-10 23:30 PT / 2026-11-11 07:30 UTC — REVIEW-ONLY, UNSENT, NOT ADOPTED**

## New high-impact finding: the 3 first-party surfaces do not set the same reader expectation
Authenticated read-only WordPress data and the current public pages reveal that **/focus/** informs new readers that some future emails may contain commission-earning recommendations, whereas **/dispatch/** promises investigations and archive finds without that qualification. The configured Jetpack welcome message likewise promises investigations/archive finds and says nothing about occasional commercial recommendations. This is **a reader-expectation and informed-choice inconsistency**, not proof of a CAN-SPAM legal violation or proof of an unauthorized send. Existing subscribers who registered through one surface may reasonably have a narrower expectation than visitors arriving through another.

**Specific first-party evidence**
- Focus page ID **1579**, https://finalvestige.com/focus/ : "Some emails may include recommendations that earn us a commission."
- Dispatch page ID **523**, https://finalvestige.com/dispatch/ : "You'll also get new investigations and useful finds from the archive when we publish them." No parallel commercial note near signup.
- Jetpack configured welcome (not a received inbox specimen): "You'll hear from us when there's a new Final Vestige investigation or a worthwhile find from the archives. No daily flood of emails." No commercial note.
- Editorial Standards page ID **17**, https://finalvestige.com/editorial-standards/ says relationships are disclosed and commercial opportunities do not determine historical conclusions.
- Newsletter get_settings as of **2026-11-11 07:31 UTC**: subscriptions enabled; auto-email new posts **OFF**; email format **full**; no-reply; categories OFF; welcome configured. Diagnostic total=3 confirmed=3 unconfirmed=2; **do not sum these**; actual provider-filtered email-eligible recipients **unknown**.
- Original six master emails PR #175 SHA d57ccdba3aee8f065e143e101c2945f4f3d01647; guard PR #201 SHA ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6. Both read. R274 #2008 head ac536262b84539f87f8043eab03ab2e3a75f64e1 is the parent of this add-only review.

## Proposed copy changes, NOT applied, NO retroactive permission assumed
**/dispatch/ — immediately adjacent to its existing form or privacy line:**
"Get the free Focus Fieldbook and occasional Dispatch emails about historical investigations, unusual evidence and the science of perception. We may sometimes recommend a relevant product; if a linked purchase can earn Final Vestige a commission, we'll disclose that clearly near the recommendation. Unsubscribe anytime. No daily emails."

**Jetpack configured welcome — one concise addition after the archive promise:**
"We also occasionally examine practical Mind & Perception tools. If we recommend a paid product and can earn a commission, we'll make that relationship clear. The Fieldbook and our source-led editorial coverage remain free. You can unsubscribe whenever you choose."

Do not change either live surface until Claude/Focus owner and founder approve it. An edited notice **does not retroactively establish affirmative consent or permission to send a new category of messages**. If a future material change in subscriber expectations warrants repermission or audience segmentation, handle that separately under subscriber privacy/consent review, with no unapproved emails.

## Conversion-first progression: ONE intended first merchant candidate, Zen12, and no live commerce
1. **Audience:** Already-confirmed, currently eligible Jetpack reader **who was told the scope** and arrived for focus/meditation evidence; never infer this from email addresses, a frontend download parameter, a follower count, or a merchant free-audio signup. No segmentation performed yet.
2. **Value:** Welcome delivers the 52-page Fieldbook; proposed follow-up remains a **non-sending editorial path** to an existing source-led Focus/Mind investigation. A reader shouldn't be asked to sign up again for the same PDF.
3. **Commercial decision:** Of the two founder-reserved commercial drafts (03 Zen12, 05 Hypnosis Live), select **Zen12 as the first candidate for authorization testing**, not as an approved recommendation. Mind #171 controls the single approved warm-up guide and merchant route. Source-led guide should ask: what is in the actual package, what is claimed vs proved, what is the current checkout/refund path, and who benefits? Only later, after the account owner's authenticated permission, guide can show an approved, attributed merchant earning URL. Do not collapse Zen12 /welcome merchant opt-in into Jetpack consent.
4. **Conversion definition:** Existing Grok asset ID / UTM → qualified human session → relevant CTA → first-party provider-confirmed lead → independently authenticated paid merchant order/commission → refunds and fees → realized net revenue. Do not infer sales from clicks. Seven- and thirty-day cohorts, tiny-sample warnings, and net revenue/1,000 qualified sessions **NOT COMPUTABLE** without denominator and settlements.
5. **Suppression:** **All six drafts HOLD_UNSENT, Issues 03/05 HOLD_MERCHANT.** No alternate copy automatically adopted.

## Official product alignment observed (PUBLIC pages; account-specific permissions UNKNOWN)
- https://zen12.com/getstarted describes a 12-level, 48-MP3 course with checkout totals that can vary by route/session/coupon. Public display is **not a verified FV affiliate offer**, and bundle guarantee wording must be reviewed against exact checkout and merchant refund policy. Do NOT put any displayed price in an email.
- https://zen12.com/welcome offers an audio trial and clearly states that the recipient joins **the seller's newsletter**. This is not a first-party subscriber event.
- https://hypnosislive.com/mental-skills/total-focus lists a 33-minute/47-MB Total Focus MP3 and a public price; claims about "100% razor-sharp concentration" are seller assertions, **not independently established**.
- https://hypnosislive.com/faq documents refund qualifications; check the actual approved sale route before making any guarantees.
- Generic affiliate portal, Mind draft or seller media do **not** establish FV partner acceptance, issued earning URL, email-promotion permission or cleared creative rights.

## Legal / actual-delivery QA that remains gated
FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires proper sender identity, a truthful subject, clear ad identification where applicable, publisher postal address and effective opt-out in commercial mail. **Final Vestige's own** current valid postal address is unverified. Jetpack unsubscribe mechanics in an **actually received** issue or welcome have not been inspected. The configured reply-to is **no-reply** and therefore is not itself proof of an opt-out route. The Automattic address in a confirmation email would be a third-party address, not proof of the FV publisher's. A native WordPress-sent received preview requires a **separately explicit founder authorization**; this review does NOT authorize sending a test.

## Release blockers and owners
| Offer → step | Blocker | Change/experiment | Evidence status | Owner |
|---|---|---|---|---|
| Zen12 → pre-sell → paid order | Merchant acceptance, email channel, final guide and earning URL missing | Authenticate owner-held account terms, verify exact checkout and live guide after permission | HARD HOLD | Mind & Affiliate #171 |
| Dispatch/Focus → informed subscriber | Commercial-scope copy differs across entry points; eligible recipients unknown | Review copy additions; reconcile private provider-filtered Email subscription=Subscribed status, no identities exported | GAP VERIFIED; FIX DRAFT | Claude/Focus #129, Dispatch #174 |
| Welcome → inbox | Actual delivery of 52-page PDF & legal footer unverified | Authorized receipt review of welcome and one genuine Jetpack render; no send without separate approval | UNKNOWN | Dispatch / Site QA |
| Grok → landing → signup | Real immutable asset to provider confirmation join absent | Check existing campaign tags and consent evidence; no new scripts | UNKNOWN | Grok/Praxxis & Claude |
| Paid order → realized net revenue | No independently reported settlements/refunds/fees + human sessions | Private first-party and merchant reconciliation | NOT COMPUTABLE | Commerce #820 |

**Scope:** No sends, drafts to WordPress, subscriber contact/import, platform/account cost, settings edits, affiliate activation, homepage #49 changes, social queue edits or merged PRs.
