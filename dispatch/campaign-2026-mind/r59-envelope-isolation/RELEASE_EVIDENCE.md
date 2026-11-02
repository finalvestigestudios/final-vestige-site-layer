# Dispatch R59 — reader MIME envelope isolation and release-evidence integrity

**Campaign owner:** GitHub Issue #174; partner-guide owner: #171. Source is the original six manuscripts of DRAFT PR #175, with release controls in #201. This change stacks only on DRAFT PR #561 (exact parent 7479c62bd52f4591646f8c830d26289dad7c8bf7). Frozen homepage PR #49 is excluded. Prepared November 1, 2026 PT / November 2 UTC.

## Material defect: attached forwarded text could supply false legal evidence

The R58 inspector traversed every MIME leaf with email.message.walk() and rejected only text leaves whose *own* Content-Disposition said attachment. An attached RFC 822 email is a multipart-like container: its child text bodies do not carry the parent's attachment disposition. Python's standard email parser therefore exposes the nested text through walk(). Previously, a forwarded different message could contribute a financial disclosure, mailing address or unsubscribe link to the outer Final Vestige newsletter's analysis even when those elements were absent from the actual recipient-facing body. This is a genuine boundary failure for legal-evidence triage. It is NOT a claim that WordPress has sent such a message.

### Precisely scoped repair

1. Traverse only the *current* message's inline reader body. Stop at attachments, filename-bearing content, or embedded message/rfc822 subtrees (even when disposition is inline). Do not open, click, fetch, or return their contents.
2. Emit only fixed integer counts for skipped attached/named and inline-forwarded content. Flag ATTACHMENT_PRESENT_HUMAN_REVIEW or INLINE_FORWARDED_MESSAGE_IGNORED. Attachment content can never satisfy early disclosure, postal match, opt-out or seller-link evidence.
3. Flag messages with two plaintext or two HTML bodies as AMBIGUOUS_MULTIPLE_MIME_BODY_PARTS; do not certify commercial disclosure parity from a concatenation of variants that a real client might choose differently.
4. Flag duplicate Subject, From and List-Unsubscribe headers as AMBIGUOUS_DUPLICATE_MESSAGE_HEADERS; do not let the first parser-selected header masquerade as unambiguous sender/subject/opt-out proof.
5. Flag NO_READABLE_TOP_LEVEL_MESSAGE_BODY when the actual reader message has no readable plain or HTML content.
6. Preserve the public inspector API, all original tests and all other release holds. No inspection verdict can set send_allowed, legal_compliance_certified, founder_final_send_approval or unsubscription_functionally_verified to true.

## Synthetic adversarial proof to run, not a received email

The 34 added tests cover: attached message/rfc822 disclosures and hidden postal/unsubscribe; attached seller URLs; nested forwarded HTML; inline forwarded messages; named and inline-filename .txt/.html; attachment-only bodies; legitimate ordinary multipart/alternative; duplicate HTML/plain variants; duplicate sender, subject and opt-out headers; no-body cases; source privacy; canonical four-editorial/two-commercial integrity; and the permanent no-send guarantee.

The original defect is reproducible from Python's standard email parser alone: when an outer EmailMessage has a text body and an attached EmailMessage, invoking walk() yields a text/plain leaf inside the attachment; the child leaf has no attachment disposition. The new traversal refuses to descend into the parent attachment. The test runner MUST execute the committed suite against the exact new PR head in GitHub Actions; do not infer passing results from a test-count estimate. This inspector cannot model every email client's rendering. A real received Jetpack email remains necessary.

## Read-only live WordPress observation

At **2026-11-02 05:30 UTC**, authenticated site 256784396 returned newsletter enabled, site_can_send true, global new-post emails OFF, format excerpt, reply-to no-reply, sender name Final Vestige, and zero *recent* sends in this diagnostic response. The welcome text still contains the 52-page Seven Day Focus Fieldbook link, but delivery/receipt is not verified. The dashboard counters total=2, confirmed=2, unconfirmed=2, suppressed=0 are **non-additive** under WordPress.com subscriber semantics; never infer four people, or that every confirmed person is deliverable.

Published /dispatch/ (page ID 523) offers historical investigations, archive finds, one Jetpack list and the Fieldbook, but has less explicit commercial-notice copy beside signup than /focus/ (page ID 1579). Editorial Standards (page ID 17) demand original evidence, explicit uncertainty and commercial independence. No live page was changed.

WordPress's [newsletter preview documentation](https://wordpress.com/support/newsletter/email-appearance/), reviewed October 6, 2026, explains that native preview becomes available with the per-post SEND toggle enabled. The global default OFF does not stop an individually enabled send on publication. Founder has NOT approved editor-toggle changes, a real test email, post publishing or any campaign send. Thus **do not switch it on to obtain a preview**.

## FTC and actual product constraints

The [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful sender and subject, identification when commercial, a valid Final Vestige business postal address, functioning opt-out and timely honoring of requests. A static HTML placeholder or Automattic footer cannot replace the publisher's mailing-address verification or functional received-email QA.

The [official Zen12 named offer](https://zen12.com/hnp) advertises twelve-minute sessions, twelve levels, four sound styles, and 48 MP3s in a full bundle. Its claims of an hour's advanced meditation in twelve minutes, specific brainwave effects and mental/health improvements are **vendor representations, not independently established outcomes for that product**. The [official Hypnosis Live Total Focus offer](https://hypnosislive.com/mental-skills/total-focus) describes a 33-minute, 47 MB downloadable audio, and advertises broad concentration results. Those benefits are not independently verified for that recording. The indexed pricing presented in the current research differs from earlier live captures; actual cart prices, refund rules and payout conditions remain UNKNOWN. Do not cite a price, suggest a guarantee was tested or imply we personally used either product.

Public Inspire3 recruitment does not establish that Final Vestige has been approved for Zen12 or Total Focus, has permission to promote either named offer through EMAIL, owns reuse rights to merchant creative, or has a verified earning URL. Mind & Affiliate Studio's newest proposed presell guide in DRAFT PR #563 is unpublished and is **not** a safe live CTA destination. A newsletter should go to a future independently reviewed live buyer guide first, then only to a verified permitted affiliate link with an adjacent disclosure.

## Release decision and founder approval boundary

**ALL SIX newsletter editions: HOLD_UNSENT. Issues 03 and 05 additionally: HOLD_MERCHANT.** Preserve original draft six-week cadence, original editorial/commercial 4:2 allocation, source manuscripts, one commercial CTA per commercial issue and exact real-world proof gates. Before any release, obtain in separate authorized procedures: genuine received Jetpack HTML/plaintext, a valid Final Vestige postal address in that received email, functional unsubscribe, privately confirmed eligible recipients and consent, an approved published first-party guide, named-product written affiliate email rights and real tracked URL, and the founder's explicit final approval of issue, recipient audience, day and destination.

No emails or test emails, no WordPress editor operations, settings updates, posts, list imports, merchant/subscriber contact, affiliate links, tracking pixels, fabricated analytics, third-party subscriptions, or homepage changes are authorized. Closing this unmerged DRAFT PR reverses all proposed repository changes; no live rollback is required.

## Evidence references

- Campaign and controls: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174
- Product ownership: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171
- Parent PR: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/561
- Canonical manuscripts: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175
- Offline inspector tests: tests/test_r59_mime_envelope_isolation.py (34 synthetic unit tests)
- WordPress preview: https://wordpress.com/support/newsletter/email-appearance/
- WordPress settings/excerpt behavior: https://wordpress.com/support/newsletter-settings/
- FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Seller pages: https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus
