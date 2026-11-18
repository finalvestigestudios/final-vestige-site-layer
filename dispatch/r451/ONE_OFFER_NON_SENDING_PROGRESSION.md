# R451 — One-offer subscriber-to-customer progression (design only; nothing sent)

**Source of truth:** [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [Revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). **Draft PR #175 manuscripts remain the canonical six originals**, all `HOLD_UNSENT`; [PR #3016](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3016) contains the isolated recipient-copy repair for Issue 05. No new email platform, list, autoresponder, paid service, segmentation tool or tracking pixel.

## Hypothesis, not an A/B result

**One audience:** viewers of a specific Grok perception/history video who voluntarily visit the matching Final Vestige investigation or existing Focus page. They are interested in evidence about perception and, optionally, evaluating a short meditation habit. **One optional future product:** Zen12 **only if** written partner approval, product-specific email permission, live disclosed FV guide and issued partner URL are authenticated. Otherwise there is **no paid recommendation**, and the existing free Fieldbook remains the next step. Hypnosis Live retains its **reserved Issue 05** position but is not the primary funnel offer or substituted for Zen12.

**Expected reader journey, not scheduled actions:**

| Stage | Reader value and non-selling message | Allowed CTA/destination | Confirmation/paid proof |
|---|---|---|---|
| A. Grok → evidence | A specific change-blindness or historical investigation; distinguish observation from interpretation | Exact verified existing first-party source page | Grok immutable `asset_id`, referrer and consent-respecting qualified human visit; Grok handles creative |
| B. Free tool → consent | /focus/ clearly offers the 52-page Fieldbook whether or not someone joins | Existing /focus/ signup only; direct free PDF remains available | *New* provider confirmation transition, not a form view or PDF click |
| C. Existing welcome | Fieldbook link and honest occasional Dispatch expectation | Already configured welcome; **no editing/sending** | Independently received welcome by authorized holder; contains working PDF |
| D. Editions 01/02 | Free source-led change blindness and Puységur evidence | One published first-party source per letter | Qualified first-party visit, never counted as purchase |
| E. **Issue 03 reserved** | An accurate, optional Zen12 buyer-evaluation checklist: program format, personal effort, seller claims vs evidence, current terms | **Disabled** [BUYER GUIDE NOT LIVE]; if later approved, one reviewed FV guide with adjacent “If you buy through links on this guide, Final Vestige may earn a commission.” | Issued affiliate link and independently reported paid commission, less refunds/fees |
| F. Editions 04/05/06 | Apollo 1 chronology; separately optional Hypnosis Live checklist **only if product/EMAIL rights independently pass**; Fisher-style focus evidence log | One selected first-party editorial page or disabled commercial guide as appropriate | Cohort revenue only from verified settlements; no list spam or artificial cadence |

**Segmentation hypothesis:** (1) source topic = history/perception from a nonidentifying campaign source, and (2) consent state = unconfirmed / newly confirmed / existing subscriber. Existing Jetpack list has **no demonstrated per-recipient topic segmentation or automation**. The table is a content-progression hypothesis, NOT a claim that Jetpack has tags, triggered follow-ups or the ability to send bespoke commercial messages. No targeting by personal attributes or any subscriber-level repository data.

## Source-tagged attribution convention; do not deploy until Claude QA

Grok outbound source (only after creative owner/Claude review):
`utm_source=youtube&utm_medium=organic_social&utm_campaign=perception_pilot_2026_11&utm_content=<immutable_grok_asset_id>`

Later editorial email CTA, only if founder-approved to send:
`utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue01_change_blindness`

Reserved commercial Issue 03, only when the **first-party buyer guide exists** and the commercial send passes all gates:
`utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue03_zen12`

Issue 05 reserved product identity remains `issue05_hypnosis_live`. **No subscriber ID, email, encoded PII, affiliate ID, paid order ID, or unique per-person query parameter in UTMs.** Email attribution is an observed landing-session context, **not** proof of a specific earlier Grok viewer or later merchant buyer. Do not carry first-touch asset attribution across browser/device without consented independently tested identity continuity. No new measurement scripts; Claude owns instrumentation. Email clicks are not orders.

## Definition of trustworthy event and scorecard

`confirmed_signup`: count once per **new provider-confirmed subscription transition** when (a) explicit opt-in request, (b) new email-subscribed provider record or previously unconfirmed → confirmed provider transition, (c) timestamped confirmation witness, and (d) duplicate existing subscriber and Reader-only follow excluded. Never emit an email address/recipient ID in shared analytics. Signup attempts, popup views and downloads are separate events; without a provider transition do not emit a confirmed lead.

`email_landing_visit`: visitor opened first-party page with a QA-approved newsletter UTM; verify URL actually works and human-session qualification separately. `guide_to_merchant_click`: outbound event on approved live buyer guide (not yet permitted). `merchant_paid_conversion`: merchant independently reports settled paid order/commission; apply timing, attribution limits, refunds and fees. **Do not represent clickthrough or checkout as a sale.**

Score 7- and 30-day cohorts separately using: qualified-human sessions, new confirmed leads, independently reported paid orders/customers, gross commission/revenue, refunds, fees, **realized net revenue per 1,000 qualified-human sessions**, paid conversion rate and lead-to-customer rate. With no independently witnessed human denominator and a complete settlement ledger, the KPI is **NULL / NOT COMPUTABLE**, never fabricated zero. Three eligible publisher-associated records are not an acquisition experiment, and neither statistical significance nor A/B lift can be claimed.

## Priority matrix: offer → funnel step → blocker → change → proof → owner

| Priority | Offer/step | Concrete blocker | Change or experiment | Required pass/fail evidence | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → first-party guide → buyer | No authenticated Final Vestige account approval/EMAIL rights, live approved guide, earning URL or exact current checkout terms | Mind gets named merchant proof; select one fully reviewed first-party guide, **no live launch yet** | Account-specific written rights and real checkout witness or FAIL/HOLD | Mind / Commerce |
| P0 | Fieldbook → confirmed lead | 3 subscriber-eligible records vs Stats Followers email=0; received welcome/new lead unproven | Reconcile the two WordPress source feeds; independently witness new consent→confirmed transition and welcome without unauthorized sends | Source-labelled reconciled report and permitted receipt, or HOLD | Focus / Claude |
| P0 | Dispatch → trustworthy delivered mail | Native post-editor preview inaccessible here; no verified FV postal or rendered opt-out | Founder-authorized in-editor **non-sending Preview**, inspect desktop/mobile, publisher address and opt-out; no test send absent separate approval | Actual source-linked evidence of Preview and compliance footer, or HOLD | Founder / Dispatch |
| P1 | Grok asset → qualified session | Immutable asset and audited human session not yet bound to any accepted sale | Use existing first-party consent-respecting instrumentation; no new scripts | Real asset→session evidence and merchant settlement ledger, or NULL | Grok / Praxxis / Claude |
| P2 | Editorial source CTA | Existing /dispatch/ and /focus/ promise emails when every investigation is published despite global default-off | Founder approves corrected “selected editions” copy only in separate release | Live page vs sender-policy verified, not merely draft | Dispatch / Founder |

**Governance:** All six existing editions remain `HOLD_UNSENT` in a 4 editorial : 2 reserved-commercial allocation. No approved customer mail, preview send, scheduled email, WordPress publish, change to welcome/list/settings, merchant link activation, merge, social post, or spending. Frozen homepage PR #49 unchanged. This plan grants NO approval to take any of those actions.
