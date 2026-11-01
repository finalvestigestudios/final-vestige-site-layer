# Final Vestige Dispatch — R41: Evidence-first measurement and attribution

**STATUS: ALL SIX HOLD_UNSENT; ISSUES 03 / 05 ADDITIONALLY HOLD_MERCHANT.** No email, test email, WordPress post, new list, customer contact, tracking code, affiliate earning link, deployment, schedule or paid service is authorized here. This release is a **source-controlled offline measurement contract**, not a marketing campaign launch.

Sources: [Dispatch master issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); [Mind / affiliate owner #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); canonical six letters [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); independent release gates [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201); direct parent WordPress field truth [draft PR #441](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/441). Homepage flagship work and frozen PR #49 remain untouched.

## Newly surfaced measurement error: recent is not lifetime

The authenticated WordPress newsletter.status read **November 1, 2026 at 11:37 UTC** returned an **empty recent_sends array**. That proves only the absence of reported sends in this API's recent window. It does **not** establish that the site has *never* sent a notification, or allow a campaign-specific lifetime send count of zero. Earlier dashboards described this as "zero sends" without clearly stating that distinction. R41 corrects the record without changing the WordPress service.

The same read returned diagnostic counters **total=2, confirmed=2 and unconfirmed=2**, no recent subscriber imports and no suppressed count. These are non-additive diagnostics whose denominator and membership are not established. They must not become "four unique subscribers" or "two consented, reachable recipients." There are no recipient addresses, exported subscriber records, emails or personal identifiers in this development. Privately reconcile administrator subscriber records and count definitions before sending.

The current Jetpack newsletter is enabled; automatic new-post emails are **OFF**; delivery mode is **excerpt**; sender display is Final Vestige; featured image is included and post date shown; reply-to is no-reply. The 52-page Focus Fieldbook is configured in the welcome text, but the October 25 confirmation email is *not* proof that the welcome was received. Separate custom preheader control is unverified. This sprint made **no** WordPress changes.

## Real measurement depends on three different evidence sources

**Jetpack email:** When actual sends happen after final founder approval, the platform may provide send, open and email link-click statistics. Open measurements can be affected by automated privacy prefetch; do not label them a count of humans who actually read the story. Under excerpt mode, the default Read-more click sends readers to a WordPress **post**. It is not identical to the article's specific Final Vestige research CTA. WordPress documentation establishes that the *post title* becomes the newsletter subject, and that a custom excerpt can be used; it does not establish that an offline HTML preview equals actual email rendering.

**Final Vestige site:** First-party aggregate measurements could eventually distinguish guide page views, meaningful onsite CTA actions, and authorized outbound merchant clicks. No newsletter campaign UTM, pixel, cookie, affiliate redirect, new analytics endpoint, personal attribution token or per-subscriber tracking is deployed here. A post view cannot be claimed as evidence of a newsletter click without an approved, verified attribution method.

**Approved merchant account:** Only verified partner reporting, under actual allowed-product and channel permissions, can establish recognized purchases and net commission, after relevant refunds. Clicking an outbound offer link is not a purchase. Even a merchant-reported order cannot automatically be attributed to a specific Dispatch issue without an approved matching method. Neither public Inspire3 marketing copy nor the user's received consumer offers demonstrate Final Vestige's affiliate acceptance, rights to promote Zen12 or Total Focus by EMAIL, an authorized earning URL, or checkout/refund terms.

The free, published editorial CTA pages remain The Missing Caption (01), Puységur’s Animal Magnetism Files (02), Apollo 1 investigation (04), and the Focus Fieldbook (06). The two commercial guide URLs remain **unpublished/inactive**. Their product material is supported only as *merchant-described specifications* from [Zen12's actual product page](https://zen12.com/hnp) and [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus). Advertised brainwave/equivalence or sharp-concentration outcomes are **not proven for the named products** by generic meditation/hypnosis research. No unstable promo price or unverified guarantee is placed in outgoing material.

## Actual R41 deliverables and non-claims

- A reproducible, date-stamped, **no-PII WordPress evidence snapshot** preserving the anomalous 2/2/2 counts, the empty *recent* sends array, unknown lifetime sends and unknown consent eligibility.
- A **standalone Python offline measurement gate** that re-reads the *current* campaign manifest, fixes the 4:2 editorial/commercial identity, checks all six hold states and first-party destinations, and refuses to manufacture delivered messages, opens, clicks, sales or revenue.
- A typed **synthetic-only aggregate validation contract**. It detects wrong channel/metric combinations (for example merchant orders attributed to WordPress views), personally identifying fields, tokenized URLs, impossible counts, invalid timestamps, false "live" evidence and unsupported A/B uplift. A structurally valid example is still labelled **STRUCTURE_ONLY_SYNTHETIC_NOT_PLATFORM_PROOF**. No actual events are collected.
- A **conservative example-rate rule**: unknown denominators cannot produce percentages; denominators under 30 are suppressed; larger examples are explicitly **ILLUSTRATIVE_NOT_OBSERVED**. This is a communications guardrail, not a test of statistical significance.
- A local, accessible static [review board](REVIEW_BOARD.html), free of network assets, affiliate URLs, cookies and scripts. The board describes what is and is not established, without fabricated marketing KPIs.
- A dedicated Python adversarial test suite that is included in the repository-wide existing Python-test discovery. No campaign manuscripts or production assets were changed.

## Measurement and release procedure

To verify on an exact checked-out stacked source head, run:

    python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
    python -I dispatch/campaign-2026-mind/r41-measurement-truth/measurement_gate.py --json

Only report tests as passed after independent execution on the exact commit and inspection of CI logs. The JSON report is a **review/state report**, not observed engagement or sales. The supported future metric taxonomy is explicitly separated by source to avoid joining incompatible denominators.

**Actual readiness priorities, in order:** (1) Final Vestige-specific *product and email channel* affiliate acceptance, URL/tracking and terms in writing; (2) reviewed, approved, published Zen12 and Total Focus independent guide destinations; (3) a valid Final Vestige physical business postal address; (4) genuine received *Jetpack* email evidence of sender, honest subject, excerpt, postal address and functioning unsubscribe; (5) private deduplication and recipient-consent reconciliation; (6) final founder sign-off for particular copy, recipient audience, date/time, tests, publish and send.

A physical business mailing address may be a qualifying registered USPS PO Box or other FTC-permitted address, but **no address is known or inserted**. The October 25 Automattic-branded subscription confirmation address does not establish a valid Final Vestige address. Do not flip a WordPress post's per-post email toggle merely to access its preview controls without explicit authorization; a genuine native preview and a received test message are different pieces of evidence.

**Official documentation reviewed November 1, 2026:** [FTC CAN-SPAM compliance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [WordPress Newsletter Appearance](https://wordpress.com/support/newsletter/email-appearance/), [WordPress Newsletter Settings](https://wordpress.com/support/newsletter-settings/), [WordPress Send Newsletter](https://wordpress.com/support/newsletter/send-newsletter-emails/). This is conservative operational QA, not a legal opinion.

No trial email has been sent and no work was performed on frozen homepage PR #49. The founder's original six canonical letters and four-editorial/two-commercial allocation remain authoritative; optional R35/R37/R38 alternative copy remains unselected.
