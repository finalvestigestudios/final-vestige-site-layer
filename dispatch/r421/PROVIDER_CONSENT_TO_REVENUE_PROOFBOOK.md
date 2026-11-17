# Dispatch R421 — consent-to-revenue proofbook, not another draft campaign

**2026-11-17 10:34 UTC read-only evidence. DRAFT / HOLD_UNSENT.** Owner: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Partners: [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [Revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Original six [master PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); independent [per-edition PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201); latest six exact-source [previews #2848](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2848); previous [parity gate #2853](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2853). No modifications to these drafts, homepage PR #49, Grok's TASK-008, WordPress or subscribers.

## New result: three separate WordPress count systems, one real PDF asset, zero proven deliveries

Authenticated **WordPress newsletter status/get_settings** returned: enabled=true; platform_can_send=true; default new-post emailing=false; full format; reply_to=no-reply; subscriber dashboard total=3 / confirmed=3 / unconfirmed=2 / suppressed=0 / paid=0. Five recent *post notification* statuses are `never_sent_opted_out` with null recipient and send counts. Do **not** extrapolate this five-post window to all historical mail, and do not mistake `site_can_send` for founder authorization.

Authenticated **Jetpack Stats followers**, separate endpoint, returned `partial=false`, WordPress.com Reader=3, direct email=0, comment=0, publicize={}, total=3. The Stats tool defines its total as a channel sum (one person may appear in multiple channels). This is **not** the newsletter Subscribers dashboard, nor a provider-authoritative deduplicated mailing audience. We cannot infer zero deliverable recipients from email=0, nor three eligible inboxes from Reader=3. The dashboard also cannot be treated as a partition: 3 confirmed + 2 unconfirmed != total 3. **Distinct permitted inboxes and current eligible confirmations are UNKNOWN, not 0, 3, or 5.**

Authenticated media library **read-only** found ID **1737**, published 2026-10-29, `application/pdf`, **599,946 bytes**, source `https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf`. This *exact URL* appears in the current Jetpack welcome_message describing the 52-page Focus Fieldbook. **NEW VERIFIED DISTINCTION: configured delivery URL is a real media-library object, but no inbox receipt or downloaded/opened PDF is proven.** Web PDF direct retrieval here was not successful; media presence does not prove public HTTP availability from every network. Do not assert that every subscriber received a copy. Existing earlier 6- and 7-page PDFs are different media items and must not replace ID 1737.

### Executable acceptance audit

Run:
```sh
python3 dispatch/r421/consent_snapshot_gate.py
cd dispatch/r421 && python3 -m unittest -v test_consent_snapshot_gate.py
```
The first emits a **non-PII** `READ_ONLY_AGGREGATE_DIAGNOSTIC` with recipient, conversion and revenue numbers explicitly null. The second supplies 20 negative tests, including forged EMAIL rights, forged welcome receipt, bogus audience arithmetic, exposed subscriber email, unsalted email-token-like field, wrong file, wrong format, numerical corruption and false send permission. This gate **does not** authenticate future private evidence or send mail. Snapshot values are historical observations; do not represent them as continuously live.

## Exact missing witnesses: consent and welcome (owner Focus / Claude)

Work only in the provider's authenticated subscriber management view and private access-controlled evidence store. Do not export emails or other subscriber identifiers to GitHub, Drive task handoffs, site event URLs or QA logs.

1. Inspect Jetpack's actual subscriber records and provider-defined statuses, including Reader following versus email delivery preferences, unconfirmed and suppression states. Document the **provider endpoint and definition of each count**, the observed timestamp, record-level dedup procedure and a private reviewer receipt. Do not assume confirmed means recipient-eligible.
2. Establish `confirmed_signup` as **one authenticated provider confirmation transition**, not a submit button, URL success state, Fieldbook download, newsletter dashboard total, Reader follow or welcome configuration. Deduplicate privately on provider-issued opaque account/subscription identity; never use a raw email, unsalted SHA-1 email or client-generated localStorage counter. Require status transition time and permission to receive this particular newsletter.
3. Preserve opt-out as a separate state: an unsubscribed identity does not become eligible merely because it formerly confirmed. Treat re-subscribe as a fresh authorized provider state transition, not an extra lead from retries.
4. For existing current subscribers, distinguish a **historical confirmed lead cohort** from today's **currently email-eligible recipient set**. Never sum these quantities.
5. Verify the exact 52-page welcome/PDF through an authorized received-inbox witness, including sender, destination account consent, actual email body, exact PDF URL, MIME/link rendering and fetch result. A previous Gmail *confirmation* message and Automattic postal address do not establish this witness. Any real test mail, re-send or new signup requires founder-specific permission; **none is authorized here**.

The private evidence handoff may record counts and proof IDs only, never addresses, unsub tokens, login links, subscriber export or raw events that can reidentify a person. A private signed witness can later supersede the null in this packet; a bare `true` toggle in a JSON fixture cannot.

## Native email and legal proof (Dispatch / Founder)

The official [WordPress email appearance documentation](https://wordpress.com/support/newsletter/email-appearance/) says an editor's **Preview email** shows desktop/tablet/mobile and works even when subscriber sending is toggled OFF; **Preview email** is distinct from the separate **Send test email** button. No available connected read-only action exposes this editor UI; it remains unwitnessed. No WordPress draft is created or edited by this PR.

Once authorized for UI inspection, capture privacy-safe screenshots of six *existing or separately approved draft* source editions, record the title-as-subject, test whether authored preheaders survive provider rendering (not assumed), inspect image alt text, heading order, 320/360/390px wrapping, focus and contrast, editorial CTA destination, no scripts/forms/tracker pixels, and a real legal footer. A native Preview is **not** itself proof that a recipient receives working mail. A genuine received-message and unsubscribe verification would require separate approval and appropriately scoped test consent.

The [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) includes commercial email promoting content on commercial websites. **Do not exempt the four editorial issues merely because they are not direct affiliate ads.** All six need accurate sender/subject, a valid *Final Vestige* physical business mailing address, and a clear functioning opt-out **where the commercial primary-purpose rules apply**; safest release rule: verify footer and unsubscribe on all six. The vendor's own postal address, Automattic's address from a confirmation email, or a link to an FV contact form is not a substitute. A `no-reply` sender is **not** a functional reply-based opt-out. Independently verify an unsubscribe link route and processing before release; FTC states an opt-out mechanism must work for 30 days and requests honored within ten business days.

### Issue-specific release matrix (no adoption)

| Issue | Purpose | Current CTA | Release decision |
| --- | --- | --- | --- |
| 01 | Perception, historical evidence | Puységur archive | HOLD_UNSENT; repeated link vs #02 |
| 02 | Suggestion/history | Puységur archive | HOLD_UNSENT; founder alternative not adopted |
| 03 | Zen12 buyer question (commercial) | free first-party resource only, paid warm-up token inactive | HOLD_MERCHANT; named EMAIL rights + approved LIVE guide |
| 04 | Apollo 1 and incomplete causation | existing published investigation | HOLD_COPY; fourteen-second interval ambiguous |
| 05 | Total Focus evaluation (commercial) | free first-party resource only, paid warm-up token inactive | HOLD_MERCHANT; named EMAIL rights + approved LIVE guide |
| 06 | Seven-day evidence log | /focus/ acquisition page | HOLD_CTA; returning subscriber may face duplicate signup |

Original 4 editorial / 2 commercial allocation remains. Existing alternatives from [#2827](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2827) are **unadopted**. Do not swap letters, schedule, merge or send without founder approval. Original HTML/text source parity checks are handled by R420; **this R421 packet addresses provider-level consent and inbox truth, not another redundant preview generator**.

## Merchant source-of-truth — seller words are not independent proof

Official [Zen12 product page](https://zen12.com/about) describes 12 levels with four listening styles and says twelve minutes equate to one hour; equivalence and immediate efficacy statements are seller marketing, not independently demonstrated Zen12 outcomes. Its separate [promotional funnel](https://zen12.com/secret/) presents a coupon price, not an authorized FV checkout or enduring public SKU. [Total Focus product](https://hypnosislive.com/mental-skills/total-focus) presents a 33-minute / 47-MB recording and separate two-recording bundle; [official FAQ](https://hypnosislive.com/faq) says fourteen-day refunds are limited to **five sessions per year**. Promotions may change and must be reverified against the actual referred checkout at release. These sources do not establish named Final Vestige affiliate acceptance, EMAIL promotional rights, approved email creative, link format, payout, referred pricing, returns or settlements. [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) owns approval and the guide; its latest R441 handoff retains all commercial holds.

**Decision:** No prices, merchant links, coupon codes, tracking URLs or performance promises go in campaign. One-offer commercial pilot is *proposed* Zen12 only after it becomes legally and technically eligible; Issue 05 retains its reserved optional second commercial slot, not a second currently active buyer journey.

## OFFER → FUNNEL STEP → BLOCKER → TEST/CHANGE → PROOF → OWNER

| Offer | Step | Blocker | Controlled next experiment / acceptance | Owner |
| --- | --- | --- | --- | --- |
| Free Fieldbook | Grok → Focus | Exact active content-to-page continuity unknown | Existing organic asset ID and permitted UTM passthrough, read-only inspection first | Grok / Praxxis / Claude |
| Free Fieldbook | Focus → confirmed_signup | Dashboard 3/3/2 and Reader3/email0 not deduplicated eligibility | Provider-authenticated state transition + privacy-safe duplicate suppression; never synthetic success | Focus / Claude |
| Free Fieldbook | Confirmation → actual welcome | Media item exists but receipt not established | Private authorized inbox witness and PDF fetch proof, no live send today | Focus / Founder |
| Zen12 | Dispatch 03 → FV guide | Guide is draft and email rights unverified | Mind obtains documented EMAIL rights, LIVE approved accurate guide and issued earning URL; no direct seller fallback | Mind / Commerce |
| Zen12 | Buyer guide → settled commission | Referred checkout and partner reporting unverified | Confirm package, return terms, independent commission settlement with refunds/fees | Mind / Commerce |
| Total Focus | Dispatch 05 (reserved) | Email rights/SKU/refund scope unknown | Separate approval path only, no activation | Mind / Commerce |
| Dispatch pilot | Compliant email preview | Native editor UI, publisher address, opt-out unverified | Founder-authorized read-only native Preview then separately consented actual inbox test | Dispatch / Founder |
| Overall | Paid buyer / per-1000 human sessions | No audited session denominator or verified settlement | Reconcile 7/30-day cohorts, net = settled gross less fees/refunds; mark missing as null | Claude / Revenue |

The pipeline remains: Grok asset `utm_source=platform`, `utm_medium=organic_social`, `utm_campaign=topic_pilot_2026_11`, `utm_content=unique_asset_id` → topical landing / Focus → provider-confirmed opt-in → editorial Dispatch → approved first-party guide → merchant referral (only if permitted) → independently confirmed settlement. A future Dispatch first-party CTA convention is `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_03`, but this is **specification only** and may need WordPress link rendering verification; do not publish active tracking links. Preserve original Grok asset ID upstream with privacy-safe first-party attribution when permission and technical continuity exist. Do not invent last-touch buyer identity, an attributed purchase, or revenue from a click.

**Business KPI:** realized net revenue per 1,000 qualified-human sessions is **NULL / NOT COMPUTABLE** today, not zero. Sample-size and missing-attribution warnings are mandatory. No platform pageviews, opens or follower counts may be substituted for paid settlements.

## Immutable permissions and site safety

No email / test email / campaign schedule / post publication / newsletter setting change / subscriber import / new mailing list / affiliate link activation / WordPress write / Grok social post / homepage PR #49 edit / merge / spend. This is an independent, additive draft proposal for founder acceptance. Any attestation update must come from actual provider or merchant evidence, not from this synthetic offline packet.
