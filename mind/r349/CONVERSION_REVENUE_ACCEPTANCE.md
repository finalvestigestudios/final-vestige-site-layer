# R349 — Revenue acceptance and restricted conversion pilot
**Date:** 2026-11-13 PT. **Lane:** Mind & Perception independent presell and source review only. All release controls remain HOLD.

## The single high-intent offer decision
Proposed offer hypothesis: Zen12 **Premium** for a visitor seeking a structured, guided twelve-minute audio routine, not a clinical or guaranteed focus treatment. Official sales page https://zen12.com/ describes all 12 levels, 48 MP3s and a displayed $87.99 as of 2026-11-13. This is a seller-page display, NOT a verified checkout total, final paid invoice or evidence of effectiveness. One-year refund is advertised by seller and must be verified in actual terms. No permitted affiliate URL or publisher acceptance is established.

**Fallback:** An FV-owned paid Mind SKU is not yet independently verified as rights-cleared, active in Payhip, deliverable, and refund-policy compliant. The existing free 52-page Fieldbook https://finalvestige.com/focus/ cannot count as a paid product. Commerce must supply authenticated owned SKU, checkout link, total, delivery and refund evidence before switching pilot. Do not improvise a sellable SKU.

## Funnel hypothesis and variant definition
**Audience:** high-intent reader seeking a manageable structured audio routine after a perception/attention story.

**A:** source-based text-only buyer guide, real package breakdown and research limits, free personal exercise, concerns and FTC prospective commission disclosure beside disabled purchase button.
**B:** identical substantive text and same disabled CTA, plus an original static poster, optional full 42-second transcript and six-cue VTT. Video is NOT encoded, embedded or hosted. Do not describe B as a tested playable-video treatment.
**Question:** when paid purchase eligibility and media exist, does an optional original short improve **confirmed paid order conversion per qualified human session**, not merely link taps, while preserving accessibility and LCP? No uplift is predicted or guaranteed.

Release only after founder-approved random assignment at the server/edge or documented privacy-respecting split, stable assignment over 7/30-day cohorts, identical traffic allocation by platform and audience, no new duplicate scripts, mobile QA and consent signoff. No performance win at tiny N; report interval uncertainty.

## Actual creator-topic-to-product fit (all media IDs awaiting Grok/Praxxis)
| Topic | Authentic live FV destination | User purpose | Commercial fit | Source of acquisition |
|---|---|---|---|---|
| Change blindness / door swap | https://finalvestige.com/2026/11/02/change-blindness/ | Understand a vivid perceptual failure | First offer is free Focus Fieldbook; optional Zen12 after guide/approval | Grok published asset_id **NULL** pending TASK-008 |
| Franklin's mesmerism / Puységur | https://finalvestige.com/2026/11/02/mesmerism/ and https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Research historical suggestion and testimony | Only a skeptical Hypnosis Live guide if specific offer approved; no medical endorsement | asset_id **NULL** |
| Inattentional blindness / memory-load surprise | No live R349 article URL (unpublished); adjacent live change-blindness article available | See counterintuitive laboratory evidence | Free personal routine; Zen12 Premium only if separately vetted | asset_id **NULL**, do not post draft URL |

Grok retains content production and social posting. Praxxis validates IDs, hooks and post URLs through the existing TASK-008 Drive docs. No direct script copy, social publication or queue changes in Mind lane.

## First-party attribution contract (engineering spec; NOT deployed)
Use existing approved measurement only. Proposed UTM payload: `utm_source=tiktok|youtube|instagram` where actual, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<verified asset_id>`. If channel only permits bio links, document that attribution limit. Never fabricate asset IDs.

Sequence: `qualified_human_session` → `mind_article_view` → `article_to_focus_click` → `provider_confirmed_signup` (only if consent/readback allows) → `offer_guide_view` → `affiliate_outbound` (only after authorized tracking link) → `merchant_confirmed_paid_purchase` / `merchant_confirmed_paid_affiliate_conversion` → recognized settlement - platform fees - payment fees - refunds / chargebacks.

An outbound click is **not** a sale. A click without consent cannot be joined to a subscriber. No persistent raw IP, names, email addresses, fingerprinting, or unsecured query-string personal identifiers. Retain aggregate metrics only under existing privacy policy and approved settings. Do not introduce GA4/Ahrefs/Jetpack duplicate scripts.

**Core KPI**, only where denominator and complete money reconciliation exist: `net_realized_revenue_per_1000=1000*(settled_gross-refunds-fees)/qualified_human_sessions`. If any required component is absent, return NOT COMPUTABLE (not 0). Report separately confirmed customers, paid orders, gross receipts, refunds, fee totals, net and paid conversion. Track 7- and 30-day cohorts by verified acquisition date, label tiny samples.

## Offer → Step → Blocker → Experiment → Evidence → Owner
1. Zen12 Premium → commission → authenticated FV approval/channel terms/unique issued URL missing → partner dashboard audit → FAIL/HOLD, no link → Founder/Commerce.
2. FV-owned Mind SKU → paid checkout → verified owned sale, buyer rights, checkout/delivery/refund missing → private inventory audit → FAIL/HOLD → Commerce.
3. Grok creator topic → qualified landing → actual immutable published IDs missing → three-asset reconciliation via TASK-008 → UNKNOWN, no post modified → Praxxis/Grok.
4. Focus Fieldbook → consented lead → Jetpack confirmation with asset-level attribution not validated → audit existing signup and delivery without test signup → UNKNOWN → Claude/Dispatch.
5. Zen12 A/B → paid conversion → playable film, real browser QA and eligible offer absent → source-controlled staged evidence only → NOT RUN → Site QA/Claude.
6. Settled purchase → net revenue → order/refund/fee/qualified-human data unavailable → real 7/30-day reconciliation when authorized → NOT COMPUTABLE → Commerce/Claude.

## QA/release plan
- Source guard: no new script/form, no live merchant href, button genuinely disabled, near-CTA disclosure, identical core in A/B, no unsupported clinical claims or fictional experience.
- Film: storyboard/transcript/VTT only; encode an original file with no music licensing issues, add controls + captions + poster, preload none, no forced playback only after separate QA and approval.
- Browser: 360,390,768,1440,1920; keyboard/screen reader, high-contrast, reduced-motion, no-JS; verify WordPress sanitizer won't corrupt source after approved CMS stage.
- Performance: ensure static poster not render-blocking; measure real LCP, CLS, mobile transfer; no third-party tracker.
- Governance: preserve PR #49, #172 and Issue #150, Jetpack /focus/ and existing Dispatch welcome; do not edit WordPress live pages, newsletter drafts, partner account, analytics or social queue. Need founder release approval.

## Public source links
Research https://pubmed.ncbi.nlm.nih.gov/21937032/ ; https://doi.org/10.3758/BF03208840 ; https://doi.org/10.1002/wcs.130 .
Offers https://inspire3.com/ ; https://zen12.com/ ; https://zen12.com/gift ; https://hypnosislive.com/mental-skills/total-focus ; https://brainwaveshots.com/focus-shot .
FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
Actual FV https://finalvestige.com/focus/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ .
