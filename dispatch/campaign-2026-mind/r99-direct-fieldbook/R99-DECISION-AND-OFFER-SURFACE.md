# Dispatch R99 — Subscriber-safe access and actual commercial surface verification
**Observation date: 2026-11-03 (21:29–21:31 UTC).** **Draft only; all six HOLD_UNSENT; 03/05 HOLD_MERCHANT.** Master PR #175 @ d57ccdba3aee8f065e143e101c2945f4f3d01647; existing stacked draft PRs #201 and #839; Issue #174 and companion Issue #171. This branch adds a *distinct*, optional Issue 06 candidate and QA without touching master, partner guides, WordPress, homepage, or frozen PR #49.

## An actionable new correction: do not ask existing subscribers to subscribe again
Original Issue 06 in master PR #175 points to /focus/, a landing page whose primary job is collecting a Jetpack subscription **from visitors who are not subscribed**. The recipient of Issue 06 would already be a subscriber. Prior R91 optional manuscript and R92 excerpt also point to /focus/, creating the same circular destination. The current welcome message already links the complete 52-page PDF. A read-only authenticated WordPress media lookup **independently confirmed** the same asset is a published attachment: **ID 1737**, `application/pdf`, 599,946 bytes, URL:
https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf

**New candidate:** one clear CTA directly to that existing verified PDF, no re-subscription or second account. It preserves original promise and historical-evidence framing, five-field reflection exercise, no medical or performance guarantee. The PDF is also publicly addressable, not a new expense or download flow. Approval is needed before swapping the original text/CTA in any newsletter.

**Limit of verification:** the WordPress media API establishes the attachment exists and its source URL. It does NOT prove every email client's PDF opening behavior, a successful newsletter welcome delivery, or a particular recipient's access. It also does not change the existing focus landing page or welcome email.

## Actual WordPress source-of-truth snapshot
- Jetpack Newsletter `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `reply_to=no-reply`.
- Welcome text includes this exact PDF URL and describes it as 52-page Complete Edition; welcome receipt still UNVERIFIED.
- Counts still contradictory: `total=2`, `confirmed=2`, `unconfirmed=2`; distinct Stats endpoint `email=0`, `wpcom=2`. These are separate classifications, **not** four deliverable people. Actual authorized email recipients remain UNKNOWN. Do not export identities.
- Five recent post send records `never_sent_opted_out`; no recorded dispatch from those five, no claim about all historical sends.
- /dispatch/ still omits the occasional commission recommendation wording that /focus/ includes. R98 contains the proposed consent copy; no duplicate implementation or live edit here.
- Native Jetpack `Preview email` requires per-post send toggle enabled (WordPress docs); we did not enable it, send a test, publish or write settings. Static HTML here is **not** actual Jetpack MIME rendering.

## Exact merchant surface checks — facts vs vendor assertions
All official links are *research sources only*, not active earning URLs.

| Product/official record | Observed public information | Status / action |
|---|---|---|
| Zen12 course: https://zen12.com/hnp | The seller describes 12 levels, four audio options per level, 12-minute sessions; claims a single session is comparable to an hour's meditation, plus brainwave and health benefits. | **Claims NOT independently product-proven**; use only attributed descriptions, not promises. |
| Zen12 checkout: https://zen12.com/getstarted | Checkout displayed 12 levels / 48 MP3s, mobile number field, $187.99 strike/base and $100 VIP reduction to $87.99 plus a time-box style countdown **in this observation**. | **Do not publish price, urgency, discount, refund promise or checkout pressure**; session/locale/tier may differ. Confirm terms with partner and checkout before guide. |
| Hypnosis Live Total Focus: https://hypnosislive.com/mental-skills/total-focus | Specific recording 33 minutes / 47 MB; observed $24.44 alongside $29.95 and bundle options; copy claims dramatic concentration outcomes. | Exact SKU features only; **no independent proof** of promised outcomes or stable price; no claims of guarantee. |
| Hypnosis Live FAQ: https://hypnosislive.com/faq | Typical $22.95 / most 40min are generic; refund within 14 days but **max five sessions refunded per year**; FAQ notes no recurring payments on typical MP3s. | Do not substitute generic specs for Total Focus or omit limitations; future checkout terms still unknown. |
| Inspire3 privacy: https://inspire3.com/privacy/ | Referring affiliates may receive buyer name/email/item details. Seller may use provided mobile numbers for SMS marketing. | Require written aggregate-only reporting/no purchaser PII and assess phone disclosures before promotions. |
| Inspire3 public affiliate portal: https://affiliates.inspire3.com/ | Public partner signup, generic payouts and special-link descriptions. | Not evidence of **named Final Vestige acceptance**, EMAIL-channel permission for exact SKUs, approved link format or creative rights. |

Vendor physical address (London) and Automattic postal address **do not count as verified Final Vestige business address**. The user's newsletter list is not a vendor contact list. No outreach to merchant or subscribers performed.

## FTC and WordPress implementation boundary
- FTC official guidance https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business applies based on primary commercial purpose, including products promoted on commercial websites; a subscriber relationship does not exempt an ad message. It requires truthful subject/header, advertisement identification, valid sender postal address, clear opt-out, mechanisms active for 30 days and opt-outs honored within 10 business days. A one-page mechanism can comply; do not misstate "mandatory one-click" under CAN-SPAM. Product-affiliate commercial messages 03/05 particularly require near-link disclosure and clear commercial nature.
- WordPress official https://wordpress.com/support/newsletter/email-appearance/ documents custom excerpt, not full email, under current settings; the native email sender address is WordPress-controlled and no independent preheader editor was verified. Manual static preview cannot prove native footer, actual opt-out or welcome receipt.
- Sender postal proof, recipient eligibility, commercial approval, live guides, unsub functionality, received genuine email, final founder approval: **ALL NOT VERIFIED / HOLD**. Hard-coded send rights cannot be granted by software tests.

## Focused decision for founder (no approval presumed)
1. When reviewing issue 06, prefer the **direct existing 52-page PDF CTA** to a second signup ask, contingent on link/browser and editorial signoff.
2. Keep issues 03 and 05 disabled until private written named affiliate/EMAIL permission and approved live buyer guides exist, with aggregate-only reporting and accurate product-specific conditions.
3. For any send, verify publisher-owned eligible postal address and real unsubscribe/welcome delivery privately and reconcile audience; do not release on WordPress setting `site_can_send` alone.
4. No changes to four-editorial/two-commercial reservation, no published site changes, no new platform, no subscriber export, no test or actual email, no scheduling, no merchant links.
