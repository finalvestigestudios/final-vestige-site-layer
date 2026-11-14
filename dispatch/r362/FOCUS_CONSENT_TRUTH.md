# Focus PDF visibility is not proof of an opted-in subscriber

## Independently checked November 14, 2026

1. [Live Focus](https://finalvestige.com/focus/) rendered an email field, **Send me the fieldbook** button, a separately visible **Download the Seven Day Focus Fieldbook** link, and text **Please confirm your email to join The Dispatch. The welcome email will include this same download link.** The page also informs readers that subscribing joins The Dispatch and that future emails may contain commission-bearing recommendations.
2. [Live Dispatch](https://finalvestige.com/dispatch/) renders an email field, Subscribe button, and a promise that the welcome email includes the complete 52-page workbook.
3. Jetpack authenticated settings: newsletter enabled; new-post auto emails **OFF**; email format **full**; sender name **Final Vestige Studios**; reply-to **no-reply**; welcome configured with the exact media PDF URL. Newsletter can technically send, but **no evidence of eligible inboxes** is supplied.
4. Jetpack status as of November 14 20:39 UTC: total 3, confirmed 3, unconfirmed 2, suppressed 0. WordPress Stats: WordPress.com followers 3, direct-email followers 0. These counts refer to different/overlapping surfaces; **do not add or subtract them to infer reachable people**. Last five sampled posts were `never_sent_opted_out`.
5. Authenticated media inventory previously found PDF attachment ID 1737, MIME `application/pdf`, size 599,946 bytes. A separate guest HTTP PDF fetch was unsuccessful (**cache miss**), so availability to a new anonymous visitor remains **UNKNOWN**, not FAIL.
6. No received Fieldbook welcome, completed double opt-in or working unsubscribed-email footer was produced in the current read-only inspection.

## The conversion-accounting correction

The funnel is **landing view → optional PDF click/download → signup attempt → provider-confirmed consent → received welcome + working PDF → future email CTA → independent merchant paid settlement**. It is not a mandatory linear path: users may click the free PDF without joining, and users may subscribe without downloading. A PDF click, direct download, signup attempt, page impression, newsletter follower count, or email click must never be entered as `confirmed_signup`. A confirmation request email does not establish confirmation completion.

**One `confirmed_signup` event** should be emitted by Claude's existing first-party analytics integration *only after* provider-backed confirmation. Deduplicate using a privacy-preserving provider receipt reference, not raw email, and retain consent scope and confirmed-at timestamp in the private provider system. The R362 offline classifier only recognizes provider-labelled *candidates*, not authenticated confirmations; Claude must verify provenance.

For Grok-origin visits, retain `utm_source=<actual_social_platform>`, `utm_medium=organic_social`, `utm_campaign=<topic_cluster>_pilot_2026_11`, `utm_content=<unique_asset_id>`. Preserve a durable first-touch attribution where available, while documenting session gaps, blocked cookie consent, profile-link indirection and other missing attribution honestly. The newsletter campaign, if approved, uses `utm_medium=email` and a separate edition code. Never modify the existing TASK-008 links or deploy duplicate measurement tags here.

## Two independent acceptance paths

**No-send path (currently authorized):** audit page/block presence, WP media metadata, exact welcome content and disabled auto-send; open the WordPress editor's **Preview email** without clicking **Send test email** if an authorized interactive editor session is available. Inspect sender identity, brand, mobile layout and visible placeholder-free footer *as a preview only*. Report what can and cannot be evaluated.

**Owner-authorized verification path (not authorized now):** use only a separately permitted owner-owned test account/address; document provider confirmation, actual received welcome RFC822, accessible PDF, complete body and footer, working unsubscribe, with timestamps and private redaction. A test send or subscription change requires explicit founder approval. Never use a public subscriber's address or forward an unredacted message into GitHub.

## Go/no-go

Without proof of provider confirmation and received welcome, classify the subscriber-to-lead step **UNVERIFIED**; without independently settled conversion evidence and qualified-human sessions, classify `net_revenue_per_1000_qualified_human_sessions` **NOT COMPUTABLE**. No inferred zero sales and no fabricated A/B lifts.
