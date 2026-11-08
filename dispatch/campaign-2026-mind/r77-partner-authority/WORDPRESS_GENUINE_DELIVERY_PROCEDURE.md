# Jetpack native preview and independent received-email acceptance — future HUMAN-AUTHORIZED procedure
**Current status: not executed. No test email authorized.** WordPress site ID 256784396 / from name Final Vestige / `no-reply` / excerpt / default new-post send OFF. Last read 2026-11-02 23:38 UTC.

## Why offline HTML cannot be the acceptance artifact
WordPress [email appearance](https://wordpress.com/support/newsletter/email-appearance/) explains that the native email is compiled from **post title (subject), excerpt or opening text, and the platform's own templates**. An independent HTML file produced by our scripts does not establish its final MIME, footer, CSS, mobile rendering, unsubscribe target, send origin, welcome-gift delivery, or per-recipient eligibility. Only **posts** cause newsletter emails under the current workflow, not standalone pages or custom types ([official send guide](https://wordpress.com/support/newsletter/send-newsletter-emails/)).

## Step A — Read-only compliance prerequisites (no list export)
1. Privately inspect Jetpack Newsletter subscriber status: count **active email subscribed**, separately count pending confirmation, paused/bounced/digest and suppressed where available. The current endpoint's `total=2; confirmed=2; unconfirmed=2` are not four recipients. Take **aggregate count only**; do not place subscriber addresses or WordPress token URLs in a ticket or repository.
2. Verify valid **Final Vestige Studios** physical postal address by confidential owner attestation (eligible registered PO box or qualifying business mailbox is possible). An Automattic/London merchant postal address is not automatically ours.
3. Confirm a human can access the actual Jetpack post editor Newsletter panel on a **draft post**. Do not toggle global settings; do not publish, schedule or send a test. Existing `email_new_posts_by_default=false` must remain unchanged.
4. Distinguish post draft display URL from **published archive route**; neither Mind PR #687 nor #692 has a published guide and no offer-based email may be sent until it does.

## Step B — Native PREVIEW after separate founder authorization (preview only; no send)
1. On a separately authorized draft **post** with no unresolved affiliate or legal placeholders, view the Newsletter panel, deliberately review the per-post 'Send this post to subscribers' control (needed for preview controls), and click **Preview email**, never **Send test email** or Publish.
2. Record screenshot evidence for desktop/tablet/mobile: subject equals actual post title; custom excerpt rendered as intended; no unattributed separate preheader claim; author/date/image according to Jetpack; first-screen disclosure appears in both commercial issues if applicable.
3. Capture reviewer decision using opaque reference ID and a qualitative PASS/FAIL. No email address in screenshots. Turn the per-post send control **OFF** before leaving; **do not save or publish** with a send flag inadvertently armed. If the editor cannot preview without toggling, stop and request separate approval.
4. Inspect brand identity, links to **approved LIVE** pages only, text contrast, meaningful link labels, keyboard navigation when applicable, no tiny legal text, visible publisher address and an unsubscribe mechanism. Native editor preview cannot prove deliverability.

## Step C — Received-email test only AFTER separate explicit approval
1. Founder names an authorized recipient inbox and permits **one test message**, distinct from final campaign approval. Do not add/import subscribers, send to the list, or publish a live post just to trigger an email unless that exact process was explicitly approved. If Jetpack's test-email feature has unknown audience side effects, STOP.
2. Download the **received message** to a private location for the R70/R73/R74 inspector; review HTML/plaintext separately. Do **not** commit `.eml`, message IDs, unsubscribe tokens, email addresses, raw headers or full message to GitHub.
3. Verify subject, preheader actually emitted (if any), display sender, alignment of first 55 visible words and source CTA; inspect valid publisher postal address and clear opt-out in **both available renderings**.
4. Confirm opt-out **functionality** only using a separately approved test recipient where disabling the subscription is permitted and reversible by that person; merely seeing an opt-out URL/header is not proof it works. Never click a real person's token.
5. Compare receipt of the configured **52-page Fieldbook welcome** separately: the October 25 confirmation email does not establish post-confirmation welcome delivery. Record only pass/fail/date and approved evidence reference.

## Step D — Release reviewer / legal signoff
No automated program can authorize this step. Final decision must identify six exact manuscript/WordPress post versions, editor and legal signoff, exact audience size and selection, approved published guide URLs for both products, 2 named-product permissions for email, valid legal footer, rendered native preview + received email acceptance, and explicit founder send date/time approval. Do not convert current traffic statistics into click or conversion rates.

**Standing status: HOLD_UNSENT ALL SIX / HOLD_MERCHANT #03 & #05.**