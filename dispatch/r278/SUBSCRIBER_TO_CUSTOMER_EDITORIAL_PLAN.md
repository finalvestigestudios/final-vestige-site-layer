# R278 — Measurable reader-to-customer journey (draft / no sends)
**Scope:** The Dispatch's existing six unsent issues; this is a conversion-focused placement and learning plan, not seven new emails and not an instruction to activate an email automation. The core brand remains historical evidence and sourced public records.

## Offer-market fit: one plausible buyer, one prospective vetted offer
**Who:** a visitor who watched a published Grok-controlled Change Blindness / Attention video, followed a genuinely associated source CTA to an independent Final Vestige article, opted into the existing Focus Fieldbook to explore a free attention routine, and later proactively read a buying guide to evaluate short meditation recordings. This is a **hypothesis**, not a confirmed observed customer segment. **Prospective commercial offer:** Zen12 (issue 03 only) if and only if Mind & Affiliate Studio provides written email-channel approval and one live publisher-authorized earning link. A more convenient routine may appeal; efficacy of this specific seller product is not established. Reader access to any buyer guide must **not** require subscribing or buying.

## Six actual-edition placement map
| Issue | Purpose | Existing subject (do not change) | ONE substantive next step | Release state |
| --- | --- | --- | --- | --- |
| 01 editorial | Reader's mental model: eyewitness evidence is not a recording | The mind is not a camera | Puységur archival research; repeated CTA conflict with #02 flagged for optional future copy choice | HOLD |
| 02 editorial | Historical evidence credibility and observation | Before hypnosis had a name | Puységur archive, first-hand vs inference distinction | HOLD |
| 03 commercial | Buyer readiness after a genuine no-cost twelve-minute practice | The twelve-minute meditation question | **Unavailable** vetted Final Vestige Zen12 guide; no direct affiliate URL | HOLD_MERCHANT |
| 04 editorial | Preserve historical investigative anchor, technical causal inference | Fourteen seconds. A much longer explanation. | Published Apollo 1 investigation | HOLD |
| 05 commercial | Evidence-based format/effect/refund checklist | Before you press play on a hypnosis audio | **Unavailable** vetted Final Vestige Hypnosis Live guide; no direct affiliate URL | HOLD_MERCHANT |
| 06 editorial | Closing evidence log and retention without pressure | What did seven days of attention reveal? | Current /focus/ is safe but repeats the welcome gift; optional new archival method destination requires founder adoption | HOLD |

Subjects and preheaders remain **source-faithful** to PR #175. Separate alternatives proposed on later draft PRs are **NOT ADOPTED**. The important work is completing the proof path, not increasing draft count.

## Ethical PAS/AIDA/story-based bridge WITHOUT overpromising
**Problem:** "You made it through a week of short practice. What changed—and how would you know?" The legitimate reader problem is comparing convenience, consistency, personal preference and marketing claims.
**Context/Agitation (without fear):** A persuasive sales page can blur measurable format (12 levels, 48 files) with effectiveness assertions ("an hour in 12 minutes"). The reader should never be made to feel deficient for choosing no product.
**Insight:** An evidence log can track **behaviors**, e.g. days attempted, minutes practiced, interruptions, fit with schedule and subjective comfort; it cannot diagnose a disorder or demonstrate product efficacy. With a tiny audience, these are personal observations, not causally controlled results.
**Action:** Guide readers through objective questions: Are audio formats optional? How is the product delivered? What is the exact current checkout route and refund condition? What independent evidence exists **for this specific product**, rather than for meditation generally? Can a free routine meet the need?
**Single qualifying CTA, ONLY if partner authorization exists:** "Read our evidence-led Zen12 buyer's guide" → the approved published Final Vestige guide → merchant link with neighboring disclosure: "If you purchase through this link, Final Vestige may earn a commission at no additional cost to you." Until approval: **no clickable buyer CTA**, no merchant redirection, HOLD.
**No coercion:** No scarcity timers, countdowns, "brain reprogramming is proven", fabricated trial, medical claims, guaranteed progress or reader-shaming.

## Non-sending stage progression hypothesis
1. **Entry source:** A real published Grok asset's immutable `asset_id` from TASK-008. The asset's topic, platform, publish date, CTA surface and declared destination must be recorded. This studio has not posted or changed Grok's content.
2. **Trust stage:** An on-site Final Vestige evidence-led article; mark qualified human sessions only through a documented first-party method, not arbitrary bot-reported visits. Existing UTMs must be preserved; no duplicate analytics snippets.
3. **Consent stage:** Someone may view /focus/, click Subscribe, or access a public PDF without subscribing. These are distinct events. `confirmed_signup` means the **first authenticated provider transition** to a currently valid subscribed state, deduplicated by an internal, nonpublished provider key and accompanied by lawful consent provenance. Existing WP.com accounts may not receive a fresh confirmation click. Unsubscribed/bounced/paused/Reader-only states never count as eligible newsletter recipients. Do not email prospects who did not consent.
4. **Value stage:** The existing configured 52-page Fieldbook welcome should be checked for actual delivery and PDF usability with properly authorized evidence; do not treat the configured URL as an observed received message.
5. **Nurture stage:** Each original editorial email establishes trust through documented source, appropriate uncertainty and one relevant site destination. Do not manually contact list; no additional unapproved sequence.
6. **Buyer stage:** A reader who voluntarily visits the **approved** independent comparison guide may choose to purchase from the actual authorized merchant route, with a nearby disclosure. No user must join the merchant's *separate* newsletter to count as a Dispatch subscriber.
7. **Revenue stage:** Merchant-reported **settled** order/commission after refunds, chargebacks and fees is reconciled. Only then may the business report attributed paid conversion. If attribution is incomplete, report "unattributed" rather than manufacture a cause.

## Attribution and metric contract
Use a single existing first-party observation chain, not a new analytics service:
- Social landing: `utm_source=<actual_platform>`, `utm_medium=organic_social`, `utm_campaign=<cluster>_pilot_2026_11`, `utm_content=<immutable_Grok_asset_id>`.
- Unique visit/session IDs and timestamp (UTC), privacy-minimized, exclude bots and QA traffic with disclosed criteria; no display of IPs, subscriber emails or other personal tokens.
- Important: don't treat an arbitrary `?subscribe=` URL parameter or visible Fieldbook download as authenticated opt-in. Check provider state separately.
- Distinct non-conversion actions: `landing_view`, `cta_click`, `signup_attempt`, `fieldbook_view`, `email_guide_click`, `affiliate_outbound_click` **only where genuinely observable**. Confirmed lead only `confirmed_signup` from authenticated provider evidence; historical first acquisition once per person. Email eligibility is a *state*, not a cumulative number.
- Revenue: `merchant_settled_order` with transaction reference and effective date, gross commission, refund/reversal and attributable fees. Verify settlement independent of a self-declared trusted flag; don't show actual-looking synthetic totals as real.
- KPI: realized **net revenue per 1,000 qualified human sessions** = confirmed realized net revenue / qualified human sessions × 1000, only when both sides truly measured for the same 7-day and 30-day cohort. If missing data, output **NOT COMPUTABLE**, not $0. Tiny denominators must be disclosed. Follow paid conversion %, order count, lead-to-customer %, separately.
- When a video/profile link cannot be matched to a unique asset, mark platform-level attribution, not video-level success.

## Editorial QA on original six
- 01/02 duplicate link to Puységur: intentional thematic continuity but a low-information second CTA; alternatives already written in other PRs; prioritize choose one only with founder editorial approval.
- 03/05 hard-stop inactive guide placeholder: **properly blocked**, never present as current purchase route.
- 06 sends recipients back to a Fieldbook already promised in welcome; a fresh research skill destination could improve value, but no measured lift or founder substitution authorization exists.
- No tiny-sample A/B or click-to-revenue narratives. Avoid separate email platforms or unsanctioned signup experiments.

## Responsible handoffs
Mind owns real product guide, authenticated partner eligibility and permitted earning link. Claude owns production analytics/code. Grok owns video creation/distribution; Praxxis QA coordinates TASK-008. Dispatch owns subject/copy, email preview, sender/consent/compliance evidence and safe release gates. Founder retains final **send, release, schedule and spending approval**. All pieces remain research-only until independently verified.

## Primary references
WordPress.com subscription eligibility: https://wordpress.com/support/subscribers/ ; newsletter preview: https://wordpress.com/support/newsletter/email-appearance/ ; FTC commercial email: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; official seller route: https://zen12.com/getstarted ; separate seller newsletter: https://zen12.com/welcome ; Total Focus details: https://hypnosislive.com/mental-skills/total-focus ; qualified refunds: https://hypnosislive.com/faq ; Final Vestige Editorial Standards: https://finalvestige.com/editorial-standards/ .
