# Dispatch R55 — human-first FTC primary-purpose and named-offer truth audit

**HARD HOLD: six UNSENT; commercial editions 03 and 05 additionally HOLD_MERCHANT.** This is a new source-of-truth review layer, not a legal opinion, live Jetpack preview, send plan, substitute manuscript, or affiliate authorization. Owner [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion merchant owner [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Base [draft PR #532](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/532), canonical source chain begins [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175). The homepage remains priority one; frozen homepage PR #49 untouched.

## Why another readiness lens is necessary

The previous R54 package faithfully models Jetpack's 55-word fallback and detects absent commercial disclosures in that *model*. R55 addresses a different release issue: **What is the primary purpose of the complete email the recipient actually sees, and do the specific named seller's claims match the specific guide and proposed commercial offer?** A source-code keyword match cannot decide that legal question, especially with mixed historical reporting and product recommendations.

The FTC states that CAN-SPAM's commercial-message definition is based on the **primary purpose**. A message can be commercial even though it contains substantive original reporting and its subject avoids the word "sale." Relevant factors in a mixed message include subject-line interpretation, placement and proportion of promotional content, and prominence of design treatment. Conversely, a strictly original historical investigation does not automatically become an advertisement merely because the publisher has an affiliate business. Human review must inspect the final *received* content, not just a type label in JSON. The FTC also warns that content promoting a commercial website can be commercial in relevant contexts. Official source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

**Policy for this six-part pilot:** treat editions 03/05 as requiring *commercial-purpose legal review*, not as automatically certified compliant simply because they carry a disclosure. Treat 01/02/04/06 as editorial/mixed-purpose **human review required**, not automatically exempt from postal/opt-out rules. For the final signoff, conservatively ensure qualifying postal and unsubscribe information is present in any commercial or uncertain message. This document cannot establish what the law ultimately classifies a particular final send as.

## Independently inspected live production snapshot — 2026-11-02 UTC

- Authenticated site ID **256784396**: Jetpack Newsletter enabled, `site_can_send=true`, new-post automatic email `false`, email format `excerpt`, sender name “Final Vestige”, no-reply setting, published /dispatch/ page 523 and /focus/ page 1579, published Editorial Standards page 17.
- The welcome template still contains the **52-page Seven Day Focus Fieldbook** URL, but no actual received current welcome MIME was verified. WordPress uses `donotreply@wordpress.com` for newsletter post notifications; the visible sender name alone does not prove a publisher's legal postal address.
- Counts remain `total=2, confirmed=2, unconfirmed=2, suppressed=0`. **Do not sum them, imply four people, or infer two deliverable opted-in readers**. The returned connector has aggregate status only, not a proof of distinct subscriptions. Reconciliation must occur privately through an authorized WordPress administrator's filtered subscriber view.
- `recent_sends=[]` means no sends returned in that diagnostic window; it does **not** prove no messages were ever sent.
- /dispatch/ promises investigations/archives and the Fieldbook but lacks a near-form note about occasional commission-supported reviews. /focus/ already includes a commission notice. A copy treatment is proposed separately in earlier R52 PR; nothing changed here.
- Connected mailbox read-only searches on this run uncovered the prior **2026-10-25 subscription confirmation**, but not a genuine final welcome or Dispatch send, nor named-product/publisher **EMAIL** approval. No subscriber identities, tokens, or MIME are committed.

WordPress references (current October 2026 revisions): https://wordpress.com/support/newsletter-settings/ ; https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://wordpress.com/support/subscribers/

**Important per-post hazard:** even though the global default is OFF, a post can be individually marked “Send this post to subscribers.” The official native Preview email UI appears only when that per-post send toggle is ON. It is not a safety-neutral button. Do **not** enable it without separately recorded preview authorization and verified OFF-after; never use it to test-send absent a distinct recipient-specific founder approval.

## The six original editions: human copy and purchase-path review

| # | Exact canonical subject (current stacked branch) | Main promise and original CTA | Primary-purpose queue | Highest-impact remaining issue |
| --- | --- | --- | --- | --- |
| 01 | The mind is not a camera | 1998 pedestrian change-blindness field work to published *The Missing Caption* | Editorial/mixed human review | Formal email title is subject; separately supplied Markdown “Preheader” is **not a verified native Jetpack preheader setting**. Actual excerpt/CTA visibility unknown. |
| 02 | Before hypnosis had a name | Puységur's primary-source dossier and historical evidence literacy | Editorial/mixed human review | Historical *royal commission* is **not** an affiliate financial disclosure. Avoid describing reconstructed testimonies as verified mesmeric effects. |
| 03 | The twelve-minute meditation question | Free self-observation exercise then proposed *Zen12* buyer guide | Commercial-purpose human review | Current original source retains **two clickable seller citations**; the buyer guide is **not approved/live**; fallback excerpt hides commercial disclosure; named-product email permission absent. Do not place seller checkout anywhere in send-ready version. |
| 04 | Seventeen seconds. A much longer explanation. | Apollo 1 records, sources and published *The Hatch Opened Inward* | Editorial/mixed human review | Preserve precise interpretation: 17.1s spans first recorded fire report to end of last transmission, **not confirmed ignition duration**. NASA did not conclusively determine one first electrical arc. |
| 05 | Before you press play on a hypnosis audio | Consumer decision checklist and proposed *Hypnosis Live* guide | Commercial-purpose human review | **Offer specificity gap:** body speaks of broad Hypnosis Live catalog while planned offer is a particular **Total Focus** SKU. Candidate R51 better aligns SKU; neither unapproved alternative nor guide is a published destination. |
| 06 | What did seven days of attention reveal? | Seven-day observation log via live /focus/ | Editorial/mixed human review | The Fieldbook already features in the welcome; distinguish this editorial assignment from a second lead-magnet promotion. Do not imply measured efficacy or fabricate subscriber results. |

### Copy-conversion conclusions

An evidence-first lead is not the enemy of conversion. The strongest legitimate action in this pilot is **one useful action the reader can confidently take**: verify a photo, follow a dated archival trail, log attention practice, or read an honest first-party product evaluation. Products 03/05 should not draw the reader directly to seller checkout: this bypasses Final Vestige's promised independent analysis and is premature without permission.

**Subject/preheader boundaries:** A Markdown preheader is an editorial annotation; it has not been shown to populate a dedicated Jetpack preheader field. Native WordPress uses the post title as the notification subject. Do not claim that proposed preview text will appear in inbox search lists until actual received MIME is examined. Avoid urgency, false guarantees and "we tested it" unless a real test occurred. Do not use artificial statistical confidence with this audience size.

**One-CTA policy:** the primary editorial CTA should direct to one *approved, published first-party destination*. Citations to independent historical records are not extra product CTAs. For 03/05, nonclickable merchant source references are preferable in a *proposed review draft*, but a founder must approve any substitution. The R50 version of 03 and R51 version of 05 remain **optional**, not silently installed.

## Exact-offer public findings, not company-level assumptions

### Zen12 — https://zen12.com/hnp

On its official sales page, the seller describes twelve-minute MP3 sessions, twelve levels and four listening styles. Its twelve-minute-to-one-hour equivalence, automatic deep meditative state and brainwave-related benefit statements are **seller promises, not independently demonstrated Zen12 outcomes**. The page advertises a one-year refund promise, but whether that exact promise applies to a buyer's current cart, geography, promotion, and checkout has **not** been verified. A full tier and format description must not be used to promise that every lower-tier purchase includes the complete library. Source also references https://zen12.com/getstarted .

### Hypnosis Live Total Focus — https://hypnosislive.com/mental-skills/total-focus

The seller presently describes an MP3 labeled **33 minutes, 47 MB**, credited to J.A. Amos, and advertises concentration improvements. No independent product-specific efficacy proof for the strong cognitive/brain-reprogramming assertions was established in our source review. The publicly accessible page shown in a fresh November 2 retrieval displayed **$2 compared against $29.95**, while a separate older indexed result showed **$17.95 against $22.95**. Those are **different website captures**, not a controlled A/B test, proof of personalization, a guaranteed current discount, or a confirmed checkout total. Accordingly **do not quote any price, discount or refund term in send-ready copy**. The public page also displays a 14-day guarantee claim; applicability to a real transaction remains unverified.

### Affiliate permission — https://affiliates.inspire3.com/

The public network recruitment page mentions **Zen12** among the operator's brands and offers a sign-up path. This is evidence of a marketed affiliate network, **not evidence that Final Vestige was accepted, that these named SKUs were enabled, or that EMAIL-channel promotions are authorized**. Public `https://inspire3.com/ll/` swipe copy is for **Limitless Labs**, a different offer. Do not use its creatives, terms or links as proof of permission for either newsletter slot. Under FTC endorsement guidance, conspicuous material-connection disclosure belongs beside a qualifying earning link in the first-party guide as well as in its relevant newsletter. Sources: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

## Proof handoff — what is actually missing

**WordPress/site owner:** privately reconcile distinct confirmed and email-eligible recipients (do not export names); designate a legitimate **Final Vestige** street address, registered USPS PO box or qualifying commercial mailbox as allowed by FTC rules; validate that a real commercial received email includes it and a functional unsubscribe mechanism. The Automattic / Inspire3 corporate postal address is **not** a substitute for the publisher.

**Preview operator, after specific founder preview-only authorization:** record exact post, draft state, exact source revision, global default OFF, per-post OFF before; enable native preview only if separately permitted; record desktop/mobile native rendering and per-post OFF afterward; ensure still unpublished. A separate **test-send authorization** naming a test recipient is required before obtaining and inspecting actual raw RFC 5322 MIME. A previous subscription confirmation proves neither welcome delivery nor commercial footer behavior.

**Mind & Affiliate Studio / partner owner:** obtain Final Vestige-specific written acceptance for **each product and EMAIL use**, allowed publisher identity, exact earning URL/link rules, licensed creative rights, permitted claims, current checkout/refunds and a **live approved first-party guide**. Current Mind guide PRs are draft-only, never use their imagined URLs as active CTAs.

**Founder final approval:** specify approved exact creative/manuscript/excerpt, audience, date, legal-footer evidence and commercial editions separately. The six original issues and 4:2 allocation remain untouched until then. No automation, source test or agent may infer that approval from the existence of a welcome email or a passing QA suite.

## What this new executable does—and does not do

`python -I dispatch/campaign-2026-mind/r55-primary-purpose/review.py --strict` emits a read-only JSON risk report. It parses canonical manifest and all six original issue files from the *current stacked branch*, maps the modeled first-55-word text to manual primary-purpose review, checks exact subject/preheader/CTA, counts direct seller citations, detects dollar figures in narrative, preserves all hard holds and rejects self-attested merchant approval. It uses Python's standard library, no network, no WordPress/Gmail calls and no subscriber data.

The tool **cannot determine legal classification**, guarantee a 55-word Jetpack rendering, infer actual welcome receipt, check unsubscribe functionality, or prove any affiliate approval. A `source_errors=[]` result does **not** change `send_allowed=false`. Test suite: `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v` on exact PR head.

No WordPress publication, post toggle, subscription import/export, message draft/send, merchant inquiry, pixel, new mailing provider, analytics collection, paid service, homepage change or production deployment in this sprint.
