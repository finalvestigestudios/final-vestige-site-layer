# Dispatch R266 — Fieldbook delivery, consent and buyer-path verification

**DRAFT ONLY / UNSENT / NO PRODUCTION WRITES.** Owner: Dispatch #174, Mind #171, Focus #129, conversion #820. Stacked on Dispatch R265 PR #1951. The founder's six original newsletter issues (#175) and the readiness PR (#201) are not changed. Homepage PR #49 remains frozen.

## Material new evidence: actual registered Fieldbook asset and matching configured URL

Authenticated WordPress read-only observations on 2026-11-10 at approximately 22:35–22:36 UTC establish three identical URLs:
1. The full publicly displayed 52-page Fieldbook link embedded in the Jetpack welcome message.
2. The published /focus/ page's download link.
3. WordPress media item #1737 source URL, with mime_type application/pdf and a recorded size of 599,946 bytes (registered 2026-10-29).

Exact matching URL:
https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf

**Classification: CONFIGURED / MEDIA REGISTERED. Not VERIFIED PDF DELIVERY.** The public web retrieval tool returned cache miss for the direct PDF, which is INCONCLUSIVE, not proof of an HTTP 404; WordPress media metadata does not prove download success, internal page count or attachment content. Actual received welcome remains unproven. Do not report a 52-page binary verification from this evidence alone.

Jetpack remains enabled, auto-new-post email OFF, full content mode, sender Final Vestige Studios, reply-to no-reply. Latest five inspected posts are never_sent_opted_out; they were not delivered. Counters are total=3, confirmed=3, unconfirmed=2, suppressed=0; separate follower breakdown email=0, WordPress Reader=3, partial=false. These are different populations, cannot be added or subtracted, and do not disclose the private provider-filtered Email subscription=Subscribed population. **Recipient eligibility UNKNOWN.**

## Previously overlooked conversion friction: repeat-signup instruction

The live /focus/ troubleshooting text currently says, if an embedded social app cannot open a PDF, use Safari or Chrome and "sign up again." That may create duplicate signup attempts, confound the lead conversion denominator, and give readers the impression they must resubscribe to retrieve the already linked PDF.

**Proposed change ONLY; do not publish without founder/site owner approval:**
"Some social apps cannot open PDFs inside their built-in browser. Open this page in Safari or Chrome and use the download link above. If you already subscribed, you do not need to sign up again. Your welcome email should contain the same link once you confirm your subscription."

Keep the download available without pretending it is a confirmed subscription. A click on this PDF is not an email confirmation, affiliate click or paid order.

On /focus/, signup language explains occasional commission-earning recommendations; /dispatch/ describes research and free guide without that explanation. Existing R260 draft copy harmonization remains NOT ADOPTED; new subscriber consent cannot be retroactively inferred.

## Executable non-sending release integrity contract

Files:
- observed_snapshot.json: deliberately non-PII authenticated observation, every external proof UNKNOWN.
- delivery_parity.js: pure JS, no network or side effects. Confirms exact media/welcome/Focus link parity, WordPress identities, sender/default auto-email safety, observed subscriber copy mismatch and nonadditive counters. Rejects empty gates, unrecognized proof keys, unexpected potential PII, wrong host/HTTP URL, fake confirmation, altered labels. Always HOLD_UNSENT even when syntactically valid proof records exist.
- verify_delivery_parity.test.js: synthetic adversarial cases executable with native Node. No live subscriber, merchant or payment data used.

The audit deliberately calls a matching WP media record OBSERVED. It NEVER calls it proof of PDF response, 52 pages, inbox receipt, subscriber opt-in, legal unsubscribe or active revenue. All external attestations remain NOT INDEPENDENTLY VALIDATED until source documents are inspected by the accountable owner.

## New official merchant claim/terms reconciliation (2026-11-10)

1. Zen12 primary sales page: https://zen12.com/hnp. The seller describes 12-minute sessions, audio brainwave entrainment and assorted well-being/focus outcomes; **seller advertising is not Zen12-product-specific independent efficacy evidence**.
2. Zen12 vendor free audio route: https://zen12.com/freeaudio redirects to https://zen12.com/gift, where the seller says customers will receive **its newsletter**. This is a separate merchant email relationship, not Final Vestige consent.
3. Hypnosis Live Total Focus exact seller page: https://hypnosislive.com/mental-skills/total-focus, describes 33-minute / 47-MB MP3 and displays variable sales/bundle pricing; avoid price promises.
4. Hypnosis Live https://hypnosislive.com/faq: the general FAQ states a typical $22.95 session price (different from the displayed Total Focus offer); the advertised 14-day refund also carries a maximum of **five refunded sessions per year**. Do not repeat an unqualified "risk-free" guarantee. Claiming 100% concentration or scientifically proven brain reprogramming would be unsupported.
5. The general affiliate portal does NOT establish Final Vestige's own approval, channel-specific email rights, exact allowed earning link, landing page, refund/price applicable to that link, or paid commission. **Commercial Issues 03/05: HOLD_MERCHANT.**

FTC CAN-SPAM guidance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business. Primary commercial purpose requires truthful headers/subjects, identification, **Final Vestige's valid postal address**, and functional recognizable opt-out. An Automattic or vendor postal address is NOT a substitute. Exact delivered Jetpack HTML/plaintext footers and unsubscribe mechanism remain untested. WordPress support https://wordpress.com/support/newsletter/send-newsletter-emails/ describes preview without sending, but an editor preview does not replace a received-message QA. Subscriber guidance https://wordpress.com/support/subscribers/ distinguishes Reader subscriptions, pending, bounced and paused status from actual Email subscription=Subscribed.

## Single-buyer-path acceptance, not more email volume

**Candidate offer:** Zen12 only after authorization; preserve four editorial/two commercial planned allocations, with Hypnosis Live as second reserved but disabled offer. Relevant journey: verified existing Grok creator asset_id and canonical UTM -> public sourced investigation -> free Focus Fieldbook -> provider-confirmed Jetpack subscription -> Dispatch editorial value -> vetted, first-party pre-sell review -> specifically approved outbound affiliate link -> independent merchant settled commission -> refund/fees -> realized net revenue per 1,000 qualified human sessions. Do not make a free download conditional on consent, and do not count any merchant signup or click as a Final Vestige sale.

| OFFER -> FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Zen12 -> buyer | Named FV account acceptance, email permission, allowed URL and approved guide missing | Mind authenticates all items and exact merchant checkout/refund/price | HOLD, no earning URL | Mind #171 |
| Fieldbook -> confirmed lead | Provider-filtered email-eligible count and consent provenance unknown | Private only Email subscription=Subscribed aggregate and dedup; no addresses | UNKNOWN; diagnostic 3/3/2, followers 0/3 | Focus #129 + Claude |
| Focus -> free PDF | Embedded-app "sign up again" wording, no independently fetched PDF/52 pages | Review UX text, controlled end-user browser PDF fetch and content verification | Configured URL match OBSERVED, delivery UNKNOWN | Focus + Dispatch QA |
| Dispatch -> inbox | Native final MIME, publisher postal address and working unsub not verified | Specifically authorized non-sending preview, separately authorized controlled received-mail test | HOLD; no emails sent | Dispatch QA / founder |
| Buyer -> realized net | No verified source-tagged human sessions, paid settlements, fees/refunds | Use R265 privacy-safe 7/30-day acquisition-cohort audit against authenticated owner-reported records | NOT COMPUTABLE, not zero | Praxxis / Commerce #820 |

## Independent test limitations

Passing native/offline unit tests validates parsing and fail-closed behavior on fixtures only. It does not establish live end-user PDF downloading, confirmed signup, mail receipt, unsub functionality, merchant permission, paid checkout or a single sale. Source code cannot on its own satisfy legal, recipient or merchant evidence. Any positive proof must have a source identifier, a human verification process, and separate founder final campaign approval before even considering sending.

**Final:** ALL SIX HOLD_UNSENT; ISSUES 03 AND 05 HOLD_MERCHANT. No WordPress changes, sending, test emails, subscriber contact, import, partner activation, social posting, spending, publication, PR merge or deployment.
