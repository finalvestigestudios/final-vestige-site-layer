# Dispatch R136 — read-only signed-out subscription verification

**DRAFT. ZERO SEND. NOT DEPLOYED.** This package is additive to R135 [PR #1079](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1079) and the original six-issue [master PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), coordinated in [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). It does **not** edit newsletter manuscripts, live WordPress, subscribers, existing homepage PR #49, analytics, merchant links or consent settings. Original **four editorial/two merchant-reserved** plan is unchanged.

## Why this is next, rather than another copy rewrite

Authenticated **WordPress content-projection reads** of published [Dispatch](https://finalvestige.com/dispatch/) page **523** and [Focus](https://finalvestige.com/focus/) page **1579** show a Jetpack Subscribe block rendered as a **same-page anchor**, with no email input or form in the API-projected fragment. This observation is real but **not proof** a signed-out visitor sees the same DOM. A native button-only modal could still work. Until a **signed-out actual-browser** observation establishes a usable labeled email form/modal, the most important direct-audience acquisition path is unproven. This is the focus of the new tool, not an assertion of a live outage.

The R135 separate false-positive issue remains: inline Focus `fvf-gift-v2` treats many arbitrary `subscribe=` values as gift-panel success. R135 [proposed v3](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1079) is **not live**, and *neither* a URL token nor visual UI marker establishes `confirmed_signup`. The free Fieldbook PDF is already public; no revenue bypass has been demonstrated.

## New executable visitor evidence

- `signedout_probe.py --fixture` runs **six offline Chromium fixtures**, differentiating (a) labeled form, (b) self-referencing link, (c) safe button opening modal, (d) inert button, (e) hidden form, and (f) no block. It emits **aggregate DOM facts only**; no entered addresses, cookies, names, form values, or DOM text.
- `signedout_probe.py --live` attempts a fresh unauthenticated Chromium context at exactly `/dispatch/` and `/focus/`. A request firewall rejects non-GET methods and disallowed origins; the script never types an address, clicks a form submit, follows a subscription confirmation, or sends a message. It clicks **only** an explicit `button[type=button]` inside the subscription block, to allow a safe JavaScript modal to appear. A real browser modal could have another trigger and thus still require manual verification.
- HTTP non-success responses fail closed. A browser observation is **not** proof of actual confirmation, welcome receipt, recipient eligibility or purchase.
- `test_signedout_probe.py` executes **25 native Python tests**, including Chromium-based DOM fixture classifications, POST/DELETE denial, lookalike host rejection, blank/HTTP/FTP refusal, no PII fields, no submissions, and no fabricated conversion evidence. Run from this directory with `python -m unittest -v test_signedout_probe.py`.
- This runtime **blocks browser navigation by administrator/network policy**. An authorized live GET-only probe was attempted at both URLs but returned **NOT_TESTED_LIVE**, not a claimed failure on the public website. No external screenshot or received email exists. Run this script in an independently authorized environment with normal browser egress before deciding whether to change the published signup UI.

### Fixture observations (native Chromium)

| Fixture | Source-level browser classification | Implication |
|---|---|---|
| Visible labeled email field | VISIBLE_LABELED_FORM_NOT_SIGNUP_PROOF | Form present; actual opt-in still unverified |
| Same-page Subscribe anchor | SAME_PAGE_ANCHOR_ONLY_PENDING_NATIVE_VALIDATION | Requires manual/modal validation |
| Safe button opens a modal | VISIBLE_FORM_AFTER_SAFE_MODAL_ACTION_NOT_SIGNUP_PROOF | Dynamic forms can work despite initial absent field |
| Type-button without effect | NO_VISIBLE_SIGNUP_FORM_VERIFIED | Candidate visitor blocker |
| Hidden form and same-page link | SAME_PAGE_ANCHOR_ONLY_PENDING_NATIVE_VALIDATION | Hidden field is not a usable visible form |
| Missing block | NO_SUBSCRIBE_BLOCK_DETECTED | No evidence of a native block |

This test differentiates **BUILT/TESTED synthetic** from **LIVE / independently VERIFIED**. It should be rerun on Chromium with 320/390/768/1440 responsive viewports and keyboard focus after any approved UI change. No user is opted in during any probe.

## Current source-of-truth WordPress (read-only, 2026-11-05 11:32 UTC)

Newsletter: enabled/sendable; default new-post emails **OFF**; email body setting **excerpt**; sender **Final Vestige**; recent five articles `never_sent_opted_out`; welcome setting contains the **52-page Seven Day Focus Fieldbook** URL. Dashboard shows **total 3, confirmed 3, unconfirmed 2** and imported within the past 24 hours **1**. These counters are **not additive**. They do not establish three **email-reachable** recipients, three received welcomes, or any new leads attributable to Grok. No matching native subscription-status filtered aggregate was exposed by the connected diagnostics. It remains unknown.

WordPress documentation distinguishes WordPress.com-account subscriptions (which may not require a second email confirmation) from those without an account. A mere absence of a confirmation email therefore does not prove invalid consent; verify authoritative provider status and source-specific consent provenance. Reference: https://wordpress.com/support/newsletter-settings/

## Conversion truth contract — Grok → Focus → Dispatch → buyer

- **Only one event `confirmed_signup`:** first provider-verified `not_subscribed/not_confirmed → subscribed` transition with consent provenance checked, opaque deduplicated subscriber key and campaign referral evidence. A client click, downloaded PDF, page message, aggregate counter, imported address or existing follower is **not** this event. Never log raw addresses or export lists.
- Use stable Grok content `asset_id` and `utm_campaign` for **qualified human session** intake. Once a reader receives an actual approved issue, candidate return URLs use `utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=dispatch_issue_0X`. Proposed parameters are not proof that tracking is live. Do not add duplicate measurement scripts.
- Preserve existing topic→trust sequence: relevant creator post → evidence-first relevant article → Focus Fieldbook → consent-eligible Dispatch → single independently verified buyer guide → approved earning link *only when entitled*. Do not put unrelated merchant products into creator videos or rewrite Grok's distribution queue.
- **Commercially verified sales only:** settled Payhip orders or independently merchant-reported attributable paid commissions, reconciled to refunds/fees. Qualified-human sessions and 7/30-day windows are prerequisites to calculating `net_realized_revenue / qualified_human_sessions × 1000`. If either source is unavailable, **NULL, NOT COMPUTABLE**. No list of three people supports significance claims or A/B performance claims.

## Native WordPress inbox and FTC verification remains OPEN

**Do not send or schedule an email or a test email** without the founder's explicit final approval. The available connector cannot produce a genuine received email; WordPress native editor preview is non-sending when used correctly, but is not proof of inbox arrival. On authorized editor access, inspect a *draft* in its email-preview pane, **do not publish**. Compare both excerpt and full-body rendering *without changing site settings*: subject, preheader, linkable primary CTA, sources, text-size/contrast, near-offer commercial disclosure for 03/05, sender, and complete footer.

Before any commercial email, verify (a) Final Vestige's **own valid physical postal address**, **not** the address of Automattic or Inspire3; (b) genuine rendered **unsubscribe** in the intended message; (c) an operable opt-out route and suppression handling. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . Live previews and real inbox behavior are **NOT VERIFIED**. Excerpt-model research in PR #1050 suggests the six original CTAs may be clipped; do not mistake that model for actual Jetpack delivered mail.

## Exact merchants (independent sales-page crosscheck — 2026-11-05)

**Reserved issue 03: Zen12 Premium**, https://zen12.com/hnp . Merchant depicts twelve levels, four styles, 48 MP3, **displayed** Premium $87.99 and a seller-advertised one-year guarantee. Its free-audio form signs visitors up for the **merchant's separate newsletter**. Claims that 12 minutes produce an hour's meditation benefits and automated focus gains are **seller marketing**, not product-specific outcomes Final Vestige has established. Do not quote a firm checkout price or refund eligibility without independent verification.

**Reserved issue 05: Hypnosis Live *Total Focus***, https://hypnosislive.com/mental-skills/total-focus . Merchant currently displays 33 minutes, 47 MB and $24.44 single-item price, plus seller-described 14-day refund. Checkout terms unverified. **Do not confuse with different product *Hypnotize Yourself***. Unverified brain-reprogramming, guaranteed-concentration and other effectiveness claims are not editorial assertions.

The public https://affiliates.inspire3.com/ describes joining the program and account-specific earning links, **not named Final Vestige approval, approved links or permission to promote by email**. Mind & Affiliate Studio [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) owns offer eligibility, actual approved presell guides, merchant rights and commission truth. Its current guides are **draft**, not live endpoints.

## Owner-ordered unblock plan

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL evidence | OWNER |
|---|---|---|---|---|
| Focus → confirmed lead | Actual signed-out form/modal unknown | Run authorized GET-only real-browser probe on both routes; independently inspect keyboard and mobile | **OFFLINE 6/6; LIVE NOT TESTED** | Site QA / Claude / Dispatch |
| Focus → gift delivery | Public gift UI mislabels arbitrary query as success | Decide R135 v3 or stronger semantic content with no false subscription statement | **Local behavioral defect tested, NOT LIVE fixed** | Dispatch / Claude / founder |
| Jetpack → eligible recipient | Aggregates nonadditive; provider status unknown | Count ONLY native `Email subscription=Subscribed` privately; retain aggregate | **UNKNOWN** | Dispatch / authorized WP admin |
| Dispatch → message CTA | Excerpt may clip CTA and disclosure | Genuine WordPress **non-sending** native preview; verify footer and consent | **UNKNOWN** | Dispatch / Claude |
| Zen12/Total Focus → paid buyer | No FV-specific account/email permission and guides not live | Exact-SKU entitlement, privacy/disclosure, live guide and verified checkout audit | **HOLD_MERCHANT** | Mind #171 |
| Grok → net revenue | No paired human sessions and independently settled transactions | One source-tagged campaign; 7/30-day cohort join; reconcile fees/refunds | **NOT COMPUTABLE** | Praxxis/Grok + Claude commerce #820 |

**Release decision: ALL SIX HOLD_UNSENT; 03/05 additionally HOLD_MERCHANT.** No WordPress/site edits, emails, subscriber contact/import, published links, affiliate activation, tracking additions, or spending in this sprint. Founder must explicitly approve any final send or production change.
