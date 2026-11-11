# Dispatch R274 — first-party category eligibility and conversion safety audit
**Date:** 2026-11-10 Pacific / 2026-11-11 UTC. **Status:** REVIEW-ONLY; all original six emails remain HOLD_UNSENT, issues 03/05 HOLD_MERCHANT. No email, test message, list mutation, WordPress update, affiliate activation, social post, spend, or analytics deployment.

## Material issue found in independent Praxxis review
The previous R271 consent lifecycle specimen counted the latest `subscribed` person as eligible whenever status was subscribed. Official WordPress subscriber guidance additionally allows a subscriber to be in that state while opted out of a given *newsletter category*. A future category-enabled Dispatch might therefore overstate recipients if it counted all subscribed users. **Live Final Vestige newsletter categories are currently DISABLED** (categories_enabled=false; categories empty): this is a forward-compatibility/measurement defect, not proof that FV is presently under- or over-emailing.

R274's executable, strictly synthetic consent decision models first provider-confirmed opt-in, replay, unsubscribe, reactivation, unsubscribed/paused/bounced/suppressed/not_sending, Reader-only status, and the opt-in choice for a specific category. It does NOT authenticate a subscriber or count external inputs. Unverified external input ALWAYS yields null actual numbers. A first provider state of Subscribed can be represented without an email click, because a previously verified WordPress.com address may bypass a new confirmation click; this is not blanket inferred consent. Actual first-party consent must be proven by the provider, not a copied `source:"jetpack"` string.

## Scope, hard limits
- Preserves original four editorial/two commercial issues in #175 and readiness #201; does not promote any NOT_ADOPTED alternative.
- `consent_category_gate.cjs` + `consent_category_gate.test.cjs`: dependency-free executable state boundary and adversarial cases; fixtures are explicitly hypothetical.
- `OBSERVATION_2026-11-11.json`: read-only source-linked status; no subscriber identifiers.
- User-facing HTML/plaintext previews in earlier R269 #1978 remain STATIC, NOT native Jetpack inbox emails.
- Do not replace actual provider subscriber filters with the three diagnostic totals (3/3/2) or WordPress.com follower counts. Distinguish **first signup**, **present category eligibility**, **actually delivered mail**, and **permission to send a commercial issue**.

## Current product and legal decisions
Official Zen12 marketing suggests twelve minutes can deliver benefits of an hour; this is a **seller assertion**, not demonstrated Zen12-specific efficacy. Its free audio is a separate merchant list, not FV Dispatch consent. Official Hypnosis Live Total Focus page displays a **33-minute / 47 MB** MP3 and strong cognitive promises that do not constitute independent proof. A merchant sales page's displayed price/discount is NOT the unverified authorized FV affiliate checkout; pricing has varied across observed routes and dates. Merchant FAQ describes 14-day refund period with **five sessions/year** refund limit. Neither merchant source nor received generic Inspire3 promotional emails proves specific affiliate account approval, rights to market by email, earning URL, licensed creatives, or commissions. There are no verified transactions or a computable net-per-1k cohort.

FTC CAN-SPAM guidance requires truthful headers/subjects, correct commercial framing, valid sender-specific postal address and accessible opt-out when applicable; Jetpack's actual rendered footer and delivery remain UNKNOWN. Do not treat Automattic's subscription-confirmation postal address as FV's address. Real Jetpack Preview Email or test delivery requires separate express founder approval.

## Measured funnel and owner decisions
| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT (NO LIVE WRITE) | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Zen12 → buyer guide → purchase | Merchant-specific acceptance, email rights, earning link and approved live guide missing | Privately authenticate one exact authorized route; keep Issue 03 CTA inactive | HOLD_MERCHANT; neither public merchant copy nor marketing mail proves permission | Mind & Affiliate #171 |
| Focus → first signup | Landing parameter or PDF button cannot prove Jetpack confirmation | Privately verify first provider-confirmed state transition + consent provenance, dedup | UNKNOWN; synthetic R274 tests only | Claude/Focus #129 |
| Dispatch → currently eligible audience | Aggregate follower counts omit category and lifecycle state | Filter provider Email subscription=Subscribed, and if categories enabled filter appropriate category, then bounce/pause/suppress | UNKNOWN; live categories disabled today | Claude/Dispatch #174 |
| Dispatch → received inbox | Publisher postal/footer, one-click-or-valid opt-out, welcome/PDF receipt not observed | Founder-authorized received-mail QA only; inspect raw headers/footer once legitimately available | UNKNOWN / HOLD; no test send | Dispatch/Site QA |
| Grok → Focus → order | No verified privacy-safe asset → first signup → settlement join | Preserve TASK-008 UTMs for genuine asset; count source-tagged lead only after provider proof | UNATTRIBUTED/NOT COMPUTABLE | Grok/Praxxis, Claude, Commerce #820 |
| One sellable, rights-cleared FV product → paid sale | No independent matching paid order/fee/refund evidence in Dispatch scope | Commerce owner verify settlement first; prefer legitimate direct product where evidence exists over premature affiliate activation | NOT VERIFIED | Commerce / #820 |

**Metric contract:** `utm_source` actual social platform; `utm_medium=organic_social`; `utm_campaign=<topic>_pilot_2026_11`; `utm_content=<immutable Grok asset_id>`. Dispatch issue attribution later only as approved `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_2026_pilot&utm_content=issueNN`. No tracking pixels or duplicate scripts. `confirmed_signup` only from authenticated Jetpack state; clicks, URL parameters, Reader-only followers and Zen12 signups cannot enter the numerator. Paid conversions require independently authenticated settled order/commission less refunds and fees for 7/30-day cohorts. With no such records, **net revenue per 1,000 qualified human sessions is NOT COMPUTABLE**.

### Prioritized deliverables requiring outside source evidence
1. Mind owner: one verified account-specific email-approved affiliate link, allowed landing/creative, exact seller checkout/refund terms, released pre-sell guide; until then 03/05 HOLD.
2. Claude/Focus: private, aggregate provider current eligibility including correct category semantics; actual receiver-owned welcome/PDF proof without contacting anyone.
3. Dispatch and founder: publisher postal address and authorized received-email preview with genuine rendered unsubscribe. No addresses/recipients in GitHub.
4. Commerce: authenticated completed purchase/payout/refund/fee records and qualified human acquisition sessions before monetization KPIs.

Sources: WordPress https://wordpress.com/support/subscribers/ and https://wordpress.com/support/newsletter/subscribe-to-a-newsletter/ ; FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; source merchant https://zen12.com/ , https://hypnosislive.com/mental-skills/total-focus , https://hypnosislive.com/faq ; original issue https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; source PR #175 and companion #171.
