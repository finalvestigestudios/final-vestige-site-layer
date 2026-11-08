# Dispatch R73 — received-MIME false-positive correction and rendition integrity

**November 2, 2026 · editorial and technical evidence · GitHub Issue #174 · companion #171.**

**Status: HOLD_UNSENT across 01–06; #03/#05 additionally HOLD_MERCHANT.** This is a technical correction to prior R70 received-email inspector/report software on the isolated R72-stacked development branch. No original newsletter issue, approved campaign mix, WordPress page, Jetpack setting, subscriber, email or merchant account was changed. Master draft PR #175 and per-edition release gate PR #201 remain untouched; homepage PR #49 remains frozen.

## The real QA defects — not more simulated assurance

The earlier R70 received-MIME inspector had **three consequential false-positive paths** and one product-copy mismatch:

1. **Plaintext unsubscribe false positive:** the combination of the word “unsubscribe” somewhere in the email and **any** HTTPS URL anywhere in the same message was reported as an opt-out candidate. A message saying “Unsubscribe anytime” and linking solely to the **Focus Fieldbook** could appear to have an opt-out URL even though that link had no identified opt-out function. **Correction:** require a URL syntactically attached to an unsubscribe/opt-out label; merely mentioning the word and offering an unrelated website no longer counts. This is a *candidate* link, never a verified working unsubscribe.
2. **Missing footer in an alternate format:** previously the address was searched in the union of HTML and plaintext. When the real WordPress message has both MIME alternatives, an address in plaintext alone masked absence in HTML, and vice versa. **Correction:** independent per-rendition boolean checks and an explicit blocker if one format lacks the private qualified-address reference.
3. **Missing disclosure in alternate format:** the first-55-word check read plaintext preferentially. A commercial issue whose plaintext disclosed the prospective commission while the HTML email omitted it was reported as having an early disclosure. **Correction:** first 55 *visible* words are checked independently in each present rendition; when both are present **both** must include disclosure, or the report fails closed.
4. **Actual draft wording:** source-controlled commercial excerpts say “Final Vestige may **receive** a commission.” The previous detector only recognized “may **earn** a commission,” a false negative. Both candid phrasings now match. More explicit and adjacent disclosure still requires human editorial review.

### Additional one-click header integrity

A `List-Unsubscribe-Post: List-Unsubscribe=One-Click` **declaration** no longer counts when the associated `List-Unsubscribe` header has no syntactically valid HTTPS destination. This is not a network test or proof of RFC 8058 compliance; it merely prevents an unsupported standalone header from appearing validated.

## New redacted evidence contract

The received-MIME inspection output is now version **fv-dispatch-received-eml-readonly-v2**. R70 HTML/text report renderer uses this same version and exposes six independent signals:

- Plaintext publisher address match; HTML publisher address match; *all-present-renditions* publisher address match.
- Plaintext first-55-word disclosure; HTML first-55-word disclosure; *all-present-renditions* early disclosure.

Existing recipient, sender, subject, address, unsubscribe token, full URL and body data remain **excluded** from stored reports. No messages are sent or clicked. The renderer refuses any data purporting to override `HOLD_UNSENT`. Old v1 reports should be **re-inspected locally** if they are ever used; v1 “true” values are insufficient to establish cross-rendition integrity. There are no real customer/source emails currently authorized as parser input.

Every report retains nonwaivable human gates: actual receipt provenance; sender and subject accuracy; legal validity and publisher ownership of the Final Vestige mailing address; working opt-out; subscriber eligibility; Jetpack native rendering; exact final founder-approved copy, audience and sending date; product-specific Inspire3 email permission and buyer guides for 03/05.

## Offline adversarial verification

New file `dispatch/campaign-2026-mind/tests/test_r73_mime_alternative_integrity.py` creates **32 in-memory synthetic cases**. Tests cover irrelevant HTTPS-link false positives, label binding, missing or cross-rendition postal text, commercial disclosures omitted from one rendition, both commission phrases, early-word ordering, missing HTTPS List-Unsubscribe with claimed one-click, hidden HTML script, redaction, spoofed JSON values and no network/send modules.

Use the existing complete native campaign test command, unmodified:

```shell
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
```

For a synthetic-only accessible HTML/plaintext demonstration, use the **existing** R70 generation utility: `python -I dispatch/campaign-2026-mind/r70-received-mime/make_synthetic_preview.py --out-dir /private/reviewer-only`. It writes only redacted synthetic report formats. Do not present this as actual Jetpack email evidence or store a real .eml in GitHub.

## Today's independent authenticated source checks

On **November 2, 2026 at 19:30 UTC**, WordPress.com site **256784396** reported: Newsletter enabled; `site_can_send=true`; `email_new_posts_by_default=false`; `email_content_format=excerpt`; sender display “Final Vestige”; `reply_to=no-reply`; `recent_sends=[]`; welcome message **contains** the 52-page Fieldbook PDF URL but a successful received welcome was **not established**. Subscriber diagnostics were `total=2, confirmed=2, unconfirmed=2, suppressed=0`; this is **not** a verified number of send-eligible individuals. No subscriber identities were requested or exposed. Published WordPress page IDs: Dispatch **523**, Focus **1579**, Editorial Standards **17**. Dispatch signup describes investigations/archival finds, while Focus has greater near-form commercial expectation language; neither page was edited.

Read-only targeted Gmail searches through November 2 found **no affirmative named-product Zen12/Total Focus email-channel affiliate grant** or actual Fieldbook welcome in the searched results. This is scope-limited absence, **not** proof that no possible authorization or receipt exists.

### Outside evidence and legal interpretation

- WordPress newsletter email appearance, last reviewed **October 6, 2026**: https://wordpress.com/support/newsletter/email-appearance/ — custom post excerpt and native Preview email/Send test email differ from our standalone drafts.
- WordPress newsletter settings: https://wordpress.com/support/newsletter-settings/ — excerpt mode without a custom excerpt ordinarily uses first **55 words**.
- FTC CAN-SPAM business compliance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — commercial primary-purpose analysis, honest sender and subject, qualified mailing address and functioning opt-out.
- FTC endorsement disclosure FAQs: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking — financial relationships must be disclosed clearly and where relevant.
- Inspire3's **public** affiliate recruitment is not partner-specific authorization: https://affiliates.inspire3.com/ . Do not copy unrelated Limitless Labs email swipe into Zen12 or Total Focus.
- Inspire3 merchant buyer-data policy: https://inspire3.com/privacy/ (potential sharing of purchaser name/email/product with affiliates; **not evidence** of Final Vestige receiving it).
- Current exact product destinations under review only: https://zen12.com/ and https://hypnosislive.com/mental-skills/total-focus . Any checkout claims/prices/refunds need another fresh named-product check before affiliate placement.

### Focused editorial decisions for the six-issue campaign

The founder's **four editorial / two reserved commercial** structure is not changed. The R72 custom excerpts remain optional and are **not yet installed**, and our `preheader_intent` text has no verified native Jetpack-to-inbox control. Issue 04's original “Fourteen seconds” and newer “Seventeen seconds” are still an **unapproved subject discrepancy**; neither describes fire duration, only a documented radio-transmission interval. Issue 03 (Zen12) and 05 (Total Focus) remain unpublishable commercial destinations because affiliate acceptance, permitted EMAIL use of tracking links/creatives, approved guide routes, price/refund claims, consumer-data handling and near-offer disclosures are unresolved.

A truthful native preview and an explicitly approved received test message are next; **they are not authorized in this branch**. This technical correction guards against a dangerously optimistic future “passed” report; it does **not** advance receipt or legal approval by itself.

## Founder-facing release verdict

**ALL 6: HOLD_UNSENT. 03/05: HOLD_MERCHANT.** No WordPress, subscriber, email, affiliate, merchant, production tracking or website writes; no new provider, cost, list or schedule. Final explicit campaign approval is still required after real inbox + unsubscribe/address and merchant evidence.
