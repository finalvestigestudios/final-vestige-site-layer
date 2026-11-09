# Dispatch R229 — email eligibility is NOT the subscriber counter
**Scope:** Independent, unsent, source-controlled review supplement to PR #175, readiness PR #201 and prior Dispatch PR #1711. Owning issue #174; Mind #171; Focus #129; conversion coordination #820. Homepage PR #49 untouched.

## Real connected-site evidence, observed 2026-11-09 10:03 UTC
Authenticated WordPress.com site 256784396: newsletter subscriptions=true, site_can_send=true, automatic new-post emails=false, content_format=full, from_name="Final Vestige Studios", reply_to=no-reply, configured welcome still includes 52-page Focus Fieldbook PDF. Five recent posts explicitly have status `never_sent_opted_out`, not delivered. This proves **neither** consent for a new campaign **nor** actual inbox delivery.

Jetpack status reported total=3, confirmed=3, unconfirmed=2, suppressed=0, paid=0; follower stats separately reported WP.com followers=3 and email-only followers=0 (partial=false). These are **overlapping, nonadditive categories**. Email-only=0 does NOT mean zero valid recipients: WordPress.com now provisions WordPress.com accounts for email subscribers, and per-subscriber email status controls eligibility. Two unconfirmed requests are not two additional confirmed leads. Actual receiving-email audience, source attribution and welcome receipt are UNKNOWN. We have not opened or exported any subscriber roster.

WordPress official definitions (reviewed 2026-11-04): https://wordpress.com/support/subscribers/ . Jetpack subscriber account change: https://jetpack.com/support/newsletter/ . Email sending / preview mechanics (reviewed 2026-10-19): https://wordpress.com/support/newsletter/send-newsletter-emails/ .

## Read-only route and source custody
- /dispatch/ WordPress page 523, published; /focus/ page 1579, published; Editorial Standards page 17, published; PDF media ID 1737, 599946 bytes and configured welcome URL match.
- Both WordPress page-content API responses contain a self-referential *Subscribe* anchor but NO HTML form in the returned content. **This is NOT evidence the live form is broken**: the public /focus/ fetched today independently exposes an email field, and WordPress can render dynamic blocks differently in page content API and visitor HTML. An actual signed-out browser DOM/form screenshot plus **authorized** provider status test would be necessary for a live functional conclusion. Do not relabel API fallback as a failed conversion.
- Authenticated /focus/ content still says "sign up again" in in-app browser help. This is an observed repeat-attempt friction; PR #1711 proposes a surgical fix. Do not duplicate or publish its code here.
- /dispatch/ visibly describes a first-time subscription and sends readers to /focus/ for preview; it is not an appropriate replacement CTA for a confirmed subscriber.
- Editorial Standards require original-source verification, dated corrections for material factual changes, and disclosure without commercial control of conclusions: https://finalvestige.com/editorial-standards/.

## What the new native guard actually does
`eligibility_guard.py` is offline only and receives provider/partner observations as input. It refuses to infer mail-ready recipients from follower counts; recognizes only explicitly authenticated, opted-in and deduplicated provider transitions for **structural event validation**, rejects PII in events, and returns NOT COMPUTABLE for the revenue KPI without reconciled paid settlements and qualified sessions. Synthetic event acceptance is NOT real-world provider authentication; the caller must supply proof and keep private identifiers out of GitHub. It permanently declines auto-sending even when given all-true fake attestations. All commercial editions #03/#05 retain their merchant-specific hold.

## Executed QA and limitations
- Python 3.13 native offline: `python -I -m unittest discover -s dispatch/r229/tests -v` — 27/27 passed against byte-identical Python source and tests later checked via Git blob IDs. No HTTP/network in module; no subscribers, send APIs or PII.
- The old PR #175 six-test source was fetched at exact SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Its six original logical assertions were independently reproduced against the exact current stacked campaign SHA `ed38970572ce17f0f40b30dafbdc91e809daf5ba`: 6/6 pass in V8. **Original Python test suite NOT natively executed on a complete checkout**. Do not advertise six native passes.
- No native Jetpack email preview or received message, exact publisher postal-address footer, unsubscribe action, merchant account receipt or checkout was tested.
- No genuine qualified-human sessions, confirmed leads with source linkage or paid orders were provided. Never use synthetic values as analytics.

## Release status
**ALL SIX: HOLD_UNSENT. #03 and #05: HOLD_MERCHANT.**
No WordPress write, email, test-email, schedule, list import/export, subscriber edit, paid product activation, Grok post, tracking script, checkout or spend. Founder retains specific release approval.
