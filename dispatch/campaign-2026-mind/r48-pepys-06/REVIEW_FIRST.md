# Dispatch R48 review first — optional historian's Issue 06 + real delivery decision

**STATUS HOLD_UNSENT / founder substitution not approved.** This PR stacks on optional Dispatch R47 PR #486 at exact SHA `dd150154139d34c757fb111702c3ef1f180ca136`; canonical six issues of PR #175 and separate QA gates PR #201 are unchanged. Homepage and frozen PR #49 are untouched.

## The story and why it fits
Original optional final editorial issue: **He saw the fire. Then he went back to bed.**. Pepys's 1666 diary of the Great Fire offers a documented example of observation versus reports from others versus interpretation. The narrative preserves the limited vantage available at three in the morning; do not project later knowledge onto the witness. A separate 2002 BMJ study is quoted only for diary-entry timing, not as proof of any meditation program or general memory-error rate. The piece gives four actionable log prompts and **one** primary editorial CTA to published first-party Focus page #1579 (https://finalvestige.com/focus/). No paid placement or active seller link.

All four synchronized manuscript formats — Markdown, plaintext, standalone table-style email HTML, Gutenberg-shaped *offline review blocks* — plus source/claim register, static local reviewer, privacy-safe live state snapshot, provider delivery decision and adversarial regression tests. Offline HTML is **not** native Jetpack HTML.

## Primary-source/claim boundaries
Pepys and Evelyn extracts https://www.nationalarchives.gov.uk/education/resources/great-fire-of-london-examine-the-evidence/extracts-from-samuel-pepys-diary/ and https://www.nationalarchives.gov.uk/education/resources/great-fire-of-london-examine-the-evidence/extracts-from-john-evelyns-diary/ ; actual shorthand artefact https://www.fireoflondon.org.uk/browse-the-collection/extract-samuel-pepyss-diary/ ; original clinical study https://www.bmj.com/content/324/7347/1193 ; NCCIH evidence overview https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety . We did NOT use or reproduce archival images because source permissions require owner contact. We do NOT assert the date a diary entry was physically written, the historical reports' exact correctness, or any audio product's efficacy.

## Strongest conversion and delivery issue to resolve
**Live Jetpack is excerpt mode**. Original full manuscripts and custom offline HTML do not guarantee a subscriber reads the story and main CTA *inside* the inbox. R48 includes `jetpack_delivery_decision.md` with provider-source discrepancy (current WordPress Oct26 55-word default versus earlier R43 uncorroborated 350-character fallback), safe reader-path design, explicit no-send native preview operator workflow and commercial partner/CTA hold table. Use real received email to resolve; do not declare either simulated excerpt authoritative.

## Verified read-only production data
Authenticated WP site 256784396, **2026-11-01 18:32 UTC**: newsletter enabled and technically sendable; `email_new_posts_by_default=false`, excerpt mode, featured image/date ON, from name Final Vestige, reply_to no-reply, welcome configured to provide 52-page Focus Fieldbook. **Welcome actual receipt unknown.** Counts total=2 / confirmed=2 / unconfirmed=2 are not proven disjoint; unique audience unknown; `recent_sends=[]` not lifetime zero. /dispatch/ #523, /focus/ #1579, /editorial-standards/ #17 are published. Read-only Gmail found only an Oct 25 subscription **confirmation**, not the welcome email and not merchant affiliate approval.

## Commerce/legal, still HOLD
Inspire3 official Limitless Labs swipes are unrelated to Zen12 and Total Focus. Independent buyer guides in Mind #171 PR #489 are UNPUBLISHED; written product-specific EMAIL permission, affiliate tracking URLs, checkout/refund terms and merchant outcomes are not verified. No made-up postal address or unsubscribe. The compliant-looking offline footer remains an intentional blocker. FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . All six original emails HOLD_UNSENT; 03/05 additionally HOLD_MERCHANT. Founder final send approval absent.

## Test
Full exact-head suite: `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v`. This run must pass on committed SHA and be inspected, not inferred. CI success does not authorize publication/send or certify CAN-SPAM. No WordPress/Gmail writes and no list access.

## Prev verified baseline
Independently reran R47 GitHub job 124925857957: replacement job **124939453724** on source SHA `dd150154139d34c757fb111702c3ef1f180ca136` returned **676/676 tests passing** and exact-head assertion. Now test all new files on R48 submitted commit.
