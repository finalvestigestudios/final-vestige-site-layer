# R27 — Two excerpt documentation models; one safer per-post route (UNSENT)
**Evidence time:** 2026-10-31 20:34 UTC. **Parent:** draft PR #345 HEAD `61ee1fe34dd77cbabe632e31b6a39712ea288ed6`. **Master:** #175 / Issue #174. **Scope:** read-only findings and offline decision aid; not an authorization to publish, preview-email-toggle, test-send, activate links, or change settings.

## Material finding: default-excerpt behavior has two published descriptions
* WordPress.com *Configure newsletter settings* (currently available): when no custom excerpt exists, the **first 55 words** are used. https://wordpress.com/support/newsletter-settings/
* Jetpack *Customize the Newsletter experience*, last updated **Oct 28, 2026**: if the per-post Excerpt field is empty, the **first 350 characters** are used. https://jetpack.com/support/newsletter/customize-the-newsletter-experience/
* These documents are not identical. Do not claim either fallback model represents actual email bytes for this WordPress Atomic site. **A received original MIME or authorized native preview is required** to determine actual delivery and footer.
* Our six original source manuscripts include their CTAs after both modeled fallbacks (see `EVIDENCE.json`), and neither modeled commercial introduction includes its near-offer disclosure. No post has been authored/published to test this.

## Important lower-risk option (subject to actual UI verification)
The same current Jetpack guide explicitly says the default email-content choice **can be overridden for an individual post in the editor sidebar**. This may permit selecting *full text* for a specifically approved newsletter while keeping the site's **global** default set to excerpt and global auto-email set to OFF. This is documented product capability, **not yet proven in Final Vestige's own editor**.

## Authorized future preview protocol — NEVER execute without founder approval
1. Preserve newsletter global `email_new_posts_by_default=false` and `email_content_format=excerpt` unless separately approved. Screenshot settings (redact any subscriber identities).
2. Only after approval, create one controlled **unpublished draft post** from the latest source-controlled Gutenberg candidate. Inspect the Jetpack Newsletter sidebar for its per-post content/full-text control. Record whether available; do not guess. Do not publish or schedule.
3. WordPress says **Preview email** is only available when the per-post “Send this post to subscribers” toggle is ON and the post is unpublished. Changing that toggle temporarily is **not authorized in this sprint**. If later authorized, ensure post stays draft and toggle is returned OFF, with an independent status check. Never send a test email without separate permission.
4. Compare the **native preview** to full source: subject, the first/middle/last substantive paragraphs, exactly one primary CTA, sources, and commission disclosure immediately beside the conditional product guide. Confirm all six have text available. Verify actual sender name and preheader; our preview's preheader field is not known to carry through Jetpack.
5. Separate later approval required for a recipient-limited **received MIME**: confirm unsubscribe functionality (not simply presence), Final Vestige's genuine valid postal address, accessibility and content, and correct recipient eligibility. Redact all recipient addresses from stored evidence.
6. No commercial issue may proceed before **Final Vestige-specific** merchant program approval, written permission for opted-in email, exact permitted SKU tracking links, finalized guides, accurate checkout/refund terms and founder final campaign/audience/date approval.

## Read-only observed configuration, 2026-10-31 20:34 UTC
Connected WordPress `newsletter.get_settings`: enabled; auto-email for new posts **OFF**; default `email_content_format=excerpt`; from-name **Final Vestige**; reply-to **no-reply**; Focus 52-page welcome body configured. `newsletter.status`: `total=2`, `confirmed=2`, `unconfirmed=2`, `suppressed=0`, `recent_sends=[]`, `site_can_send=true`. Counts may be nonadditive. No recipient-level eligibility or actual welcome receipt demonstrated. Connected Gmail found **only an October 25 subscription-confirmation message**, not a delivered welcome or merchant authorization.

## Legal/ethical and data safety
All **six HOLD_UNSENT**, Issues **03/05 HOLD_MERCHANT**. The commercial source manuscripts' disclosures are retained but they cannot become eligible merely by including a disclaimer. FTC requires a valid physical postal address, accurate identification, and a working opt-out; a generic Automattic postal address is not a substitute. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

**No platform purchase; no subscriber import/contact; no merchant outreach; no WordPress writes; no affiliate link; no emails or test sends; no homepage/PR #49 changes.**
