# R78 — genuine cross-API subscriber reconciliation, not a new newsletter system

**Recorded:** November 2, 2026, 16:36 Pacific (November 3, 00:36 UTC).
**Owner:** FV Dispatch Campaign Studio; master #174, Mind partner #171.
**Stack:** PR #175 original, PR #201 release safeguards, PR #695 parent. Frozen homepage PR #49 unchanged.
**Release status:** ALL SIX `HOLD_UNSENT`; issues 03/05 additionally `HOLD_MERCHANT`.

## New authenticated finding: two different counters disagree

Read-only WordPress `newsletter.status` for blog **256784396** returned:
`total=2`, `confirmed=2`, `unconfirmed=2`, `suppressed=0`, `site_can_send=true`, `recent_sends=[]`; source snapshot at **2026-11-03T00:36:37Z**. Its `newsletter.get_settings` at **00:36:42Z** separately confirmed Jetpack enabled, new-post default emails **OFF**, `email_content_format=excerpt`, sender **Final Vestige**, `reply_to=no-reply`, and a configured welcome with the 52-page Focus Fieldbook. That is configuration evidence, not receipt.

A **separate** authenticated `wpcom_jetpack_stats_followers` observation reported `total=2`, **`email=0`**, `wpcom=2`, `comment=0`, `publicize={}`, `partial=false`. We must not conflate WordPress.com Reader followers with recipients who actually receive email. The data sources disagree about email reachability. One endpoint saying *confirmed 2* and the other saying *email followers 0* **does not demonstrate either 0 or 2 email-deliverable users**. Nor is total+confirmed+unconfirmed a partition: unconfirmed people are excluded from the total, per WordPress documentation.

**Critical correction to campaign reporting:** Do not describe "2 email subscribers" as an established deliverable audience. The only defensible observation is two totals from distinct APIs, zero email followers in one classification, and **UNKNOWN** send-eligible subscribers. This exceeds the earlier R75/R77 analysis that discussed only the nonadditive newsletter counts. No names, addresses or tokenized links were retrieved or saved.

## Private, source-of-truth operator check (read-only; no exports)

1. In the authenticated WordPress Dashboard choose **Jetpack → Newsletter → Subscribers**. Do not download CSV or open/record individuals' email addresses.
2. Apply the **Email Subscription** filter and record only the count where status is **Subscribed**. Do not count `Not subscribed` (Reader only), `Not confirmed`, `Bounced`, `Emails paused` or `Not sending` as deliverable.
3. Independently apply **Not sending (any reason)** and count exclusions; note whether either filter double-counts or has different populations. WordPress documentation warns the marketing subscription tally can include Reader-only people.
4. Record the interface name, filter, timestamp, count and *no personal identities*. Compare to both APIs. Distinguish operator-observed status from actual deliverability: an opted-in status is not a received-email proof.
5. If still inconsistent, retain `UNKNOWN` and request official WordPress support **without sending subscriber details in the GitHub issue**.

Official subscriber mechanics: https://wordpress.com/support/subscribers/ . WordPress.com follower classifications may be sampled via Jetpack follower stats but are not a row-by-row recipient list.

## Separate Jetpack, legal, and affiliate release gates — no execution

**Native rendering:** WordPress post titles become email subjects; separate preheaders remain editorial planning, not a verified editable field. The site is in excerpt mode, meaning a custom excerpt or the first ~55 words; disclosure in full manuscript after a link is inadequate. The **Preview email** editor tool is not the same as an actually received MIME. An authorized received email must show HTML and plaintext visible disclosures, a verified **Final Vestige** postal mailing address, and a working unsubscribe. A post editor's "Send to subscribers" toggle is currently default OFF; do not change it or send a test until separately authorized. https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ .

**FTC baseline:** A qualifying commercial email must identify the sender accurately, use a truthful subject, make commercial nature clear, include a valid publisher postal address and an operable opt-out. The postal address from Automattic's October 25 *subscription confirmation* is **not** evidence of a Final Vestige publisher postal address. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

**Merchant:** The actual Mind buyer guides remain draft/unpublished: latest Zen12 PR #700 and specific Total Focus PR #692. Product partner **acceptance, email channel rights, authorized creative, exact offer link, price/refund limits and customer-data handling** remain unverified. No guide CTA or seller checkout link can be activated. A draft guide in GitHub is not a published pre-sell route. No vendor claims treated as product-specific efficacy proof.

## 4:2 editorial trust, measurements, and accountable next milestone

Maintain **four editorial** issues and **two commercial-reserved** issues (03 Zen12 and 05 Total Focus). Do not substitute fallback letters without founder approval. Do not send or schedule any messages. No new platform, expense, imports, subscriber list, or homepage changes.

Aggregate traffic metrics are not newsletter metrics: no opens, click-through rates, sales, conversion rates, or A/B significance are observed. Only after authentic delivery and permitted privacy-safe instrumentation may a reporting baseline be developed; leave all unobserved measures **UNOBSERVED**, never fabricated zeros.

**Gate that actually moves the project:** authenticated filter counts (only), an authorized genuine received Jetpack email, functioning publisher-specific opt-out/address, two published approved warm-up guides, separate product-specific *email* rights, and final founder campaign approval. This script remains fail-closed regardless of any attestations.
