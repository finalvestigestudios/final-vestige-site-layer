# Dispatch R82 — observed non-send provenance (not a delivery launch)

**Recorded 2026-11-02 21:03 PT / 2026-11-03 05:03 UTC. HOLD_UNSENT.** Source-of-truth read: authenticated WordPress Jetpack Newsletter status and settings, not a synthetic marketing estimate. Owner: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), commercial: [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Original campaign [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), release safeguards [draft PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), stacked parent [draft PR #721](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/721). Neither the original six issues nor alternate drafts were edited. The founder's allocation remains four editorial + two commercial-reserved, all unsent. Homepage release #49 remains untouched.

## Materially new actual WordPress evidence: five *opted-out non-sends*

A fresh read now reports **five recent `never_sent_opted_out` post events**, rather than the previous snapshot's empty `recent_sends` array. These are *regular published site posts*, **not pilot newsletter sends**. Their post IDs are 1917, 1920, 1922, 1924 and 1926, recorded in newest-first order in `SNAPSHOT.json` with exact provider timestamps and titles. Every record reports `dispatched_at=null`, `failure_reason=send_subscription flag is false`, and `recipients/sent/bounced/blocked_by_recipient=null`. **They confirm the per-post newsletter-send flag was false for those five events.** They are positive operational evidence that some publication paths retained the no-auto-email rule; they are not evidence of deliverability, a live successful suppression mechanism for every post, or subscriber consent.

**Interpretation discipline:** no delivered emails are shown in these five returned records. That is **not all-time zero**, not an assertion there are no other sends, and not a claim of an effective global mailing stop. Jetpack still reports `site_can_send=true`; this capability flag does **not** mean a message was actually dispatched. Underlying CMS content may be published by other lanes; this audit performs read-only work and does not claim authorship, schedule, or permission for those posts.

The subscribed audience conflict also remains: Newsletter diagnostics `total=2, confirmed=2, unconfirmed=2, suppressed=0`; independent follower statistics `total=2, email=0, wpcom=2, partial=false`. These are categorically different endpoints. **Actual email-eligible subscribers are UNKNOWN**, never the sum four and never established as zero. An authorized site owner must inspect native Subscribers filters in private and record *counts only* by active email status, confirmation and suppression, without exporting names, emails, tokens or rows.

## Authoritative live channel state (read-only)

| Field | Observed | What it establishes |
|---|---|---|
| Jetpack newsletter | enabled | Channel configured, not campaign approval |
| Site can send | true | Technical eligibility, not a successful send |
| Email new posts by default | **false** | Site-wide post editor defaults to opt-out; verify each post individually |
| Email content format | **excerpt** | Full editorial HTML mockups are not proof of email body |
| Reply-to | no-reply | Requires working online unsubscribe mechanism for commercial messages |
| Sender label | Final Vestige | Not verification of full RFC sender or received headers |
| 52-page Focus Fieldbook welcome | configured | **No actual delivered final welcome verified** |
| Five recent post records | never_sent_opted_out | Only these five returned events show no dispatch |
| Publisher address | unverified | Automattic address or Inspire3 UK address is not Final Vestige's postal address |
| Subscriber identity and deliverability | UNKNOWN | No export, duplicate list, or recipient address permitted |

The published /dispatch/ signup page (#523) promises historical investigations and archive updates; the published /focus/ page (#1579) already warns of occasional possible commission-earning recommendations. Their **same Jetpack list** is preserved, but this mismatch still needs a separately approved, nondeceptive explanation before commercial sends. The published Editorial Standards (#17) say commercial relationships never determine historical conclusions. All three pages were read with authenticated WordPress access. Do not treat a REST-rendered Subscribe anchor as evidence that a live browser form works or fails.

## New reproducible inspection

The exact WordPress aggregate snapshot lives in `SNAPSHOT.json`. Run locally, with **no network and no WordPress permission required**:

```bash
python dispatch/campaign-2026-mind/r82-send-provenance/verifier.py
python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_r82_send_provenance.py' -v
python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_campaign.py' -v
```

The verifier uses a strict allowlist, confirms chronological order and valid timezone offsets, requires five observed opted-out records with null delivery counts, rejects any false positive send, rejects changed counters or a newly verified gate, and prints **only redacted aggregate interpretation**. It does not inspect recipient identities, send, schedule, publish, track, modify WordPress, verify legal compliance or approve a campaign. New evidence must produce a new dated snapshot, not a retroactive edit to the October/November provenance record. Use the static [HTML reviewer](REVIEW.html) and [plaintext version](REVIEW.txt) to explain this to a human reviewer.

## Independent current product-specific claims and permissions

Commercial slots **03 Zen12** and **05 Hypnosis Live Total Focus** remain **HOLD_MERCHANT** independently. Actual official product pages were checked November 2: [Zen12 product page](https://zen12.com/hnp) advertises 12-minute tracks and *hour-equivalence / brainwave / health and focus* results; these are **seller promises**, NOT independently demonstrated performance of the named product. [Total Focus seller page](https://hypnosislive.com/mental-skills/total-focus) calls the product a 33-minute / 47-MB recording and advertises concentration and brain-reprogramming results; these are seller claims. Its storefront shows multiple prices and bundle placements; price/refund/checkout terms must not be fixed in copy without current authorization and matching checkout. [Inspire3 privacy](https://inspire3.com/privacy/) describes potential disclosure of buyer details to affiliates. No customer data should be imported or assumed available to Final Vestige.

Read-only Gmail searches during this run returned public/consumer promotions, **not verified Final Vestige-specific written acceptance or permission to promote Zen12 and Total Focus by email**. Public affiliate recruitment and a consumer newsletter do not constitute channel authorization. Mind & Affiliate Studio's [draft PR #728](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/728) includes a new Zen12 guide; it is NOT approved or published, and the product eligibility gates remain closed. The Total Focus guide also remains unpublished. No price, refund duration, payout, approved tracking destination or promotional-rights statement is promoted in this packet.

## Release sequence: evidence, not more provisional copy

1. **In private native WordPress:** count email-eligible subscribers with correct filters and record an aggregate-only screenshot/attestation. Do not infer from `confirmed=2` or `followers_email=0`. Verify per-post opt-out setting persists. No subscribers contacted.
2. **Publisher identity:** supply a real qualifying business physical address (registered PO Box or properly registered private mailbox may qualify) and confirm how it appears in *both* actual HTML/plaintext received commercial email. Do not substitute Automattic's address.
3. **Native visual preview separately from received MIME:** before any test send, obtain separate explicit approval for draft post / preview operations and named controlled recipient. Preview email is NOT equivalent to delivery; a real received email must prove sender, disclosure in excerpt, footer, working unsubscribe, accessibility, and no unexpected tracked URLs. No test was made here.
4. **Commercial approval, product by product:** Mind & Affiliate Studio must supply signed/recorded account acceptance, specific permitted email channel, allowable approved creative, link format, buyer-guide publication approval, current checkout/refund facts, data-handling decision, and privacy-safe reporting. Direct merchant links stay inactive.
5. **Founder final review:** approve each final subject, post excerpt, destination, recipient segment, valid publisher postal address, email delivery evidence, date and sending action explicitly. Site remains default-off; no generic campaign approval should be interpreted as permission to publish or email.

The [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful identification/subject, proper disclosure when commercial, a valid sender physical mailing address and functional opt-out, including mixed promotional messages as applicable. WordPress's [Newsletter appearance documentation](https://wordpress.com/support/newsletter/email-appearance/) distinguishes native preview from actual test-send and confirms excerpt versus full-text behavior. **Neither code tests nor screenshots can replace real received-email/legal signoff.**

**Decision: all six HOLD_UNSENT; commercial 03/05 additional HOLD_MERCHANT.** No CMS write, post/email publish or schedule, newsletter configuration, subscriber import/contact, new service, cost, offer link or tracking occurred in R82.
