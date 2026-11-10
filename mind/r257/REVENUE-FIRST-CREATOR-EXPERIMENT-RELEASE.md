# R257 · Revenue-first Mind buyer decision: offer → evidence → release

**Date:** 2026-11-09 PT. **Status:** BUILD PREVIEW / COMMERCIAL HARD HOLD. **Workstream:** #171 only. **Sources of business truth:** Issue #820 and charter #818. **Base:** R256 exact SHA `ebe7ab5eb6d3a5f097845686322c56e48c7b47d0`. Source-only stacked branch. No WordPress writes, no merge, no release, no link, no paid platform, no social/email changes.

## What changed materially, instead of generating another duplicate landing page

R253–R256 produced several near-identical Zen12 storyboard variants. Their scientific arguments converged while the actual commercial blocker remained unchanged. R257 therefore changes the unit of work: **one defensible purchasing question** (free timer versus structure), **one full evidence-reviewed buyer field guide**, **a genuinely locally rendered 42-second original educational film** with a source-controlled renderer and WebVTT track, plus **one prospective controlled A/B** using identical offer copy.

A and B are held source previews; the MP4 is a local nonpublic artifact, generated from the committed reproducible Python renderer, **not a binary in the PR and not a WordPress media asset**. B currently offers a fully readable optional poster/transcript `<details>` segment; adding a real `<video controls preload="none">` would require explicit media QA and release approval. This explicitly avoids broken production video URLs, remote players, autoplay, and phantom "rendered" claims. A is a complete page without film. B adds the film only; identical buyer information and disabled controls.

### Actual source and output evidence

- Exact seller standard: https://zen12.com/hnp (Premium 12 levels, 48 recordings, four sound styles, seller-displayed $87.99 on 9 Nov 2026, seller-advertised one-year refund).
- Distinct seller promotion: https://zen12.com/secret/ (seller-displayed $37 coupon offer; different context and countdown). Not proof of parity, coupon eligibility, final checkout or real expiration.
- Parent Inspire3: https://inspire3.com/ ; public signup portal https://affiliates.inspire3.com/ ; **neither authenticates FV-specific acceptance**.
- Independent EEG: https://doi.org/10.1371/journal.pone.0286023 (14 studies: 5 supportive, 8 contradictory, 1 mixed; mechanisms, not commercial outcomes).
- Meditation evidence/safety: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety and https://pubmed.ncbi.nlm.nih.gov/32820538/ (not product-specific).
- FTC endorsement/claims: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
- First-party existing free funnel: https://finalvestige.com/focus/ ; live Journal https://finalvestige.com/blog/ shows 66 results on Nov 9 rather than #171's historical 61.
- Issue #171 Puységur deep-resource URL https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ could **not** be opened; do not put it in navigation before Site QA confirms.
- Original video generated locally: **42.000s, 540×960, 12 fps, H.264, no audio, ~254 KiB**; original seven distinct illustrated cards, no merchant imagery, two-lines-wrapped text, reviewed seven-panel contact sheet. Audio-free film must have visible readable text and a separately available captions/transcript. Server-side `ffprobe` verifies duration; future real-browser playback/a11y still untested.

## Which offer can make actual money?

**Option 1 (prospective affiliate):** Zen12 Premium meets high intent for people curious about short guided audio, but commercial eligibility is **not proven**. Public program ads are not an approval letter. Do not ask Dispatch to send or Grok to promote. All **16/16 gates HARD HOLD** in `CLAIM-PROOF-OFFER-REVENUE-GATES.json`.

**Option 2 (nearer-term owned alternative):** Existing FV Payhip Products 001–015 are reportedly live in older project context. However, we have not authenticated a specific current **Mind/Perception** paid SKU's price, rights, checkout, refund policy, fulfillment and orders. An owned SKU is **not automatically sellable or appropriate** simply because the overall store exists. Commerce/Founder must privately verify one eligible SKU; if none, continue with **only** the existing free Focus Fieldbook. We do not invent a $19 product or new sale page.

**Current measurable safe CTA:** `/focus/` link from an evidence-backed Mind investigation and the unpublished buyer guide. It is a free lead path and must never be reported as a sale. The Zen12 control remains a **disabled button**, not an `href`, with adjacent future-conditional disclosure. Normal first-party attribution (if existing approved Claude stack supports it) can record a distinct `focus_cta_click`; provider confirmation must validate the subscriber. No new form or event script.

### Offer → step → blocker → change/experiment → evidence → owner

| Priority | Offer / funnel step | Current blocker | Proposed experiment or repair | Pass/fail proof required | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → legitimate outbound offer | Named FV acceptance, issued URL, channel rights, checkout/returns and promo parity missing | Authenticate publisher dashboard/terms; screenshot or redacted export with date and issued link; independently verify exact offer | Valid documented named authorization + permitted web/social/email channels + verified link → PASS; public signup/consumer email alone → FAIL | Founder + Mind |
| P0 | Existing FV SKU → paid order | Eligible rights-cleared Mind SKU not authenticated | Inspect original Payhip inventory under Commerce lane; choose one already sellable exact SKU before building a new paid pitch | Authenticated SKU ID + rights + buyer-accessible checkout, real live current price and refund process → PASS; otherwise HOLD | Commerce + Founder |
| P1 | Social asset → article | Actual published Grok IDs/hooks/destinations unreconciled | Praxxis inspect existing TASK-008 and dated handoff; **three existing posts only**, no new Grok assignment | Original platform URL, immutable asset_id, publish date, matched signed-out mobile landing and permission for each → PASS | Praxxis + Grok |
| P1 | Article → free Focus lead | Source-campaign session matching and provider confirmation uncertain | Request read-only existing first-party analytics/Jetpack crosswalk, no scripts | Session_id pseudonymous in consented first-party system where lawful; `focus_cta_click` distinct from provider-confirmed subscription | Claude + Dispatch |
| P1 | Zen12 A/B → paid customer | No legal offer, video not hosted, and no release approval | Keep identical buyer copy; A text only, B plus user-initiated short film; test after required gates | Accessible B playable; random assignment and holdout; resolved checkout conversion, refund-adjusted revenue; pending → NOT LIVE | Mind + Site QA + Claude |
| P2 | Paid order → net realized revenue | No settled merchant/commission receipts and bot-filtered denominator | Read-only 7/30-day receipts reconciliation | Provider order IDs + cleared commission or paid order + refunds, fees, costs and de-duped qualified sessions → VERIFIED, otherwise NULL | Commerce + Analytics |

## Three research/creator joins (do not create or edit Grok content)

| Source-grounded topic / suggested factual hook for matching *existing* assets | Verified landing | Next reader step | Optional commercial topic fit | Published media receipt |
|---|---|---|---|---|
| **Change blindness** — "You can miss a person swap, even facing them" | https://finalvestige.com/2026/11/02/change-blindness/ | Observe flicker test → optional https://finalvestige.com/focus/ | Zen12 only after a separate honest meditation-format bridge; **not** a cure for change blindness | `asset_id`: UNKNOWN; Praxxis must find exact Grok video ID/URL/date |
| **Invisible gorilla / inattentional blindness** — "The gorilla is not invisible; your task matters" | Live canonical article URL NOT verified; do **not** invent one. Use published Journal index temporarily. | Science source → optional Focus | No immediate merchant recommendation; low buying intent | `asset_id`: UNKNOWN |
| **Thatcher illusion** — "Why upside-down faces conceal distortions" | Canonical public URL NOT verified; current Journal index only. | Source explanation → optional Focus | No direct commercial upsell; if any, generic focus formats require honest bridge | `asset_id`: UNKNOWN |

The user-appointed Grok creator lane handles production and posting, Praxxis handles existing Drive TASK-008 research/QA. Exact hooks and asset IDs require Grok/Praxxis verification **before** UTM naming or matching event counts. The user-provided Drive documents are existing handoff locations, not permission to change their task queue: TASK-008 https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit ; handoff https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit .

## High-intent landing contract and controlled experimental hypothesis

**Intent:** visitor coming from a clearly relevant video/search question such as "Is Zen12 Premium worth it?" (versus change-blindness casual science visitors). Preserve content-to-destination relevance. **Promise:** product content, evidence limits, seller offer discrepancy and a no-cost alternative. **Decision:** voluntary visit to an approved verified merchant **only after future gates**. **Hold copy:** "Explore verified Zen12 offer — unavailable"; this button is not clickable, so cannot be counted as a referral.

**A (control):** independent text-only buying guide, no media at all. **B (treatment):** exactly the same buying guide plus an optional original 42-second silent illustrated film with native readable transcript and WebVTT, never autoplay. This tests whether a short film **increases independently confirmed net paid conversion** for relevant visitors; no uplift is assumed. If the film has no material incremental business effect or harms loading/reading, keep A. Neither version adds a second email CTA/form, expensive video SaaS or remote tracker.

**Allocation proposal, not activated:** Claude's existing compliant first-party mechanism should randomly assign 1:1 *once per consented qualified visitor/experiment* without a new cookie or fingerprint; if persistent assignment cannot be done without violating privacy, use server-side campaign-rotated blocks with caveats on comparability or do not call the results randomized. Preserve all browsers' no-JS access to complete buyer text and a functional single-CTA arrangement only after approval. Exclude bots/nonhumans using transparent existing filters; avoid personal attributes, demographic profiling and unconsented tracking.

**Primary outcome:** independently confirmed paid order/cleared affiliate commission adjusted for refunds and fees per qualified-human session. **Secondary:** confirmed leads, lead-to-customer, approved link clicks, accessible video play, bounce/scroll diagnostics. Source events alone do not prove a sale.

**Cohorts:** report 7-day and 30-day **matured** windows by `utm_campaign`, `asset_id`, `landing_page`, `variant`, promotion exact-SKU and calendar/time. Currency conversions and fee basis need documentation. Use only lawful, privacy-safe and existing measurement. For a tiny sample give raw count and strong uncertainty warning; do not call random noise statistically significant. Prespecify minimum data quality, adequate orders and safe performance before choosing B. No manufactured A/B uplift.

### Measurement contract (design-only; no tracking code installed)

`session_attribution`: `{event_id, event_time, source_platform, asset_id, utm_campaign, landing_path, consent_scope, verified_human_flag, variant}`. No full IP, email, name, fingerprint or cross-site ID in analytics payload. Implement only through Claude's already-approved first-party instrumentation with privacy and consent controls; no additional script.

`cta_interaction`: `{event_id, related_session, placement_id, offer_sku, action: focus_cta_click | affiliate_click}`. No events for disabled merchant control; clicked destination is only recorded after verified partner permission.

`provider_lead_confirmed`: `{provider_event_reference, provider_confirmation_date, campaign_key_if_provider_supports, status: confirmed}`. An internal inferred signup is NOT confirmed.

`merchant_settlement`: `{merchant_order_reference, offer_sku, paid_date, settlement_date, gross_amount, currency, platform_fees, refunded_amount, chargebacks, net_commission_or_owned_receipts, attribution_provenance, report_date}`. Store order-level restricted data in Commerce's protected records; aggregate only for analytics. A manual bank deposit/Payhip/affiliate dashboard reconciliation may be necessary. Do not assume anonymous web client events can causally match purchases if merchant reporting lacks crosswalk. A refund may arrive after a 7-day cohort closes; apply 30-day maturation and corrections.

**Net revenue / 1,000 qualified human sessions =** `1000 × audited realized net revenue / verified qualified human sessions`. *Undefined (NULL)* if denominator or paid receipts missing—not zero. Avoid subtracting fees twice from provider already net payouts. Record gross, refunds, fee and direct attribution basis separately. When attribution is missing, report only site-level net business revenue, never per-asset attributed conversion.

## Accessibility, privacy, film and deployment acceptance

**Built locally:** original SVG hub and B poster, complete A/B text, no-JS details, attached disclosure, renderer Python+FFmpeg, exactly 7 VTT cues spanning 42 seconds. A source link citation is not an approved product CTA; held HTML contains **no active Zen12 seller `href`** even in sources, only plain-text source addresses. Full research article may link sources as citations but never earning redirects.

**Test now:** native Node source acceptance for claims/gates, no scripts/forms/merchant anchors, identical offer copy outside film, caption clock validity, caption text, SVG title/desc, role and accessible disabled button; native FFmpeg verifies video duration/portrait encoding. **Still required before any launch:** human copy review, responsive browser screenshots 360/390/768/1440/1920, keyboard order, WCAG 2.2 AA audits, reduced-motion/no-JS check, WordPress sanitizer preview, full media caption playback and transcript review, mobile LCP/CWV/no third-party cost regression, merchant checkout, legal source terms, signed-out links, production release approval.

**Branch policy:** Source files confined to `mind/r257/`. Preserve homepage PR #49, issue #150, canonical Mind hub PR #172, and Dispatch Issue #174. Homepage art lead may adopt a small unrelated portal idea only in their own branch after review. No PR merge, deployment, WP/CMS/nav/settings, Jetpack/email, Grok posting/queue edits, or spending.

## Release decision and blockers

**COMMERCIAL HARD HOLD.** Independently verified Zen12 acceptance, authorized link, promotional permissions including email, checkout/refund terms and settled affiliate commission remain unavailable. An eligible rights-cleared FV-owned paid Mind SKU is also unauthenticated; therefore no paid pilot can honestly be described as live. The **existing free fieldbook is the only known appropriate Mind next action**. Scientific findings and valuable free research stand regardless of merchant approval. A source-controlled draft PR and a locally playable film are development outputs, **not evidence of verified revenue**.

## Issue handoff

Record exact final branch SHA, PR link, 20 negative-test results, film `ffprobe` receipt, source links, untested browser/checkout outcomes, and release HOLD in #171. Mirror revenue blockers in #820. Post scoped read-only reviewer requests to Site QA #126, homepage art #150 and Dispatch #174. Coordinate matching creator IDs only in existing Praxxis/Grok TASK-008 and dated handoff (no new task queue).
