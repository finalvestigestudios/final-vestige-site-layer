# The Dispatch: Received-email proof (HOLD)

**Date:** October 30, 2026. **Owner:** [Dispatch Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). **Stack:** PR #208 → this draft. The six original editions and their 4:2 editorial/commercial allocation remain untouched.

This is an **offline, read-only, standard-library Python** auditor for the original RFC822 MIME of a **separately founder-authorized, received WordPress/Jetpack test newsletter**. It does not create drafts, change settings, email readers, activate affiliate URLs, alter subscribers, publish, schedule, or provide legal signoff.

## Why we need this

The live WordPress newsletter currently uses **excerpt** delivery and automatic sending is disabled. WordPress says uncustomized excerpts otherwise default to approximately 55 words; the site already has six authored excerpts in the inherited delivery package. Previewing a newsletter in the WordPress editor is different from receiving the final HTML/plain email. The six issue-level release gates from PR #201 and aggregate attribution system in PR #208 cannot establish that a physical postal footer, unsubscribe mechanism, subject, custom excerpt and disclosure actually survived in a delivered message.

**Read-only snapshot, 2026-10-30 23:31 UTC:** subscribers 2 total / 2 confirmed / 2 unconfirmed (**contradictory**, not evidence of four people), imported last 24h: 1, no recent campaign sends, can-send true, 52-page Focus Fieldbook welcome message unchanged. The published /dispatch/ and /focus/ pages are unaffected. There is no eligible-audience proof.

## Exact audit route once an actual test is separately approved

1. The site owner reviews an actual **WordPress draft post** for the relevant edition in the editor. The Newsletter panel has **Preview email** and **Send test email** options. Inspecting a preview is not a send. **Do not use Send test email without founder approval identifying its exact testing recipient.** No publish or production email should be attempted.
2. The *authorized* test recipient saves a received MIME message privately as a local **.eml**. Never commit or copy the raw MIME, any subscriber names, recipient email addresses, private confirmation/one-click unsubscribe links, actual mailing address or partner authentication into GitHub/CI/report attachments.
3. The business mailing address is verified privately by the founder or appropriate reviewer. Supply its *literal text* **only as environment variable** FV_COMMERCIAL_POSTAL_EXPECTED; the auditor never prints that value. Automattic's corporate address from the October 25 subscription-confirmation email is not a substitute for Final Vestige's valid sender postal address.
4. Run the audit from a checkout containing the original campaign manifest and delivery excerpts:

   python -I dispatch/campaign-2026-mind/mail-proof/received_email_audit.py --edition 1 --mode excerpt --eml /private/approved-test.eml

   For no test email yet, **omit the --eml option** to generate an honest HOLD_NO_RECEIVED_EMAIL result. For any future approved **full** message, use --mode full and --full-marker with a uniquely expected *non-sensitive* phrase near the end of the complete edition.
5. **Manually verify** the real opt-out route works, that the final message and sender are legally correct, the postal address belongs to Final Vestige, the HTML and plain content are legible, the intended CTA is live, recipient consent is reconciled and any commercial partner explicitly allows email promotions. **Never mistake a visible link for proof that unsubscribe actually works.**

## What the auditor actually checks

- Decodes multipart/alternative MIME without fetching or executing external resources; skips HTML style/script/head content and rejects messages larger than 2 MB.
- Verifies WordPress's documented from address (donotreply@wordpress.com) and Final Vestige display name, exact subject, nonempty displayed text, and absence of draft-only placeholder tokens.
- In excerpt mode, checks **both the first and last twelve words** of the authored custom excerpt in the *HTML version when HTML exists*, catching silent first-55-word truncation or misplaced disclosures.
- Requires a first-party Final Vestige route, visible opt-out mechanism (not merely List-Unsubscribe header), independently expected *FV* postal address in the displayed body, and in issues #03/#05 a visible commercial disclosure with no direct merchant links.
- Keeps confirmation of opt-out **function**, actual authorized recipient, merchant email permission, preheader appearance, live product guide, independently substantiated claims and final founder signoff **UNKNOWN**. All statuses stay HOLD even when synthetic tests pass.
- Emits **only status codes**, issue numbers and manual-gate labels, not received text, tokenized links, subscriber details or postal values.

## Proven scope

34 adversarial synthetic MIME unit tests passed locally. This does **not** prove WordPress delivered a newsletter, that a recipient opted in, merchant affiliate authorization, actual CSS rendering, legal compliance, live link function or green GitHub Actions. On this sprint, inherited local test groups also passed: 14 delivery, 25 per-edition readiness and 27 attribution tests. Total 100 passing local checks, subject to independent exact-head and hosted CI verification.

**No received campaign test email was authorized or obtained.** All six remain held. Editorial #01/#02/#04/#06 can be reviewed independently from commercial partner gates, but no issue may be sent without the founder's explicit creative/audience/date authorization.

## Sources and editorial contract

- [WordPress newsletter appearance / preview](https://wordpress.com/support/newsletter/email-appearance/)
- [WordPress settings, excerpt and sender](https://wordpress.com/support/newsletter-settings/)
- [FTC CAN-SPAM compliance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [Final Vestige Editorial Standards](https://finalvestige.com/editorial-standards/)
- [Final Vestige Affiliate Disclosure](https://finalvestige.com/affiliate-disclosure/)
- [Official Zen12 positioning (seller assertions)](https://zen12.com/about)
- [Official Hypnosis Live Total Focus (seller assertions)](https://hypnosislive.com/mental-skills/total-focus)

Merchant-specific **affiliate acceptance, allowed advertising channels, tracking format, current checkout price/refunds and direct product efficacy remain unverified**. Vendor sales copy and consumer marketing emails do not establish account-specific partner authorization.
