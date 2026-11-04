# R106 — Dispatch consent → confirmed lead → paid customer (DRAFT; NO SEND)

**Scope:** add-only child of [R105 PR #884](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/884), original founder six-issue campaign [PR #175 at `d57ccdba`](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175). Ownership: Dispatch [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), Focus signup [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), Mind/affiliate [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), conversion instrumentation [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), commercial charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Grok/Praxxis own TASK-008 in their existing shared Google Drive; this does **not** change their assignment or create a parallel content queue.

## Source-of-truth snapshot: November 4, 2026, 05:38 UTC

Authenticated live WordPress reads (not an offline inference):

- Existing Jetpack newsletter **enabled**, `site_can_send=true`, new-post auto-email **off**, `email_content_format=excerpt`, `reply_to=no-reply`.
- Welcome-message *configuration* links the **52-page Seven Day Focus Fieldbook**; no authenticated evidence of an actually **received** welcome message, PDF retrieval, or actual commercial newsletter rendering.
- Newsletter counters: `total=2`, `confirmed=2`, `unconfirmed=2`. They conflict; neither four people nor two verified email-eligible recipients follows. Separately reported Jetpack followers: **email=0 / WordPress.com=2** (different metrics, do not combine).
- The latest five recorded sends all show `never_sent_opted_out`, `dispatched_at=null`, and unknown recipient/sent counts. They are five non-sends, **not** proof that no historical email was ever delivered.
- Live `/focus/` already explains occasional commission-earning recommendations. `/dispatch/` does not; this is a consent-expectation discrepancy to evaluate before any commercial campaign. Both pages remain unchanged.
- Published [Editorial Standards](https://finalvestige.com/editorial-standards/) insist on documented sources, uncertainty, correction notices and disclosure of financial relationships.

## Single intended journey — not activated

One real **Grok Mind/Perception asset** (a current immutable asset_id/post URL has *not* been supplied to Dispatch) → relevant existing history/perception article or `/focus/` → native Jetpack signup attempt → **authoritatively confirmed** consented subscription transition → *genuine received* current welcome email → free 52-page Fieldbook → existing four editorial Dispatch issues → optionally one contextual *merchant-approved*, independently evaluated presell guide (Issue **03** Zen12 candidate, not a verified approval) → independently merchant-confirmed paid purchase → fees/refunds → **realized net revenue**. Issue **05** retains a second commercial-*reserved* slot; two slots does not mean two emails may now be sent.

**Hard commercial blocker:** The 52-page Fieldbook is a proven configured **free acquisition asset**, **not a paid product**. Neither a rights-cleared, currently sellable/fulfillable FV Payhip SKU nor a named Inspire3 email-eligible affiliate account and approved live presell guide has been independently verified for this conversion route. Therefore **NO ONE PAID OFFER IS SELECTED**. The next task is obtaining real seller/rights/order evidence, not inventing a product or link.

## Proposed no-send progression within the EXISTING six issues

This is a **test plan**, not an additional drip series or revised campaign approval.

| Stage | Message and genuine value | One CTA | Gate |
|---|---|---|---|
| Existing Jetpack welcome | The already-configured complete Fieldbook; no additional subscription request | Existing 52-page PDF | Received welcome + opens PDF **unverified** |
| Editorial Issue 01 | Seeing is not knowing: distinguish attention experiment from confident memory; preserve original investigative brand | One existing live evidence article, final URL requires edition selection | Four editorial slots unchanged; send hold |
| Editorial Issue 02 | Puységur's documented witness problems and the evidentiary limits of mesmerism | Existing Puységur archive | Send hold |
| Reserved Issue 03 | Seller's Zen12 feature list versus evidence, limitations, and free attention-log alternative; **no assumed efficacy** | APPROVED live independent Zen12 guide **only if** acceptance, email rights, privacy and link/claim checks pass | HOLD_MERCHANT |
| Editorial Issue 04 | Apollo 1 and source-vs-single-cause interpretation | Existing Apollo investigation | Send hold |
| Reserved Issue 05 | Total Focus exact recording features and buyer verification checklist | APPROVED live guide **only if** permissions pass | HOLD_MERCHANT |
| Editorial Issue 06 | A week-long attention record and how to judge it rather than trust a feeling | Direct existing Fieldbook PDF, **not a second signup** (optional proposal, not selected) | Send hold |

**Segmentation is a hypothesis, not a new subscriber field.** Someone arriving from a Mind-related Grok asset may be interested in a practical focus resource; someone reading Apollo 1 may prefer source documentation. Native Jetpack's ability to retain acquisition source for confirmed subscribers is **unverified**. Do not infer identity, create a second list, upload audience tags or use behavioural profiling without privacy review and consent. If no first-party source join exists, lead-source attribution stays **UNKNOWN**.

## Exactly one confirmed_signup event

Use the same naming as [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820):

`utm_source=<real platform>&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=<Grok immutable asset_id>`.

The asset ID and final landing link need Grok/Praxxis/Claude QA before public use. A TikTok bio/proxy route may break asset attribution; show missing data instead of guessing. No duplicate tracking pixels/scripts.

**Do NOT emit `confirmed_signup` on:** button press, form submit, confirmation email sent/opened, page refresh, `/focus/` download click, dashboard total increment or a guessed person count. Emit **one aggregate unit** only when an authenticated first-party Jetpack adapter observes **not-confirmed → confirmed**, a valid consent record and an internal, one-time dedup key. Dedup within that adapter using native internal site+subscription keys; **never export keys or hashed emails in analytics events**. If the connector cannot expose an authoritative transition safely, `confirmed_signup=UNOBSERVABLE`. Do not create a test subscriber or send an email to prove it without founder approval.

The offline `unique_confirmations` simulator demonstrates repeat-submit, retry, suppression and opt-out handling with **synthetic identifiers only**. It does not connect to WordPress or validate a real subscriber.

## Purchase evidence and revenue accounting

An `affiliate_outbound` is **not** a paid sale, nor is a checkout start, subscriber, downloaded PDF or platform view. Order evidence requires seller-originated payment status, an actual order (de-duplicated inside merchant adapter), observable attribution to the campaign if available, and fees/refunds accounted. Only aggregate metrics leave the source system; no buyer names, customer emails or order IDs in repo, URL UTMs or analytics. If source, denominator, refunds or merchant access are missing, show **N/A**, not zero, an estimated dollar value or a click-to-sale conversion.

For 7-day and 30-day cohorts, report: actual qualified-human sessions per verified source asset, relevant landing/CTA counts, *confirmed* leads, merchant-confirmed orders/customers, gross earned, fees, refunds, realized net, paid conversion rate, lead-to-customer conversion, and net revenue per 1,000 qualified-human sessions. All presently **UNKNOWN/N/A**. Tiny sample: no statistically credible A/B claims.

## Priority offer → funnel → blocker → change → evidence → owner

| Offer | Funnel step | Blocker | Next change/experiment | PASS/FAIL proof | Owner |
|---|---|---|---|---|---|
| Existing free Fieldbook (LEAD only) | Grok Mind asset → landing | Actual immutable asset link and permitted CTA not received | Review one existing social asset and source-tagged destination, do not post | Exact source URL + permitted placement + staged mobile landing evidence; **PENDING** | Grok/Praxxis/Claude |
| Existing free Fieldbook | Form → confirmed subscriber | Counts conflict; no authoritative consented record transition | Read-only first-party reconciliation; no exported PII/test subscriber | Authenticated one-time transition + consent, or **UNOBSERVABLE** | Dispatch/Claude |
| Existing free Fieldbook | Welcome → PDF | Saved welcome ≠ received welcome; PDF not proven opened | Controlled, explicitly authorized test when founder approves | Actual redacted received MIME and working 52-page file; **PENDING** | Dispatch/Site QA/founder |
| Zen12 candidate (**not approved**) | Issue 03 guide → seller | No named affiliate acceptance, email-promo rights, published approved guide, buyer-data permission | Independent actual seller/affiliate verification and guide QA | Merchant evidence, live guide, accurate disclosure; **FAIL/HOLD** | Mind Studio/founder |
| One paid **FV** SKU (NOT selected) | Relevant guide → checkout → paid order | Payhip inventory, delivery rights, refund/fee record unverified | Commercial owner selects **one** audited in-stock SKU with intent fit | Actual purchasability + fulfillment + order/refund data; **NOT VERIFIED** | Claude/commerce owner/founder |
| All six | Native email, legal footer, opt-out | Excerpt truncates CTA/disclosure; native received test, publisher mailing address/unsubscribe absent; draft-version drift | Exact founder creative selection + authorized end-to-end test | Accessible actual email, verified Final Vestige postal & functional unsubscribe, final founder approval; **HOLD** | Dispatch/Site QA/founder |

## QA + release boundary

`python -I -m unittest discover -s dispatch/campaign-2026-mind/r106-confirmed-signup-revenue-gate/tests -v`

`python -I dispatch/campaign-2026-mind/r106-confirmed-signup-revenue-gate/gate.py`

These tests are offline synthetic gate checks; passing them is not evidence of WordPress delivery, live conversion or paid revenue. Read companion `contract.json` for the exact source status and `reviewer_board.html` for an accessible no-JS review. Full original six-issue copy remains held in PR #175; no new email newsletter issues are created by this PR.

**FTC legal source:** [CAN-SPAM business guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business). Requires truthful sender/subject and appropriate commercial identification, a valid physical postal address and effective opt-out. A WordPress/Automattic postal address in a subscription confirmation is not verified as Final Vestige's commercial mailing address. This is risk-check documentation, not a legal certificate.

**RELEASE: HOLD_UNSENT.** No email or test send, scheduling, post publication, WordPress writes, new subscriber lists, affiliate links, vendor calls, tracking deployment, social posts, commerce activation or spend. Keep homepage PR #49 untouched.
