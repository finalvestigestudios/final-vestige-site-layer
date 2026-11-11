# R278 — The Dispatch: buyer conversion and legitimate-email evidence runbook
**Status: RESEARCH/QA ONLY · ALL SIX ISSUES HOLD_UNSENT · November 11, 2026.** Owner: Dispatch Studio. Original campaign PR #175; release-gate PR #201; previous stacked PR #2028. Sources of truth: issues #174, #171, #129, #820. This is NOT an order to publish, send, test-send, alter subscriber data or activate links.

## One commercially decisive hypothesis
Audience: a person who arrived from a Grok-owned attention/perception story, voluntarily requested the 52-page Focus Fieldbook, remains eligible to receive Dispatch emails, and is comparing a low-time-commitment guided-audio product against a no-cost self-directed focus routine. Preferred prospective offer to vet: **Zen12** via the **actual approved Final Vestige warm-up guide**, NOT the merchant signup page or a generic product catalog. No assertion that this buyer segment currently exists or has purchased.

A qualified conversion is an independently reconciled settled purchase minus refunded fees/costs, not a visit, newsletter click, self-reported interest, merchant opt-in, or triggered tracking pixel. The other potential product, Hypnosis Live Total Focus, remains a separate reserved commercial slot (#05). Four original issues (#01, #02, #04, #06) remain editorial, two (#03, #05) under offer-review hold.

## Ground truth: WordPress snapshot (authenticated read-only 2026-11-11 10:36 UTC)
- Newsletter subscriptions **enabled**, site **can send**, **new-post default auto-email OFF**, email content **FULL**, sender "Final Vestige Studios", reply-to **no-reply**, category filtering OFF.
- Subscriber diagnostics: **total 3, confirmed 3, unconfirmed requests 2, suppressed 0**. Separate observation from earlier WordPress subscriber breakdown: WP.com followers **3**, email followers **0**. Categories differ; **never add these counts** or infer 3 eligible recipients.
- Five listed recent November 3 WordPress post entries have `never_sent_opted_out` and `dispatched_at=null`. This is evidence that these five did not send, **not** that no email was ever sent anywhere.
- `site_can_send=true` is a system capability, **not authorization**. `email_new_posts_by_default=false` controls the **default** for a new post; an operator can turn sending on for an individual post. Any later publication work MUST independently verify `_jetpack_dont_email_post_to_subs=true` on that post **before publication** (and founder must approve the publication separately).
- Existing welcome says it delivers the Fieldbook PDF at `https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf`. This proves configuration only, **not inbox receipt, working download, or consent**. Actual received welcome remains unverified.
- /dispatch/ page #523, /focus/ #1579, Editorial Standards #17 are published. No production changes were made.

### Non-sending native WordPress preview — operator evidence checklist (no test email)
Official WordPress documentation states **Preview email works whether per-post Send is on or off**. This is a viable preview path, but the present connector exposes newsletter settings/status and post content, **not a rendered email preview call**.
1. In an authorized editor session, inspect an existing **draft only** after verifying the edition's identity and that "Send this post to subscribers" is **OFF**; do **not** create/publish a post for this QA without explicit separate founder permission. The user has not authorized post creation or emails.
2. Open Newsletter panel → **Preview email**. **Never press Send test email**: a test email is an email and remains forbidden. Avoid Publish and Schedule; merely opening a preview should not send.
3. Check desktop/tablet/mobile with at least 320px/390px/768px viewports. Record device, UTC timestamp, browser, visual defects, plain HTML headings, evidence/source links, subject/preheader alignment, and one visible intended CTA. Mask any personal address and all subscriber PII in screenshots.
4. Inspect the actual rendered/footer view for **Final Vestige's valid physical postal address** (a legitimate registered USPS PO box/private mailbox may qualify), sender identity and functional unsubscribe. **Do not borrow Automattic's, Inspire3's or a seller's address.** A static HTML placeholder is **not** proof.
5. The separate unsubscribe verification must use a controlled, independently authorized non-production proof or an actual existing delivered email supplied by an authorized mailbox; **no click on a live subscriber's opt-out**, no changing list status, and no sending test messages without founder approval. If not independently verifiable, label UNKNOWN.
6. Check that the preview does not unexpectedly include post metadata, older featured images, hidden commercial CTA, tracking pixels, or brand claims unsupported by source. The published site page is **not** the inbox preview.
7. Preserve evidence reference/timestamp and note explicitly whether this is **editor preview**, **test email received**, or **actual previously received message**. Only the latter two establish delivery, and they are not authorized this run.
**Current status: NATIVE_PREVIEW_NOT_PERFORMED; RECEIVED_EMAIL_NOT_OBSERVED; POSTAL/UNSUB_UNVERIFIED.** Never promote a static mockup into a claimed Jetpack-native preview.

Official instructions: https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/disable-newsletter-emails/ .

### Count mismatch: exact read-only provider resolution
WordPress support (last reviewed **2026-11-04**) defines "Not subscribed" as Reader-only, "Not confirmed" as an unconfirmed request, "Bounced", "Emails paused", and "Not sending" as delivery-ineligible distinctions. The subscriber's Email subscription field, rather than the diagnostic total, is the appropriate recipient gate.
**When authorized access to the private subscriber UI exists:** Jetpack → Newsletter → Subscribers → filter Email Subscription = Subscribed, then exclude Not sending/paused/bounced. Record ONLY aggregate counts and filter timestamps; don't download/import a list or reveal email addresses. Distinguish verified provider subscription transition from email-link click (verified WP.com accounts may not need a new confirmation click). Record first confirmed entry once per stable provider subscriber key; never expose the key in public reports. Verify consent provenance and actual edition/category scope. If private UI access is absent, the recipient count remains UNKNOWN, not zero.
Official: https://wordpress.com/support/subscribers/ .

### The legal gate
The FTC CAN-SPAM guide requires accurate header/sender, honest subject, clear identification of advertisements where required, **Final Vestige's valid postal address**, a functional opt-out and timely honoring of opt-outs. A general site affiliate-disclosure page does **not** substitute for a clear, adjacent disclosure next to qualifying commercial CTA. Consent and CAN-SPAM are separate responsibilities. An unverified postal/address line or placeholder blocks a commercial send. No legal opinion is inferred from the offline tests.
FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Source-specific vendor-to-editorial alignment (no commercial activation)
### Zen12 / proposed Issue 03
Merchant source: https://zen12.com/getstarted and https://zen12.com/welcome . Public Zen12 pages describe a 12-level/48-MP3 offering and market "one hour in twelve minutes"; that comparative efficacy claim is **the seller's assertion**, not independent Zen12-specific proof. The free-audio page enrolls readers in **Zen12's** own newsletter, which is neither a Dispatch signup nor a legitimate evidence of Final Vestige subscriber consent. Some seller landing routes show varying coupon prices/countdown widgets: do not repeat a price, discount, guarantee, timer, or quote copy without exact route/current checkout and account approval. Product content and terms require current merchant verification near launch.
Acceptance evidence REQUIRED from Mind Studio: actual partner account approval, precise permitted email-marketing channel, legitimate identified Final Vestige earning URL and promotion creative authorization, latest checkout/refund details, published accessible warm-up guide with independent evidence and near-link disclosure. No screenshots of a public catalog can prove account-specific authorization.

### Hypnosis Live Total Focus / proposed Issue 05
Merchant source: https://hypnosislive.com/mental-skills/total-focus (33-minute / 47MB recording shown publicly; seller makes sweeping effectiveness claims) and https://hypnosislive.com/faq (14-day refund-request window, **maximum five sessions refunded annually**). Public site prices and discounted bundles vary; buyer guide must reflect only exact verified route/checkout terms and distinguish stated seller benefits from clinical proof. Vendor website general affiliate-program language is not Final Vestige-specific email-marketing acceptance. Same authorization/guide/disclosure rules as Zen12.

### Critical seller-policy pitfall
A public Inspire3 campaign page for *another product* may offer "swipe copy" and note that email marketing is possible for eligible approved affiliates. That **does not** prove approval or permitted email channel for Final Vestige's **Zen12/Total Focus** placements. Never substitute merchant identity or approved routes across offers.

## Owner → action → acceptable evidence
| Offer → funnel step | Blocker | Change/experiment (draft, no live changes) | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Zen12 → FV warm-up guide → authorized earning link → paid sale | Partner email rights, approved guide, and earning link not authenticated | Authenticate exact publisher account + email terms; validate one guide in full | **HOLD** until named written acceptance + account-authenticated URL + live guide + disclosed working link | Mind & Affiliate Studio |
| Focus form → provider-confirmed lead | Read-only totals 3/3/2 conflicting with follower 3/0 | Privately filter eligible email status, record consent provenance and first confirmation; dedupe | **UNKNOWN**, not 3 confirmed email recipients | Focus/Claude |
| Fieldbook configured → received welcome → verified PDF | Only configured URL known | Read existing authorized received email or obtain separately approved testing | **UNKNOWN**; no real received message | Focus / Dispatch |
| Original six → intended CTA → Jetpack inbox | Preview/footer and unsubscribe unknown | Native draft preview without send; address and opt-out evidence capture | **HOLD**; no native preview or postal evidence | Dispatch / Site QA |
| Grok asset_id + UTMs → page → lead | No provider-confirmed attribution link | Use existing `utm_source`, `utm_medium=organic_social`, `utm_campaign=<topic>_pilot_2026_11`, `utm_content=<unique_asset_id>`; do not deploy duplicate trackers | **HOLD_DATA** until actual first-party events linked to real assets | Grok / Praxxis / Claude |
| Merchant transaction → refund/fees → realized net | No authenticated settlements | Reconcile independent merchant orders/commissions vs refunded/reversed transactions | **NOT COMPUTABLE**; no fake click → sale extrapolation | Commerce / Praxxis |

## Strict go/no-go
A draft/branch/test passing does not authorize an email. Global prerequisites: founder final campaign approval **including audience and cadence**, active eligible subscriber evidence, actual welcome/PDF evidence where promised, verified legal footer and rendered unsubscribe, native inbox preview, every destination live/verified and no activation of automated post sends. Additional for #03/#05: named partner approval, email channel permission, exact earning link, evidence-correct claims, accurate public offer terms, and functioning reviewed warm-up guides. If any proof is absent, HOLD that issue. The offline validator intentionally **never** returns READY or synthesizes revenue.

No sends, subscriber contact, imports, settings writes, social publishing, paid services, WordPress writes, merchant activation or merge are authorized by this document.
