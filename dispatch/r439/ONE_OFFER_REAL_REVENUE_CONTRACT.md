# R439 — One-offer subscriber-to-settlement progression (NOT ACTIVATED)

**North star:** net realized revenue per 1,000 audited qualified-human sessions, not clicks or newsletter volume. No qualified-human denominator, independently settled transaction, actual refund/fee reconciliation, current merchant approval or email recipient eligibility is available. **Current KPI = NOT COMPUTABLE**, not zero. All values below are definitions or clearly synthetic examples, not business results.

## Ordered high-intent path

**Target reader:** a genuine Final Vestige history/perception reader who visited a cited experiment or investigation, voluntarily explored /focus/, and later expressed interest in practicing attention. Do not infer an individual's health condition, mental status or purchase readiness from viewing a page. Source-to-landing relevance, not broad demographic inference, defines intent.

1. **Grok asset → cited investigation**: Grok chooses actual platform CTA, keeps creative ownership, records immutable `utm_content=<asset_id>`; use the existing campaign convention `utm_medium=organic_social`, `utm_campaign=<topic_cluster>_pilot_2026_11`, `utm_source=<actual platform>`. For platform bio/profile links, note loss of asset-level fidelity; never invent attribution.
2. **Investigation → Focus/Dispatch**: a relevant first-party CTA leads to the freely accessible 52-page Fieldbook or existing Jetpack subscription. `focus_signup_click` and `focus_pdf_click` are *not* `confirmed_signup`.
3. **Provider-confirmed Dispatch consent**: only provider-authenticated consent scoped to this newsletter, deduplicated using a private stable identifier, can increment the event `confirmed_signup`. Logged-in WordPress.com subscribers may skip a separate confirmation email.
4. **Welcome and resource**: require actual receipt witness before stating the Fieldbook was delivered. The PDF may also be downloaded without consent; preserve that option.
5. **Four editorial letters**: history of witness reliability, documented experimentation, Apollo 1 and evidence logging; source links and one contextually relevant first-party CTA per issue. **No targeted segment exists** in current Jetpack configuration; hypothetical journey is not an automation.
6. **Two reserved commercial letters**: 03 Zen12 and 05 Hypnosis Live, with independent first-party educational guide CTAs; **both remain inactive** until the exact named seller/channel permissions, reviewed live guide and checkout proof exist.
7. **ONE offer in a possible future consented follow-up**: provisionally choose *Zen12* only when Mind/Commerce has authenticated that specific EMAIL offer and founder approves the recipient cohort. If Zen12 fails the gate, use an **editorial-only resource**, not an unapproved replacement. Do not promote Total Focus as though it were Issue 05 Hypnosis Live.
8. **Paid sale**: only merchant/publisher-reconciled settled transaction with source identity, gross amount, refunds, chargebacks and fees counts as monetization. Unattributed or duplicate sales remain excluded from source-specific revenue calculations.

## Hypothesis, not an active segmentation feature

**H1:** Readers arriving via a specific evidence-based attention story who voluntarily view a practical Fieldbook explanation may be better aligned to an independently written Zen12 buyer guide than readers from an unrelated history topic. Do not target by private identity or silently enable newsletter categories. Compare source-topic *aggregates* at 7/30-day maturity only when consent and adequate human traffic exist. Tiny samples are descriptive, never statistically significant.

## Analytics schema — no additional script

| Event | Required keys | Reject when | Owner |
|---|---|---|---|
| Qualified human session | opaque server session aggregate, timestamp, known source/asset campaign, anti-bot rules, consent-compliant analytics basis | bot, self-test, missing referrer resolution, duplicate session | Claude / Praxxis |
| Relevant CTA click | `cta_id`, `edition_id` or `asset_id`, on-site destination, event time | invented link, no live destination, duplicate clicks treated as unique leads | Claude |
| `confirmed_signup` | provider-authenticated confirmation, private dedup key, Dispatch purpose, provider timestamp | client-only click, free download, WordPress Reader follow alone | Focus / Claude |
| Genuine received welcome | authorized inbox witness with PII removed, matching WordPress configured resource | mere configured message, old confirmation email | Focus / Founder |
| Affiliate outbound click | only activated authorized merchant URL, approved guide, disclosed offer/SKU | placeholder, unverified earning URL | Mind / Commerce |
| Paid order | merchant-issued immutable settlement reference, SKU, gross, currency, actual attribution | cart, click, unverified conversion pixel | Commerce |
| Net recognized revenue | paid settlement less refunds, chargebacks, commissions/transaction fees, reconciled cohort | no return period or incomplete merchant statements | Commerce / Praxxis |

Never put hashed email, addresses, purchase IDs, IPs, or account secrets into publicly viewable GitHub files. Tests use synthetic numbers and opaque *evidence references*, not customer records.

## 7-/30-day cohort definitions

- Cohort origin: date of first audited qualified-human source session, with immutable first-qualified-source preference; keep first touch and last touch as separate views rather than claiming exclusive causation.
- `net_realized_usd = settled_gross_usd - refunds_usd - chargebacks_usd - fees_usd` (and subtract other clearly itemized partner deductions if applicable).
- `net_revenue_per_1000_qualified_human_sessions = 1000 × net_realized_usd / audited_qualified_human_sessions`, **only** with both verified numerator and a nonzero audited denominator; otherwise return null/NOT_COMPUTABLE.
- Lead-to-customer = **distinct settled customers linked to provider-confirmed leads / unique confirmed leads**, with clear windows and only aggregate reporting. If merchant cannot link customer to a lead without disallowed personal data, mark attribution unverified.
- 7-day and 30-day reports must show cohort completeness, refund maturity, and tiny-sample warning; never fill unknown with zero.
- Synthetic example solely to test code: 100 genuinely audited sessions, 1 independently settled $20 order, $2 refunds and $3 fees gives **$150 per 1,000**. No such actual Final Vestige data exists.

## Conversion-first priority board

| Offer → funnel step | Blocker | Change/experiment | PASS/FAIL evidence | Owner |
|---|---|---|---|---|
| Free Fieldbook → confirmed lead | /focus/ browser signals can imply a signup without provider consent | R436 source-only public-PDF patch + R439 copy correction candidate; no CMS change | Offline code PASS; live source changed? **NO**; actual provider confirmation **UNKNOWN** | Focus / Claude |
| Dispatch acquisition → eligible inbox | 3 confirmed vs 0 direct-email/3 Reader; provider recipient filter unobserved | Private aggregate `Email subscription=Subscribed` witness | **HOLD** until direct provider proof | Focus / Founder |
| Dispatch subject → genuine inbox | Native preview, subject/preheader and legal footer not seen | Non-sending native WordPress Preview plus published-post toggle OFF check | **HOLD**, screenshots/receipt not provided | Dispatch / Founder |
| Zen12 → guide → verified checkout | Email rights, actual URL/SKU/current terms missing | Mind validates merchant-issued permissions and approved live independent guide | **HOLD**, seller page alone fails | Mind / Commerce |
| Hypnosis Live → guide → verified checkout | Other coordination accidentally labeled Issue 05 Total Focus | Pin original Hypnosis Live identity; verify exact audio/terms/permission | Code rejects substitution; **partner HOLD** | Mind / Commerce |
| Social asset → qualified sale | No known asset-specific confirmed attribution/settled merchant order | Preserve Grok asset IDs, reuse Claude analytics; avoid extra script | **HOLD**, net/1k NOT_COMPUTABLE | Grok / Praxxis / Claude |

No pre-sell guide activation, newsletter send, targeted follow-up, social publishing, paid service, site post or analytics instrumentation was authorized by this package. Issue #820 remains the aggregate conversion coordination source; homepage flagship remains priority one, PR #49 frozen.
