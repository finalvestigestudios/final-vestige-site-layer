# R421 non-sending subscriber-to-customer path — one prioritized offer, six existing issues

**Research-and-review specification only.** No new campaign, list, domain, tracker, schedule, platform, subscriber message or WordPress post is created here. Do not treat page visits, clicks or a welcome configuration as sales. Cross references: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [master #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [preview pair #2848](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2848), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).

## One audience, one economic outcome

**Audience hypothesis (not a known segment size):** someone who voluntarily confirmed The Dispatch, used the existing Focus Fieldbook or chose to read a neutral focus-audio buyer guide, and wants an inexpensive, time-bounded way to experiment with attention without strong efficacy promises. No sensitive psychographic profiling, opened-email retargeting or behavioral automation is assumed. Readers can reach the guide without handing over an email address. Avoid claims that the person suffers anxiety, depression or another medical condition.

**One *candidate* offer:** the 12-level Zen12 recording course, not an invented FV product or an activated recommendation. It cannot be sold via Dispatch until Mind owns confirmed named FV partner approval **for EMAIL**, issued earning URL, approved first-party guide, checked checkout/SKU/refund terms, evidence-qualified copy and founder clearance. Product-specific outcome claims remain unproven. A published catalog listing or public promotional coupon is NOT permission.

**Economic result:** independently reported **settled** referral order/commission attributable to the approved route, net of applicable fees and refunds, divided by audited qualified-human session cohort where attribution permits. If a merchant provides only aggregate commissions, do not attribute to individual emails. Explicitly label unattributable revenue and missing denominators. Zero clicks and zero sales are not inferred from unavailable data.

## Planned progression without sending

| Stage | Existing artifact | Immediate reader value and *one* CTA | Eligibility / progression hypothesis | Hold |
| --- | --- | --- | --- | --- |
| 0, pre-pilot | Current Jetpack confirmation + 52p Focus welcome | Actual PDF URL after provider confirmation (no second signup) | Provider-authenticated double opt-in and a received welcome are individually verified | HOLD_RECEIPT |
| 1, editorial | Original Issue 01: mind is not a camera | Distinguish witness observation vs interpretation; one archive link | Broad history/perception interest; no offer | HOLD_INBOX |
| 2, editorial | Original Issue 02: before hypnosis had a name | Archival evidence vs explanation, one archive link | Builds skepticism and trust, not intent to buy | HOLD_COPY / repeated destination |
| 3, commercial reserve 1 | Original Issue 03: twelve-minute meditation question | Honest self-observation protocol; conditional approved FV Zen12 buyer guide, disclosure next to CTA | *Only after permission and guide live:* self-selected visitor may investigate one specific product | HOLD_MERCHANT; CTA token inactive |
| 4, editorial | Original Issue 04: Apollo 1 and cause | Investigative facts, one existing historical case CTA | Re-establish FV's archive identity independent of purchases | HOLD_COPY; corrected alternative not adopted |
| 5, commercial reserve 2 | Original Issue 05: before hypnosis audio | A no-cost evaluation checklist; Total Focus guide only if separately approved, never automatic cross-sell | Secondary optional experiment; no active second product while single-offer evidence incomplete | HOLD_MERCHANT; CTA token inactive |
| 6, editorial | Original Issue 06: evidence log | A practical record-keeping exercise, CTA should go to a useful post-welcome resource after founder review | Serve confirmed members, avoid duplicate lead counting | HOLD_CTA; original /focus/ may prompt new signup |

The stages above are conceptual issue positions, **not scheduled automation**. Retain **four editorial / two commercial-reserved** slots. No conditional send, purchase-triggered automation, reminder email, abandoned-cart email or broadcast without founder final campaign approval.

## Copy and attribution constraints

- Publisher name, exact issue subject and available preheader behavior must be verified in the *native Jetpack editor* (not only static HTML). User-established canonical subjects are preserved until individually approved changes. WordPress may take the post title as the actual email subject; do not assume separate preheader control exists.
- Only one clear *editorial* CTA per issue, even when a free source link appears as supplemental citation; Issue 03's future first-party buyer guide must not be swapped with a public Zen12 checkout link. If the email points to an approved guide, disclose nearby: **“If you buy through a link on the linked guide, Final Vestige may earn a commission.”** The guide must also disclose beside any actual affiliate link. Plaintext must carry the same disclosure.
- A non-transactional commercial email's valid **FV** postal mailing address and functional opt-out are necessary irrespective of the editorial-heavy tone. Do not count an editorial issue as legally exempt just because it contains no direct affiliate purchase link. Source: [FTC guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).
- Existing Grok paid-approval boundary remains: channel owners supply a true unique asset ID and `utm_content`; no new social content or spoken CTAs from this lane. Proposed, inactive link contract: `utm_source=youtube|tiktok|...`, `utm_medium=organic_social`, `utm_campaign=<topic>_pilot_2026_11`, `utm_content=<unique_asset_id>`. Then `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_03` for approved first-party link **only after** Claude validates existing analytics and consent, with no duplicated scripts.
- `confirmed_signup` is emitted only on a provider-confirmed transition with a **private** durable provider event ID; retrying a signup form or refreshing its success URL is never a new lead. Never publish provider IDs or SHA-1 hashes of email addresses. Use separate cohort counters for historically confirmed, currently opted-in, welcome received, clicked guide, and merchant paid settlement. Do not deduce customer IDs from a shared device, cookie or email opening.
- Preserve 7/30-day cohorts by *real observed times*, note when independent merchant data lack order-level attribution, and report gross, refunds, fees, net plus count of paid orders separately. A checkout click is not a paid order.

## Distinct acceptance tasks from today's source truth

1. **Focus/Claude:** Request private subscriber provider eligibility view under authorized account, reconcile 3/3/2 dashboard with Reader3/email0 definitions, establish deduplicated consent proof and *real received* Fieldbook welcome. Site media library already confirms the configured PDF object ID 1737; do not repeat media inventory.
2. **Mind/Commerce:** Request named affiliate approval and **EMAIL** promotional permission for exact Zen12 SKU/guide/creative, issued tracking format, actual referred checkout and settlement reporting. No public merchant URL is a substitute. Keep second Total Focus offer blocked.
3. **Founder/Dispatch:** Review existing six HTML/TXT pairs from R419, run *non-sending* native email Preview in authenticated WordPress editor, witness mobile/desktop rendering, valid FV physical postal line, actual functional unsubscribe and preheader behavior. **Sending even a test requires additional authorization.**
4. **Claude/Revenue:** Match authorized asset-level first-party visits to confirmed transitions and partner settlement reports. Without independently observed paid transactions, net revenue per 1,000 qualified human sessions remains **NOT COMPUTABLE**.

**Success condition for the research lane:** trustworthy consent, content and legal readiness evidence, not volume of drafted emails or display metrics. Founder approval remains separate and necessary for any actual send.
