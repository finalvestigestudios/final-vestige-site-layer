# Dispatch R85 — Received Jetpack email evidence gate (HOLD)

**Status: UNSENT / UNPUBLISHED / NO TEST SEND.** Owner: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Original [draft #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175). Commercial guide owner [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Stacked after [R84 draft #741](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/741), entirely separate from frozen homepage PR #49.

## Material production finding — the off-by-default distinction

At **2026-11-02 23:34 PST** (WordPress source timestamp 2026-11-03 07:34 UTC), authenticated WordPress reads reported that the existing Jetpack newsletter is enabled and CAN send. New-post email is **not checked by default**; this is a POST-EDITOR DEFAULT, **not a master no-email lock**. A future editor could enable sending on a particular post. Five recent posts (1917, 1920, 1922, 1924, 1926) individually report never_sent_opted_out; these five did not initiate Jetpack newsletter sends. This does not prove no other post/email could send.

Other settings were email_content_format=excerpt, reply_to=no-reply, sender name Final Vestige. The existing welcome message contains the 52-page Focus Fieldbook link; receipt remains unverified. The diagnostic counts still conflict: total 2, confirmed 2, unconfirmed 2; separate follower analytics say email 0, WordPress.com 2, total 2. **Do not infer exactly zero, two or four email-eligible recipients** from these separate classifications.

A second important distinction: the original six long-form manuscripts in PR #175 are *not necessarily what Jetpack will email* in excerpt mode. WordPress post title determines email subject; a draft preheader is not an independently verified native control. WordPress requires the per-post newsletter toggle on to access **Preview email** or **Send test email** in its editor. These operations have different privacy and authorization implications, and neither occurred in R85.

Official sources:
- WordPress newsletter appearance (reviewed October 6, 2026): https://wordpress.com/support/newsletter/email-appearance/
- WordPress newsletter sending procedure (reviewed October 19, 2026): https://wordpress.com/support/newsletter/send-newsletter-emails/
- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- FTC endorsement/disclosure: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- Publisher Editorial Standards: https://finalvestige.com/editorial-standards/

## New executable capability

**audit_received_eml.py** only reads a locally held, previously *authorized* received RFC822 .eml file. It never connects to an API, sends, subscribes, publishes, adjusts settings, activates an affiliate link, clicks unsubscribe or grants release permission.

It can check the specified approved subject, presence of readable MIME parts, exact first-party HTTPS destination, commission disclosure visibility and its rough first-350-character positioning, whether a *locally supplied* Final Vestige business postal address appears in the body, and whether the MIME or body includes unsubscribe mechanism indicators. All reports are **fixed-key categorical JSON**, excluding sender, recipient, body, exact URL, postal address, message ID, click token and content digest.

**All outputs intentionally remain HOLD_UNSENT_REQUIRES_HUMAN_VERIFICATION.** A matching postal string is NOT proof of lawful publisher ownership; a List-Unsubscribe header is NOT proof that unsubscribing works. The script is not a legal compliance attestation or a Jetpack rendering simulator. Actual email clients may hide content, modify tracking, or display alternative parts differently.

### Use only after the founder authorizes a single controlled test

Do not store real emails in Git, source-control comments, CI artifacts or public folders. Set the final qualifying business address only in a private local process environment, as FV_DISPATCH_POSTAL_ADDRESS. Run the Python file with the private eml path and arguments --subject, --cta and optionally --commercial. The CTA must be an exact HTTPS URL at finalvestige.com, not an Inspire3 link. Review the categorical JSON locally and then secure/delete private received-message material appropriately.

Offline synthetic verification, without messages being sent:

    python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_r85_received_mail.py' -v

Full campaign regression:

    python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v

## Real-world steps still required

1. In the WordPress Subscriber screen, reconcile recipient eligibility, opt-in state, suppressed recipients and the distinct Reader-follower classification. Review only aggregate results for this GitHub issue; never export identities.
2. Obtain founder-approved qualifying **Final Vestige-owned** business mailing address through a private channel. The Automattic address on an October 25 confirmation email and the merchant's corporate address do not establish that.
3. Founder must independently approve *editor-native preview* and separately approve any *actual test email* before executing either. Keep any preview draft unpublished, and never conflate the test send with permission to broadcast.
4. Compare WordPress post title, custom excerpt, CTA, front-of-excerpt commercial disclosure, footer, sender information, images and reading order against the real received email. Controlled, authorized unsubscribe functional evidence is required. Do not click a third party's token.
5. For commercial slots 03 Zen12 and 05 Hypnosis Live **Total Focus**, require verified partner approval, product-specific **email promotion permission**, allowed earning URL/creative, claim scrutiny against exact product pages, current checkout/refund conditions and two approved **published first-party buyer guides**. Never turn seller efficacy promises into Final Vestige-certified science.
6. Explicit founder approval remains mandatory for final chosen versions, audience, dates and actual sends. The 4 editorial / 2 commercial-reserved pilot remains unchanged and all issues HOLD. No performance, subscriber, sales or A/B measurements are invented.

FTC's CAN-SPAM guide makes clear that promotional content linking to a commercial website can itself be commercial even without a checkout button in the email. A warm-up CTA cannot be treated as an automatic exemption.

**This sprint changes no WordPress content/settings, recipients, affiliate URLs or homepage files, and sends or schedules no email.**
