# R194 — Consent-to-revenue release blockers (NO SEND, NO CMS WRITE)

This is a read-only operational evidence guide, NOT evidence that delivery or sales were completed. Existing original six drafts (#175), commercial allocation 4 editorial / 2 commercial, hard gate (#201), homepage freeze (#49) unchanged.

## Site evidence, November 7, 2026 at 21:34 UTC
Authenticated WordPress Jetpack newsletter STATUS: enabled; new-post auto-email OFF; recent five published posts marked never_sent_opted_out; site_can_send=true (capability, NOT authorization); dashboard total=3, confirmed=3, unconfirmed=2, suppressed=0. Separate stats: three WordPress.com followers and zero email-only followers. Counters are **NONADDITIVE**. Neither these follower counts nor a browser Focus "download ready" state proves provider-confirmed *email-eligible* recipient status. Actual eligible audience is UNKNOWN.

Authenticated GET_SETTINGS: full content mode (historical excerpt finding is stale); from-name Final Vestige Studios; reply_to no-reply; configured welcome contains 52-page Fieldbook PDF link. Configured ≠ received. No test message sent.

## No-send provider/consent diagnostic (Dispatch + Claude)
A. Read-only native Subscribers filter **Email subscription = Subscribed**, distinguish WordPress.com Reader followers, paused delivery and unconfirmed requests. Log ONLY de-identified AGGREGATE total and observation date. Do not fetch/export individual addresses. Do not infer zero from email-only follower counter.
B. Inspect an ALREADY received, owner-controlled confirmation and then separate final welcome. Require actual evidence of second message and working 52-page PDF, without generating another subscription or contacting list. Old Oct 25 confirmation request is not proof of completion.
C. Seek true non-sending native Jetpack email preview through authenticated editor. If preview cannot prove real recipient headers/footer, label EDITOR_PREVIEW_ONLY; a received-email claim requires separately authorized sending. Log actual title-derived subject, preheader if provider creates one, mobile rendering, accessible links, publisher postal footer and functional unsubscribe. No test send here.
D. Do not insert a guessed physical address. A legal FV postal address must be verified and visible in actual commercial mail; Automattic and Inspire3 street addresses do NOT count. CAN-SPAM: honest sender, title, marketing identity, physical address and opt-out.

## Single-verified-offer commercial path (Mind #171 owns offer)
Current intended offer: Zen12 Premium, not a rotating catalog. Seller page https://zen12.com/hnp describes 12 levels, multiple recordings and an asserted twelve-minute-to-hour equivalence. The latter is a seller **claim**, not proven product efficacy. Hypnosis Live https://hypnosislive.com/mental-skills/total-focus describes a 33-minute/47-MB file and a 14-day refund representation; these are NOT settled checkout or efficacy proofs. Public affiliate landing https://affiliates.inspire3.com/ establishes neither specific FV account acceptance, permission to market by EMAIL, issued earning link, licensed creatives, refund terms, nor a LIVE site guide. Mind drafts including PR #1467 are UNPUBLISHED. Never link drafts as live destinations.

Partner acceptance gate must be supported by private publisher-specific portal evidence and clear EMAIL-channel permission; keep account references private, record only non-identifying attestations. Only Mind-approved published guide may be used as CTA in issue 03. Affiliate promotion must be disclosed adjacent to offer and in the same email. Do not activate a link based on the public seller site.

## Non-sending progression and measurement
Welcome containing the Fieldbook (no trigger here) → one editorial evidence issue → (conditionally, only if verified, approved) ONE issue 03 Zen12 buyer-guide CTA → independent merchant transaction. Existing issue 05 remains commercial HOLD; do not quietly double frequency or add a second active offer. Editorial issues stay editorial. All sends require separate final founder approval of content, audience and schedule.

Confirmed_signup event SPEC: only authoritative provider subscription confirmation with consent source and deduplicated opaque provider event/subscription key; never browser success, PDF click or Reader follower; no email address in analytics. Grok asset_id plus first UTM acquisition fields are captured at landing (when already permitted) and never overwritten by later Dispatch utm_source=dispatch, utm_medium=email, utm_campaign=fv_dispatch_pilot_2026 and utm_content=issue03_zen12_guide. No new scripts/platforms are authorized.

Realized net revenue per 1,000 qualified HUMAN sessions = 1000 * (independently settled payouts - verified refunds and attributable fees) / verified qualified sessions. Both 7-day and 30-day cohorts require a defensible denominator and confirmed accounting. No fake zero-sales assumption or invented A/B improvements with three counted followers.

## R194 offer → step → blocker → change/experiment → evidence → owner
1. Zen12 → buyer: partner email rights/approved earning link/live guide unverified → named partner attestation and independently reviewed live warm-up guide → FAIL/HOLD_MERCHANT → Mind/Founder.
2. Focus → provider-confirmed subscriber: filtered eligible aggregate absent → read-only provider status crosswalk, dedupe → UNKNOWN/HOLD → Claude/Dispatch.
3. Confirmed subscriber → welcome: delivery not observed → inspect authorized already-received final welcome/PDF → UNKNOWN/HOLD → Dispatch.
4. Dispatch → compliant email: native rendered recipient evidence, valid FV address, working opt-out absent → true preview; receipt only with future explicit approval → FAIL/HOLD → Dispatch/QA.
5. Buyer → realized net income: no independent settled order and denominator → reconcile paid order, refunds, fees and source → NOT COMPUTABLE → Commerce/Praxxis #820.

No email was sent or scheduled, and no WordPress/content/subscriber/analytics/commercial live change is authorized by this document.