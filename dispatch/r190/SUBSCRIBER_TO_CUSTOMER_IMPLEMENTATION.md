# R190: the one authorized subscriber-to-customer proof path (NO SEND / NO DEPLOY)

**Source-of-truth:** Dispatch #174; Mind #171; Focus #129; Conversion #820; original pilot PR #175; per-edition gate PR #201; upstream R189 #1440. PR #49 remains frozen and separate. These are proposed controls, not deployed code, authenticated sales, or permission to contact subscribers.

## Conversion decision, not newsletter volume

One high-intent audience: a person who has **explicitly confirmed The Dispatch** after requesting the 52-page Focus Fieldbook and has independently chosen to investigate focus or meditation tools. Proposed first commercial candidate: **Zen12**, *only if* Mind #171 authenticates FV account acceptance, permission to promote specifically by email, current earning link format, creative rights, accurate seller terms, and an independent LIVE guide. Hypnosis Live Total Focus remains separate and equally held. Neither email can be sent on the current evidence.

The free Fieldbook has already been promised in the welcome message. **Do not ask existing recipients to re-subscribe to download it.** Offer editorial investigations or a deep link to the PDF as the relevant next step. For people who show no interest in commercial tools, keep the four editorial letters editorial. This is a *segmentation hypothesis*, not a built segment or claimed observed behavior.

## Proposed sequence, non-sending

1. **Grok → /focus/**: preserve external asset_ID in `utm_content`, named platform in `utm_source`, `utm_medium=organic_social`, and subject cluster in `utm_campaign`. Only Grok/Praxxis/Claude approve/publicize actual source-tagged links. No new browser pixel.
2. **Subscription attempt → pending**: UI displays 'check your inbox'; neither the query parameter `subscribe=...` nor visible download box nor subscriber totals establish confirmation. Grant Fieldbook access as the public flow currently allows, but **never** call it a confirmed lead on those grounds.
3. **Authoritative provider confirmation → one `confirmed_signup`**: only a server-side/signed backend provider record with `email_subscription=Subscribed`, recorded consent provenance and provider confirmation timestamp may qualify. Filter by actual email delivery eligibility, not merely WordPress Reader followers. Dedup by the provider's stable internal subscription key + confirmed state transition (private back-end); emit one aggregate `confirmed_signup` per genuine transition and avoid exposing email addresses, tokens, raw IDs or hash-reversible identifiers to frontend analytics. Consent for product-specific email marketing still requires scope review.
4. **Configured welcome → receipt proof**: The WordPress setting contains the 52-page PDF link; inspect existing authorized mailbox evidence, including subject and MIME parts, for a **real received welcome**. An October 25 confirmation request is not receipt of the welcome. No test sends authorized.
5. **Four editorial / two conditional offer letters**: only after founder's explicit content/audience/date signoff; commercial #03/#05 carry near-link commission disclosure and one first-party verified guide CTA. The guide and its permitted merchant earning link must be LIVE/approved first.
6. **Email CTA attribution** (proposal; not live): `utm_source=dispatch&utm_medium=email&utm_campaign=fv_dispatch_mind_pilot_2026_11&utm_content=issue_03_zen12_guide` on the guide CTA after exact URL review. For other issues use `issue_01_puysegur`, `issue_02_puysegur`, `issue_04_apollo1`, `issue_05_total_focus_guide`, `issue_06_fieldbook`. DO NOT embed in original drafts until vetted. Store earlier Grok first-touch on legitimate consent-preserving measurement only; source and email touchpoints are different.
7. **Settlement only → paid conversion**: affiliate clicks, checkout starts, confirmation requests and email opens are funnel signals, never paid orders. A purchase requires independently reported settled partner order/commission, net of refunds, reversals and applicable costs, and de-duplication. The KPI **1,000 × verified realized net revenue / verified qualified human sessions** is UNKNOWN, not zero, until both numerator and denominator exist. Review 7- and 30-day cohorts; tiny samples are descriptive only.

## Legal & native email hard stops

Jetpack status at 2026-11-07 17:31 UTC: enabled, automatic post emails OFF, format FULL, counted=3, confirmed counter=3, unconfirmed=2, suppressed=0. Counts are not additive and **actual email-eligible count is UNKNOWN**. Five latest posts are never-sent opt-outs, not evidence of welcome delivery.

WordPress currently offers documented email preview through the post editor Newsletter panel; the public support document says Preview email is offered when the per-post send toggle is on. The current connector has no authenticated native preview action. A normal web preview or our local HTML file **is not a genuine Jetpack email**. Do not toggle, save, publish, or send just to get one without explicit permission.

FTC commercial email rules require a valid **Final Vestige Studios** physical postal address and a conspicuous functional opt-out in actual recipient output, accurate headers and truthful subjects, plus conspicuous advertising identification. Automattic's address in a WordPress confirmation email is **not** Final Vestige's verified commercial mailing address. The local preview intentionally retains conspicuous impossible-to-send placeholder markers. Even a native preview would not prove an unsubscribe link actually works for a recipient.

## Highest-impact owner plan

| OFFER → FUNNEL | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Zen12 → guide/purchase | Named partner + EMAIL rights + live guide unverified | Mind authenticate explicit account permissions, exact vendor SKU, claims, earning links, refund/price/creative rights, then publish only with separate approval | **FAIL/CLOSED**: official seller page alone ≠ authorization | Mind #171 |
| Fieldbook → confirmed lead | Untrusted browser success, follower ambiguity | Claude verify provider-signed subscription/consent transition, first-touch attribution and dedup | **UNKNOWN**: WordPress total=3/confirmed counter=3/unconfirmed=2 only | Claude / Focus #129 |
| Lead → welcome | Configured ≠ received | Dispatch inspect authorized actual received welcome evidence | **UNKNOWN**: Gmail targeted search negative, no authorized new send | Dispatch #174 |
| Newsletter → recipient | Postal, unsubscribe and real rendering unverified | Read-only native preview if feasible; explicit founder-approved received-mail test later | **FAIL/CLOSED**: static HTML and platform docs are insufficient | Dispatch #174 |
| Commerce → realized net | No real orders or qualified-session denominator | Commerce reconcile settlement, fees, refunds and 7/30d qualified sessions | **NOT COMPUTABLE** | Commerce / Praxxis #820 |

## Source and channel custody

Official seller SKU descriptions: https://zen12.com/hnp and https://hypnosislive.com/mental-skills/total-focus . Seller promises are not independent efficacy studies. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . WordPress native preview: https://wordpress.com/support/newsletter/email-appearance/ . Historical editorial alternative sources in `02_OPTIONAL_CLEVER_HANS_UNSENT.md`.

Grok owns media production and distribution via TASK-008 in the existing shared Drive. Claude owns web/measurement production. Mind owns product eligibility. Dispatch owns drafts/QA only. Founder retains release approval. No account expense, paid platform, new subscriber list, active affiliate, WordPress write, import, notification, posting, tracking code, email, or changed WordPress settings.
