# Dispatch R45 — Real received-email evidence gate
**November 1, 2026 · isolated, unmerged DRAFT · master Issue #174, Mind & Affiliate Issue #171**

This iteration addresses a gap no amount of static HTML, mocked email, AI-based copy editing or passing Python tests can close: **we have never examined a genuinely received Final Vestige Jetpack Dispatch email.** This folder adds a **local-only, read-only RFC 5322/MIME email inspection utility** and 49 synthetic adversarial unit tests. No email has been sent, test-sent, imported or scheduled. The original founder-approved four editorial / two commercial drafts are preserved in canonical PR #175. This branch is stacked on #466, not on the frozen homepage PR #49. The independently maintained edition readiness PR #201 is also unchanged.

## Current verified production status, 2026-11-01 15:39 UTC
Authenticated WordPress read-only diagnostics for site 256784396:
- Newsletter subscriptions are enabled and WordPress reports technical ability to send. That **does not** grant permission to send.
- Automatic emailing of newly published posts remains OFF; email_content_format=excerpt; featured images and post dates in outgoing newsletters ON; display sender name Final Vestige; reply-to no-reply.
- The welcome message is configured to include the **52-page Seven Day Focus Fieldbook** hosted PDF. This configuration is NOT proof that an inbox actually received that complete welcome.
- recent_sends=[] means **no reported recent sends**, not demonstrably zero lifetime sends.
- total=2 / confirmed=2 / unconfirmed=2 / suppressed=0. These counters are nonadditive and contradictory as a simple audience breakdown; do not claim four total or two independently eligible contacts. Consent and deduplication remain a private human WordPress verification task.
- WordPress pages read unchanged: /dispatch/ ID 523, /focus/ ID 1579, and /editorial-standards/ ID 17. The published standards demand original primary-source research, precise numbers, transparent uncertainty, accurate corrections, and independent financial relationships.
- Read-only mailbox queries found Inspire3 **consumer marketing**, not product-specific Final Vestige publisher acceptance or contractual permission to market Zen12 or Total Focus via EMAIL. The prior October 25 WordPress subscription confirmation is not the completed welcome or a sent Dispatch issue. No subscriber identities, mail tokens, raw messages or personal email addresses were recorded in this repository.

## What this development delivers
- **received_email_gate.py:** stdlib-only offline interpreter for local MIME/EML; independently checks the plain and HTML alternatives for disclosure, mailing-address text and unsubscribe instructions so one complete alternative cannot mask omissions in another. It decodes text/plain and HTML content, compares actual subject against an operator-supplied expected WordPress post title, examines displayed sender name, flags internal drafting banners, checks the presence (not functionality) of unsubscribe links/headers, compares an **operator-supplied** mailing-address string without ever revealing it, and reports potential remote 1×1 images.
- Links in actual MIME parts are audited for direct Zen12 / Hypnosis Live / Inspire3 seller domains, subdomains, encoded redirect wrappers and executable link schemes; it does not remove or rewrite live links.
- For issues 03 and 05 only, it records whether a commission disclosure appears and whether the operator's hypothetical first-party buyer-guide URL is actually present. Merely appearing in a message DOES NOT prove that a guide is live, approved or sale-safe.
- **Synthetic test suite:** malicious links, encoded redirects, fake sender, invalid subject, absent disclosure, missing address, provider's own address mistaken for ours, unsub header but untested functionality, disclosure hidden in HTML script, private token leakage, internal DO NOT PUBLISH banner, MIME variants and more. All assertions remain release-blocked.
- **EVIDENCE_READINESS.json:** public-safe WordPress snapshot and all-false operational attestation flags. Neither the snapshots nor the validator handle raw subscriber data.
- **REVIEW.html:** accessible static operator summary; no JavaScript, tracking, forms or merchant CTA.

## Use ONLY after a separately authorized, privately controlled inbox test
This is a tool to evaluate a future legitimate received artifact, not permission to generate one. Founder must separately approve test edition, owned recipient, exact content/post settings, use of Jetpack, timing and any necessary test send. Sending an email, even to oneself, was **not** approved by the draft-campaign directive and has not occurred.

1. An authorized operator obtains the original delivered email in their *private* inbox after that separately approved test and saves the original .eml outside the repository and all shared artifacts. No subscriber export or import is necessary.
2. Privately verify the actual Final Vestige commercial mailing address, if one exists; never reuse Automattic's or Inspire3's mailing address as Final Vestige's.
3. Set a private local environment variable FV_DISPATCH_MAILING_ADDRESS to that founder-verified address, without writing it into shell command history or source control. It must contain the actual approved address, not the synthetic test address.
4. Run this command from within dispatch/campaign-2026-mind:

       python r45-received-proof/received_email_gate.py /private/received.eml --issue 3 --expected-subject "Actual WordPress post title"

   The --expected-guide argument can optionally be added **only as an expected comparison string**, not a live promotion. It will never turn a commercial issue send-ready.
5. The tool writes only status/count/boolean JSON to standard output: no To/From addresses, URL tokens, raw subject, body, postcode or private postal string. Do not upload the raw MIME message or link-bearing HTML to GitHub. Manual private visual inspection in the email client is additionally required.
6. Actually exercise the newsletter's unsubscribe/opt-out on an **authorized controlled recipient** and confirm it takes effect; a List-Unsubscribe header or visible link is *not functional proof*. Save only a non-identifying private attestation of this procedure. Reconcile distinct consent-eligible subscribers privately using WordPress Subscriber controls before any mailing decision.
7. Source identity, mailbox authenticity (e.g. trusted DKIM/SPF headers), native preheader, subject spoofing, footer address legal validity, recipient consent, content delivery, link reachability and true opt-out functionality are **not** established by this parser. An invented .eml can pass text inspections; therefore the returned actual_received_message_verified flag is **always false**.

## Specific official merchant alignment, current read November 1, 2026
**Zen12** official product page: https://zen12.com/hnp . The seller advertises a 12-minute listening format; four styles; first-six-level Beginner 24 MP3, all-twelve Premium 48 MP3 and last-six Advanced 24 MP3. It also advertises a one-hour-meditation equivalence, brainwave entrainment and health/focus benefits, plus a year-long money-back guarantee. These are **seller claims** and web-displayed terms, not independently demonstrated product results, live-checkout/refund evidence or Final Vestige authorized promotional claims.

**Hypnosis Live Total Focus** official product: https://hypnosislive.com/mental-skills/total-focus . Its listing specifies **33 minutes and 47 MB**, and currently presents a "$2" promotional price alongside "$29.95" crossed-out price and an advertised 14-day refund. The public sales page's alleged brain reprogramming and productivity improvements are **not independently substantiated for this specific audio**. The displayed promotion may vary and has not been independently validated at checkout. **Do not insert price or refund language into the newsletter without contemporaneous final verification.**

**Inspire3 Limitless Labs** affiliate page: https://inspire3.com/ll/ . It advertises mailing swipe copy, but its own page requires an approved partner and covers **Limitless Labs**. This is neither a signed acceptance for Final Vestige nor a Zen12/Total Focus EMAIL-rights grant. Never convert unrelated public creative into invented partner approval, earnings, allowed link formats or a product efficacy endorsement.

**Campaign clickpath:** The existing original Issue 03 includes six live ordinary merchant hyperlinks across Markdown, preview HTML and Gutenberg transfer blocks (two distinct purchase-capable seller URLs repeated); the R44 route guard flags them. Their lack of an earning parameter does not make an unreviewed direct merchant journey satisfactory. The original Issue 05 has no direct merchant hyperlinks in its matched representations. Independent Mind Studio Zen12 guides in PRs #456, #464 and #469 remain **unmerged unpublished drafts**, not usable outgoing newsletter URLs; Total Focus's guide also remains unpublished. Do not send readers to inactive warm-up pages or use direct merchant workarounds.

**Official technical/legal:** Jetpack's newsletter help (updated 2026-10-28) documents an email no-custom-excerpt fallback of **350 characters**, rather than the generic WordPress **55-word** excerpt model; neither tells us the actual email MIME or mobile inbox rendering. https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ . The FTC CAN-SPAM compliance guidance requires truthful sender identification and subject, a real physical business mailing address and functional opt-out for commercial mail: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . The prudent editorial gate checks these fields across all six potential mails without pretending a legal decision has been made for every editorial issue.

## Release evidence still missing — ALL SIX HOLD_UNSENT
1. Founder-approved REAL Final Vestige mailing address and actual email footer containing it.
2. Separately authorized actual Jetpack received-email proof and demonstrated functional opt-out.
3. Private deduplication and eligibility/consent reconciliation (total 2 / confirmed 2 / unconfirmed 2 is not an additive count).
4. Genuine welcome-message delivery confirmation, not merely its configured text or a prior subscription confirmation.
5. Published, founder-approved, evidence-aligned first-party Zen12 and Total Focus guide pages, after Mind Studio independent QA.
6. Written exact-SKU affiliate/publisher acceptance AND explicit EMAIL-channel permission, allowed creative/link tracking format, current checkout and refund terms, and substantiation/exclusion of product-specific outcomes.
7. Independent founder final approval of exact newsletter content, audience and weekly send dates.

**No emails, test emails, posts, scheduling, subscriber contact, list imports, WordPress settings or new platforms, paid products, analytics trackers or merchant links were created or activated in R45.** This is engineering evidence intake only; homepage flagship remains priority one.
