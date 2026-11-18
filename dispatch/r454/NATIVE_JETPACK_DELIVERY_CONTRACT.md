# R454 — WordPress/Jetpack transport truth: manual native-email acceptance, no sends

**HARD HOLD / SOURCE ONLY** · November 18, 2026, 19:32 UTC · Site 256784396 · Dispatch Issue #174 · upstream draft #3032 @ `aee015b2d2dfbdc50351272b32449b21e2339dfd` · original #175, safety #201, homepage #49 untouched.

## High-impact newly verified transport constraint

**WordPress.com's native Newsletter sends post notification emails, not an independent six-email campaign object.** Its [official sending guide](https://wordpress.com/support/newsletter/send-newsletter-emails/) says **the post title becomes the email subject**, only post-type publications trigger the email, and published posts cannot be re-emailed merely by editing them. A markdown manuscript subject or an offline HTML reviewer is *not* the delivered subject or body. The supported [email appearance guide](https://wordpress.com/support/newsletter/email-appearance/) documents an editor-local **Preview email** flow and optional **Send test email**. We are NOT authorized to click Send test email. This means no current artifact is a native received preview, despite many HTML review specimens.

**Preheader cannot be attested from current settings.** Neither the connected `get_settings` response nor the current official native workflow establishes a controllable independent preheader field for this site. Treat R446's preheaders as editorial goals, not proven Jetpack transport fields. Do not install a plugin or new email tool to obtain one. If the editor's non-sending preview supplies no separate preheader, establish the first visible body sentence as a clean, plain-text preview line (human editorial proposal), and document the actual inbox clipping only after founder authorizes a controlled received-message test.

## Fresh connected source-of-truth at 2026-11-18 19:32 UTC

- Newsletter STATUS: 3 total/confirmed, 2 additional unconfirmed reported separately, suppressed 0; last five `never_sent_opted_out`, no dispatch timestamps; `site_can_send=true` means technical ability, **not permission**, delivered messages or compliant marketing.
- SETTINGS: subscriptions ON, **email_new_posts_by_default OFF**, `email_content_format=full`, `reply_to=no-reply`, `from_name=Final Vestige Studios`, `featured_image_in_email=true`, `newsletter_categories_enabled=false`; 52-page Fieldbook URL configured in welcome.
- Stats Subscribers filtered EMAIL=3, Reader-only=0; Stats Followers EMAIL=0, WordPress Reader=3, `partial=false`; Stats Emails: 0 post-email rows. **Do not sum or substitute these categories.**
- Dispatch live page ID 523 promises “new investigations and useful finds ... when we publish them”; Focus ID 1579 promises similar. Current default-OFF means only deliberately selected posts can generate emails. Editorial correction should say “occasional selected editions” rather than every post.
- Focus ID 1579 offers a **direct PDF download** and an optional Dispatch join. That is a valuable conversion path: do not count PDF downloads as confirmed leads or compel signup for the free resource.
- Editorial Standards page ID 17: primary records, visible disputed evidence, meaningful corrections, no unsupported inference; commercial relationships must not determine historical findings.
- No verified Final Vestige **publisher** mailing address in any sampled settings; WordPress/Automattic postal information in a confirmation email is not FV's own address.

## EXACT real native preview acceptance — founder-only editor or authorized read-only screen witness

1. **Prior state:** capture post ID, draft status, owner, current `Send this post to subscribers` toggle OFF, and settings hash/screenshot. The post must be an **existing authorized nonpublic draft**. If creating a draft would itself be a WordPress write, that is NOT authorized by this campaign approval and this step must be deferred. Do not republish or switch post status just to force email.
2. Without publish, schedule, test send, or toggle change: open the existing draft's Newsletter (paper-airplane) sidebar → Email → **Preview email**. Official WordPress guidance confirms preview works even when the send toggle is OFF: https://wordpress.com/support/newsletter/email-appearance/ . If there is no eligible existing draft, mark `NATIVE_PREVIEW_NOT_WITNESSED`, not “passed.”
3. Witness true Preview at desktop/tablet/mobile: subject equals actual Gutenberg post title, visible first-body text, only ONE main CTA, citation links readable, disclosing affiliate interest directly before commercial CTA, images with alternatives, no script/form, constrained width, no reviewer instructions, no fabricated offer URL. Capture screenshot/review URL internally with no PII.
4. **Footer:** verify in that actual preview whether **Final Vestige's valid physical postal address** and **functional unsubscribe option** are visibly present; a decorative “unsubscribe” word is not enough. If preview cannot prove recipient-level functionality, retain separate final received-mail witness hold. The address must be founder-supplied and valid; never use merchant or Automattic address as substitute. FTC guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
5. **Reply-to:** `no-reply` is current native setting; do not imply readers can reply with questions. Proposed footer can link to the live public contact/corrections page rather than soliciting replies, subject to founder review.
6. Confirm no actions in transmission logs from review, no list import, no subscriber contact, no new post, no new scheduled item and no config change. Check `recent_sends` again read-only if needed.
7. Mark `PREVIEW_WITNESSED` only for actual native preview with evidence reference. Mark `RECEIVED_DELIVERY_WITNESSED` **false** until separate founder-authorized test. An offline rendered HTML file cannot satisfy either.

## Post→email mapping needed BEFORE any commercial release

| Editorial component | GitHub manuscript | WordPress native requirement | Current evidence |
|---|---|---|---|
| Subject | R446 clean proposed subject | Actual **post title** controls subject | Manuscript candidate, not loaded |
| Preheader | Plain editorial preheader | No verified standalone native preheader field | **UNKNOWN / transport mismatch risk** |
| HTML body | Hand-authored offline specimen | Native post-block transformation and site email design | **NOT WITNESSED** |
| Plaintext | Reviewed `.txt` | Actual multipart plaintext or fallback content from provider | **NOT WITNESSED** |
| CTA | Source-tagged intended first-party landing URL | Live approved first-party destination, one main action | #03/#05 guide **NOT LIVE APPROVED** |
| Footer | Draft disclosure + placeholders | Actual FV legal address and functional opt-out | **NOT VERIFIED** |
| Attribution | UTM campaign conventions in #820 | Existing sanctioned measurement, real source-to-purchase proof | **NOT LIVE VERIFIED** |

**Release outcome:** six issues `HOLD_UNSENT`. Existing native Jetpack list only. No automatic drips, segmentation, scheduled email, sender contact or plugin change. A prior source-only layout pass is not a transport acceptance.
