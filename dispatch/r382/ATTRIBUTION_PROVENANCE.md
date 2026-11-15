# Dispatch R382 — source-to-sale provenance and one-offer follow-up
**Status:** SOURCE-ONLY / NEVER_SEND. Refer to master [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), affiliate [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129) and business charter [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Stacked above Draft PR #2637; original Draft PR #175 unchanged; frozen homepage PR #49 out of scope.

## New, specific failure mode
A YouTube or TikTok asset can produce a UTM-tagged first-party Focus pageview. A person can then confirm a Jetpack newsletter subscription. **Those two facts do not, without a consent-safe verified source join, prove that the same person did both actions.** Likewise, a newsletter guide click may reach a merchant, yet a real sale cannot be claimed until independent, publisher-specific settlement records exist. An affiliate customer's $37 or $87.99 checkout is not automatically $37 or $87.99 of Final Vestige income.

The committed reference module deliberately returns *confirmed but unattributed* when authoritative subscriber confirmation is present but the source join is missing. It returns a noncomputable revenue KPI if verified sessions, exact paid commission, finalized refunds/fees or duplicate-free orders are missing. Even when an authentic paid commission is established, allocation of that payment to Grok's individual content asset remains *unattributed* without authorized merchant sub-ID lineage, source-to-guide continuity and separately checked first-party mapping. Synthetic proofs in offline tests are not production attestations.

## Live read-only configuration — 2026-11-15 16:32 UTC
- Jetpack newsletter ON and site send-capable, automatic new-post emails OFF; email content format FULL; sender display Final Vestige Studios; no-reply.
- Subscriber dashboard: total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**. These are overlapping/filtered views, not five unique deliverable inboxes. Unique consenting recipients remain UNKNOWN. Five recent post notices show never_sent_opted_out; no claim about lifetime zero sends.
- Configured welcome message includes the 52-page Seven Day Focus Fieldbook PDF; **actual welcome receipt and actual successful PDF delivery through email are unverified**.
- Published /dispatch/ page ID 523, /focus/ page ID 1579, Editorial Standards page ID 17 inspected through WordPress. Focus uses a client query/class-based gift reveal; it is not authoritative provider consent. An earlier proposed fix in draft PR #2584 is not proof of a live deployment.
- **Real Jetpack native Preview email not seen**, custom preheader transport not evidenced, Final Vestige qualifying postal address and delivered unsubscribe operation not verified. Preview email is not a delivered message; never conflate it with Send test email.
- No signed named Inspire3 publisher agreement, product-specific EMAIL permission, approved creative, issued earning link, live independently vetted Mind warm-up guide or referred checkout has been demonstrated. Source page promotion language is not a private authorization.

## One verified offer target — conditional Zen12 only
**High-intent hypothesis:** readers voluntarily working through the Fieldbook's audio claims checklist and choosing to inspect the meditation evidence guide. Do not profile subscribers by medical status, mental-health category or inferred protected characteristics. No implicit consent to affiliate email from opening the free PDF.

**Existing six weekly pilot slots, not an extra drip:** 
1. Editorial 01 establishes observation versus memory; one source-led editorial destination. 
2. Editorial 02 traces Puységur documentary evidence, one archive CTA.
3. Commercial **03 remains blocked**: free timed comparison and at most one independently verified, voluntarily opened Zen12 guide CTA after named email rights and final founder signoff. Disclosure beside the offer. **No merchant earning URL now.**
4. Editorial 04 remains copy-held pending the Apollo factual correction.
5. Commercial 05 remains independently blocked pending Total Focus rights; do not use its hypothetical approval as permission for 03.
6. Editorial 06 retention: practical evidence log or founder-adopted alternative, no repeated subscription CTA for an already confirmed reader.

Subscriber progression is **hypothetical** until actual consent and observation are verified. No behavior-triggered emails, list imports, segmentation engine, new software, automated branch sends, tracking pixels, affiliate link activations or dual signup lists.

## Event contracts and adversarial failure behavior
**Grok/Praxxis source:** existing TASK-008 supports actual per-asset source attribution: utm_source = legitimate platform, utm_medium = organic_social, utm_campaign = [topic]_pilot_2026_11, utm_content = real unique asset_id. Platform metrics and pageviews are diagnostic. TikTok caption links may not be clickable; map actual destination and acknowledge missing referrers.

**Claude qualified-human session:** legitimate first-party de-duplicated, bot-screened session. Site analytics event definitions must be audited before reuse; do not install duplicate scripts. If denominator unknown or zero, do not output a numeric net-revenue-per-1000.

**Jetpack confirmation:** provider-authoritative email-eligible confirmed status, opaque subscription ID and legitimate proof reference. Dedup only this provider ID per cohort. No email addresses or hashes of emails in GitHub, source links, web analytics or user-visible reports. Client ?subscribe values, is-subscriber CSS, Reader followers and Focus PDF clicks are NOT confirmed_signup_v1. Source-credited lead further requires legitimate, privacy-safe, explicit first-party-to-provider join. Unjoined leads remain unattributable rather than falsely zero.

**Mind/Commerce source-of-truth:** exact SKU Zen12 guide live and independently reviewed, issuer-approved email promotion and link formatting, independently inspected referred price/refund/upsells/eligibility. Not verified. Never display the public merchant price as guaranteed referred price; seller audio/brain effectiveness claims remain vendor assertions.

**Paid settlement:** actual merchant statement confirming publisher-paid commission, opaque order ID, finalized refund/clawback window, fees and currency. Retail checkout revenue is not publisher income; an outbound click, checkout start or pending order is not a paid commission. Disentangle overall settled net commission from asset-attributable commission. An individual asset deserves credit ONLY with permitted merchant sub-ID matched to verified first-party campaign provenance. Otherwise report settled publisher income as unattributed.

**7/30-day cohorts:** set a timestamped same-zone cohort window. Report qualified-human sessions, confirmed unique provider leads, source-matched leads, disclosed offer-guide clicks as diagnostics, independently settled paid commissions, refunds, fees, net revenue per 1,000 verified qualified-human sessions, and unassigned revenue separately. No statistical A/B conclusion on a list of three.

## Proof collection (not performed)
- [ ] WordPress provider proves exact unique deliverable inbox audience and confirms recipient consent; no addresses exported.
- [ ] Authorized founder-owned inbox provides actual welcome receipt and PDF availability (no test/send until explicitly approved).
- [ ] Actual non-sending Jetpack Preview email shows post title as email subject, layout, accessible links, inline disclosure; transport preheader remains unverified absent real header evidence.
- [ ] Actual Final Vestige physical mailing address and functional opt-out evidenced, not merely the Automattic address from an October confirmation.
- [ ] Mind/Commerce furnishes private named publisher and SKU EMAIL rights and a live authorized independent Zen12 guide; no credentials or tracked URLs in public tickets.
- [ ] Founder approves the final exact six email copies, eligible audience, cadence and any actual sends.
- [ ] Claude validates existing first-party attribution without new instrumentation or unauthorized identity joins.
- [ ] Merchant statement and settlement show actual publisher commission, refunds and fees before monetization reporting.

## Sources / cited authority
- Live standards: https://finalvestige.com/editorial-standards/
- WordPress preview/subject: https://wordpress.com/support/newsletter/send-newsletter-emails/
- WordPress email appearance: https://wordpress.com/support/newsletter/email-appearance/
- FTC commercial email: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Zen12 public seller page: https://zen12.com/secret/ (conditional $37 coupon, separate from unverified FV referred checkout)
- Total Focus official product: https://hypnosislive.com/mental-skills/total-focus (seller 33-minute/47-MB recording, no demonstrated efficacy)
- Grok/Praxxis source-of-truth TASK-008: https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit

## Highest-impact owner work
**Mind / Commerce:** FIRST pursue authoritative Zen12 EMAIL permission, issued earning link and live approved guide; affiliate email is otherwise not a viable commercial step. **Founder / Dispatch:** native preview, qualifying address and actual unsubscribe evidence without contacting subscribers. **Focus / Claude:** consent state and dedup; explain whether a privacy-safe UTM to provider subscription join is even feasible, without creating one by raw-email matching. **Grok/Praxxis:** hand off real asset IDs, not hypothetical traffic or impressions. **Final founder approval** governs all sends/publishes/expenses. This sprint changed only source control.
