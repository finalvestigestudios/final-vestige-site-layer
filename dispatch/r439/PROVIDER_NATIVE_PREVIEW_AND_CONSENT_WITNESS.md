# R439 — Read-only provider witness and no-send acceptance protocol

## Exact verified live state (2026-11-18 04:31 UTC)

Site ID **256784396**. Authenticated WordPress Jetpack newsletter enabled, `site_can_send=true`, `send_blockers=[]`, `email_new_posts_by_default=false`, `email_content_format=full`, sender-name Final Vestige Studios, reply-to `no-reply`; original welcome message contains link to existing 52-page Focus Fieldbook. The five most recent post-notification records were `never_sent_opted_out` / `send_subscription flag is false`; this is **not** a claim about all past mail.

Newsletter counters: total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**. Unconfirmed is excluded from the main confirmed total. Jetpack Stats Followers (partial=false): **0 direct email**, **3 WordPress.com Reader**. The Stats data explicitly says followers across types need not be unique and Reader preferences can differ. **Eligible subscribed inboxes remain unknown.** Neither `site_can_send` nor a WordPress-account follower state certifies a specific inbox or actual received mail.

No subscriber address, raw ID, hash, confirmation token, IP, email response header or recipient-specific attribute may enter GitHub, the marketing event stream, or public QA fixtures.

## The provider path that is not available via current connector

There is no exposed connected action to read the Subscribers tab's **Email subscription = Subscribed** filtered count, nor a native `Preview email` result. Do not simulate those checks by summing `total`, `confirmed`, `email`, `wpcom`, or repeated pageviews. A permitted authorized reviewer may inspect that filter privately in the WordPress dashboard and record **aggregate count + timestamp + screenshot/evidence pointer without addresses**. Real native Preview should be inspected in the editor of an unsent, unpublished safe working draft; do not press Publish or Send test email, and do not create a WordPress draft through this run.

### Specific receipt classes

1. **Eligibility** — aggregate count from private provider Subscribed filter; note whether site is in WordPress.com, Reader or email subscription mode. If filter cannot be used without exposing addresses, record UNKNOWN.
2. **Confirmation** — provider `confirmed` status vs a *separate* email-only confirmation message. As WordPress documents, existing WordPress.com users may skip the separate confirmation email and receive welcome immediately; do not require a confirmation email for every legitimate confirmed subscription.
3. **Welcome** — actual copy received by a separately authorized pre-existing inbox; verify sender, Fieldbook URL and whether it is a welcome vs confirmation, with address redacted. No new test subscription or test email is authorized.
4. **Fieldbook** — WordPress Media Library record + actual PDF retrieval and page check, kept distinct from delivery of the welcome. The configured link alone proves neither.
5. **Rendered newsletter** — native desktop/tablet/mobile Preview within WordPress editor for a held draft, verify subject, header/first paint, genuine footer, unsub rendering, sender naming and legal postal address. Preview is not an email receipt.
6. **Commercial legal** — founder-provided, publisher-valid mailing address and actual working unsubscribe route in a permitted receiving test. A general WordPress unsubscribe promise or Automattic postal address is insufficient.
7. **Affiliate** — independent Mind/Commerce source evidence of account-level EMAIL promotion permission and exact SKU, referred checkout, refund terms, attribution and affiliate earnings. Seller-owned copy is not permission.

### Recipients and consent-state truth table

| Interaction | Visitor path | Legitimate evidence | Count as `confirmed_signup`? |
|---|---|---|---|
| Email submitted | Email-only | Attempt only | NO |
| Confirmation email sent | Email-only | Email confirmation request | NO |
| Provider confirms the subscription | Email-only | Authenticated provider state, scoped Dispatch | YES, deduplicate |
| User follows while logged into WordPress.com | WordPress account | Provider-confirmed subscriber state and scope (may skip separate confirmation message) | ONLY WITH AUTHENTICATED PROVIDER RECORD |
| Reader follow only | WordPress.com | Reader status and recipient preferences | NO, unless provider validates Dispatch email subscription |
| Fieldbook PDF opens | Any | Public-resource interest | NO |
| `?subscribe=foo` URL state | Any | URL parameter | NO |
| Existing confirmed subscriber revisits Focus | Any | Repeat visit | NO ADDITIONAL LEAD |
| Email opened or link clicked | Eligible recipient | Engagement event, often privacy-limited | NO NEW LEAD |
| Merchant checkout initiated | Any | Funnel attempt | NO SALE |
| Merchant reports settled paid conversion | Any | Independently reconciled merchant record | YES PAID ORDER, not automatically net revenue |

The event `confirmed_signup` must have a real provider confirmation timestamp, purpose `dispatch_newsletter`, a stable deduplication key kept outside analytics/public repositories, and a provider-authenticated source record. This is a **measurement design**, not deployed event instrumentation; coordinate with Claude to reuse the existing event system instead of injecting a duplicate script.

### Zero-live-action acceptance script

- Record snapshot timestamp and checksum/immutable reference; do not record addresses.
- Verify default new-post send remains OFF and review any per-post toggle separately; no publish.
- Compare actual `/dispatch/` acquisition promise with manual-send workflow; founder chooses *one* revised copy candidate if desired.
- Validate direct Fieldbook availability without treating PDF access as a subscriber.
- If authorized read-only provider filters or genuine Preview remain inaccessible, leave them UNKNOWN and release HOLD; do not “prove” receipt with source HTML or static/offline simulation.
- Treat actual partner email permission and settled merchant orders as entirely separate attestations.
- No follow-up segmentation until WordPress categories and legally valid targeting are explicitly approved. Current categories are disabled, so the one-offer sequence is only editorial progression, not a deployed targeted nurture automation.

**No WordPress content, settings, subscribers or posts were changed in this workstream.**
