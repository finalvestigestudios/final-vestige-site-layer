# Dispatch R200 — consent-to-order implementation contract / NO SEND

2026-11-07 Pacific. Scoped to Dispatch #174, Focus #129, Mind #171, conversion #820; stacked on PR #1517. Homepage priority #1 and frozen PR #49 untouched. Source-only proposal, not deployed analytics or subscriber-eligibility proof.

## Highest-value finding

Producing another email does not establish revenue. The bottleneck is proving each boundary: qualified human arrival from a specific Grok asset; provider-confirmed email consent; receipt of the promised Fieldbook; voluntary passage to a relevant published offer guide; explicitly authorized account-level affiliate outbound link; independently reported settled order; real fees/refunds; reconciled net revenue. Every unavailable transition must remain UNKNOWN rather than zero or success.

## Fresh read-only verification

WordPress diagnostic captured 2026-11-08 03:36 UTC: Jetpack newsletter enabled; automatic new-post sending OFF; format FULL; sender Final Vestige Studios; reply-to no-reply; counted total 3, confirmed counter 3, unconfirmed requests 2, suppressed 0; all five recent published posts status never_sent_opted_out. The counters must not be added as unique persons. Real email-eligible recipient count is UNKNOWN until the platform's filtered Email subscription = Subscribed aggregate is available. The welcome message includes a 52-page Focus Fieldbook PDF, but actual final welcome receipt is UNKNOWN. A 2026-10-25 subscription-confirmation message is not welcome delivery.

Live /focus/ WordPress page 1579 contains fvf-gift-v2, which reveals the Fieldbook state based on a permissive non-error subscribe query value or the is-subscriber CSS class. Neither establishes provider-confirmed subscription. A successful PDF download, visual thank-you panel or Reader follow must NOT trigger confirmed_signup. Claude/Focus owns any server-side correction; Dispatch owns read-only verification and event specification.

## Event and attribution state machine (for production owner to implement and independently test)

States: VISIT → FORM_ATTEMPT → PENDING_CONFIRMATION → PROVIDER_EMAIL_SUBSCRIBED → WELCOME_RECEIVED_EVIDENCE → GUIDE_VISIT → AUTHORIZED_AFFILIATE_CLICK → MERCHANT_SETTLED_ORDER → NET_RECONCILED. An opt-out or suppression is a separate suppressing state; never assume consent reactivates. Only the authoritative provider transition PENDING_CONFIRMATION → PROVIDER_EMAIL_SUBSCRIBED can create one confirmed_signup event. If provider event-level data is unavailable, provide aggregate count only; do not mint fabricated events from a dashboard count difference.

Provider opaque subscription ID or keyed server-side HMAC may be used privately for deduplication subject to retention/security review. Do not send email addresses, raw hashes, subscriber IDs or merchant order IDs to public analytics or GitHub. Never infer identity joins from first-party cookie, query parameter, CSS class or unconfirmed email signup. The event's acquisition attribution may remain UNKNOWN when source-to-confirmation linkage is unavailable.

Grok source convention: utm_source=actual_platform, utm_medium=organic_social, utm_campaign=topic_cluster_pilot_2026_11, utm_content=unique_grok_asset_id. Do not publish new links until Grok and Claude verify permitted link surfaces, landing intent and consent. Proposed outbound Dispatch guide convention, only after verification: utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_pilot_2026_11, utm_content=issue_01 to issue_06. Never append personal identifiers. A newsletter click is not a sale. Public URLs must be tested for consent and tracking policy before activation.

## One-offer commercial progression hypothesis

Person interested in evidence about attention or focus → an appropriately matching on-site article → optional 52-page Fieldbook → truly provider-confirmed subscriber + verified welcome delivery → weekly evidence-first editorial → reader *chooses* seller-neutral Zen12 buyer guide → if and only if merchant channel approval, issued link and live vetted guide are verified, independently disclosed purchase option → independently reported paid commission. Hypnosis Live issue #05 stays its own separate merchant hold. Four editorial / two commercial pilot remains unchanged; no blanket automated drip or unapproved commercial blast.

Commercial-source truth is NOT the public Inspire3 catalog or sales page alone. Mind must verify named FV publisher acceptance, explicit email marketing permission, approved account-issued earning URL, allowed pre-sell creative/link formats, live vetting of claims, current checkout and refund for the actual offer. Public product prices and claims are seller descriptions, not authenticated final purchase terms or efficacy results.

## Honest economics and cohorts

Revenue event originates only in merchant settlement/reporting or owned payment-provider records, with unique order ID deduplication and adjustment for refunds, reversals, chargebacks and fees. No affiliate clicks, checkout starts, email opens, confirmation-page loads or pageviews become paid sales. Gross/net revenue, paid customers, lead→customer conversion and 7-/30-day cohort metrics require independent order and attribution data, with explicit tiny-n caveats. Key KPI = 1000 × verified realized net revenue / verified qualified human sessions. With no reconciled denominator and no merchant sales records, record NOT COMPUTABLE, not $0. A complete signed reporting window is necessary even to claim zero orders.

## Email release legal + native preview protocol

WordPress official documentation describes a preview under the post editor newsletter icon, only when its per-post Send to subscribers toggle is enabled. Neither the toggle nor Send test email may be exercised without required founder permission; DO NOT make an editor draft or publish a post in this lane. No genuine received Jetpack email has been inspected. Current static HTML is NOT native render proof. Verify sender, truthful subject, final publisher postal address (not Automattic's address), accurate commercial identification, clickable native unsubscribe and opt-out honoring before approval. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . WordPress: https://wordpress.com/support/newsletter/email-appearance/ .

## Priority — OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER

| Offer / step | Blocker | Change/experiment | Proof today | Owner |
|---|---|---|---|---|
| Fieldbook / qualified lead | False equivalence between UI success and subscribed | Provider-confirmed transition + dedupe | FAIL as confirmation proof; visual state observed | Claude / Focus #129 |
| Fieldbook / welcome | Final received email missing | Inspect existing authorized inbox receipt without sending | UNKNOWN; configured only | Dispatch |
| Zen12 / buyer-guide click | No email rights + guide not live | Merchant account permission + live independent offer guide | HOLD_MERCHANT | Mind #171 |
| Dispatch / recipient | Actual native footer, postal and unsubscribe missing | Authorized genuine native preview and compliance test | FAIL release, unverified | Dispatch / QA |
| Buyer / net revenue | No settled reports + no qualified session denominator | Real reports, refunds, fees, 7/30-day cohort join | NOT COMPUTABLE | Commerce / Praxxis #820 |

## Operating safeguards

All six original Issue #175 emails HOLD_UNSENT. Commercial #03/#05 additionally HOLD_MERCHANT. Alternative editorial included here is unapproved and not a seventh issued send. No posting, sending, scheduling, subscriber exports, imports, settings or live tracking changes. No A/B results invented. Founder explicitly approves copy, recipients, timing and legal/merchant release separately.
