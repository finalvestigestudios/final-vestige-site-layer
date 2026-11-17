# WordPress-to-inbox transport and consent witness protocol — R425
**Scope:** standalone technical review; no live writes.

## 1. The native-channel constraint
Jetpack's public guidance (https://jetpack.com/support/newsletter/) explicitly states the notification unit is a **new WordPress post**. A page, an edit of an old post, a static HTML file or a GitHub Markdown draft is not equivalent. At present the site's post-email default is OFF, which is the deliberate fail-safe. Never turn the toggle on merely to make the newsletter work. Source: https://wordpress.com/support/newsletter/email-appearance/ (documentation last reviewed Nov 9, 2026).

## 2. Proof ladder: do not skip rungs
A) WordPress settings `subscriptions=true`: platform capability, **not** an approved campaign.
B) Dashboard counts `total=3,confirmed=3,unconfirmed=2`: not unique eligible recipients. Reader-follower and email-delivery group definitions differ.
C) Provider-confirmed identity/consent evidence: a private authoritative eligible membership record, independent of URL query strings, CSS classes, or PDF download events. Beware existing WordPress.com-account subscribers: Jetpack says its normal confirmation email may not be sent to them (https://jetpack.com/support/newsletter/customize-the-newsletter-experience/).
D) Welcome configuration: PDF hyperlink in settings. Only an actually received welcome (with redacted private witness) establishes delivery to that inbox.
E) WordPress editor `Preview email` on a matching unpublished draft post: previews responsive source conversion only, not inbox delivery.
F) Actual received authorised test mail: only after separately explicit founder permission; inspect MIME, link destinations, sender identity, opt-out and physical postal address. Do not assume Automattic's postal address is ours.
G) Real approved campaign sends: separately authorized audience, edition, schedule. None approved.

## 3. Non-sending preview steps for a founder-supervised future review
1. Confirm there is no unsent-to-subscribers background job. Capture current newsletter status and current draft's editorial hash.
2. Before creating any WordPress draft or using the editor, obtain explicit permission for that WordPress write. The current automation has none.
3. In the WordPress connected post editor, choose the *Newsletter* paper-plane control, then *Preview email*. **Do not click 'Send test email'; do not click Publish**. This path is documented as working with the send-to-subscribers toggle OFF.
4. Review desktop, tablet and mobile, long lines, clickable anchor text, commercial disclosure adjacency and readable references; capture a sanitized screenshot with no subscriber email addresses.
5. Check sender display separately from `donotreply@wordpress.com`, which Jetpack controls. Preview is not proof of an actual inbox footer or unsubscribe endpoint's operation.
6. If authorised later, use a permitted self-owned receiving inbox for received-message HTML/plaintext/MIME witness. Verify a physical Final Vestige address (street, registered PO Box or registered CMRA), not the WordPress/Inspire3 address. Test opt-out only through authorized accounts with appropriate consent. Do not send to the list for testing.
7. Record the human signer, provider source identity, date, and issue hash in a private attestation. Only a redacted ID and public Issue #174 link belong in repo.

## 4. Two distinct consent concepts
'Confirmed signup' means a person has a provider-authoritative eligible subscriber record, matched to the one existing Jetpack list; one event per *new* provider confirmation transition, not every page click, success parameter, JavaScript CSS reveal or re-confirmation. Permission to send *affiliate* marketing is separately scoped by the subscriber relationship, publisher promise, suppression settings, applicable law and merchant partner contract.

## 5. Attribution contract; do not implement a second script
Claude owns the existing event path. At most ONE `confirmed_signup` per new provider identity and event ID; dedupe server-side. Campaign name should be stable, e.g. `fv_dispatch_mind_pilot_2026`; email edition marker `dispatch_03_zen12_review` (only if a guide actually goes live and approval exists). Keep Grok `asset_id` and `utm_campaign` from creator link through page session, CTA and guide where technically lawful and available. Require separately reported settled merchant order and subtract refunds/fees for realized net revenue. Never multiply a nominal affiliate payout rate by clicks or speculate revenue. Do not put email identities or secrets in UTM parameters.

## 6. Observed screenshot/status boundaries
At 2026-11-17T15:05:27Z WordPress reports new post sends for five November 3 posts `never_sent_opted_out`. This proves those five post notifications did not go out, not that no newsletter has ever reached anyone. All automated post notifications must remain OFF. A native preview has not been taken in this sprint and no subscriber has been contacted.
