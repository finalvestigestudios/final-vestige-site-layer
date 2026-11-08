# FV Dispatch R206 — canonical reviewer pack; HOLD UNSENT (2026-11-08)

**Master #175 SHA:** `d57ccdba3aee8f065e143e101c2945f4f3d01647`. **Readiness #201** and **parent R205 #1558** retained. **Homepage frozen #49 untouched.** Six original messages unchanged.

## Delivered
The `previews/` directory contains 12 **source-derived, static** files: one inline-style, table-layout, single-column HTML reviewer and one plaintext reviewer for **each of the original six**, preserving all original subject/preheader strings, original text, and mandatory `[[VALID_POSTAL_ADDRESS_REQUIRED]]` and `[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]` hard stops. Commercial Issues 03 and 05 retain **inactive** warm-up-guide tokens and adjacent commercial disclosures, with no merchant earning link. All snapshots are clearly labelled **UNSENT**. `preview_audit.cjs` provides zero-network, source-level fail-closed checks; run `node dispatch/r206/preview_audit.cjs` from the repository root.

Original master was independently checked this sprint: 8/8 Git blob IDs matched available local copy, native Python suite 6/6 PASSED. Separate locally generated offline HTML/TXT specimens were checked with 5/5 native Node test groups after correcting a test-only wording expectation. **Committed files are a separate generator output and are not claimed byte-identical to that local specimen.** No real Jetpack email, browser/email-client or functional unsubscribe test has been conducted.

## Exact issue-to-conversion evaluation
- **01 editorial**: historical perception → Puységur article; repeats 02's destination.
- **02 editorial**: Puységur primary-source critique → same published Puységur article; date/source nuance needs a copy review.
- **03 commercial-review**: optional Zen12 → unapproved, NOT LIVE Mind guide; **HOLD_MERCHANT**.
- **04 editorial**: NASA Apollo 1 investigation → existing article; NASA's original fire review board shows multifactor conditions, ignition initiation not conclusively identified.
- **05 commercial-review**: optional Hypnosis Live Total Focus → unapproved, NOT LIVE Mind guide; **HOLD_MERCHANT**; seller describes 33 min/47MB and a 14-day refund, but FAQ restricts refunds to five sessions/year.
- **06 editorial**: Focus Fieldbook → **/focus/ signup** even though recipient already subscribed; R205 alternative points to a relevant published investigation, but founder has NOT approved substitution.

Research: [NASA report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/); [Zen12 exact sales page](https://zen12.com/hnp) (seller describes 12 levels, 48 MP3, claims 12-minute meditation equivalence without product-specific independent proof); [Total Focus exact sales page](https://hypnosislive.com/mental-skills/total-focus); [its FAQ](https://hypnosislive.com/faq) (5 refunded sessions/year); [generic Inspire3 affiliate portal](https://affiliates.inspire3.com/) **does not establish Final Vestige acceptance or EMAIL-promotion permission**. Prices, checkout/refund performance, authorization, earning links and audio efficacy remain unverified.

## Live read-only subscription evidence, 2026-11-08 09:36 UTC
Jetpack newsletter `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=full`. The welcome includes the configured 52-page Fieldbook PDF URL. Subscriber counters total=3, confirmed=3, unconfirmed=2 are **not additive**. Jetpack follower breakdown separately WP.com=3, email-only=0. **Actual provider-filtered eligible `Email subscription=Subscribed` count UNKNOWN**. Five recent posts marked `never_sent_opted_out`, not campaign sends. No final welcome RECEIPT or actual email rendered HTML/plain/legal-footer proof. WordPress documentation: https://wordpress.com/support/subscribers/ . Logged-in WP.com subscribers may bypass a separate click-to-confirm, but require provider-confirmed subscription eligibility: https://wordpress.com/support/newsletter-settings/ .

/dispatch/ REST response presents a subscription self-link fallback; this is **NOT proof live hydrated form fails**. /focus/ public display of a PDF is not a `confirmed_signup`. The public Focus troubleshooting text suggests 'sign up again' when an in-app browser cannot open PDF; **propose** Claude revise to 'open the same link in Safari or Chrome' to avoid unnecessary repeat requests, without asserting duplicate subscribers.

## Subscriber → paid customer, one-off provisional journey
For creator source asset `asset_id` use the existing Grok TASK-008 `utm_source=<platform>&utm_medium=organic_social&utm_campaign=<topic>_pilot_2026_11&utm_content=<asset_id>`; then topic-matched /focus/ → provider-confirmed email subscription → actual Fieldbook welcome → evidence-based editorial → vetted live Zen12 guide **only if expressly authorized** → account-issued merchant URL → independently reconciled paid transaction net of refunds/fees. For proposed *newsletter CTA* only, design `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_0N_<slug>`; do not deploy links until approvals. **confirmed_signup** must be a single deduplicated provider-verified opt-in, not browser-success/download/Reader follow, with opaque identifiers private and no subscriber addresses on GitHub. Count independently paid settled orders, not clicks. 7-/30-day realized net revenue per 1,000 qualified human sessions **NOT COMPUTABLE** while revenue numerator and denominator absent.

## OFFER → FUNNEL → BLOCKER → CHANGE/TEST → OWNER
1. **Zen12 → vetted guide/purchase → named Inspire3 acceptance, EMAIL rights, issued affiliate URL, live approved guide absent → obtain account-verified proofs privately → HOLD / Mind #171**.
2. **Fieldbook → confirmed lead/welcome → provider eligible aggregate and genuine delivered welcome absent → read-only consent-safe reconciliation/authorized evidence → UNKNOWN / Claude Focus #129 + Dispatch**.
3. **Dispatch → commercial email → Final Vestige physical postal address, actual Jetpack HTML/plain rendering and functioning unsubscribe not proven → native editor preview plus consented received-message evidence/opt-out QA → HOLD / Dispatch/Site QA**.
4. **Creator source → net paid order → verified settlement/refund/fees and qualified-human denominator absent → privacy-safe independent reconciliation for 7/30-day cohort → NOT COMPUTABLE / Commerce/Praxxis #820**.
5. **Issue 06 → useful deep dive → redundant /focus/ CTA → consider R205 editorial option, keep canonical untouched → DRAFT REVIEW / Dispatch**.

FTC source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . Publisher address cannot be replaced by Automattic or merchant address. **All six HOLD_UNSENT; 03/05 additionally HOLD_MERCHANT.** No sending, test mail, subscriber contact/import, WordPress edit, promotion, publisher setting change, money spent, sales claimed, or live analytics.
