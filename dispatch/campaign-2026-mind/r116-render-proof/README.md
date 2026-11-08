# R116 — Original six-letter offline inbox review and conversion decision

**Owner:** FV Dispatch Campaign Studio · **canonical:** [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) · **partner decisions:** [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) · **Focus:** [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129) · **revenue:** [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).

**Status:** BUILT / LOCAL TESTED / NOT LIVE / UNSENT. Branch is stacked on R115 [draft PR #950](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/950); this package changes **only new r116 files** and leaves all six original letters, [master PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), readiness PR #201, final public content, homepage PR #49, account settings, subscribers and Grok's production queue untouched.

## Why this is different from the static reviewer boards

Previous sprints created preflight contracts, proposed alternate copy and static summaries. R116 starts **with the six actual original Markdown manuscripts**, rather than writing a seventh email or displaying substitute fragments. It creates twelve full-body **offline** HTML/plaintext candidate views (plus an index/audit), with the source subject/preheader, copy, source links, and conspicuous legal-and-merchant holds. This is reproducible native-Python transformation, not a WordPress service call. It allows a founder/editor to review exactly what the original campaign *says*, with mobile width QA, before choosing which already-proposed corrections to adopt.

### Reproduce without sending

At repo root, run:

```sh
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
python -I -m unittest discover -s dispatch/campaign-2026-mind/r116-render-proof/tests -v
python dispatch/campaign-2026-mind/r116-render-proof/build_offline_previews.py /tmp/fv-dispatch-r116
```

Then open `/tmp/fv-dispatch-r116/index.html` locally. The output includes 01–06.html, 01–06.txt, audit.json, index.html. It uses **no external packages**, signups, HTTP calls, SMTP, Jetpack API, unsubscribe execution or recipient identifiers. HTML contains no scripts, images, pixel beacons, forms or external merchant links. Candidate first-party links only point to `https://finalvestige.com/`. The merchant-guide tokens remain inert. All emails visibly say **HOLD — REVIEW ONLY — NOT A JETPACK EMAIL** and include unresolved compliance placeholders.

The source SHA is pinned to the exact master PR #175 commit `d57ccdba3aee8f065e143e101c2945f4f3d01647`. The output is not intended to reproduce WordPress.com's MIME wrapper, its real preheader behavior, excerpt truncation, one-click unsubscribe, delivery, promotional classification or physical footer. A real authorised editor Preview Email and an approved *received* email must still be separately inspected before any campaign release. **Do not upload these previews to WordPress or send them.**

## Hard-hitting conversion and editorial review — November 4, 2026

**What works:** Original Issue 01 opens with a meaningful archival/perception bridge. Issue 02 asks three verifiable questions about witnesses. Issue 03 offers a free, low-pressure meditation trial before mentioning any product; Issue 05 applies buyer skepticism rather than merchant hype. Issue 04 retains the historical-investigation identity. Issue 06 encourages an evidence log without inventing outcomes.

**What fails today:** Both commercial guides are placeholders, not published buyer destinations. No named Final Vestige affiliate acceptance or email-channel authorization exists in the evidence examined. Both original emails still contain a second free inline link besides the principal guide CTA; this can dilute offer attribution. Issue 06 routes existing subscribers back to the acquisition signup page instead of a verified direct Fieldbook download, risking duplicate intent/sign-up confusion. Issue 04's precise fourteen-second subject has no explicitly sourced interval; NASA's official chronology describes a different interval (17 seconds from first indication to last crew communication). Keep Issue 04 on editorial hold until the alternative subject from R114 is approved. Do not silently overwrite the original. A potentially material expectation gap also exists: `/dispatch/` says email on publication, while native new-post automatic emailing is off; a proposed revision already exists under R112.

**Product-specific counterevidence:** The Zen12 sales page `https://zen12.com/hnp` describes twelve 12-minute levels and Premium 48 MP3 tracks and makes **unverified equivalence** and brainwave claims. Another official seller path `https://zen12.com/secret/` displays a separate coupon-led $37 landing price. The various seller prices are **not a single verified checkout price** or an approved price for FV emails. Hypnosis Live Total Focus `https://hypnosislive.com/mental-skills/total-focus` is advertised as a 33-minute/47 MB download, with one displayed standalone price and a separate two-product discounted price; the seller says 14-day refunds. **Do not advertise guaranteed concentration, mental-health results, an unrestricted coupon, or current pricing** without specific offer and transaction verification. Seller descriptions do not provide product-specific clinical proof. The public affiliate signup portal does not prove account acceptance, channel permission or commission settlement. Full read-only observations in `merchant_claims_20261104.json` are a dated, revisable research snapshot, *not* commercial authorization.

**Legal transport:** Commercial messages require an honest promotional identity, a valid **Final Vestige Studios** postal mailing address (not Automattic's or Inspire3's), and a functioning opt-out in the actually received message. The FTC's CAN-SPAM guide governs this. The FTC's Endorsement Guides require clear material-connection disclosure in context. Original commercial emails contain near-offer *prospective* disclosures; these are drafts, not proof that Jetpack will render them in excerpt mode. All six original messages still include explicit postal/unsubscribe placeholders, so none is sendable.

## Actual production source checks (read-only November 4, ~15:37 UTC)

- WordPress Jetpack Newsletter ON; automatic new-post notification OFF; `email_content_format=excerpt`; no-reply sender; welcome configuration points to the 52-page free Focus Fieldbook.
- Five most recent newsletters were `never_sent_opted_out`, consistent with the controlled publishing workflow, **not** evidence of failure or successful delivery.
- Diagnostics show `total=2 / confirmed=2 / unconfirmed=2 / suppressed=0`. Counts are *not additive*. Prior follower summary showed `email=0 / wpcom=2`; that has **not** been resolved to actual reachable subscribers. Never expose subscriber identities.
- Authenticated WordPress `/dispatch/` page ID 523 has exactly one native subscriptions block but lacks Focus's explicit commission language. `/focus/` page ID 1579 uses the same native subscription system and states commercial context. Neither an authoring preview nor a received welcome, consent transition, actual public PDF download, postal footer or unsubscribe has been verified here.

## Offer → funnel → blocker → change/test → pass evidence → owner

| Priority | Offer / funnel | Blocker | Change / experiment | PASS evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 | High-intent Mind visitor → one paid offer (Zen12 provisional) | No verifiable email rights, unique affiliate URL, live authorised buyer guide or merchant paid order | Mind selects **one** proof-backed approved offer or rights-cleared FV-owned alternative; do not activate the other offer | Written partner account/email authorization, live approved guide and independently verified paid settlement minus refunds/fees | Mind #171 / Claude |
| P0 | Existing subscriber → Fieldbook → relevant offer guide | Actual welcome receipt, reachable audience and PDF retrieval unknown | Obtain **authorized**, privacy-minimised received-email/attachment evidence without sending a test email | Evidence of completed native opt-in, received welcome and functioning Fieldbook download (private identifiers excluded from public reports) | Dispatch / Site QA / Claude |
| P0 | Commercial Issue 03/05 → destination | Approved destination and promotion disclosure rendering absent | Review original and R115 alternatives in offline previews; choose later, AFTER live guide exists | Actual Jetpack email Preview and allowed received-message footer with near-offer disclosure, exact subject/excerpt and working opt-out | Founder / Dispatch / QA |
| P1 | Grok asset → Focus → confirmed lead | Native signup eligibility and attribution missing | Use existing UTM contract: source=platform; medium=organic_social; campaign=cluster_pilot_2026_11; content=asset_id; dedup only authoritative confirmed native opt-in | Sanitized campaign IDs + native consent evidence, **not** clicks / unconfirmed attempts | Grok / Praxxis / Claude / Dispatch |
| P1 | Buyer → recorded net revenue | No merchant-confirmed settled conversions or qualified-human denominator | Reconcile 7/30-day qualified sessions with order IDs held privately by merchant; subtract actual fees/refunds | Realized net revenue per 1,000 qualified human sessions, with tiny sample warning; otherwise **N/A** | Claude commerce / Mind |
| P2 | Editorial Issue 04 → investigation | Unsourced subject precision | Adopt historically supported R114 candidate only after editor review | Source-checked chronology, exact WordPress title and genuine mail preview | Dispatch / Editorial QA |

Do **not** claim paid sales from clicks, subscribers, merchant page prices or WordPress pageviews. The paid-order KPI and conversion rate are NOT COMPUTABLE until both numerator and denominator are verified.

## Independent verification

- Exact master SHA #175 remains unchanged. The original six manuscripts, `manifest.json` and `tests/test_campaign.py` were reconstructed locally from GitHub and verified byte-for-byte against their exact blob SHAs; **6/6 native Python 3 tests passed**.
- This R116 builder and test source were fetched back from GitHub and their blob SHAs compared with the locally tested copies; **22/22 native Python 3 tests passed**.
- Independent headless Chromium `set_content` rendering: **30/30 mobile/desktop combinations passed** at 320/360/390/768/1440 pixels × all six previews; no horizontal overflow, script/image/form elements, merchant links or missing hold banner. An initial run **failed 18/30** on mobile due to long legal placeholder tokens. The bug was fixed in the committed builder with `overflow-wrap:anywhere;word-break:break-word` and fixed table layout; 30/30 rerun passed. This is honest **offline Chromium QA**, not website/Jetpack client testing.
- No hosted CI claim, no email preview or production deployment claim.

References: [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [FTC Endorsement FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking), [FV Editorial Standards](https://finalvestige.com/editorial-standards/).

**Campaign release:** ALL SIX HOLD_UNSENT. 03/05 ADDITIONAL HOLD_MERCHANT. No messages, test emails, lists, posts, settings, affiliate links or commercial purchases were touched.
