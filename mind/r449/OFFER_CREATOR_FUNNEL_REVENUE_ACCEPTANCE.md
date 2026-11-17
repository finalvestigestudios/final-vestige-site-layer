# R449 — Offer → funnel → blocker → acceptance design

**17 November 2026 · Final Vestige Mind lane only · draft/hard hold.** No live WP, newsletter, Grok posts, affiliate promotion, tracker, checkout or merchant authorization created here.

## Decision first: is anything payable?

1. **Zen12**, the intended primary affiliate: publicly sold by Inspire3, but named Final Vestige partner approval, channel rights, specific issued earning URL, referred SKU and settlement rules are **not established**. Affiliate portal marketing material and consumer mail are not proof. HOLD all purchase controls.
2. **Alternative FV-owned product:** the existing [52-page Seven Day Focus Fieldbook](https://finalvestige.com/focus/) is **free**. No actually payable, rights-cleared FV-owned Mind SKU with working checkout, delivery, returns and seller ledger was authenticated. Do not fabricate one to satisfy a landing-page target. Founder/Claude must provide a real SKU and transaction pathway before any owned paid pilot.
3. **Direct reader value today:** the [published change blindness article](https://finalvestige.com/2026/11/02/change-blindness/) and [Puységur archive](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) offer free, evidence-first destinations. The new CT-gorilla article is source-only, not a public destination.

## Three creator/topic → published article → free step → possible offer fits

| Candidate creator hook (not confirmed social asset) | Public article today | Optional free step | Future independently verified offer | Intent / mismatch |
|---|---|---|---|---|
| "Did you miss the person switch?" | [Change Blindness](https://finalvestige.com/2026/11/02/change-blindness/) | [Focus Fieldbook](https://finalvestige.com/focus/) | Zen12 only after approval, if routine-help buyer intent emerges | High curiosity, LOW immediate buying intent |
| "A gorilla was inside the lung scan" | **None until R449 article approved/published** | Existing Focus Fieldbook via another live route only | No automatic jump to checkout; independent Zen12 comparison at later stage | High curiosity, potentially medical confusion; no health-benefit pitch |
| "A magnetic somnambulist's testimony was recorded" | [Puységur Animal Magnetism Files](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) | Existing Focus Fieldbook only when useful | Hypnosis Live Total Focus, ONLY after precise product/approval review | Historic proof ≠ modern hypnotic efficacy |

**Praxxis/Grok gate:** Obtain exact *already published* platform asset_id, original post URL and date, actual hook, license/rights, permitted mobile link, and an actual clicked/tested route. All three media IDs currently **UNVERIFIED**. The above are topics, not proposed posts or task assignments. No editing Grok's TASK-008 queue.

## Single purchasing hypothesis, not endless undirected pages

**Audience:** reader searching for "Zen12 12 minute meditation review" and assessing whether the downloadable formats justify paying for convenient short listening sessions. The promise we can ethically evaluate is *convenience and format choice*, not a medically or neurologically proven shortcut.

**A control:** complete, no-JS high-intent text purchasing guide with free 12-minute baseline and five buying questions.

**B treatment:** identical substantive buying guide + optional original 42-second narrated video with an original SVG poster, WebVTT caption plan and full transcript. In this sprint B is **static storyboard**, not playable. To execute B a rights-cleared original encoded video, accessible controls/no autoplay, browser measurement and founder authorization are still required.

**Hypothesis:** B may increase *informed buyer intent* among qualified, high-intent readers without reducing quality or performance. No assertion of a positive effect or paid lift before valid test. Do **not** count watching or affiliate_click as paid order.

**Pre-registered primary outcome after commercial activation:** independently verified **refund-adjusted net revenue per 1,000 qualified-human landing sessions**, by assigned A/B version. Secondary: paid buyers / qualified visitors; confirmed original Jetpack leads / eligible visitors; independently matched merchant commission; revenue from purchased offer; any adverse disclosure misunderstanding. Diagnostic only: link click, scroll, video play, watch time, impressions.

**Assignment (future only):** immutable server-side first-party variation at landing based on a randomly generated consent-safe experiment token, *no* cookies or fingerprints unless approved under privacy policy. Deterministic assignment if user returns only with consent; avoid double-counting. Baseline split 50/50; report variant exposure and conversion windows in 7/30-day cohorts. No new analytics script before Claude's approval; leverage existing instrumentation.

**Performance safety:** Film optional with poster-first; never preload a heavyweight media file or autoplay. The no-JS page must be fully readable and permit the identical buying flow once authorized. Disable B if WCAG 2.2 AA/keyboard, captions, mobile Core Web Vitals, consent or merchant gate fails. Draft only today.

## First-party attribution, not pseudo-revenue

Proposed minimal event contract for Claude/Issue #820, not deployed:

```json
{
  "event": "campaign_landing | article_to_focus_click | confirmed_signup | affiliate_click | merchant_paid_sale | merchant_refund",
  "asset_id": "verified immutable Grok video identifier ONLY",
  "utm_source": "youtube | tiktok | ... real platform",
  "utm_medium": "organic_social",
  "utm_campaign": "mind_perception_pilot_2026_11",
  "utm_content": "same verified asset_id",
  "landing_route": "first-party canonical page",
  "variant": "A | B, when test actually runs",
  "event_date": "YYYY-MM-DD",
  "consent_basis": "applicable consent status",
  "merchant_reference": "restricted finance ledger only, never exposed client-side"
}
```

Use aggregate daily/weekly records, no device fingerprint, no medical data, no email address in URLs, no duplicate vendor pixels, no fabricated event stream. Require provider-confirmed Jetpack subscription for lead status; confirm no duplicate list or welcome replacement. `affiliate_click` is *outbound* only, and `merchant_paid_sale` must originate from independent merchant commission ledger, not inferred from click. Include settlement, refunds and fees; separate gross, pending, and realized. When denominator is missing, report **NOT COMPUTABLE**, never $0 or assumed sales. Tiny sample warning for <100 qualified sessions or <10 paid outcomes in any variant; no significance promises.

## Priority acceptance ledger

| Offer → step | P0 blocker | Change / experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Zen12 → paid commission | No named affiliate acceptance/issued URL | Obtain portal-issued authorization and contract | FAIL / no authenticated FV approval | Founder/Commerce |
| FV owned Mind → paid order | No authenticated payable SKU | Inspect paid product catalog & live checkout | FAIL / free Fieldbook is not paid | Founder/Claude |
| Creator → published page | Three real media IDs not established | Verify Grok source assets and mobile links | FAIL / candidates only | Praxxis/Grok |
| Article → optional confirmed lead | Jetpack provider confirmation not independently tested | Read-only audit of existing flow | NOT TESTED / no new subscriber | Claude/Dispatch |
| Text A vs film B → authorized purchase | No encoded original film, browser and rights signoff | Encode; accessibility and page speed; controlled trial | NOT TESTED / storyboard only | Mind/Site QA |
| Order → net settlement | No verified commission, qualified sessions or refund ledger | Reconcile merchant order and commissions | FAIL / KPI NOT COMPUTABLE | Commerce/Claude |

## Affiliate disclosure, isolated from investigation conclusions

Near the (currently disabled) purchasing control: "If Final Vestige is approved and you later purchase through an authorized link on this page, Final Vestige may earn a commission at no additional cost to you. No earning link is active now." Before any commercial activation, ensure final, unambiguous relationship language at the actual link; test on mobile and with assistive technology, independent of the site-wide disclosure.

**Source documents:** [Drew et al. 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/); [Hults et al. 2024](https://doi.org/10.1186/s41235-024-00537-x); [Inspire3](https://inspire3.com/), [Zen12 about](https://zen12.com/about), [Zen12 main checkout catalog](https://zen12.com/), [Zen12 promotion](https://zen12.com/secret/), [partner portal](https://affiliates.inspire3.com/); [FTC endorsements](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking); [FTC health claims](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance).

**Protected:** homepage #49, Mind hub #172, homepage art #150, Dispatch #174, Issue #820 Claude metrics, existing Jetpack welcome; no write authority requested or exercised.
