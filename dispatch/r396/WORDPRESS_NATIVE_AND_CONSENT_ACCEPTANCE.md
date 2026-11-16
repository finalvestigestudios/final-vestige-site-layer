# R396 — Dispatch to actual inbox: provider truth and consent-owner acceptance

**As of authenticated WordPress read-only 2026-11-16 07:03:46Z. NO subscriber mutation, no test mail, no preview or send.**

## Source-of-truth findings

| Measure | Fresh provider observation | What it proves / does not prove |
|---|---|---|
| Newsletter master `subscriptions` | true | Newsletter feature enabled, not permission to send |
| `site_can_send`, blockers | true / [] | Technical capability only |
| `email_new_posts_by_default` | false | Default auto-email OFF; all 5 recent send-status rows `never_sent_opted_out` |
| `email_content_format` | full | Current setting, **not** delivered HTML/MIME or subject/preheader proof |
| From name / reply-to | Final Vestige Studios / no-reply | Configured identity; native sender address managed by WordPress.com |
| `total`, `confirmed`, `unconfirmed` | 3 / 3 / 2 | Unconfirmed *excluded* from total; **do not add to make five eligible inboxes** |
| Jetpack follower `wpcom` / `email` | 3 / 0 | Separate follower feeds, not an additive recipient count |
| Confirmed unique email-eligible receiving addresses | **UNKNOWN** | Needs private provider-filtered `Email subscription status = Subscribed` check, with notification preference/digest review |
| Welcome message | References same 52-page PDF, seven-day routine and 30-day log | Saved settings only, not proof of received final welcome |
| Sent email / mobile email preview | **NONE** | No native preview and no real inbox rendering evidence |
| Postal address / functional opt-out | **UNVERIFIED** | Must be verified on the actual rendered Final Vestige commercial message |

The live [Dispatch](https://finalvestige.com/dispatch/) and [Focus](https://finalvestige.com/focus/) pages both present the same Jetpack subscribe experience. A visible PDF-download prompt or success message is **not** provider-confirmed email consent; an already-confirmed subscriber re-requesting the PDF is not a second `confirmed_signup`. The Focus page is already showing a public downloadable resource; a download alone cannot prove an email was delivered.

### Explicit private proof sequence (no outreach authorized)

1. **Focus/Claude owner, read-only:** In Jetpack Subscribers, use the platform's **email subscription status** filter; record only aggregate totals of actually email-subscribed/eligible recipients and notification preferences. Do not export subscriber emails or post screenshots with PII. Confirm distinction between subscriptions, Reader-only followers, and pending subscriptions. If no privileged list/status view is available, mark **UNVERIFIABLE_WITH_AVAILABLE_CONNECTOR**; dashboard totals alone never close this gate.
2. **Welcome acceptance:** Locate the real *previously authorized* confirmed inbox message if accessible; check it is the **final welcome**, not an "Confirm your subscription" message. Confirm the real final received PDF link and whether it opens, without contacting the list. October 25 Gmail confirmation is not sufficient; searches through November 15 yielded no verified final welcome.
3. **Native rendering acceptance:** [WordPress native Preview email](https://wordpress.com/support/newsletter/email-appearance/), under the Newsletter sidebar of an existing authorized draft, is an on-screen preview, distinct from **Send test email**. Do not create or publish posts just for this. Verify preview's actual post-title subject, *actual displayed preheader*, disclosed optional CTA, system sender, visual and plaintext accessibility, and a publisher-specific **qualifying physical postal address** and opt-out. Never infer actual delivered MIME from offline HTML. If no existing authorized draft is available, this gate remains UNKNOWN.
4. **No functional unsubscribe experiment:** Do not click unsubscribe in an actual subscriber mailbox without final approval. Read-only UI availability is **not** proof of a functioning endpoint. The FTC's opt-out and address requirements are mandatory; don't use Automattic's address or a merchant's address as Final Vestige's publisher address.
5. **Founder final gate:** Explicit creative, audience, owner verified address, merchant SKU permissions, final WordPress post plan and send approval are all required. No site setting, list import, test email, welcome resend, publishing, scheduling or sending here.

### Deterministic `confirmed_signup_v1` design (proposal, not instrumented)

Emit at most once per **provider-authoritative transition to actual subscribed-and-email-eligible state**, with `opaque_subscriber_key` (not a mailbox), `source_event_id`, `provider_status_as_of`, `campaign_id` and `confidence`. Dedup by subscriber/event key. Treat provider snapshot increases, success banners, file downloads, WordPress Reader follows and pending records as **not countable new leads**. If an existing WP account bypasses confirmation email, the authoritative provider status still governs. Preserve incoming Grok UTM fields only when truly observed and consent-supported; otherwise `source=unattributed`. Aggregate cohort size warnings, no full user-level linking in GitHub.

### Fundamental deployment limitation

Jetpack's native workflow emails **post notifications** (published posts whose per-post email checkbox is enabled). A GitHub HTML email specimen is **not** a proven standalone Jetpack campaign template and a draft in this repo cannot be imported directly as an approved mail. [WordPress sending guide](https://wordpress.com/support/newsletter/send-newsletter-emails/). A native on-screen preview needs an editor draft; clicking Preview does not send. The final six-week delivery plan will require separate founder approval for the associated WordPress editorial post/publish/email actions. Never silently change `email_new_posts_by_default`.

### Authoritative references

* WordPress [newsletter Preview vs Send test](https://wordpress.com/support/newsletter/email-appearance/) and [Disable new-post emails](https://wordpress.com/support/newsletter/disable-newsletter-emails/) (last reviewed Oct 6, 2026).
* [FTC CAN-SPAM business guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business); [FTC Endorsement disclosure questions](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).
* Public site [Editorial Standards](https://finalvestige.com/editorial-standards/), [Focus](https://finalvestige.com/focus/) and [Dispatch](https://finalvestige.com/dispatch/).

**Release state:** 01–06 HOLD_UNSENT; 03/05 HOLD_MERCHANT; 04 HOLD_COPY; actual reachability/delivery and realized commission NO_PROOF.
