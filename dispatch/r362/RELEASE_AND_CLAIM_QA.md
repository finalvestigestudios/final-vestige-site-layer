# Source-to-inbox and merchant release gate

## Exact read-only provider state, November 14, 2026, ~20:39 UTC

Jetpack `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, sender **Final Vestige Studios**, full content, `reply_to=no-reply`; configured 52-page welcome PDF URL. Subscriber dashboard `total=3, confirmed=3, unconfirmed=2, suppressed=0` (overlapping/non-additive). Stats `email=0, wpcom=3`. Sampled last five post notifications `never_sent_opted_out`. All six drafts stay HOLD_UNSENT. **Being technically able to send is not evidence of legal/consent/recipient eligibility or a sender authorization.** No paid sales verified.

## Legal and native renderer verification: FAIL-CLOSED / NOT TESTED

According to the [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), applicable commercial messages require accurate sender/subject, clear advertising character, a valid publisher physical postal address and an opt-out method that works; requests must be honored under the rules. This is not established by a site privacy footer, WordPress confirmation email's **Automattic** address, or a hardcoded template placeholder. Confirm a business-qualifying Final Vestige publisher address with the founder without publishing a private residence by mistake.

[WordPress's email appearance documentation](https://wordpress.com/support/newsletter/email-appearance/) specifically distinguishes **Preview email** (desktop/tablet/mobile, non-sending) from **Send test email** (actually sends a message), even if the per-post send toggle is OFF. The former is the next permitted non-sending UI validation if editor access exists; the latter is not authorized. An offline browser or Markdown renderer is neither a native Jetpack preview nor a received email, and an unsubscribe-looking string is not a functioning opt-out.

**Pass evidence:** real native preview screenshots without publishing; genuine owner-authorized received test message after founder approves it; valid FV mailing address; recipient-tested unsubscribe/opt-out and confirmation/delivery proof in a private, redacted record. **Current:** absent. Do not mark the six issues send-ready.

## SKU-specific merchant claim and approval boundary

- [Hypnosis Live *Total Focus* official sales page](https://hypnosislive.com/mental-skills/total-focus) currently describes a 33-minute, 47-MB product, and displays varying single/bundle prices and a headline 14-day refund promise. Its claims about “reprogramming” focus and productivity are **seller assertions**, not Final Vestige-proven scientific outcomes. Refund limitations require review of the actual policy **and referred checkout**, not merely the attractive headline. No price is inserted into an unsent edition.
- Zen12's official product information was reviewed in earlier Mind/Dispatch work as twelve levels with four audio styles (48 MP3 files). Promotional equivalence between twelve minutes and an hour of meditation is **not independently established** for that product. Public affiliate catalog or sales-page access does not prove named Final Vestige publisher approval or permission to email.
- **Source-of-truth still missing:** named acceptance of Final Vestige Studios; offer-specific permitted promotion channels including EMAIL; permitted links/copy/creative license; actual earning URL; destination guide approved and LIVE; exact current referred price and checkout/refund; vendor/processor-issued paid commission reporting. This remains owned by Mind/Commerce Issue #171, not Dispatch. A draft permission request in R361 was NOT sent.

### Release verdict per edition

Issues 01/02/04/06 = editorial **HOLD_UNSENT** (consent, native preview, footer, founder). Issues 03/05 = commercial **HOLD_UNSENT + HOLD_MERCHANT** (all base gates plus partner permissions, offer guide, actual checkout). The founder's 4:2 plan remains unchanged, all optional manuscript alternatives are NOT_ADOPTED. No WordPress, affiliate, social or commerce activation, no cost.

**Pass/fail distinction:** original six draft contents and locally rendered previews exist; native Jetpack preview, full received email, unsubscribe, consent and merchant earning evidence are **NOT VERIFIED**. Do not substitute “built” for “live,” “clicked” for “purchased,” or “configured” for “received.”
