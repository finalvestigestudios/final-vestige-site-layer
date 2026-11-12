# Dispatch R296 — received MIME QA (review only)

**NO SEND.** Original campaign #175 unchanged; 4 editorial and 2 conditional commercial drafts. Issues 03/05 HOLD_MERCHANT. Stacked on #2137 and no site, WordPress, subscriber, homepage #49, analytics or affiliate changes.

## Distinct deliverable

The accompanying lossless source-only ZIP (encoded as base64 text because the connector only writes UTF-8) contains Python-standard-library **read-only RFC 5322/MIME inspector** received_email_audit.py and 22-test native suite test_received_email_audit.py. It processes only an authorized locally obtained .eml and audits real multipart HTML/plain variants, encoded Subject, visible unsubscribe, first-party CTA path, unresolved placeholders, active HTML, raw merchant URLs including plaintext autolinks, and personal query parameters. It outputs only status codes and booleans, never message body, address, URLs, recipient identities or secrets. A structurally valid message CANNOT approve sending. Reconstruct: base64 -d source_only.zip.b64 > source_only.zip && unzip source_only.zip.

Locally executed **22/22 native Python tests passed** on synthetic fixtures; original PR #175 current HEAD d57ccdba3aee8f065e143e101c2945f4f3d01647 native Python suite **6/6 passed** from previously archived byte-verified originals. Tested sources SHA256: inspector 0c6a595de448c49cca79b303fa2f43814d21339781da59bf1b53908b7989cd6b, test suite 8df2c741fcaa6bb0cb7d4da08d7bbea59cff73d3d79afa8a6b805ee1ab92a2c7. NO genuine Jetpack preview or inbox received; no email sent.

## WordPress read-only · November 12, 2026 04:37 UTC

Newsletter enabled, auto-new-post mails OFF, full content, welcome configured. Diagnostic subscribers total=3, confirmed=3, unconfirmed=2; distinct Stats WP.com followers=3, email followers=0. These are **not additive**; true email-eligible audience UNKNOWN. Last five displayed post sends each opted out, not lifetime-zero proof. No actual completed welcome proof, publisher valid postal address evidence or functional unsubscribe evidence. /dispatch/ commercial signup expectation differs from /focus/; parity proposal #2131 not adopted.

## Seller and compliance evidence

- https://zen12.com/about: seller specifies 12 levels and four variations per level; 12min=1h effect is an **unverified seller efficacy assertion**. No FV EMAIL affiliate permission, issued earning URL, account-specific price or refund terms, or verified live buyer guide. Mind owner PR #2141 handles presell.
- https://hypnosislive.com/mental-skills/total-focus: 33min/47MB product specification, stronger concentration claims unverified; price/return terms not approved for FV copy.
- FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires truthful header/subject, ad identification, valid physical postal address, clear and functional opt-out for commercial mail. List-Unsubscribe header alone is NOT enough. Material affiliate relationship requires near-offer disclosure: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking . Jetpack subscription statuses https://wordpress.com/support/subscribers/ ; local standards https://finalvestige.com/editorial-standards/ .

## OFFER → FUNNEL → BLOCKER → PROOF → OWNER

| Offer / step | Blocker and required acceptance | Status | Owner |
| --- | --- | --- | --- |
| Zen12 → vetted guide → purchase | Written acceptance for EMAIL promotion, issued link, finalized live guide | HOLD_MERCHANT | Mind / Commerce |
| Focus → confirmed signup | Authenticated per-recipient Email subscription status, dedupe; no identity export | UNKNOWN | Claude / Focus |
| Dispatch → real inbox | Native non-sending editor preview; separately authorized received MIME; legal postal and tested unsubscribe | UNTESTED | Dispatch / Founder |
| Grok asset → qualified visit | Real asset ID and UTM/source join in existing analytics; no duplicate scripts | INCOMPLETE | Grok / Praxxis / Claude |
| Order → net revenue | Verified settled transactions, refunds/fees, 7/30-day cohort | NOT COMPUTABLE | Commerce |

**Release decision:** ALL SIX HOLD_UNSENT. Commercial 03 and 05 HOLD_MERCHANT. No final founder campaign approval, test mail, subscriber changes, sends, affiliate links, live edits, spending, or commerce claims. The archive's source is not inline-reviewable in GitHub; the separately provided unpacked reviewer package and native test logs permit source inspection.