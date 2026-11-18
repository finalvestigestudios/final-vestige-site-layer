# R448 — Draft landing-page honesty and conversion copy (NOT ADOPTED)

**No live site edits.** These are exact suggested text replacements for **founder and Claude review**, not an authorization to publish, change Jetpack, or change the newsletter list. Read-only WordPress retrieval 2026-11-18 13:31 UTC confirms page 523 /dispatch/ and page 1579 /focus/ are published. Newsletter: `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, `reply_to=no-reply`, sender name "Final Vestige Studios". Last five post notifications `never_sent_opted_out`. Site can technically send, but no campaign send has been authorized.

## Why this matters to conversion

The main issue is a promise-to-delivery mismatch, **not** necessarily broken WordPress behavior. Existing page copy implies each new investigation is emailed as it publishes, while the current site has automatic new-post emails OFF and individual notifications opted out. A visitor who subscribes for immediate or every-post email updates may be disappointed; rebuilding trust is more important than boosting nominal signup count.

### /dispatch/ (page 523)

**Current deck (verbatim):** "New investigations and archive finds by email, when we publish them."

**Proposed deck:** "Occasional investigations and archive discoveries, selected by our editors and sent when there is something worth sharing."

**Current supporting promise (final sentence):** "You’ll also get new investigations and useful finds from the archive when we publish them."

**Proposed supporting promise:** "After you confirm your subscription where required, The Dispatch will send occasional research-led editions and carefully selected discoveries. We do not email every time a post goes live."

**Current confirmation line:** "Enter your email below. If WordPress asks you to confirm the address, click the confirmation link and you’re in."

**Proposed confirmation line:** "Subscribe using the existing WordPress form. Depending on your account, WordPress may ask you to confirm your email. Your Fieldbook link is also available on the free Focus page; subscribing is optional for access to the PDF."

**Keep:** transparent "Unsubscribe anytime" and Privacy Policy. The welcome copy remains the current 52-page Fieldbook; do not change it in this sprint. Do **not** imply a guaranteed arrival time, paid offer, or automatic sequence.

### /focus/ (page 1579)

**Current consent line (verbatim):** "By subscribing you also join The Dispatch, our email of new investigations and archive finds, sent when we publish them. Some emails may include recommendations that earn us a commission. Unsubscribe anytime."

**Proposed consent line:** "If you subscribe, you join The Dispatch on the existing WordPress list. We send occasional, selected investigations and useful research notes—not an automatic email for every published post. Some future editions may contain clearly disclosed affiliate recommendations. You can unsubscribe anytime. The free Fieldbook is available without purchasing or subscribing."

**Current reveal:** "Your fieldbook is ready to download." / "Please confirm your email to join The Dispatch."

**Recommendation:** Retain the free PDF reveal; ensure in QA that the revealed download is not presented as proof of subscription or as confirmation of welcome receipt. Show three independent states in analytics: `fieldbook_revealed`, provider-confirmed `confirmed_signup`, and **actual welcome delivered**, which still requires a private proof. Never count the first as the second.

### A truthful, small CTA journey

Grok's actual published attention/focus video (asset ID supplied by Grok, not invented) → matching research article or /focus/ → optional existing Jetpack subscribe → provider-confirmed signup (new transition only) → welcome with free 52-page PDF → selected editorial Dispatch edition(s) → **only after separate named approval** Zen12 first-party guide → issued merchant link → independently reported settled commission. Do not force a newsletter signup to view the free book, use a new list, or route directly to a coupon funnel.

## Release QA acceptance

Founder/Claude compare live and proposed copy; independently check visible form, navigation, mobile focus states, the true WordPress confirmation experience for a safely authorized account, duplicate signup behavior, and PDF availability without contact. Owner can implement only upon separate production authorization. Proposed copy is deliberately not inserted into published pages or current campaign files.
