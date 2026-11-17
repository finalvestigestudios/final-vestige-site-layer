# R416 — founder-only proposed consent wording and non-sending preview acceptance

**DRAFT COPY, NOT LIVE.** For founder approval and Claude/Focus implementation review only. Do not write to WordPress, change the Jetpack welcome/subscribe settings, or contact subscribers. No new platform or list. Must not imply the newsletter has already sent or that a fieldbook arrived in a real inbox when it has only been configured.

## 1. Proposed /dispatch/ copy (recommended default)

**Heading:** The Dispatch  
**Deck:** Occasional investigations and archive finds, delivered when an edition is ready.  
**Support paragraph:** Get the free 52-page Seven Day Focus Fieldbook and join The Dispatch, Final Vestige Studios' occasional research letter. We don't email for every new site post, and we don't send a daily series. Some future editions may include an optional, clearly disclosed product recommendation that supports the studio.  
**Subscribe label:** Subscribe to The Dispatch  
**Consent beneath form:** Please confirm your email if WordPress asks. The newsletter welcome is set up to include the Fieldbook download. Joining does not require a purchase. You can unsubscribe at any time. See our Privacy Policy.  
**Footer expectation:** Investigations, archives and tools under review; not an automated update on every article.

**Why:** The actual `email_new_posts_by_default=false` configuration contradicts a literal expectation that every new post triggers a newsletter. The current page promises emails “when we publish them” but its newest five post notices are all opted out of sends. An occasional-edition promise accurately reflects founder-controlled release without promising future delivery schedules. Marketing copy about email receipt remains conditional pending an actual independently witnessed welcome.

## 2. Proposed /focus/ copy (congruent with Dispatch)

**Heading:** The Seven Day Focus Fieldbook — Free, 52 pages  
**Support:** A twelve-minute starting routine, seven guided days, a 30-day log and a checklist for evaluating meditation-audio claims. Downloading the guide is free; it is not a promise of clinical or productivity outcomes.  
**Signup context:** If you subscribe, you also join The Dispatch for occasional evidence-led investigations and archive finds. We don't automatically email every time a web post appears. A future edition may explain an optional paid recommendation, with any financial relationship disclosed beside it.  
**Confirmation:** If WordPress requests confirmation, use its confirmation link to complete the subscription. The welcome message is configured with the same PDF URL.  
**Accessible download-state caution:** If the page displays the PDF button after a form attempt, the button means only that the download is available here; it is not proof that WordPress has confirmed your email or that you are eligible to receive newsletters. Do not create or report `confirmed_signup` from display state.

**Do not implement until:** Claude/Focus separately verifies the existing form and its confirmation behavior, founder approves legal/UX copy, and the site's published wording is revised in an authorized release. Do not remove free access to the Fieldbook just to force lead collection.

## 3. Required adaptation to native Jetpack's actual capabilities

The six optional newsletter preheaders are **editorial suggestions**, not verified native fields. WordPress documents a preview action in the post editor, post-title-based notices and a distinction between full and excerpt. A promised inbox preheader is not an acceptance criterion unless actually observed in native Preview and then a separately authorized received email. Avoid email screenshots that reveal addresses.

For the eventual founder-approved draft, confirm **one clear first-party content CTA**, with source citations visually secondary; for 03/05 keep CTA and affiliate URLs **null** until validated by Mind. DO NOT solve a blocked CTA by linking directly to a vendor or presenting a source link as if it is an approved earning link. An official merchant sales page may be cited for critical analysis; a commercial recommendation cannot activate without named EMAIL rights.

## 4. Commercial disclosure and CAN-SPAM evidence (template only, not a live footer)

*Issue disclosure next to an approved optional buyer-guide CTA:* “If you buy through a qualifying link in our guide, Final Vestige may earn a commission.” If the link itself is an approved direct paid referral, the wording must refer to that link instead. Both must plainly disclose the commercial relationship before the reader leaves for checkout.

*Publisher identity*: Final Vestige Studios (verify actual sender domain/address and header).  
*Publisher postal address*: **UNVERIFIED — do not insert a personal address, platform provider's address or merchant's address**. Founder supplies a legally valid FV business address or registered mailbox as appropriate.  
*Unsubscribe*: **UNVERIFIED — insert no imagined token or web path**. Must be visibly rendered and proven functional by the actual platform, under separate authorization. “Reply to this email” is inappropriate while `reply_to=no-reply`.

A copy-only HTML preview can test legibility, but cannot establish real mailing-list delivery, inbox headers, Jetpack's native signature, postal address or a working opt-out. No test email is authorized.

## 5. Founder acceptance sequence — deliberately separate decisions

**A: Editorial decision (no sending).** Review six existing proposed alternatives from R415; accept/reject slot-specific revisions without changing canonical #175, and prioritize correction of original Issue04's ambiguous fourteen-second claim.  
**B: Product legality (no sending).** Mind supplies privately authenticated, named Final Vestige email-promotion approvals for Zen12 and/or Total Focus, exact SKUs and earning links, verified buyer pages and checkout/refund terms. Issued permission for one cannot authorize the other.  
**C: Platform witness (no sending).** On a founder-authorized WordPress *draft editor*, use **Preview email**, not Send test email; record redacted screenshots at phone and desktop widths, subject actually shown, first body lines, exact publisher postal footer and visible unsubscribe. If no permitted editor access, leave untested.  
**D: Recipient and welcome proof (read-only).** Authenticated recipient-level status + consent/eligibility/suppression, deduplicate privately, and verify a consenting owned inbox actually received the 52-page welcome without sending any new test mail.  
**E: Independent functional opt-out (separate later authorization).** A genuine opt-out test can change a subscription and therefore is **not** performed now; obtain explicit authorization and a safe, consented test identity before it happens.  
**F: Paid conversion instrumentation (design only).** Claude uses the already-authorized source-of-truth analytics and independent merchant/checkout settlements; no new tag, platform, or person-level URL ID.  
**G: Founder final campaign authorization (not granted).** Only after A–F are documented can founder separately authorize the exact email creative, eligible audience, dates, schedule and any actual sending.

## 6. Specific proof card to keep out of GitHub

Provide **opaque receipt IDs only** in GitHub. Restricted evidence may include actual affiliate account acceptance, contractual email marketing conditions, current product URL/coupon formats, referral attribution, direct checkout and merchant statements, a valid publisher postal address, recipient-level provider statuses and already-received email screenshots. Do not post private merchant agreements, subscriber emails, passwords, tokens, consent identities or bank/commission records in public GitHub issue comments. The private owner makes a boolean attestation without copying secrets.

**Release state:** `HOLD_UNSENT`, 03/05 `HOLD_MERCHANT`, original 04 `HOLD_COPY`; alternative manuscripts `NOT_ADOPTED`. No WordPress changes, emails, test emails, list imports, affiliate activation, social posts, PR merges or spending.

References: https://finalvestige.com/dispatch/ · https://finalvestige.com/focus/ · https://wordpress.com/support/newsletter/email-appearance/ · https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
