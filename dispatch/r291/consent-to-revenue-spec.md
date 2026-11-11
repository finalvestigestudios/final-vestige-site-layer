# R291: finite, non-sending subscriber-to-customer acceptance path

This is an **operator specification**, not a running campaign. Existing WordPress Jetpack list only; no new platform, subscriber import, email, or paid service.

## Segments based on observable consent (not inferred interests)
A. Visitor / PDF downloader: no proof of email permission. Never counted as a newsletter subscriber.
B. Pending opt-in: confirmation email requested, but recipient not provider-confirmed. Never eligible for marketing.
C. Provider-confirmed + eligible: active publisher subscription, provider verified, no suppression; still do not contact absent founder approval.
D. Known, consented recipient who voluntarily clicked a *topic-matched* email CTA: hypothesis for relevant guide follow-up, not a fact about purchase intent. Do not use hidden tracking, do not create segmentation automatically; only privacy-safe aggregate campaign data.
E. Verified buyer / commission: merchant/Payhip settled evidence only. A click or opened checkout is not a sale.

## Follow-up journey (UNSENT, 4 editorial + 2 reserved commerce)
Welcome: existing configured 52-page Fieldbook, do not resend or modify. Week 1 original Issue01 attention history → existing Change Blindness analysis (if adopted); Week 2 documentary hypnosis history; Week 3 Zen12 commercial evaluation only if partner email permission and Guide/CTA are independently live/approved; Week 4 Apollo 1 primary source Atlas; Week 5 Hypnosis Live evaluation only after same approval; Week 6 reader evidence log and archive follow-on without redundant Fieldbook pitch. This proposal does not select or contact any individual.

## One confirmed_signup event contract
Emit exactly once when existing authenticated WordPress/Jetpack subscriber provider establishes subscription status 'confirmed/active', permissions sufficient for the relevant content, and no suppression. Use non-PII opaque HMAC digest or provider opaque durable id server-side for deduplication; never expose addresses, tokens or identifiers to client analytics. Reconfirmation after an unsubscribe requires documented new permission and separate lifecycle.

Never fire on /focus/?subscribe=..., form-submit success screen, email confirmation-request generation, PDF download, popup dismissal, or manual change to a follower counter. Store only aggregate source attribution when supported and consent lawful.

## Attribution and economics
Preserve incoming source on landing only when actual platform permits: utm_source=(youtube,tiktok,...), utm_medium=organic_social, utm_campaign=<topic>_pilot_2026_11, utm_content=immutable_grok_asset_id. Dispatch editorial links may use consistent utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue04 only after legitimate deployment and URL QA; no new scripts deployed.
Aggregate in 7- and 30-day cohorts; count qualified-human sessions from existing verified analytics, unique provider-confirmed leads, independently settled orders or commissions, refunds and fees. Net revenue per 1000 = 1000 × (settled gross minus refunds minus fees) / qualified sessions. If denominator or merchant proof missing, report NOT COMPUTABLE; never substitute 0.

## Blocker priority
1. Founder/Commerce: authenticate one permitted affiliate channel and earning URL or a rights-cleared sellable owned SKU. No existing rights-cleared paid Mind SKU has been authenticated.
2. Claude/Focus: reconcile provider signup and suppression state privately, remove false client-side completion proof.
3. Dispatch/Founder: native NON-SENDING WordPress Preview email in editor, followed only by explicitly permitted real received-email test if approved. Confirm actual sender postal address, visible working opt-out, email consent and mobile accessible rendering. Preview ≠ received.
4. Mind: publish vetted guide only with appropriate approval; no commercial CTA otherwise.
5. Commerce: independently verify paid settlement to compute net revenue.

## Release policy
All six issues HOLD_UNSENT, #03 and #05 HOLD_MERCHANT. No activation under this document.
