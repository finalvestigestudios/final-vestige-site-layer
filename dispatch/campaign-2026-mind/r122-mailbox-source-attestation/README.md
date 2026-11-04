# Dispatch R122 — source-attested, inert mailbox review specimens

2026-11-04 | Dispatch Studio | NOT A DISTRIBUTION SYSTEM | All six issues HOLD_UNSENT; #03 and #05 additionally HOLD_MERCHANT.

## The newly detected provenance defect

R116's offline HTML/plaintext preview generator hard-codes original master SHA d57ccdba3aee8f065e143e101c2945f4f3d01647 into its audit JSON, irrespective of which checkout supplies the manuscripts. The six current stacked manuscript Git blob hashes differ from those on original #175 (R121 proves all six changed). Thus the source_commit field in a fresh R116 render is **not reliable provenance** and cannot prove that an output contains master-approved copy. This is a derived-preview metadata defect, NOT evidence of a production send.

R122 does NOT alter R116 or the original manuscripts. Its Python verifier independently computes the actual Git blob SHA-1 of each of the six manuscripts and checks R121's source-by-source audit ledger. Reviewers must explicitly select master or stacked snapshot. Any mismatch in source blob, subject/preheader, issue order, 4-editorial/2-commercial allocation, active merchant link or publishing state stops the build. The proof marks R116's hard-coded SHA as an untrusted legacy claim.

## A real new QA surface: RFC822 alternatives without sending

For a checkout whose six files match the attested selected snapshot, the generator produces six RFC822 .eml inbox specimens containing real MIME text/plain + text/html alternatives from the existing R116 offline renderer. They are suitable for LOCAL mailbox-rendering inspection, not production. There is no SMTP/network operation, WordPress write or subscriber address. Each MIME has no To/Cc/Bcc, no Return-Path, an invalid-domain QA sender, subjects prefixed [UNSENT FIXTURE], both-body warning text, and an explicit automated-sending-not-allowed header. The absence of a real List-Unsubscribe is intentional: a fake header would create a false compliance claim.

From a full local checkout of this branch:
    python -m unittest discover -s dispatch/campaign-2026-mind/r122-mailbox-source-attestation/tests -v
    python dispatch/campaign-2026-mind/r122-mailbox-source-attestation/mime_review.py --snapshot stacked --out /tmp/fv-r122-qa

The output includes 01-INERT-UNSENT.eml through 06-INERT-UNSENT.eml, inherited offline HTML/plain files and source-verified proof.json. Calling --snapshot master on the stacked branch is intentionally rejected. PR #175 alone lacks R121 audit and R116 renderer; never claim the stack is the original master.

Twelve native local synthetic tests check hash algorithm, snapshot differentiation, source mutation, subject drift, status and allocation changes, activated merchant links, missing body alternatives and no-recipient mailbox structure. A full source-attested end-to-end build requires an actual branch checkout. The generated MIME is NOT a genuine received Jetpack message or a verified real-email client rendering.

## Latest actual operational evidence, read-only

WordPress newsletter.status at 2026-11-04 21:29:59 UTC reports total=3, confirmed=3, unconfirmed=2, suppressed=0, imported_last_24h=1. These counters are nonadditive; they do NOT establish a newly opted-in human, valid source attribution, consent, a reachable inbox or a paid lead. The last five posts returned never_sent_opted_out because send_subscription=false; no email failed or was actually sent.

WordPress newsletter.get_settings at 21:30:02 UTC: Newsletter ON, new-post automatic email OFF, excerpt format, reply-to no-reply, sender display Final Vestige, configured welcome with existing Focus PDF. A media read verifies PDF record 1737, application/pdf, registered file size 599946 bytes. Public PDF retrieval through web failed during R122, so opened PDF and page count are unverified. Neither a WordPress media record nor a configured welcome message proves inbox delivery.

Narrow read-only Gmail queries located one October 25 Final Vestige subscription confirmation, but no completed Fieldbook welcome in the queried messages. The result is not an exhaustive absence finding. An October ordinary Inspire3 promotion was NOT named Final Vestige affiliate acceptance, written email-promotion permission or proof of a paid order. No subscriber identities were exported or disclosed.

## Legal, product and conversion release gates

FTC CAN-SPAM guidance (https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires accurate sender details, truthful subjects, valid publisher postal address, usable opt-out and prompt opt-out processing for commercial messages. Automattic's postal address from its confirmation email is NOT Final Vestige's publisher address. Offline previews are not sufficient: acquire and review a genuine, appropriately authorized Jetpack delivered message with real footer and unsubscribe before release.

Official seller Zen12 https://zen12.com/hnp describes 12 levels, 4 audio styles per level, 48 Premium MP3s, and advertises twelve minutes as comparable to an hour. That claimed equivalence and cognitive efficacy have NOT been independently substantiated for this exact product. Official Total Focus https://hypnosislive.com/mental-skills/total-focus describes 33 minutes and 47 MB plus promoted benefits; these are seller representations, not independently established product-specific outcomes. Exact seller checkout price and refunds may vary. General portal https://affiliates.inspire3.com/ does not establish named Final Vestige acceptance or permission to advertise by email.

Mind & Affiliate Studio Issue #171 owns the approved first-party buyer guide and merchant eligibility. ONE provisional offer hypothesis is Zen12 for reserved Issue03. Issue05 remains unapproved and inactive. Both require an honest, close-to-offer commission disclosure if ever activated. No direct affiliate link is included or approved here.

Grok / Praxxis TASK-008 owns creator asset_id and approved social UTMs (utm_source actual channel, utm_medium organic_social, utm_campaign topic_cluster_pilot_2026_11, utm_content verified asset_id). Dispatch recommends deduplicated confirmed_signup only with native consent and confirmation proof. An observed subscribe form submit is not an independently verified subscriber. Claude is engineering and analytics owner; do not add duplicate scripts or circulate subscriber PII.

One paid conversion means authoritative settled Payhip order or a merchant-reported paid affiliate settlement. The sales count is not derived from email clicks, downloads, follows or signup counts. Fees and refunds must be deducted to compute 7/30-day realized net revenue per 1,000 qualified-human visits. That KPI remains NOT COMPUTABLE, not zero.

## Priority acceptance matrix: OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

1. Fieldbook → confirmed lead → reported 3/3/2 subscribers and one import lack consent/reachability provenance → privately reconcile native eligibility and opt-in source → NOT VERIFIED → Dispatch/Claude.
2. Welcome → Fieldbook access → configured only, no received welcome and PDF open proof → authorized received-message and link/PDF inspection before any public claim → NOT VERIFIED → Dispatch/QA.
3. Editorial → inbox → source drift and hard-coded renderer SHA → independently hash-verify sources and review no-send MIME; then obtain genuine Jetpack email preview, real subject/excerpt/footer → BUILT + synthetic tested / TRANSPORT NOT VERIFIED → Dispatch/QA.
4. Zen12 guide → purchaser → named partner/email promotion permission, live buyer guide and buyer/privacy terms absent → Mind Studio official approvals and authorized first-party guide → HOLD_MERCHANT → #171.
5. Grok → realized net → no source-matched settled orders/refunds/fees → independently reconcile paid settlements and qualified visits → NOT COMPUTABLE → Claude/Praxxis.

## Firm exclusions

No emails (including tests), scheduling, WP publishing or settings, subscriber import/contact, affiliate activation, new email platform, spending, social posting, analytics scripts, payments, PR merge or deployment. Homepage PR #49 stays frozen. Original six draft manuscripts and four editorial / two commercial reservation remain unchanged. Founder must approve exact canonical copy, actual channel, audience and schedule before any future send.
