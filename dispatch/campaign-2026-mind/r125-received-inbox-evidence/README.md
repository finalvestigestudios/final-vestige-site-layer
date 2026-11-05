# R125 — Actual received-message audit, not another synthetic preview

**Status: DRAFT / HOLD_ALL_UNSENT.** Owner Issue #174, companion #171, baseline PR #175 and gate PR #201, stacked parent PR #1007. November 4, 2026 Pacific.

## Why this exists
R116–R124 produced offline previews and a proposed Focus consent fix; **no actual WordPress/Jetpack-generated, received email has been inspected**. Offline HTML or RFC822 fixtures do not prove a native post title/excerpt, real unsubscribe, publisher postal address, welcome delivery or recipient eligibility. This self-contained standard-library Python script reviews a locally saved RFC822 .eml entirely offline and emits a **sanitized aggregate** JSON report. It has no SMTP, network calls, subscriber writes, or activation functionality.

If the founder later authorizes a genuine test message to an owned inbox, save that exact message as a local .eml. Do NOT commit it, its recipient, real unsubscribe token, publisher private address or received headers. Run locally:

    python received_email_audit.py --eml path/to/received.eml --expected-subject "Exact WordPress post title" --report local-sanitized-report.json

For approved commercial postal footer QA, supply --approved-postal-text locally, from an authenticated founder-approved address reference. Its presence in text does not establish legal validity. Do not test opt-out by clicking a genuine subscriber's unsubscribe link. A .eml can be forged; separately prove owner-controlled inbox provenance and operational opt-out. Nothing here grants permission to send a test email.

## Audit fields (diagnostic only)
The checker evaluates the exact subject, HTML/plaintext alternatives, offline-fixture marker, release placeholders, HTTPS body CTA candidate, clickable unsubscribe or List-Unsubscribe, optional one-click header, presence of founder-provided postal text, sender, Received and Authentication-Results headers. **Headers are untrusted and neither DKIM/SPF nor receipt is independently proven.** No raw addresses, unsubscription URLs, message bodies, or private subscriber data are output. Regardless of structural success, release_status remains HOLD_UNSENT; actual_delivered remains NOT_ESTABLISHED_BY_EML_ALONE.

17 native local Python tests passed on exact GitHub-committed Python source and test bytes, verified by Git blob comparison. Six archived R122 artificial mailbox .eml specimens were independently inspected; all six intentionally fail the not_fixture check and remain HOLD_UNSENT. Synthetic success cannot waive required human/legal checks.

## Authenticated production status at 2026-11-05 00:32 UTC
Jetpack Newsletter ON, new-post auto-email OFF, delivery format excerpt, from-name Final Vestige, reply-to no-reply. Configured welcome message includes the free Focus Fieldbook media URL. WordPress reports total 3 / confirmed 3 / unconfirmed 2 / imported_last_24h 1. These buckets are **not additive**, and none prove email reachability or new consensual signup. The last five WordPress post notifications are never_sent_opted_out (send_subscription false). A limited Gmail search located the 2026-10-25 subscription **confirmation** but no received completed Fieldbook welcome or named FV affiliate authorization. PDF media metadata is not proof of successful PDF retrieval/page count. The published /focus/ and /dispatch/ share one Jetpack list.

## P0 gaps and owners — OFFER → STEP → BLOCKER → EXPERIMENT → EVIDENCE
1. **Free Fieldbook → confirmed lead**: URL/class gift-panel reveal is not consent. Founder-authorize Claude to deploy independently reviewed R124 public-download and accurate signup copy, preserve single Jetpack list. Require WordPress authenticated consent state and deduplicated confirmed_signup; read-only source finding/tested patch, **not live**. Dispatch + Claude.
2. **Dispatch → reachable subscriber**: WordPress.com followers != Email subscription Subscribed. Privately filter Jetpack Newsletter → Subscribers → Email Subscription; count Subscribed vs Not subscribed, Not confirmed, Bounced, Emails paused, Not sending. Record *aggregate only*, no export or contact. **NOT VERIFIED**. Dispatch.
3. **Newsletter → actual inbox**: Excerpt rendering, exact subject, footer, unsub, postal and welcome not verified. Permissioned genuine WordPress editor preview (no send) then separately authorized received test and offline .eml audit. Do not switch send toggle on without authorization. **NOT VERIFIED**. Dispatch / Site QA.
4. **Zen12 → legitimate paid buyer**: Named Final Vestige Inspire3 approval, email-channel rights, exact approved URL, current checkout/refund, verified live warm-up guide, privacy-safe aggregate conversion reporting all absent. Mind R129 PR #1009 has disabled commercial UI; public official pages alone do not prove efficacy. **HOLD_MERCHANT**. Mind Studio #171.
5. **Grok / Focus → net revenue**: No verified human source sessions, native confirmed leads, settlement/refund/fee records. Deduplicate utm_content=asset_id with source/medium/campaign; join to verified paid transaction in aggregate with 7/30 day window. **NET REVENUE PER 1,000 NOT COMPUTABLE**. Claude/Praxxis #820.

## Evidence and source links
- Original campaign: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175
- Original hold gates: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201
- Consent proposed repair: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1007
- Mind merchant work: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1009
- WordPress native subscriber statuses: https://wordpress.com/support/subscribers/ (reviewed 2026-11-04)
- WordPress native email preview (no test send required): https://wordpress.com/support/newsletter/email-appearance/
- Welcome behavior: https://wordpress.com/support/newsletter-settings/
- FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Seller pages: https://zen12.com/hnp and https://hypnosislive.com/mental-skills/total-focus

**Release control:** All six issues HOLD_UNSENT. Commercial 03/05 also HOLD_MERCHANT. Founder retains campaign/recipient/send/spend approval. Original four editorial/two reserved commercial structure unchanged. Do not contact any subscriber, import addresses, publish posts, modify WordPress, link affiliate offers, or activate tracking in this branch.
