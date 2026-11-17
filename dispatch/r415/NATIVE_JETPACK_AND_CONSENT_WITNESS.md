# R415 Jetpack actual email / consent / footer witness — non-sending protocol

**No native Preview was performed in this run.** This plan is an acceptance test for an authorized WordPress editor, not evidence that the test happened. Do not capture or post subscriber addresses, tokens or unredacted messages.

### Native editor preview, with send disabled

1. In the existing site's WP post editor, create/open an **unpublished draft** only under founder authorization. Keep per-post **Send this post to subscribers** OFF and leave global automatic emailing OFF. Do not publish, schedule or touch subscribers. Any draft creation itself requires founder approval; until then only read the documentation.
2. Use Newsletter (paper airplane) → **Preview email**, which WordPress documents as operating even when the send toggle is off. Explicitly **do not click Send test email**. Capture desktop/tablet/mobile renderings with a redacted opaque evidence reference, date and reviewer.
3. Match actual post title to displayed email subject; examine the first inbox-text lines. Planned preheader fields in Markdown are **not verified as supported by Jetpack**. Document precisely what the editor shows, never assert a separately programmable preheader.
4. Verify single meaningful primary CTA, first-party source URLs, the full versus excerpt body (site currently FULL), image alt text, mobile width/tap contrast/legibility, disclosure immediately beside commercial offer and no covert vendor claims. WordPress's newer Email Design feature is staged, so do not presume the site has access to it.
5. Verify a **valid Final Vestige Studios physical business postal address** visibly appears where required and clearly readable unsubscribe instructions/URL appear in the actual email template. An Automattic address in a confirmation request and the configured no-reply address do not satisfy these proofs. A static preview cannot prove the unsubscribe works, which needs an individually authorized functional test (not authorized now).
6. Distinguish a real received email from an editor rendering. Final Fieldbook welcome receipt requires an already-authorized, consented account and actual inbox evidence and accessible PDF; the October 25 confirmation message cannot count as the welcome. **No test email is authorized**. Never post raw received mail or inbox identity.
7. Private subscriber eligibility: source dashboard 3/3/2 vs Reader3/email0 (not additive). Compare authoritative provider confirmation, email delivery eligibility, suppression and duplicate IDs privately, publish only a deduplicated aggregate with timestamp and a restricted proof ID. If the platform does not expose it, return UNKNOWN, not 0/3/5.
8. Independently authenticate FV-named SKU email rights and the actual authorized presell pages before considering issues 03/05. Obtain founder's separate final approval for exact content, recipients and send date even if technical checks someday pass.

### Witness acceptance card

| Proof | Current observed result |
|---|---|
| Native Jetpack preview | NOT WITNESSED |
| Verified post-title subject and inbox preview text | NOT WITNESSED |
| Valid FV physical postal address rendered | NOT WITNESSED |
| Clearly visible unsub in email | NOT WITNESSED |
| Functional opted-out test and honoring suppression | NOT AUTHORIZED |
| Deduplicated eligible recipient count | UNKNOWN |
| Received Fieldbook welcome and working PDF | NOT WITNESSED |
| Merchant named product EMAIL authorization / guide / issued link | NOT VERIFIED |
| Paid order or settled affiliate commission | NOT VERIFIED |
| Founder release authorization | NOT GIVEN |

**Outcome: HOLD_UNSENT regardless of offline HTML or test results.** References: https://wordpress.com/support/newsletter/email-appearance/ , https://wordpress.com/support/newsletter-email-design/ , https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
