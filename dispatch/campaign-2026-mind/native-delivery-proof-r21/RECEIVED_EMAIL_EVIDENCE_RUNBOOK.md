# Dispatch R21 — native Jetpack email evidence intake, privacy and release controls

**October 31, 2026 | DRAFT / UNSENT / READ-ONLY.** This is a new, narrowly scoped verification instrument; it is **not** an alternative newsletter, actual WordPress email, mailing-list export, publishing tool, tracking service, postal-address determination, or send authorization. Owner: GitHub Issue #174; companion Mind & Affiliate owner: #171. Campaign master draft PR #175; R20 parent PR #307. Frozen homepage #49 is out of scope.

## Why this work is necessary

The existing 13 review-only HTML/plaintext files are locally deterministic and mobile-tested, but they are **not WordPress/Jetpack's actual outgoing MIME**. At `2026-10-31T14:31:19Z`, the authenticated existing-site configuration still said `email_content_format=excerpt`, `email_new_posts_by_default=false`, `subscriptions=true`, `reply_to=no-reply`; `2026-10-31T14:31:17Z` subscriber counters said total=2, confirmed=2, unconfirmed=2, suppressed=0, recent_sends=[] and site_can_send=true. **Site-can-send is a capability flag, not consent to send.** WordPress excludes pending confirmations from subscriber total; the two and two categories do not prove four individuals or a permissioned campaign audience. The configured Focus Fieldbook welcome text proves configuration, not inbox receipt.

WordPress documents that a published post's **title** supplies the actual email **subject** and that email sending can be previewed from the editor. Our standalone preheaders remain planning copy: they have not been proven to surface in a native client's first line. The excerpt default risks cutting off our sourced research, CTA and commercial disclosures. Nobody should silently change to `full` mode or send a test. [WordPress: Send newsletter emails](https://wordpress.com/support/newsletter/send-newsletter-emails/), [Email appearance](https://wordpress.com/support/newsletter/email-appearance/).

The FTC's [CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) specifically requires accurate sender/subject, a valid **sender's** physical postal address, and a clear functioning opt-out for covered commercial messages. An Automattic address in an October 25 subscription-confirmation email is **not** a substitute for Final Vestige's address. [FTC Endorsement Guidance](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) requires clear disclosures of material relationships near relevant promotions. A `List-Unsubscribe` header alone does **not** prove the opt-out works or that the user can see an adequate explanation. A received `.eml` alone cannot authenticate provenance or lawful subscriber consent.

## Only after distinct, specific founder authorization

1. Independently approve exactly **which issue** is being tested, the actual WordPress post/editor preview route, intended recipient controlled by the founder, whether a **separate** received-email test may be sent, and the test timing. This draft campaign does **not** grant any of those permissions. Do not use the actual subscriber list or add a new testing list. Do not submit a subscription form as a test without authorization.
2. Keep received MIME (`.eml`) and any Final Vestige mailing-address note on a **private local device** only. Never paste, attach, commit, upload, or publish a real email message/headers/token; they may contain the recipient's address or opt-out secrets. Do not inspect mailboxes through this program. No addresses are embedded in or printed by this QA tool.
3. A permitted reviewer may export a received message as `.eml`, then run the read-only local check. From `dispatch/campaign-2026-mind`:

   `python native-delivery-proof-r21/check_received_mime.py --eml /PRIVATE/SAMPLE.eml --issue 1 --json-report /PRIVATE/REDACTED.json`

   For a **covered commercial sample** only, the actual sender business mailing address may be kept in a separate **private** UTF-8 file and matched locally:

   `python native-delivery-proof-r21/check_received_mime.py --eml /PRIVATE/SAMPLE.eml --issue 3 --private-postal-file /PRIVATE/FV_ADDRESS.txt --json-report /PRIVATE/REDACTED.json`

   These example paths are placeholders, **not** existing sample files or permission to send. Do not commit either private file. The report contains boolean observations and named blocker codes only. Even `postal_text_matches_private_input=true` does **not** establish whether the private address is legally qualified or current; obtain separate business/legal verification. Avoid command-line arguments containing the address itself.
4. Reviewer verifies the actual displayed email on mobile and desktop, subject, visible commercial disclosure **before** a qualifying offer, published working first-party guide, display of one CTA, source/reader value under the excerpt setting, and a clear visible unsubscribe. In the **authorized self-owned test**, only with further authorization, safely check whether an unsubscribe is functional. Never click a live subscriber's unique unsubscribe token or make a list-changing request during read-only QA.
5. Attach only the **redacted JSON** plus a private evidence reference to the internal acceptance tracker. Independently review identity, source and claims, subscriber consent, legal postal qualifications, opt-out operation, affiliate email rights, authorized tracked URL, and founder signoff. Do **not** flip the existing `edition_attestations.json` booleans without this real evidence and founder approval.

## What the analyzer *does* and *cannot* conclude

- Parses an **already provided** RFC822/MIME file offline with the Python standard library; never network-connects, sends email, or follows a URL.
- Checks exact planned subject, plain and HTML alternatives, obvious unsent placeholder leaks, body-length/excerpt warning, the presence of a **visible** unsubscribe link or plaintext instruction, optional `List-Unsubscribe` and `List-Unsubscribe-Post` header syntax, a near-offer commission phrase for Issues 03/05, and private literal address presence.
- Produces structured **HOLD_UNSENT_UNVERIFIED** even when all observed booleans are true. This is by design: a local text parser cannot verify opt-out functionality, the legal sender's address, account-specific Inspire3 permission, who gave consent, actual inbox render, SPF/DKIM provenance, or founder send authorization.
- Fails conservatively when malformed, empty, over 2 MB, lacking essential headers, missing subject, or truncated. It refuses to print sender/recipient IDs, URLs, unsubscribe tokens, real message text, or business address. Its unit tests use `example.invalid` exclusively.
- Only indicates a possible `List-Unsubscribe` header and a claimed one-click post header, **not** that one-click is mandatory under CAN-SPAM or functional under a mailbox provider. The user-visible message's clear opt-out still matters.
- This tool's substring-based disclosure observation is *not* a prominence or proximity approval. A human must check that exact commercial copy and CTA are visible together in the delivered email and that the intended disclosure is correct.

## Editorial and merchant facts that remain unresolved

**Issues 01,02,04,06:** Published editorial CTA destinations already exist, but actual WordPress received-copy parity, legal postal/opt-out and verified reachable consent have not been attested. The source is at R20 draft PR #307; all six remain hold.

**Issue 03 / Zen12:** Official [About](https://zen12.com/about) advertises twelve-minute listening, 12 levels and four style choices; [Get Started](https://zen12.com/getstarted) describes 48 MP3s, an order form that asks for a mobile number, displayed timer, price and refund-related copy subject to change. Seller's promise that 12 minutes equals an hour of ordinary meditation, automatically changes brainwaves, or achieves health benefits is not independent SKU evidence. Final Vestige's first-party guide is **unpublished** and the placeholder must remain unclickable. Affiliate account acceptance, approved creative, email marketing permission, tracked earning URL, real product terms and refund policy **remain not verified**.

**Issue 05 / Total Focus:** Official [specific SKU](https://hypnosislive.com/mental-skills/total-focus) advertises an MP3 session, 33 minutes, 47 MB, a preview and J.A. Amos attribution. Its attention-enhancement and 'brain reprogramming' benefits are seller claims and not independently proven for this recording. The checkout's dynamic price/discount and refund terms must be checked at launch, not copied into an unsent newsletter. Specific email promotion/earning-link rights and the independent public guide remain **not verified**.

**Funnel:** Published `/dispatch/` (page 523), `/focus/` (1579), and the independent source-based Editorial Standards (17) remain intact. Native Jetpack Subscribe blocks are present in both saved pages, but anonymous visitor click/confirmed signup and welcome inbox receipt have **not** been browser-proven. Do not create a new provider/list or submit an email address without approval.

**Analytics:** With a potentially two-person eligible audience, no open-rate inference, A/B significance, ROI attribution, affiliate revenue or conversion lift is supported. The proposed future aggregate-only events (`issue-number`, `CTA ID`, `approved first-party destination`, voluntary website click count) are conceptual only; no tracking has been enabled. Do not place a `utm` or merchant conversion pixel in the message without permitted terms, consent/privacy review and site QA.

## Decision ledger, October 31, 2026

| Gate | Status |
| --- | --- |
| Four editorial / two commercial original campaign preserved | YES |
| Native WordPress sample actually received | **NOT VERIFIED** |
| Sender's valid postal address qualified and shown | **NOT VERIFIED** |
| Visible, functioning unsubscribe verified on received copy | **NOT VERIFIED** |
| Newsletter preheader actually rendered as planned | **NOT VERIFIED** |
| Full valuable message including source and near-offer disclosures survives excerpt | **NOT VERIFIED** |
| Reachable, permissioned subscriber audience established | **NOT VERIFIED** |
| Zen12 and Total Focus product guide CTAs live | **NO — DRAFT ONLY** |
| Final Vestige Inspire3 acceptance, email promotion rights and approved links | **NOT VERIFIED** |
| Final founder content / audience / date / any test-send approval | **NOT GRANTED** |
| Hosted `local-content-safety` CI | **FAILED; prior job had no recorded runner or steps; cause unknown** |
| Production change, post publication, schedule, send, list manipulation | **NONE PERMITTED** |

**Release state: all 6 HOLD_UNSENT; 03 and 05 additionally HOLD_MERCHANT.** Do not touch flagship PR #49, send settings, subscription lists, or merchant earning links. The new tool makes any later **authorized, genuine MIME evidence** independently reviewable, but it cannot create that evidence.
