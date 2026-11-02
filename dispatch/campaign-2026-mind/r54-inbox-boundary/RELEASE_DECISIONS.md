# R54 — Decision-ready evidence collection protocol

**State: ALL SIX HOLD_UNSENT; COMMERCIAL #03/#05 HOLD_MERCHANT.** This is a future human signoff protocol, not permission to take the steps. No actual WordPress, Gmail, merchant or subscriber action is scheduled by this document.

## Decision A · Which email experience are we actually approving?

**Current production fact:** Jetpack is configured as `email_content_format=excerpt`. In the WordPress product, this is **not** a stand-alone email campaign editor with a guaranteed separate subject and preheader. The **post title** supplies the email subject. Custom post excerpts are *post-specific content decisions* rather than evidence of actual delivery.

Possible owner decisions, each separately authorized and *not yet made*:

| Design | Expected subscriber journey | Editorial consequence | Required native proof |
|---|---|---|---|
| A: Current excerpt fallback | Subject → approximately first 55 words → WordPress's generated read-more → first-party post → its own research CTA | Neither #03 nor #05 shows the existing commercial disclosure in the modeled first 55; the intended primary CTA is not in the modeled first 55 of any issue | Confirm **actual** first 55 text, generated link, visible promotional nature and legal footer in a controlled native preview and received message |
| B: Proposed PR #187 custom excerpt | Subject → specifically written custom excerpt → generated read-more → first-party post → independent guide CTA | Six previously drafted excerpts include product-specific disclosure in #03/#05; they are **not installed** and do not substitute for near-earning-link disclosure on guide | Native evidence that exactly this excerpt appears, is not cut/truncated, and that the reader reaches an approved source-led live post |
| C: Full post email | Subject → full article and sources → one approved primary CTA | Potentially more value in inbox but full content, seller citations and footer must be independently rechecked; existing #03 seller citations allow direct bypass of the independent guide | Explicit separate permission to change newsletter delivery setting or per-post configuration, a controlled email preview, actual MIME, and a separate final send decision |

**No mode has been approved for sending.** Do not apply one setting globally or convert a WordPress page into a post because an offline preview looks good. WordPress's official [sending guide](https://wordpress.com/support/newsletter/send-newsletter-emails/) states that **posts** trigger subscriber newsletter notifications, not standard pages or custom post types. Republishing old posts has distinct behavior; any unpublished/scheduled post must be handled as if a send might occur once the per-post toggle is enabled.

## Decision B · A genuine preview is a controlled risk

WordPress's [Email Appearance](https://wordpress.com/support/newsletter/email-appearance/) requires the individual **Send this post to subscribers** toggle ON to expose **Preview email** (and **Send test email**). This is *not* consent to publish and *not* a safety neutral toggle. The global **Email new posts to subscribers by default: OFF** does not override an individual post toggled ON.

A future founder-authorized **preview-only** workflow must record: proposed post identity and exact source commit; pre-existing per-post send OFF; who will handle the draft and when; native preview desktop/mobile images redacted of private information; then independently verified **per-post send OFF** and unpublished state. If an operator cannot demonstrate the final OFF state, they must not publish.

A separate authorization must precede a **test email**. It should go only to a recipient the founder explicitly authorizes, never to the entire subscriber list, and only after confirming where that message might be delivered. The prior October 25 **subscription confirmation** cannot be used as a surrogate: it is not the updated Focus Fieldbook welcome, and its Automattic sender/footer is not Final Vestige's verified mailing address. The existing R45 received-MIME test tool can inspect the real RFC 5322 message privately without publishing email addresses. An HTML preview alone cannot verify MIME headers, the plaintext alternative, unsubscribe function or final legal footer.

## Decision C · CAN-SPAM and affiliate disclosure are two distinct checks

The **FTC CAN-SPAM Act compliance guide** calls for truthful header/subject, a valid **publisher postal address**, a usable opt-out, honoring opt-outs and clear advertisement identification where required by the message's primary purpose. An ISP/provider footer, an original draft's `[[VALID_POSTAL_ADDRESS_REQUIRED]]` token, or the statement *Unsubscribe anytime* on a landing page are not sufficient evidence of a received commercial email's legal footer. Reference: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

The **FTC Endorsement Guides** also require material-connection disclosure when an endorsement is made. The current proposed #03/#05 custom excerpts mention possible commissions, but readers also need disclosure clearly and near an eventual qualifying recommendation/earning link on the first-party guide. Reference: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .

These determinations require examination of the actual final creative and purpose, not a blanket conclusion that every editorial issue is a commercial advertisement. The six letters may have different primary purposes. Do not represent the Python checks as legal certification.

## Decision D · Recipient count and welcome delivery need direct evidence, never extrapolation

Current authenticated diagnostic totals **2 total, 2 confirmed, 2 unconfirmed, 0 suppressed** are inconsistent as additive audience figures. We do **not** know whether these are overlapping counters, cached snapshots, separate scopes or something else. WordPress's [subscriber help](https://wordpress.com/support/subscribers/) describes filtering users by subscription type, email subscription status, and not-sending reasons. A future authorized administrator should inspect those filters *privately* and produce only a count of **distinct confirmed, email-enabled, not suppressed, category-eligible recipients**, with digest preference noted where observed. Do **not** export, screenshot, upload or paste identities or confirmation tokens into source control.

The welcome template currently includes the 52-page Fieldbook download, but receipt of the **final actual welcome** remains unverified. A separate, approved recipient-side original message is necessary if that verification is required. An already-received confirmation message does not prove the welcome reached the inbox.

## Decision E · Two commercial slots have a separate dependency chain

Mind & Affiliate **Issue #171** owns independent first-party product guides. Its current source-controlled Zen12 work, including [draft PR #527](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/527), is **unpublished and not an approved reader destination**. The source manuscript of Dispatch Issue #03 still has two clickable ordinary merchant citations despite R50's separate quarantined optional proposal. Neither product has a verified approved tracked earning URL or Final Vestige-specific EMAIL-channel permission. There is no finding that public [Inspire3 affiliate recruitment](https://affiliates.inspire3.com/) grants those rights. Official [Zen12](https://zen12.com/hnp) and [Total Focus](https://hypnosislive.com/mental-skills/total-focus) claims cannot be assumed true as product-specific efficacy evidence; current checkout/refund/creative rights require review.

The approved audience journey, **once separately cleared**, is: truthful Dispatch excerpt or article → **published** vetted Final Vestige evaluation with factual evidence and adjacent disclosure → authorized exact merchant destination. No direct merchant source citations should accidentally bypass a required first-party review step. No earnings attribution should be inferred from a mere outgoing click.

## Proof-of-work ledger and owner handoff

| Evidence item | Present now? | Who can resolve | Not permitted without explicit founder approval |
|---|---|---|---|
| Canonical six original written drafts, 4:2 allocation | YES in PR #175 | Dispatch editorial owner | Replacing approved originals silently |
| Six optional excerpts | YES as *uninstalled PR #187 source files* | Dispatch + founder editorial review | Changing WP post excerpts |
| Fallback first-55 simulation | YES in this R54 branch; offline only | Dispatch QA | Presenting it as received mail |
| Native Jetpack desktop/mobile preview | NO | Authorized site editor | Enabling per-post send toggle |
| Genuine received RFC 5322 commercial test | NO | Explicitly authorized recipient + editor | Test-sending any message |
| Valid Final Vestige physical address in delivered message | NO | Founder/site operations | Inventing or adopting Automattic address |
| Functional one-click/acceptable unsubscribe in received message | NO | Site operator + recipient | Declaring page wording sufficient |
| Distinct consent-eligible audience | NO; 2/2/2 diagnostic conflict | Authorized WP administrator | Exporting/listing subscribers publicly |
| Actual final welcome Fieldbook receipt | NO | Authorized recipient | Claiming confirmation proves it |
| Zen12/Total Focus named EMAIL affiliate rights | NO | Partner account owner / Mind | Merchant outreach or earning links |
| Approved published independent buyer guides | NO | Mind #171 + founder | Linking to draft-only pages |
| Explicit final issue + audience + date approval | NO | Founder | Any publish, schedule or send |

## Minimal next concrete step

**First decision:** Founder separately authorizes a *controlled native preview* of **one editorial-only** candidate under documented per-post OFF-before/after protection, or defers preview. That is a narrower, safer first operational milestone than trying to send a commercial edition. The preview still does not deliver to any subscriber and must never be mistaken for inbox evidence. This proposal does not constitute the required approval.

**Until then:** no emails or test emails, no WordPress changes, no subscriber or merchant contact, no activated affiliate links, no tracking, no new list/provider/cost, no homepage edits.
