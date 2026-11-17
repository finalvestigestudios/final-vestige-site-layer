# Dispatch R413 — source-of-truth QA, acceptance witnesses and release decision

## Verified in this run (2026-11-16 evening Pacific)

* Read GitHub **Issues #174 and #171**, latest owner comments including Mind R433 #2813, the original master **draft PR #175**, original independent readiness **draft PR #201**, and prior Dispatch **draft PR #2811**. All open and unmerged at inspection, no change to canonical six drafts.
* Verified master PR #175 HEAD exact `d57ccdba3aee8f065e143e101c2945f4f3d01647` and matching **8/8** Git blob SHAs against locally extracted original source/manifest/tests from R409 QA archive. Independently ran original Python native suite `python -m unittest discover -s dispatch/campaign-2026-mind/tests -v`: **6 tests / 6 passed**, exit 0.
* Authenticated WordPress read-only Newsletter status/settings on **2026-11-17 02:38 UTC**: newsletter enabled, `email_new_posts_by_default=false`, `email_content_format=full`, `reply_to=no-reply`, sender `Final Vestige Studios`, 52-page welcome PDF link configured, recent five posts `never_sent_opted_out`; reported `total=3 / confirmed=3 / unconfirmed=2 / suppressed=0` (not additive). Separate authenticated followers read returned total 3, email 0, WordPress.com 3, comment 0, partial=false. **Unique actual email-eligible recipients UNKNOWN.** Provider configuration is NOT recipient delivery proof.
* Read WordPress production `/dispatch/` page 523, `/focus/` page 1579 and public Editorial Standards page 17 (sources first, ambiguity visible, commercial conclusions independent, on-page disclosures). No WordPress writes made.
* Read existing creator handoff TASK-008 and Praxxis-Grok Google Drive handoff through authorized Drive connector; no modifications. Grok remains primary acquisition content/distribution owner.
* Private connected Gmail searches (after 2026-10-01) found merchant promotional emails but NO matching explicit Zen12/Total Focus approval or email permission in the searched messages. A negative search cannot prove no agreement exists elsewhere. A search for a Final Vestige welcome message returned no match and does not disprove delivery to a different mailbox. No subscriber email addresses were read or revealed.
* Official independent claims checked: James 1890 chapter XI, Goyal et al. 2014 (PMID 24395196), NIH NCCIH evidence limits. Official Zen12 product page describes 12 levels and four styles and claims 12 minutes ≈ one hour; alternate seller promotional funnel advertises a coupon/urgency. These vendor representations are **not proven Zen12 outcomes nor FV-specific checkout/affiliate approval**. Public Inspire3 affiliate pages do not establish named rights for this SKU/email channel.
* New optional Issue03 original editorial **475 words of prose**, one disabled CTA, disclosure alongside, five research/merchant source links, HTML/plaintext offline parity and source-to-claim JSON; original 4:2 issue ratio preserved. Automated local V8 checks of authored strings: **15/15 passed before commit**. All seven first-wave R413 committed files independently re-fetched from the draft branch; 33/33 post-commit source checks PASS. Offline HTML is NOT Jetpack-rendered email.

## Critical unverified acceptance evidence (all must be TRUE before send)

| Gate | Current evidence | Status / owner |
| --- | --- | --- |
| Named Inspire3 FV acceptance + exact Zen12 SKU EMAIL permission | Public pages only | **HOLD** Mind / Commerce |
| Issued approved earning link + exact referred checkout, offer, refund, restrictions | No authenticated partner dashboard | **HOLD** Mind / Commerce |
| Independent vetted, owner-approved, actually LIVE Zen12 first-party warm-up guide | Draft concept only | **HOLD** Mind |
| Provider-level confirmed and eligible distinct inboxes and explicit consent scope | Aggregates conflict with follower channels | **HOLD** Focus / Claude |
| Real welcome message actually received with intact 52-page PDF and correct access | Settings configured only, prior Gmail confirmation not welcome | **HOLD** Focus / Founder |
| Genuine non-sending **Jetpack Preview email** on real editor draft; desktop/mobile proof | Connector read-only, no native editor preview | **HOLD** Dispatch / Founder |
| Valid FV publisher physical address in actual outgoing email | Seller/Automattic addresses not FV's | **HOLD** Founder |
| Real, usable Jetpack opt-out and proper headers in rendered actual email | No received email or native rendered preview witness | **HOLD** Dispatch / Founder |
| Final founder campaign approval | Six-issue *draft* only | **HOLD** Founder |
| Settled customer conversions and audited qualified-human sessions | Not available | **NOT_COMPUTABLE** Commerce / Claude |

WordPress documented behavior: Preview email is a **non-sending** editor action distinct from **Send test email** (which would actually transmit). Never use Send test email absent founder approval. With `reply_to=no-reply`, replying to the message is not a supported substitute for the actual unsubscribe control. Do not assume an editor preview proves received-inbox delivery or accessibility in every mail client.

FTC CAN-SPAM: commercial messages require accurate routing, truthful subjects, clear ad identification, real publisher address, easy opt-out and honoring requests; an ordinary subscriber relationship does not automatically exempt promotional emails. Do not misclassify an edition solely because its first paragraph is editorial. See https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . Also preserve the WordPress platform's current policy and merchant's email-channel authorization as separate acceptance gates.

## Novel R413 acceptance tests

Case A: Fake `?subscribe=confirmed` with no provider event → `NO_CONFIRMED_SIGNUP`. Case B: WordPress total=3, confirmed=3, unconfirmed=2, follower email=0, wpcom=3 → `DISTINCT_INBOXES_UNKNOWN`. Case C: approved Zen12 offer guide but no SKU-specific EMAIL rights → `HOLD_MERCHANT`. Case D: email creative uses official vendor `$37` coupon as FV-valid checkout → `FAIL_CLAIM`. Case E: seller Inspire3 postal address inserted into FV footer → `FAIL_ADDRESS`. Case F: offline HTML passes accessibility checks but no Jetpack preview → `HOLD_NATIVE_PREVIEW`. Case G: email CTA click but no merchant paid settlement → `NO_PAID_SALE`. Case H: discount countdown not authenticated → `DO_NOT_USE_URGENCY`. Case I: provider-eligible confirmed subscriber but opt-out has since been recorded → `DO_NOT_SEND`. Case J: real 7-day gross paid order, but refunds/fees or human sessions unknown → `NOT_COMPUTABLE`.

## Release + prioritization

**Issue 03 alternative: NOT_ADOPTED / HOLD_MERCHANT / HOLD_UNSENT.** Original issues 01, 02, 04, 06 remain 4 editorial placements; 03 and 05 remain 2 prospective commercial placements. Original Issue04 remains HOLD_COPY until the founder approves source correction R412. Footer, eligibility, welcome receipt, native Preview and merchant channels are still blocked. No sends, test emails, WP writes, subscribers contacted, tracking scripts, price guarantees, affiliate activation, merges, publishing or spending.

**Priority matrix:** Zen12 → vetted guide → merchant eligibility → private proof / source-only alternative → HOLD / Mind; Fieldbook → welcome/consent → private provider eligibility → dedup plan → HOLD / Claude; Dispatch → inbox → address+unsubscribe+preview → non-sending native witness → HOLD / Founder/Dispatch; Grok → sale → audited sessions+paid settlements → existing measurement join → NOT_COMPUTABLE / Claude/Grok.

Sources: https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://wordpress.com/support/newsletter-settings/ ; https://wordpress.com/support/subscribers/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety ; https://pubmed.ncbi.nlm.nih.gov/24395196/ ; https://zen12.com/about ; https://zen12.com/secret/ .
