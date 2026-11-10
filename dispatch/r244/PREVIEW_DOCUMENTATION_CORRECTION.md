# Dispatch R244 | Official Jetpack preview guidance changed on November 9, 2026

**No send, no CMS draft, no subscriber contact.** This is a correction to prior internal wording, not permission to operate the WordPress editor.

## Verified primary source
WordPress.com Support, *Modify the appearance of newsletter emails*, "Last reviewed on November 9, 2026": https://wordpress.com/support/newsletter/email-appearance/

The published procedure under **Preview an email** now says that **Preview email** and **Send test email** controls work with the per-post **Send this post to subscribers** toggle **ON OR OFF**. Therefore R243's statement that preview **requires** toggling this flag ON is **not supported by the updated official documentation** and should be replaced in future runbooks. This was documented as a material correction, not a failure of the author's original safety objective.

**Still blocked:** Founder approval to create a *controlled unpublished WordPress draft* has not been granted. This correction does not authorize creating one or navigating the editor state. The two buttons are NOT equivalent: Preview email is a visual preview, while Send test email transmits a real message. Do not click test, Publish, Schedule, or activate a notification toggle.

## Read-only production checks (2026-11-10T00:39:23Z)
Jetpack site blog ID 256784396, newsletter ON; global `email_new_posts_by_default=false`; `email_content_format=full`; sender Final Vestige Studios; reply-to no-reply; welcome copy contains the 52-page Focus Fieldbook PDF. Status: total=3, confirmed=3, unconfirmed=2, suppressed=0; these fields are NOT ADDITIVE. Followers via separate API: WP.com=3, email-only=0. Provider-based **email-eligible audience UNKNOWN**. Five recent posts show `never_sent_opted_out`, not delivery. No evidence of received final welcome, real postal footer or functional unsubscribe.

## Proof hierarchy and safe protocol
1. **Offline review:** source-pinned HTML/plaintext and subject/preheader safety, one CTA, source claims, disclosures. An offline mock is not a Jetpack email.
2. **Unpublished native visual preview, separate founder authorization first:** create one controlled post draft only when explicitly authorized; leave global and per-post email sending flags OFF; use Preview email only. Capture desktop/mobile results, actual resulting title and header behavior; close without publication. The current official guidance indicates Preview is available with the per-post toggle OFF, but access still depends on site/account state. Record any contrary behavior without enabling sends.
3. **Received-message compliance, separately authorized:** founder approval is needed even for one real test email to a specific authorized address. Inspect raw received MIME, delivered sender/subject, link resolution, unsubscribe in email and actual Final Vestige valid postal address—not Automattic's unrelated postal address. Retest after any production template change.
4. **Production send:** never inferred from any other approval. Requires separate founder-approved issue, exact approved source revision, audience, cadence, partner rights for #03/#05, compliant rendering, consent and actual receiving configuration. No automatic send.
5. **Do not assume a special Jetpack preheader editor.** A drafted preheader is NOT evidence of actual rendered inbox preview text. Subject derives from WordPress post title; record actual native result only.

Sources: https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Owner handoffs
Dispatch/Site QA owns this correction and offline evidence. Claude owns production infrastructure. Founder authorizes any draft, test email or send. Grok owns social content/distribution. No new platform, list, cost or script.