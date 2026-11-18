# R447 — Non-sending Jetpack preview and received-welcome witness

**Hard boundary:** this is a procedure for founder-authorized *read-only review*. The current plugin actions cannot simulate the actual WordPress visual email Preview, and no test-email permission exists. NEVER use `Send test email`, `Publish`, `Schedule`, `Email subscribers`, `Resend`, `Import`, `Update Settings` or `Save` merely to prove a preview. If an already-existing compatible unsent editor draft cannot be inspected read-only, mark `NOT_WITNESSED` rather than creating/editing a WordPress draft.

## Official UI distinction

WordPress documents two separate editor functions in [email appearance](https://wordpress.com/support/newsletter/email-appearance/): **Preview email** visualizes desktop/tablet/mobile without delivering; **Send test email** sends a real message. Their UI may be adjacent. A static HTML source artifact, site-page preview or theme preview is not a native email Preview. The current six campaign copies are in unmerged draft GitHub PRs, **not** a WordPress email editor.

## Safe verifier rubric (zero subscriber data in PR)

| Field | Test or observation | Evidence type | Current |
|---|---|---|---|
| Provider newsletter identity | Exact site, sender “Final Vestige Studios”; keep new-post auto-send OFF | authenticated settings, time | VERIFIED READ-ONLY |
| Recipient eligibility | 3 records filtered `email_subscriber` / `Subscribed`; 2 additional unconfirmed excluded | aggregate provider filter only | VERIFIED INVENTORY, not deliverability |
| Non-sending Preview | WordPress editor **Preview email**, all three viewport options visible | private screenshot with PII redacted, existing authorized draft identifier | NOT_WITNESSED |
| Subject and preheader | match founder-selected source text, no misleading urgency or client truncation | preview screenshot/subject audit | NOT_WITNESSED |
| Sender postal | genuine Final Vestige valid physical postal, not merchant or Automattic | securely recorded business address attestation + final email render | NOT_WITNESSED |
| Unsubscribe | rendered usable opt-out URL; actual process audited without contacting list | provider-doc confirmation and authorized isolated QA | NOT_WITNESSED |
| Commercial disclosures | adjacent to Issue03/05 qualifying guide CTA, clearly visible on narrow viewport | visual proof; check link text and near-link context | NOT_WITNESSED |
| Welcome / 52-page Fieldbook | actual consented recipient receives the **welcome**, opens correct 52-page PDF | private inbox witness without disclosing any address/message headers | NOT_WITNESSED |
| Successful delivered Dispatch | actual received campaign email and link after explicit campaign release approval | provider send and recipient witness | NOT_WITNESSED; ZERO SENDS AUTHORIZED |

### Accessibility review for eventual true native preview

Check at 320/375px and desktop: main text 16px or comfortable equivalent, one clear CTA, no horizontal scroll; high-contrast button text and focus targets; images with useful alt text and no text-as-image dependency; semantic heading order; meaningful standalone links; source links remain distinguishable from principal CTA; meaningful reading order in plaintext. Confirm links remain visible without images and in forced dark mode. Native provider may remove CSS and may rewrite links; offline table markup passing lint is not sufficient.

### Postal and opt-out

A commercial email needs Final Vestige's sender identity, appropriate valid publisher mailing address, and a clear functional unsubscribe that honors requests. Do not place an unverified personal address in a public repository. Store proof privately; public attestation may record reviewer, date and an opaque evidence handle rather than subscriber/provider secrets. Do not claim legal compliance merely because a template includes a `[[POSTAL]]` token or a general privacy-policy link.

### Consent and lead count

A person may view or download the PDF **before** completing email confirmation; such access is useful but not a new subscriber. WordPress.com account subscriptions may have a different confirmation path than a new standalone email address. Require an actual provider-origin state transition into `Subscribed` / email eligible, deduplicated under a privacy-safe private account key. **Never commit** the recipient's email, account identifier, stable hash or click-level records.

When a new signup is observed, record only an aggregate transition count for 7/30-day cohorts with a clear before/after evidence window; welcome receipt is an additional, separate outcome. Before any authorized external test, explicitly verify the founder approved that exact test and whether it would send a real email; currently no such approval exists.

### Evidence states

`BUILT` = local/GitHub HTML or code; `TESTED` = recorded native Python/Node or offline browser test; `LIVE` = WordPress production behavior witnessed; `VERIFIED` = dated source-of-truth proof of actual recipient/merchant event. Do not conflate the states. A fake screenshot, manual mock click, guessed email receipt or JavaScript-inferred signup is not provider proof.

### Stop conditions

Any uncertainty around a real email send, recipient address disclosure, a new WordPress draft write, a mailing-address proof, the approved affiliate destination or a live transaction **stops** that specific verification. All six editions stay `HOLD_UNSENT` regardless of local test status. The original four editorial + two commercial reservation is preserved; Issue03 Zen12, Issue05 Hypnosis Live.
