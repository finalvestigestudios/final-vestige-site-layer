# Dispatch R40 — Native WordPress post-field evidence bridge
**1 November 2026, authenticated observation 10:38 UTC** · [Campaign #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) · [Mind handoff #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) · [original six manuscripts PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) · [per-edition gates PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) · [direct parent R39 PR #429](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/429)

> **REVIEW / HARD HOLD.** These files cannot publish, schedule, email, preview in WordPress, obtain recipient data, operate affiliate links, or assert a compliant actual message. No post, draft, email/test-email, subscriber, site setting, merchant, or tracking action occurred.

## Material advance: field-level alignment is a fourth surface

Prior work established that the authored long letter, a standalone HTML rendering, and the *native Jetpack email* are not interchangeable. R40 formalizes a fourth surface: the fields an actual WordPress **post** would need—title, body, **explicit custom excerpt**, post state, and the **per-post** notification switch.

The new offline Python checker aligns those fields with the six *current* canonical manuscripts and the optional R30 excerpt ledger. It specifically rejects:
- Missing/changed **custom excerpt**, changed native subject/title, wrong post type, any post not explicitly in `draft`, a missing or true post-level send toggle, or a scheduled state.
- A careless copy/paste of Markdown draft metadata, hard-stop warnings or legal placeholders into a would-be reader-visible post.
- Direct seller or tracking links in body text, including merchant URLs presented as 'citations' that would still bypass the independent buyer guide.
- Apparent or claimed merchant approval, actual subscriber consent, postal footer, and inbox proof inferred from a `draft` or successfully rendered offline page.

A synthetic field-alignment PASS means **only** that a *redacted admin-field snapshot* matches the checked excerpt/title/body constraints. The function still reports **HOLD_UNSENT**, footer UNVERIFIED, inbox UNVERIFIED and audience UNKNOWN. Neither real WordPress editing nor email sending is within this code's capabilities.

### Live source-of-truth, checked November 1, 2026

WordPress authenticated site ID 256784396, 10:38 UTC:
- Newsletter `subscriptions=true`; platform can technically send, but **new-post auto email disabled**; `recent_sends=[]`; default `email_content_format=excerpt`.
- Sender display **Final Vestige**; reply-to **no-reply**; email sender domain is controlled by WordPress, not a verified custom FV sender.
- **Featured images included at top of email** and **post dates shown**. These visual elements may displace the disclosure or story opening on small screens; they require a real native preview and delivered-email check.
- **Newsletter categories disabled.** Do not assume placing a post in a special category controls distribution or limits subscribers.
- Subscriber counters return **total=2, confirmed=2, unconfirmed=2** (zero suppressed and zero new imports), with no exposure of individual addresses. These are not additive; **unique consenting and reachable email audience is unresolved**.
- Existing welcome copy includes the 52-page *Seven Day Focus Fieldbook* link; no independently verified successful welcome receipt. An October 25 subscription-confirmation email is not the delivered welcome.

Authenticated published pages: [/dispatch/](https://finalvestige.com/dispatch/) (523), [/focus/](https://finalvestige.com/focus/) (1579), [Editorial Standards](https://finalvestige.com/editorial-standards/) (17). Editorial Standards requires checking primary records, preserving uncertainty and clearly separating financial relationships from conclusions.

### What official Jetpack documentation establishes, and does **not** establish

[WordPress newsletter settings](https://wordpress.com/support/newsletter-settings/) (reviewed Oct 26, 2026): excerpt mode uses a specific post excerpt when supplied, or roughly the opening 55 words otherwise; featured images and dates are configurable. [WordPress email delivery](https://wordpress.com/support/newsletter/send-newsletter-emails/) (reviewed Oct 19, 2026): **post TITLE is native email subject; only posts** trigger native newsletter emails, not a standalone HTML file or WordPress page. Subscriber digest preferences may delay individual delivery. [WordPress email appearance](https://wordpress.com/support/newsletter/email-appearance/): native **Preview email** and **Send test email** are different actions, and exposing the preview controls can require temporarily turning on the **per-post** send toggle in an **unpublished** draft. No control over a separate preheader field is verified.

**Operational hazard:** `email_new_posts_by_default=false` is only the default. A manually enabled per-post send switch may still send when someone publishes. A preview workflow cannot be inferred to be harmless if its toggle is left on. No one may turn it on or create/edit/publish/schedule a WordPress post under this Dispatch task without separately documented approval. R40 records no preview or test receipt as complete.

### Six edition-specific decisions

| Issue | Current native proposed subject | CTA destination | R40 status |
|:--|:--|:--|:--|
| 01 | The mind is not a camera | Published The Missing Caption investigation | **HOLD_UNSENT** |
| 02 | Before hypnosis had a name | Published Puységur historical files | **HOLD_UNSENT** |
| 03 | The twelve-minute meditation question | Zen12 warm-up **UNPUBLISHED**; product email authorization absent | **HOLD_UNSENT + HOLD_MERCHANT** |
| 04 | Seventeen seconds. A much longer explanation. | Published Apollo 1 investigation | **HOLD_UNSENT** |
| 05 | Before you press play on a hypnosis audio | Total Focus warm-up **UNPUBLISHED**; authorization absent | **HOLD_UNSENT + HOLD_MERCHANT** |
| 06 | What did seven days of attention reveal? | Published free Focus Fieldbook | **HOLD_UNSENT** |

**Potentially valuable reviewed alternatives are still NOT selected.** R37 corrected the seller-route bypass in 03; R38 provided a single-action 05 candidate; R35 improved 06 diary-sensor precision. Original 4:2 composition remains authoritative pending founder approval of any substitution. No R40 production/post candidate silently replaces them.

### Exact merchant alignment and current uncertainty

The official [Zen12 HNP page](https://zen12.com/hnp) advertises twelve-minute recordings, Premium's twelve/48 MP3 and Beginner/Advanced's six/24 tiers, with hour-equivalence and brainwave claims. Package descriptions are seller-reported specifications, **not independent proof of outcomes**. Official [Total Focus](https://hypnosislive.com/mental-skills/total-focus) describes a 33-minute, 47 MB audio; seller marketing claims of improved concentration/brain reprogramming are **not independently validated for that recording**. The public Total Focus URL shows **different price snapshots across crawls / pages** (e.g., $2 promotional versus alternate non-checkout visible offers). No actual checkout, location-specific offer, recurring status or refund eligibility was independently tested; do **not** include a price, savings, refund guarantee or efficacy claim in launch copy.

[Inspire3's Limitless Labs promotion page](https://inspire3.com/ll/) offers list-mail swipe material **for that distinct product** and explicitly requires affiliate approval. That is *not* evidence Final Vestige is approved to promote Zen12 or Total Focus by email, use a merchant creative, or construct a click-tracked URL. Companion Mind Studio's Zen12 buyer guide in [draft PR #439](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/439) remains **UNPUBLISHED**, with zero live seller links and no verified permission. Do not route a reader to checkout via apparently harmless research citations.

### How to obtain real evidence safely **only after separate permission**

1. **Owner** privately reviews the actual subscribed/confirmed/notification-eligible counts in WordPress (do not export addresses); confirms deliverability and whether digest frequency changes immediate delivery. Store only aggregate non-PII evidence.
2. **Owner** establishes a valid Final Vestige postal address and a functioning, clear unsubscribe route. The Automattic postal address in a transactional subscription confirmation does **not** identify Final Vestige. FTC guidance: [CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) and [endorsement disclosures](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking). Be conservative across all six, not only the two affiliate editions; primary-purpose classification depends on the actual message.
3. **Founder** separately authorizes any WordPress **draft creation and native visual-only preview**. Start from a clean post with title matching manifest and an **explicit per-post excerpt** from the optional reviewed excerpt copy (not raw Markdown banner or legal placeholder), with publishing and notifications *disabled*. Where the editor requires temporary per-post email toggle ON to expose preview, request and document separate approval; **never publish**, never send a test email, and verify OFF after inspection. Record an evidence artifact of actual **Preview email** (desktop/mobile), without subscriber details.
4. A received test email is a **distinct permission** from visual preview. Only with separately authorized non-list test recipient and test-send permission, use existing [R33 offline EML verification](../) on a privately provided, redacted email. Verify exact sender, actual subject/preheader behavior, commercial wording, published CTA path, final business address, and real unsubscribe endpoint/behavior (do not click personal tokens in shared logs).
5. Product-specific merchant approval, email-channel rights, first-party published guide, authorized SKU earning link, documented current final checkout/refund terms and founder commercial copy signoff must be present for each of **03/05**. The public affiliate catalog is not authorization.
6. **Final founder release approval** of exact six issues, recipients and weekly cadence is a separate event. Engineering PASS or WordPress's `site_can_send=true` is NOT approval.

No affiliate earning links, post-ID-specific audience identifiers, email addresses, synthetic conversion rates or experiment claims should be logged into GitHub. With two displayed confirmed subscribers there is no justified statistical A/B finding; use first-party site destination views or *aggregate* clicks only if later approved and measurable, and describe small-n results as descriptive.

### Code and QA

`python dispatch/campaign-2026-mind/r40-native-post-proof/native_post_field_gate.py --json` prints six **review packets** from canonical source/manifests: exact subject/title, proposed excerpt, current CTA, hard holds, CMS field requirements and explicit uncertainties. It does **not** generate a WordPress publishing payload. `audit_manual_post_snapshot(packet, snapshot)` accepts a *redacted* field snapshot from a **separately authorized** actual WP draft (or synthetic test), checks for drift and unsafe seller routes, and returns HOLD_UNSENT even on a clean field match. The unit suite uses safe synthetic fixtures; tests do not touch WordPress or real mail.

`python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_*.py'` runs the existing campaign regression suite plus these R40 tests on an actual checked-out GitHub head. Host CI execution evidence must be read from that PR's GitHub Actions run; no result is asserted here before it exists.

**No changes** to canonical six manuscripts, prior optional alternatives, `/dispatch/`, `/focus/`, site Editorial Standards, Jetpack settings/list/welcome, PR #49, or Mind Studio pages. This is isolated new read-only instrumentation.