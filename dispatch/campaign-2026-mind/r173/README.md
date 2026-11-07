# Dispatch R173 — commercial disclosure proximity / conversion gate (UNSENT)

Date: **2026-11-06 Pacific**. Scope: stacked on PR #1322, preserving master campaign PR #175, readiness #201, frozen homepage PR #49. Owner Issue #174, merchant alignment Issue #171, Focus Issue #129, conversion Issue #820.

## Actual regression discovery (native synthetic MIME)

R167/R168 `received_eml_preflight.py` considers a commercial disclosure **present anywhere in the received email** to be acceptable for its `commercial_disclosure_visible` *component* check. An original synthetic MIME with a first-party guide CTA, **420 unrelated characters**, then "Final Vestige may earn a commission" in a footer returned `commercial_disclosure_visible=True`. The older checker **still returns HOLD_UNSENT**; this is a **near-offer compliance-evidence false positive**, not proof of an unauthorized send.

New `offer_proximity_gate.py` catches distant footer-only copy, hidden/aria-hidden/style-hidden disclosures, missing plaintext disclosure, multiple offer CTAs, non-vetted URLs, direct affiliate hrefs, unresolved legal placeholders and suspect timing/efficacy phrases. This is a companion to, **not a replacement for**, the R167/R168 email MIME checker. It accepts precisely one canonical first-party guide CTA and a disclosure within 220 visible-text characters. It always returns **HOLD_UNSENT** regardless of results; visible-text proximity is *not* visual adjacency or legal approval. The expected guide pages are not live, so no actual email meets the gate today.

## Independently executed native results

- `python -m unittest -v test_offer_proximity_gate.py`: **17/17 pass**, CPython native. The initial run exposed one malformed-HTML end-of-file guard error (16/17); patched; full final rerun green. Source/test Git blob SHA-1 matches locally tested exact bytes: **source `c2dc927ea636a9682f0fa235735be4b2ddaa2c3d`**, **tests `e0d73d1c919cae15671699411f9c64897b3ff6cf`**.
- Synthetic reproduction: prior `commercial_disclosure_visible=True`; R173 `disclosure_adjacent_to_every_qualifying_html_cta=False`; **both remain HOLD_UNSENT**.
- Original PR #175 Python test suite is **not rerun natively at its exact GitHub PR head this sprint** because container DNS cannot fetch the private repository. No false CI claim.
- Offline reviewer and source code package attached separately. The reviewer is not a genuine Jetpack email or evidence of delivery.

## Current verified WordPress (read-only 2026-11-07 00:34 UTC)

Newsletter enabled, new-post default email disabled, **full** body setting, displayed sender **Final Vestige Studios**, no-reply, existing welcome message contains 52-page Focus Fieldbook. Five last posts are `never_sent_opted_out`. Reported counts **total 3 / confirmed 3 / unconfirmed 2 / suppressed 0**, nonadditive. WordPress support (last reviewed 2026-11-04) confirms Not confirmed isn't counted and Reader-only / paused / bounced may not be email-reachable: https://wordpress.com/support/subscribers/ . **Email-eligible recipient count unknown** until private provider-native Email subscription status tally (do not commit addresses).

`/dispatch/` page #523 contains the Jetpack Subscribe block in editable content; whether public signed-out visitors see a usable email field is still unverified. `/focus/` page #1579 still has unsafe client-only visual gift-reveal signaling in `fvf-gift-v2`; do not claim a `confirmed_signup` from a query string, CSS class or Fieldbook click. Claude/Site QA own implementing already-drafted #1272 fix after release approval.

## Merchant and legal source findings

Exact https://zen12.com/ public seller page describes Zen12 Premium **12 levels / 48 MP3**, an advertised **one-year guarantee** and public listed price **$87**, while another dated source review reported **$87.99**. Checkout and refund execution NOT authenticated. Do not echo either price, seller's "12 min equals 1 hour", or independently unsubstantiated mental/medical effects in a commercial email. Hypnosis Live https://hypnosislive.com/ still contains promotional "$2" language and a **June 30, 2026** cutoff despite this November run: no timed-offer claim permitted. The public https://affiliates.inspire3.com/ page is **not named Final Vestige approval**, channel-specific email authorization or an earning URL. Connected Gmail bounded search found no qualifying individual authorization; consumer promotions do not confer rights.

FTC guidance https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires truthful senders and subjects, clear ad disclosure, a valid publisher physical postal address and functioning opt-out for covered commercial messages. These are still **unverified in a genuine received Jetpack message**; Automattic's address is not FV's address. Editorial Standards https://finalvestige.com/editorial-standards/ prioritize archival sources, transparent uncertainties and commercial independence.

## One-offer subscriber-to-customer sequence: PROPOSED, NOT AUTOMATED

1. Keep existing **one Jetpack list** and 52-page welcome; only native `Email subscription=Subscribed` evidence can justify `confirmed_signup`. Use R172 cross-run deduplication; resumed delivery != new subscriber. Do not collect PII in GitHub.
2. After *separate explicit founder send approval*, editorial Issues 01/02 build confidence with real historical/perception research and live first-party destinations. Original **4 editorial / 2 commercial** mix remains unchanged; no unapproved substitution.
3. Candidate single commercial offer is **Zen12 Premium** via the **Mind Studio-owned, independently vetted /mind/zen12-guide/** only when it is LIVE, link/terms/email-permission VERIFIED, and disclosures visibly beside the specific CTA in actual email and guide. Until then Issue 03 stays HOLD_MERCHANT; Hypnosis Live Issue 05 independently HOLD_MERCHANT. No direct earning link; no secondary platform or list.
4. Email attribution convention (PROPOSED only): `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_03`, only after governance/first-party analytics integration approved. **No per-person query tokens**. Confirmed lead and actual paid purchase must be separate events.
5. Revenue: verified paid order or independently settled affiliate conversion minus refunds/fees, per 1,000 qualified human sessions in 7/30-day cohorts; preserve negative net. No attribution/sales data currently => **NOT COMPUTABLE**. Email clicks and PDF downloads are not paid orders.

## Highest priority blocker → change → owner

- Focus gift/consent | remove browser-only confirmation and prove native email status in real guest flow | Claude/Site QA | **DRAFT not live**.
- Dispatch eligible list/welcome | private read-only email status tally and authorized existing received-welcome inspection | Dispatch | **unknown**.
- Zen12 purchase | named affiliate approval + permitted email promotion + exact authenticated earning link + published vetted guide | Mind Studio | **HOLD**.
- Commercial email | adjacent disclosure, FV postal address, rendered unsubscribe, real Jetpack preview/received MIME | Dispatch/Founder | **partially tested only**.
- Net money | partner paid order/fee/refund reconciliation with qualified cohorts | Commerce/Praxxis | **not computable**.

**Release: ALL SIX HOLD_UNSENT; #03/#05 ADDITIONAL HOLD_MERCHANT.** No sends, test emails, scheduling, publication, WordPress writes, subscriber changes, tracking scripts, payment actions, social posting, affiliate activation or spending.
