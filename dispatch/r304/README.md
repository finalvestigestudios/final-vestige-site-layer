# Dispatch R304 — count semantics, actual reader eligibility, and six-issue conversion decisions (DRAFT / NO SEND)

**Snapshot:** 2026-11-12 12:30 UTC. This is a new, isolated, additive review stacked on draft #2186 (head 96b3303fa3112db324be5f2754ad313eae6233a1), which itself is part of the #175 / #201 newsletter QA chain. Home page #49 remains frozen; no source originals or other studios' branches altered.

## New material finding: the "3/3/2" totals are not inherently inconsistent
WordPress.com's subscriber documentation says **Not confirmed entries are not counted in total subscribers**. Thus the snapshot `total=3, confirmed=3, unconfirmed=2` does not by itself mean five confirmed people or a broken count. This resolves the *apparent arithmetic contradiction*, **not** the question of how many people are currently email-eligible. WordPress's independent followers summary reports WP.com 3 / direct email 0, different populations. The only reliable answer requires a private per-row **Email subscription = Subscribed** status aggregation; the connector does not surface it.

## New substantial deliverables
- `status-gate.mjs`: pure offline diagnostic that refuses to convert WP totals, Reader followers or unconfirmed into `confirmed_signup` or eligible recipients. Allows a later, source-authenticated, privacy-safe aggregate for eligibility while distinguishing already-verified WP-account and email-link pathways.
- `status-gate.test.mjs`: checked behavioral cases. No network, subscriber import, live instrumentation, or emails.
- `six-issue-decision.md`: concrete conversion-focused editorial and merchant redlines for every original #175 email; founder's 4/2 allocation intact; no alternative adopted automatically.
- `merchant-and-delivery-proof.md`: merchant account, EMAIL rights, direct first-party guide and genuine received-mail/postal/unsubscribe evidence contract; claims verified against official offer pages.
- `subscriber-status-runbook.md`: no-PII private account reconciliation, digest cadence, and `confirmed_signup` acceptance instructions for Claude/Focus.
- `reviewer.html`: accessible, non-sending printable decision board.
- `evidence.json`: source dates, links, status and immutable branch proof.

## Conversion-only acceptance
Offer: Zen12 optional audio evaluation. Funnel: Grok actual asset_id → first-party Focus guide → provider-confirmed subscription → weekly editorial → **approved, published Zen12 buyer guide** → permitted earning link → independently settled paid commission, refunds/fees → realized net per 1,000 qualified-human sessions. Direct guide access without subscription must remain possible. Nothing in the current data permits claiming any paid customer, qualified session denominator or commission.

**All six emails HOLD_UNSENT**, 03/05 additionally HOLD_MERCHANT, alternative issues NOT_ADOPTED. No email/test email, list access/export, settings/content write, affiliate activation, code deployment or spending.

## Source-of-truth links
- Canonical Dispatch [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), original [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), baseline safeguards [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201).
- Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129); conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).
- https://wordpress.com/support/subscribers/ (last reviewed Nov 4, 2026); https://wordpress.com/support/newsletter-settings/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://wordpress.com/support/troubleshooting-not-receiving-notification-emails/ .
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://finalvestige.com/editorial-standards/ .
