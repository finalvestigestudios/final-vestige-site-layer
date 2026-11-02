# Native Jetpack received-email acceptance script — instructions ONLY, not authorization

**What is still missing**: a genuinely received WordPress/Jetpack newsletter sample, a separately authorized real test-send, a publisher-owned qualified physical mailing address, confirmed unsubscribe operation and the actual eligible recipient count. None can be manufactured from an offline preview or a passing Python test.

## Stage A: current read-only proof (completed Nov 2 15:41 UTC)
- Site id 256784396; Newsletter ON; `site_can_send=true`; `email_new_posts_by_default=false`; `email_content_format=excerpt`.
- The WordPress post editor ordinarily uses a *post title* for the notification subject; its appearance and excerpt are customizable, but an arbitrary `preheader` field from our source-controlled manifest is **not verified to be delivered as a hidden preheader**.
- Custom excerpt can replace opening-body snippet in excerpt setting. Without it, WordPress says the first ~55 words are used.
- Existing six drafts live only in GitHub. No WordPress content was created/published; no list contacted.

## Stage B: founder-authorized non-public native preview (NOT PERFORMED)
1. Founder selects **exact six final source file SHA values**, text/subject and **site-first excerpt vs full inbox** intent.
2. Founder authorizes any draft creation or editing in WordPress **separately** from email delivery (do NOT publish). Keep global new-post auto-send disabled.
3. For an individual controlled test post only, WordPress says Preview email and Send test email controls appear if “Send this post to subscribers” is ON. Enabling this UI toggle must be reviewed for risk, and **does not constitute permission to publish/send**. Do not touch it in an unattended run.
4. Capture a private screenshot of WordPress's actual **Preview email** in desktop/mobile. Record the link, subject/preview experience and visible disclosure if a commercial edition.
5. Stop. **Preview is not evidence of actual inbox/MIME or legal footer.**

## Stage C: separate explicit named test-recipient send (NOT AUTHORIZED / NOT PERFORMED)
1. Founder explicitly authorizes a single controlled **test email** and its recipient (no sitewide send).
2. In private, capture header sender/reply-to, the exact plain + HTML bodies, preview snippet, link destinations and postal + unsubscribe footer. Do not reveal addresses or unsubscribe tokens publicly.
3. Check commercial issue #03 or #05: the affiliate disclosure is actually in delivered excerpt *and* beside its qualified guide link. An excerpt that ends before disclosure is a **fail**, even if a web article contains one.
4. Verify an unsubscribe link through a separately permitted safe test path (ensure not accidentally unsubscribing genuine readers); check mechanism stays active at least 30 days and operational follow-up. Store only redacted boolean/dated evidence, never token or PII.
5. Verify valid Final Vestige publisher postal address **in the received message**, not from the footer of a WordPress confirmation or seller email. If absent, block commercial dispatch; do not borrow another company's address.
6. Repeat where email layout differs. If rendering loses the CTA or disclosure, hold and correct under review—never assume a desktop offline rendering carries over.

## Stage D: campaign approval (NOT GRANTED)
The publisher's exact audience, send dates, frequency, six SHA IDs, validated CTA routes, current merchant email authority and tracking, delivery mechanism, opt-out/address, and contingency are approved explicitly. An email test approval must **not** automatically authorize a campaign send. For actual roll-out, founder controls action, not an hourly automation.

## Decision on the next technical step

Because Jetpack sends **post notifications**, the current excerpt setting is not equivalent to six fully formatted letters. The lowest-risk initial *design candidate* is site-first researched stories plus approved custom excerpts (original list expectation), but it has **not** been founder approved. Never silently change site-global excerpt/full settings or activate email toggles.

Official: https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter-settings/ ; https://wordpress.com/support/subscribers/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .