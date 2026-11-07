# R185 · Dispatch consent-to-revenue proof contract (DRAFT ONLY)

**Review time:** 2026-11-07 04:33 PT (time in connected read-only WordPress snapshots 2026-11-07 12:32 UTC). **Parent:** stacked on Dispatch R184 draft PR #1403 (623cea5d2782c3e949910d61348ef5c585799173). **Master:** #175 (d57ccdba3aee8f065e143e101c2945f4f3d01647); edition gates #201; coordination #174, #129, #171, #820. This is NOT an approval or a live implementation.

## P0: what is actually true

- WordPress connector read: Jetpack subscriptions **enabled**, site **can send**, new-post automatic email **OFF**, full-content format, sender **Final Vestige Studios**, `reply_to=no-reply`, Fieldbook 52-page welcome **configured only**. Most recent five posts `never_sent_opted_out`; that is correct and must remain so.
- Subscriber diagnostics: total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**, paid **0**; followers endpoint **3 WordPress.com/Reader, 0 email-only**. **Do not add these figures**. WordPress subscriber guidance states unconfirmed people do not count toward total, and Reader followers are not necessarily mail recipients. **Email Subscription=Subscribed aggregate is unknown**; no subscriber rows or addresses fetched or exported. See https://wordpress.com/support/subscribers/ .
- Fieldbook welcome in settings does not prove any real delivery. Connected Gmail bounded searches found **no received copy** of `Welcome to The Dispatch` or the Fieldbook from Oct 1 onward. One Oct 25 **confirmation request** previously documented is **not** the completed welcome.
- Focus success rendering can be induced from query text; it is NOT a provider-confirmed lead. Sign-up event must come from actual provider status with consent provenance; do not send test emails or add subscribers without separately approved controlled testing.
- Actual WordPress **View → Email preview** is described in October 30 documentation, but has **not been obtained**. No final FV mailing address, Jetpack unsubscribe behavior, inbox preheader or real received MIME has been verified. Static HTML and Gutenberg are NOT Jetpack output. https://wordpress.com/support/newsletter-email-design/ .

## Six-edition offer map and cohort progression

| Edition | Job | Only primary destination | Release status |
|---|---|---|---|
| 01 | Introduce evidence-first Mind stream | Existing Puységur file | HOLD; same CTA as 02 means repetition |
| 02 | Explain witness-versus-claim | Existing Puységur file | HOLD; alternative CTA review needed |
| 03 | Practical meditation question / optional Zen12 guide | **Guide NOT LIVE**; exact vendor-approved affiliate URL NOT VERIFIED | HOLD_UNSENT + HOLD_MERCHANT |
| 04 | Preserve historical investigation identity | Existing Apollo 1 investigation | HOLD; normal editorial |
| 05 | Assess recorded hypnosis / optional Total Focus guide | **Guide NOT LIVE**; channel permission NOT VERIFIED | HOLD_UNSENT + HOLD_MERCHANT |
| 06 | Evidence log and reader retention | Existing /focus/ repeat signup is a friction risk | HOLD; optional non-re-signup editorial alternative in this PR |

**One-offer hypothesis:** once the Mind Studio independently verifies named Inspire3 acceptance, email-channel permission, an approved first-party Zen12 guide, *exact* permitted link and merchant checkout/refund disclosures, target only existing genuinely opted-in and still email-subscribed readers who elected to receive the existing Dispatch. No behavioral profiling or new list. Stay at 4 editorial and 2 commercial **draft placements**. If merchant approval does not arrive, commercial issues remain frozen. A first-party rights-cleared Payhip product may be evaluated separately by Commerce; this repo makes no claim one is sellable.

## Consent and event truth

**Client events:** focus_page_view, subscribe_button_click, `?subscribe=`, opened download panel, and WordPress follower counts are *not* confirmed_signup. **Authoritative candidate:** current Jetpack Email Subscription=Subscribed status with signed-up/confirmed/consent evidence and opaque dedup key, checked by an authorized reviewer; no PII in GitHub. This code creates **zero** confirmed_signup events and never claims to verify signatures. Avoid user-level tracking or false positives; only aggregate confirmed counts after provider reconciliation. For creator origin, when Grok supplies real asset IDs, use utm_source=actual platform, utm_medium=organic_social, utm_campaign=mind_pilot_2026_11, utm_content=actual asset_id. Do not fabricate an asset ID or treat TikTok captions as necessarily clickable. An email CTA can later use utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_mind_pilot_2026_11, utm_content=issue03_zen12, **only after** rights and live-guide verification. Do not deploy scripts or modify links from this memo.

**Revenue proof:** qualified-human session cohort → first-party guide → CTA → separately authorized merchant checkout → merchant-confirmed *settled* purchase → refunds, fees → realized net publisher revenue. Only calculate realized net revenue per 1,000 independently validated qualified-human sessions if ALL source systems and attribution are reconciled; otherwise NOT_COMPUTABLE, never zero by default. Report 7/30-day cohorts once denominators exist. Offline fixture outputs are NEVER live analytics.

## CTA / copy conversion audit of the original master

01 and 02 both send readers to the identical Puységur file; a weekly subscriber sees little destination progression. 03 and 05 have deliberately **inert** guide placeholders. 06 sends a person who already received the Fieldbook welcome back into the signup path. These are the three highest-leverage copy/funnel repairs, not evidence that alternative drafts were approved. Do not rewrite master #175. Source-controlled R177/R182 alternatives exist; R185's optional 06 adds a 2009 primary research lead and a **different published research article**, no merchant CTA.

## Commercial seller-source claims vs proof

- Zen12 seller exact https://zen12.com/hnp describes **12 levels** and **48 MP3s**, with four styles. Vendor also advertises '1 hour in 12 minutes', brainwave effects, stress/focus gains, and guarantee. Those **are seller claims**, not verified efficacy, verified checkout or verified refund execution. Do not use claimed outcomes as FV evidence.
- Total Focus seller exact https://hypnosislive.com/mental-skills/total-focus describes **33 minutes / 47 MB**, advertises concentration outcomes and a **14-day** satisfaction promise. These are marketing descriptions, not product-specific clinical findings. Displayed price and actual checkout can vary; do NOT quote price in emails now.
- Public https://affiliates.inspire3.com/ describes a general program but **does not identify FV** or establish channel permission, a special earning link, permitted promotional creative, or FV's approval. The merchant's own London contact address is NOT Final Vestige's sender address.
- FTC business email standards https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business require truthful sender/subject, clear applicable ad identification, valid sender postal address, effective unsubscribe and honoring opt-outs. Affiliate near-link disclosure must be conspicuous in each qualifying issue; footer-only disclosure is insufficient.

## Blocking decision sequence; owners / pass criteria

1. **One sellable offer → merchant authorization → HOLD.** Mind #171 obtains named acceptance, email promotion rules, permitted creative and precise earning URL. Pass = dated, private source-of-truth terms. No existing evidence meets this.
2. **Focus signup → provider-confirmed lead → HOLD.** Claude/Site QA #129 verifies actual signed-out flow and provider evidence without unauthorised submissions. Pass = authoritative consent + dedup (aggregate only).
3. **Confirmed lead → delivered Fieldbook welcome → HOLD.** Dispatch uses an already-authorized received message or independently granted safe test. Pass = genuine final welcome; not just a confirmation-request email.
4. **Jetpack email → postal + opt-out + render → HOLD.** Dispatch obtains non-sending native **View → Email preview**, observes opt-out and FV mailing address; does not toggle email, save a post or send. Pass = actual preview evidence + genuine channel compliance assessment.
5. **Creator asset → paid reconciliation → UNKNOWN.** Grok owns actual asset_id, Claude analytics, Commerce/Praxxis paid orders. Pass = 7/30-day verified revenue per 1,000 qualified humans with refunds/fees accounted; otherwise NOT_COMPUTABLE.

**Release: ALL 6 HOLD_UNSENT, 03/05 additionally HOLD_MERCHANT.** Founder final campaign authorization missing. No post, mail, test email, WP write, subscriber action, affiliate activation, social post, tracking script, checkout or spend in this deliverable.
