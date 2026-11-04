# Dispatch R110 — native subscription-state correctness and revenue-proof contract

**2026-11-04 | Dispatch Issue #174 | Focus Issue #129 | Mind Issue #171 | conversion Issue #820 | Business #818**

**Status: BUILT + NATIVE NODE TESTED; NOT LIVE; NO MESSAGES SENT; NO APPROVAL TO SEND.**
Stacked on R109 draft #914 and original pilot #175. This folder is additive and **does not change** the six historical manuscripts, 4-editorial/2-commercial allocation, signup pages, existing list, WordPress settings, or frozen homepage #49. R109 reviewed native blocks; R108 created a no-send .eml inspector; R106 proposed a confirmed_signup metric. **This sprint repairs a logical edge case in that metric without replacing R106's production instrumentation.**

## A material correction to the R106 measurement rule

The prior proposal treated an unconfirmed→confirmed transition as essential. WordPress's **official Newsletter Settings documentation (last reviewed 2026-10-26)** explicitly says that when a subscriber already has a WordPress.com account, the confirmation email **is skipped** and the welcome email may arrive immediately. Those users should not be erroneously lost from the funnel. Conversely, the separate **Reader-only** WordPress follower is not proof of email-reachable consent.

Native routes requiring separate proof:

| Route | Prior status | Native evidence required | What counts |
|---|---|---|---|
| Email address / not already verified | not_confirmed | clicked confirmation + native Subscribed status + site consent | one confirmed_signup |
| Existing verified WordPress account | none | native verified-account subscription event + native Subscribed email status + explicit site consent | one confirmed_signup, **no confirmation click required** |
| WordPress Reader follow only | any | Not subscribed to email | **not** an email confirmed_signup |
| Bounced / paused / not sending / unconfirmed | any | ineligible email status | **not** currently eligible; no release proof |
| Imported / administrator-created record | any | not an independent new opt-in | do not create a confirmed_signup event |
| Existing subscribed account repeats click | subscribed | no new opt-in transition | deduplicate, do not manufacture growth |

A WordPress account being **preverified for identity** does **not** mean an individual necessarily consented to FV's email marketing. The implementation still requires explicit site-newsletter opt-in and native email subscription evidence. This implementation is a spec for authorized future source-of-truth integration, not an instruction to scrape identities or send messages.

## Implementation and verification

`confirmed_signup.mjs` is an offline pure function with **no network, mailbox, WordPress account mutation, subscriber export, local storage, analytics emission, tracking pixel, login cookie, external SDK, or emailing code**. It accepts synthetic records that express native confirmations. `test_confirmed_signup.mjs` contains **38 native Node tests** exercising both valid confirmation paths, deduplication, human-source attribution, unknown/unsupported WordPress statuses, suppressions, illegal PII-shaped identifiers and incorrectly inferred sales.

Run at repository root:
```
node --test dispatch/campaign-2026-mind/r110-confirmed-signup/test_confirmed_signup.mjs
```

**Independent offline proof**: native Node 22 executed 38/38 tests PASS. Locally tested source file Git blob SHA `7b54ed6013bcff1c8a22ad63a65c5cfd1adf73d0` and test file blob SHA `5756387bff234e9bfd50ca31498effe9741e21c0`; both **match the exact blobs independently re-fetched from the GitHub branch**, rather than a synthetic V8 adaptation. This is not hosted CI, real browser, consent-field accuracy, received-email proof, or merchant transaction proof.

## Privacy, attribution and event semantics

`confirmed_signup` represents **one newly confirmed email subscription with explicit site consent**, not button clicks, Fieldbook PDF clicks, WordPress.com Reader follows or configured welcome text. It should emit only when the authoritative native Jetpack status and event provenance are available; because the connected site APIs presently reveal only aggregate counts, **do not deploy or infer this event**. The offline function requires a privacy-preserving opaque `h:` 64-hex digest with a *separately governed secret HMAC*, not a raw email or a plain unhashed address (plain SHA hashing of emails is vulnerable to dictionary attacks). The code validates the identifier format, not that a secure HMAC was used: that must be attested separately. Synthetic keys and event_ref values must not be published in an analytics event.

Attribution is optional and must be **null** if the verified native subscription cannot be joined to a first-party qualified-human landing. Only already-approved `/focus/` or `/dispatch/` routes, allowed `utm_source` values, `utm_medium=organic_social`, `utm_campaign=<cluster>_pilot_YYYY_MM`, and a sanitized Grok `utm_content=asset_id` can be associated. Never infer source from a traffic spike, platform views, or WordPress visitor totals. Real Grok asset IDs remain to be supplied by TASK-008; no source attribution is live. The offline aggregate function intentionally returns **null** for reachable-subscriber count, paid orders and net revenue: counting signups is not a revenue report.

## Read-only WordPress snapshot — 2026-11-04 09:33 UTC

Connected newsletter settings: `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `reply_to=no-reply`, sender display "Final Vestige". The 52-page Focus Fieldbook PDF URL is present in the configured welcome message; **received welcome, live PDF retrieval, and subscriber click are not verified**.

Connected subscriber status: `total=2`, `confirmed=2`, `unconfirmed=2`, `suppressed=0`. Separate follower evidence previously showed two WordPress.com followers and zero email followers; **do not add these numbers or call two people reachable**. WordPress [official subscriber documentation](https://wordpress.com/support/subscribers/) states unconfirmed subscriptions are excluded from total. A private aggregate count of native `Email subscription: Subscribed / Not subscribed / Not confirmed / Bounced / Emails paused / Not sending` is still required to resolve the **email-reachable** denominator. No subscriber addresses should be copied into source control or public issue comments. Five recent posts have `never_sent_opted_out` and `dispatched_at=null`, not successful email delivery.

Published WordPress `/focus/` page #1579 and `/dispatch/` page #523 each have one native Subscribe block. The read-only REST-rendered fallback link is **not proof** a real browser form functions. Focus discloses potential commission-earning recommendations; Dispatch currently lacks equally specific signup-context disclosure. Remediation was proposed in R109 but is not approved/published. Fieldbook direct download requires no subscription, and must not be counted as a lead.

## Native Jetpack delivery caveats (documented, not observed)

Official WordPress [newsletter settings](https://wordpress.com/support/newsletter-settings/) says uncustomized excerpt emails generally contain ~55 initial post words. With `email_content_format=excerpt`, polished long manuscripts and their later disclosures/CTA should **not be presumed to arrive in the inbox**. The official [email appearance/preview guide](https://wordpress.com/support/newsletter/email-appearance/) explains how to preview desktop/tablet/mobile from the editor and offers a separate **Send test email** action. **A preview window is not evidence that a real message was received, its List-Unsubscribe mechanism works, or a publisher mailing address is present**. Neither preview nor test sends are initiated here; no one should toggle a send option or create a test subscriber absent the founder's separate express authorization.

## Commercial holds and factual claim controls

Issue 03 remains a Zen12 research/offer-guide placeholder; Issue 05 remains a specific Hypnosis Live Total Focus offer-guide placeholder. Mind Studio draft #916 provides one candidate Zen12 guide and separate fail-closed revenue math, **not a verified live authorized earning destination**. The official [Zen12 sales page](https://zen12.com/hnp) is the current SKU to check; its 12-minutes=hour claim is a **seller claim**, not an independent product-specific clinical outcome. [Total Focus](https://hypnosislive.com/mental-skills/total-focus) seller listing describes a 33-minute/47 MB MP3 and unsupported promises of focus improvement. The full current SKU price, refund details and checkout conditions can change; require an exact fresh seller snapshot before any recommendation. Existing seller privacy policy may permit identifying purchaser data shared with affiliates; Final Vestige must secure buyer-privacy/reporting protections before promotion.

**All six: HOLD_UNSENT. Issues 03 + 05: HOLD_MERCHANT.** Do not activate links or convert vendor assertions into verified benefits. Verify exact FV-specific affiliate approval, approved email channel, current official creatives, earning URL, privacy terms, live warm-up landing destinations and merchant order reports. Choose one real paid offer first; do not create another email list, paid tool, automated sends, or a second analytics script.

## Release and financial controls

FTC [CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful commercial email headers/subject, a valid publisher postal address, conspicuous promotion where applicable, a functioning opt-out that remains available and honoring opt-outs within 10 business days. The address used in an Automattic confirmation email is **not** evidence of a qualifying Final Vestige Studios business address. No actual received Jetpack email, functional unsubscribe/suppression test or valid FV postal address has been verified. **Never fill missing address with a fake one.**

For real conversion, require merchant-signed order/commission, verified fulfillment, refunds and fees and attributable first-party qualified human sessions; 7- and 30-day cohorts with tiny-sample warnings. No paid order or measured net revenue is documented here; `net_revenue_per_1000` remains **N/A**, not 0.

**Owner handoff:**
- **Dispatch/Focus**: native consent and confirmation proof, two-path event implementation spec, privacy-safe aggregate status audit, R108 received-email inspector only on an already-authorized message.
- **Claude/Site QA**: stage page-rendering, CTA destination, consent parity, frontend transport and no-duplicate-tracking verification. Never touch frozen #49.
- **Mind & Affiliate**: obtain current merchant approval and email permissions, one canonical eligible offer and independently reviewed live guide; no live affiliate CTA before approval.
- **Grok/Praxxis**: maintain TASK-008 ownership of actual social asset IDs and handoff; Dispatch does not draft or publish social assets.
- **Founder**: final creative, live post/sending, postal business details, testing and offer decisions.

**Release gate remains CLOSED independent of local tests.**
