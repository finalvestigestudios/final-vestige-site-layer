# R390 consent, welcome and native Jetpack acceptance contract

**Authenticated read-only snapshot:** 2026-11-16T00:37:30Z, site finalvestige.com (blog ID 256784396). Newsletter ON, site_can_send=true, 3 total, 3 confirmed, 2 unconfirmed, 0 suppressed, 0 paid, 0 imported last 24h; five recent posts marked never_sent_opted_out. New-post auto-send FALSE. Full-content email, From “Final Vestige Studios,” reply-to no-reply. Welcome settings point to the 52-page Complete Edition PDF. No emails sent by this run.

## Counts are semantically different, not necessarily inconsistent

WordPress subscribers documentation excludes unconfirmed from displayed total. The 3 confirmed plus 2 unconfirmed records must not be represented as 5 unique email inboxes. WordPress.com followers and email subscriber subcounts may overlap or represent Reader-only choices. We DID NOT access any subscriber addresses, export an eligible-recipient list, attempt a new signup or trigger a confirmation email.

For consent proof, owner must privately filter by email subscription status, verify permissions in provider's authoritative record, dedupe by provider opaque ID, document whether WP.com accounts skip separate confirmation, and return only aggregated count and scope. Name event confirmed_signup_v1 only for a provider-confirmed state transition, not a Focus page button click, PDF panel display or front-end URL parameter. No fabricated mapping to Grok asset_id.

## Free download is not a lead

On public /focus/ the ready-to-download panel and “Please confirm your email” copy can coexist. Public UI is not an authoritative double opt-in receipt. WordPress saved welcome copy is not proof an email was received or its download opens. Avoid calling either state a converted lead. Site /dispatch/ is live and displays the existing Jetpack signup block. Original report's subscriber count change 2→3 has no identified individual or consent-path attribution.

## Native preview without sending (founder/editor UI)

1. Open an **unpublished** owned newsletter post in the WordPress editor with its send-to-subscribers toggle OFF. Do not create or publish a post without separate authorization; existing suitable drafts only.
2. Open Newsletter → Email → **Preview email** (WordPress/Jetpack documented non-sending preview). Do **not** click Send test email, Publish or enable sending.
3. Observe desktop/mobile render, actual post-title subject, any actual preheader (do not assume custom preheader support), source links, editorial CTA, sponsor disclosure when present, sender name, mailing address and unsubscribe footer.
4. Capture redacted preview screenshots/reference, theme/version, post ID, date, device widths and URL behavior; avoid subscriber PII.
5. **Preview alone cannot prove an actual recipient footer, welcome receipt or unsubscribe operation.** Functional received-message and opt-out require explicit founder permission for a controlled test, never an unsolicited production message.
6. Founder provides current qualifying business postal address (PO Box or eligible registered private mailbox acceptable) and the business controller for opt-outs; Automattic's confirmation footer is not an FV postal address.

## Subject/preheader contradiction to prevent

Jetpack's current documentation confirms **post title controls the newsletter content/subject presentation**, and the native preview can be opened before publishing. There is no verified account-specific custom preheader setting in the authenticated get_settings response. R390 HTML preview's hidden preheader is a local mock, NOT proof Jetpack uses it. If the preview displays other text, record it rather than claiming A/B performance.

## Attribution and tiny-list thresholds

Record qualified-human session per actual Grok asset campaign only with independently published asset_id and eligible privacy-safe web signals. Record relevant CTA click separately. Record confirmed_signup_v1 from Jetpack provider proof only. Record independently settled paid commissions after fees/clawbacks only from merchant reporting. Do not compute or display zero net revenue per 1,000 when the cohort denominator or settlement ledger is missing. Seven- and thirty-day windows are retrospective, no A/B inferential claims with 3 confirmed records.

**Status:** all six original issues HOLD_UNSENT, 03/05 HOLD_MERCHANT, original 04 HOLD_COPY; proposed R390 Apollo edition NOT_ADOPTED. No native previews, test sends or real recipient delivery performed.
