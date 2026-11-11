# Dispatch R269: Six original-manuscript previews and Focus consent boundary (UNSENT)

Canonical [campaign PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) source HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`; [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); merchant ownership [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). This R269 branch is stacked from Dispatch R268 [PR #1973](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1973) at `aa019626ebe3b380616471c8fe27276ca186369c`.

## Source-faithful review delivery

The `previews/` folder contains **six full 600px table/inline-styled static HTML emails and six matching plaintext editions**, derived from the six founder-approved manuscript bodies. These are non-sending offline specimens, **not native Jetpack email previews**. The original subjects, preheaders, body text, free first-party article/Fieldbook links, qualified affiliate disclosures and blocked commercial guide tokens are preserved. Each HTML has one H1, explicit hold banners, readable semantic text, no scripts, no forms, no images/tracking pixels and no live merchant earning URL. Legal postal/unsubscribe placeholders remain visibly blocked. Read-only source checks were run against all six original GitHub manuscripts and all generated outputs; this is not a received email-client rendering result.

## New high-impact analytics / consent finding

Authenticated WordPress `/focus/` page ID 1579, last modified `2026-11-05T17:44:02`, contains the `fvf-gift-v2` script. The logic reads `URLSearchParams(window.location.search).get('subscribe')` and shows the gift when the value is truthy but not one of `invalid_email, error, blocked_email, opted_out, blocked`. Therefore even arbitrary `?subscribe=anything` qualifies for **client-side gift display**. The script may separately reveal the gift when a subscriptions element has the `is-subscriber` class.

This is not necessarily a download-access defect: the PDF is intentionally offered free. Crucially, gift visibility, success redirects, URL queries, button clicks, download events and CSS classes **are not evidence of double opt-in or a provider-confirmed lead**. No evidence suggests the live measurement system currently misclassifies these states. `confirmed_signup` must be derived only from authenticated provider accepted/subscribed confirmation, deduplicated by stable provider event ID, without exposing email addresses. Claude/Focus Issue #129 owns any future engineering; no instrumentation is installed in this PR.

## Seller and legal evidence

- Zen12 [actual seller offer](https://zen12.com/hnp): Premium advertises 48 MP3 files and 12-minute recordings; alleged one-hour-equivalence, automatic brainwave effect, benefits and refund terms are **seller assertions**, not independently verified product-specific outcomes or an authorized FV checkout.
- Zen12 [free audio signup](https://zen12.com/freeaudio): expressly introduces **the merchant's own newsletter**, separate from Dispatch consent.
- Hypnosis Live Total Focus: exact checkout price, refund conditions (including seller FAQ's annual-session qualification), final approved partner creative/URL and email permission remain **unverified**.
- [FTC CAN-SPAM compliance guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business): sender identification, honest subject, valid physical mailing address, effective unsubscribe and honoring opt-outs must be verified in **received** emails before release. The Automattic address in a Jetpack confirmation email is not verified FV publisher address.
- Primary source relevant to Issue 04: [NASA Apollo 204 report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). Primary bibliographic check for Issue 02: [NLM Puységur catalog](https://www.ncbi.nlm.nih.gov/nlmcatalog/440836).
- Latest authenticated Jetpack diagnostics 2026-11-11 01:34 UTC: total=3, confirmed counter=3, unconfirmed requests=2, suppressed=0; nonadditive. Actual provider-filtered `Email subscription → Subscribed` audience unknown. Newsletter ON, new-post auto-send OFF, full format, Focus welcome configured but **delivery not verified**. The PDF/welcome link is configured but successful actual document retrieval and final welcome receipt have not been established.

## OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| Offer | Step | Blocker | Safe next experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Zen12 | Evaluated guide → paid purchase | No account-specific affiliate approval, permission for email, vetted guide URL or issued earning URL | Privately verify authorization/checkout and guide with merchant-approved resources | HOLD_MERCHANT | Mind #171 |
| Fieldbook | Gift visibility → confirmed lead | Frontend indicator cannot establish consent; subscriber eligibility unknown | Provider-only deduplicated confirmation and aggregate email eligibility | NOT VERIFIED | Focus #129 / Claude |
| Dispatch | Preview → received email | Native Jetpack render, FV address and live unsubscribe unverified | Separately approved, isolated native-preview/received-email QA | STATIC-ONLY | Dispatch #174 / Site QA |
| Grok asset | Qualified session → verified lead | Source-level tags and identity join missing | Validate TASK-008 canonical UTMs and immutable asset IDs without a new script | UNKNOWN | Grok / Praxxis #820 |
| Affiliate | Paid sale → net revenue | No verified orders, paid commissions, fees/refunds | Reconcile merchant settlement data | NOT COMPUTABLE | Commerce #820 |

**Release:** All six originals HOLD_UNSENT. Issue 03/05 HOLD_MERCHANT. All alternatives NOT_ADOPTED. No WordPress writes, emails/test sends, subscriber contact/import, affiliate activation, new analytics script, social content or spend. Homepage PR #49 untouched. No fake A/B metrics or implied sales.
