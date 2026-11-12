# R329 — One offer, one measurable purchase, and the launch gate
**Research-only / draft pull request / November 12, 2026**

## Decision, before another landing page
The main affiliate vertical remains **Zen12** because product format is independently verifiable against official seller pages and it fits the existing twelve-minute Focus Fieldbook. This is an editorial fit hypothesis, **not** evidence of publisher approval, efficacy, real demand or a paid sale. A truly purchasable, licensed FV-owned Mind product has **not** been established because private Payhip inventory is not accessible here; absence of public evidence is not absence of inventory. The pilot consequently stays under **commercial HOLD** instead of pretending a product is available.

The final pre-sell audience is a search/social reader who wants a time-bounded meditation audio and needs to decide whether a 12-minute guided format is worth paying for. The **expected user action before authorization is free research/Fieldbook**, not a merchant click. Only after written affiliate acceptance, exact issued link and channel rights are validated may the founder evaluate activating a link.

## Topic-to-offer mapping — social source of truth is Praxxis/Grok TASK-008
| Proposed viewer hook | Genuine source article | Free/capture bridge | Optional fit | Asset ID |
|---|---|---|---|---|
| The invisible gorilla is missed while looking | Published archive / canonical inattentional-blindness investigation after slug verification | Existing https://finalvestige.com/focus/ | Zen12 buyer guide only if audience explicitly asks about structured meditation | UNVERIFIED — do not invent |
| Two rapid targets, one disappears | R327 attentional-blink draft, not public | Existing Focus Fieldbook and Dispatch | Zen12 guide, no 3-month-meditation-to-Zen12 extrapolation | UNVERIFIED |
| Can hypnosis make learning harder? | R329 sourced lecture-encoding investigation (this PR; unpublished) | Existing Focus Fieldbook / Puységur archive | Compare Zen12 format vs separate Total Focus product; no efficacy inference | UNVERIFIED |

No new social scripts or posts. Grok owns content and distribution; Praxxis verifies real asset_id, post, topic, link permissions, media ID and allowed mobile path. No separate newsletter issue drafts.

## Canonical architecture
Archive/indexed investigations should be one source canonical page per scientific topic; R317 covers suggestion/Stroop and R319/R328 cover overlapping ideomotor behavior. R329 covers *lecture encoding versus other task outcomes*, explicitly different from R317. Main /mind/ hub remains PR #172; the R329 review-only HTML must not be converted into a competing live CMS page. No homepage PR #49 or Issue #150 changes.

Suggested internal link structure after editor approval: real published archive -> the canonical Mind article -> an independent Tools Under Review page (not an endorsement) -> existing /focus/ -> optional seller link only under authorization. Readers may reach any guide without signing up. Place near-link FTC disclosure every time the earning URL is shown; use no dark patterns. Preserve existing WordPress navigation and Jetpack/Dispatch subscriber flow.

## A/B protocol, non-binding
* **A:** full evidence-first Zen12 buyer guide, text only.
* **B:** literally the same substantive guide plus an **optional** 42s original film module. This sprint includes the poster, timed transcript and VTT; **no encoded playable film**. Neither variant currently exposes a merchant anchor, an active purchase button, tracking script, email form or autoplay.
* Random allocation must be designed by Claude using existing first-party facilities and no additional analytics tag; user-facing no-JS page remains readable. B film must be fully optional, user initiated, captioned, accessible on phone and encoded with a low-cost poster/preload=none once produced. No claim that video increases conversions.
* If the source guide and encoded film reach staging, first measure mobile content parity, LCP/CLS/INP, keyboard access, contrast, caption synchronization, reduced-motion, no-JS, CSP, and no PII leakage at 360/390/768/1440/1920. Then after authorized seller and founder release, judge A/B on **net realized revenue per 1,000 qualified-human sessions**, not clicks or minutes watched. Pre-register 7-day and 30-day cohort snapshots, refund/fees adjustments, valid consent and minimum-volume constraints. **Do not declare a winner from tiny samples.**

## Measurement contract
Required first-party campaign keys: `utm_source` = actual permitted creator platform, `utm_medium=organic_social`, `utm_campaign=mind_hypnosis_learning_pilot_2026_11`, `utm_content=verified_actual_asset_id`. Accept only an actual published asset id verified with Grok/Praxxis; otherwise use unknown rather than an invented ID. Respect existing consent settings and retention. Do not append email, phone, IP, name, raw affiliate click identifiers or freeform query strings to event payloads.

Stages, never conflated:
1. `campaign_landing`: qualified-human landing session with honest source, privacy-safe session dedupe.
2. `article_to_resource_click`: user chose existing Focus/Dispatch destination.
3. `confirmed_signup`: only provider-confirmed Jetpack opt-in, not form view/submit.
4. `affiliate_click`: only after active authorized link and lawful measurement; an outbound click is **not** a purchase.
5. `merchant_confirmed_purchase`: only from authorized partner report or independently reconciled seller ledger.
6. `refund_or_chargeback`, processing fees and adjustments; realized net revenue is actual received sum net of attributable expenses/refunds.

Primary KPI = (verified realized net revenue / qualified-human sessions) × 1,000. With missing denominator or settled numerator, status is **NOT COMPUTABLE**, not zero and not 'positive conversion.' Distinguish confirmed buyers from leads, purchases from refunds, and A/B variants from changes in product/traffic quality.

## Security, accessibility, disclosures
Static review HTML has no forms, scripts, iframes, active merchant link, tracking pixels or remote third-party asset embeds. All external research and existing FV URLs are ordinary links; the commerce CTA is disabled. Variant B uses local SVG image in an explicitly optional `details` disclosure with a visible text transcript and caption file. No autoplay. CSS has visible focus states and reduced-motion rule; semantic landmarks, responsive columns and descriptive alt text are source present. **Actual browser WCAG audit not yet done.**

FTC: clear prospective “may earn a commission” disclosure lives immediately before the disabled commercial control. If a link becomes active, preserve obvious text next to it. Do not rely on the generic policy page. Objective benefit claims require adequate evidence for the specific product. No personal testimonials, medical promises, wealth assurances, countdown urgency or permanent price claim.

## Release table
| OFFER → STEP | BLOCKER | CHANGE / CONTROL | Evidence status | Owner |
|---|---|---|---|---|
| Zen12 → paid commission | Publisher terms, account acceptance, issued earning URL unknown | Verify dashboard and written allowed channels; no public link now | HOLD | Founder/Commerce |
| FV digital Mind → paid sale | SKU, rights, fulfillment and returns unknown | Secure actual Payhip inventory audit | HOLD | Commerce |
| Grok asset → sourced article | Three exact matching published IDs unknown | Read TASK-008 and verify published mobile destinations | HOLD | Praxxis/Grok |
| Existing Fieldbook → confirmed lead | Subscriber source/consent not reconciled | Existing Jetpack provider report only | HOLD | Claude/Dispatch |
| Variant A/B → paid sale | Encoded B film and independent mobile QA absent | Same-copy comparison, real staged player and no-JS tests | SOURCE ONLY | Site QA/Claude |
| Merchant sale → revenue KPI | Settlements/fees/refunds/qualified sessions missing | Reconcile vendor ledger and first-party cohort | NOT COMPUTABLE | Commerce/Claude |

## Release checklist
- [ ] Founder-specific Inspire3 approval / terms, allowed channels, approved assets and issued tracking URL verified (no credentials in issues).
- [ ] Appropriate paid FV-owned alternative checked in the actual Payhip inventory.
- [ ] Editorial source owner approves canonical topic and distinguishes R317/R329.
- [ ] Staging browser/a11y/security/source QA signs off, independent of authors.
- [ ] Optional video encoded and tested, or B explicitly marked not ready.
- [ ] Founder approves commercial and production release separately.
- [ ] Only Claude engineers permitted production analytics, if justified; no duplicate scripts.
- [ ] All changes limited to isolated Mind-owned files; never merge/deploy by automation.

**No live WordPress CMS, Navigation, Jetpack, Dispatch, social, commerce, tracking or spend changes are authorized by this document.**