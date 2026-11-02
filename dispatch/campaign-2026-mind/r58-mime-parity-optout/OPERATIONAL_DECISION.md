# Dispatch R58 — Plaintext / HTML parity and commercial-mail route verification

**DRAFT / UNSENT — November 1, 2026 PT.** Owner [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); product owner [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Stacked on [draft PR #552](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/552); original six-letter [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) and gates [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) remain authoritative. The homepage PR #49 is excluded.

## Release decision

**All six HOLD_UNSENT; commercial 03/05 additionally HOLD_MERCHANT.** Preserve the original four-editorial/two-commercial pilot, subjects, canonical manuscripts, one-CTA plan and all placeholders. No fallback has been approved as a substitute. No contact with subscribers or vendors, WordPress writes, sends/test sends, scheduling, signup import, analytics activation, affiliate earnings links, paid services, or site changes.

## Why this work is material

The original R56/R57 read-only MIME inspector modeled the HTML part ahead of plaintext. Consequently, a financial disclosure in the HTML could pass an early-disclosure observation while the email's plaintext alternative lacked the disclosure entirely. Readers and email clients choosing plaintext would receive a different commercial presentation. **R58 independently examines both MIME alternatives, explicitly records their early financial disclosure, and adds an extra HOLD when both populated parts do not carry that disclosure within their first approximately 85 words.** A regex is not a substitute for an actual rendered test.

The old unsubscribe detector could pair a plausible URL from a “Read more” link with the word “unsubscribe” anywhere elsewhere in the message. R58 requires the *same visible hyperlink* to have matching unsubscribe/opt-out anchor text and a plausible HTTPS unsub/subscription/follow destination. It filters direct seller URLs. The List-Unsubscribe header is still only a structural candidate; unrelated seller or purchase URLs do not qualify. These conservative filters can flag opaque but valid endpoints for human review: a missing candidate does not establish that a real link fails, and an accepted candidate never proves it works.

Previous merchant-link quarantine examined anchors, but a direct seller route can also be embedded in image-map areas, forms, button/input form actions, iframe/object sources or meta-refresh tags. R58 scans these routing attributes, malformed links and unsafe URI schemes. It also detects external CSS URLs embedded inside style tags. This is **offline static analysis only**, not JavaScript execution, image fetching, inbox rendering, tracking activation or legal certification. No raw address, source link or opt-out token appears in the results.

## Authenticated WordPress fact snapshot

At **2026-11-02 04:33 UTC**, site 256784396 reported: newsletter subscriptions enabled, site technically sendable, automatic new-post email disabled, email excerpt mode, reply-to disabled, sender “Final Vestige,” and no reported *recent* sends. The currently configured welcome message links the complete 52-page Seven Day Focus Fieldbook; actual successful receipt remains unknown. Subscriber dashboard showed **total=2, confirmed=2, unconfirmed=2, suppressed=0**, whose totals are non-additive under [WordPress Subscriber documentation](https://wordpress.com/support/subscribers/): unconfirmed registrations are excluded from total. The unique opted-in, deliverable *email* audience is still NOT VERIFIED; do not report four people or imply that all two confirmed are available for mailing.

The published [Dispatch page](https://finalvestige.com/dispatch/) (ID 523) emphasizes historical investigation, archives, one list and a free Fieldbook. Unlike the separately published [Focus page](https://finalvestige.com/focus/) (ID 1579), Dispatch does not clearly mention occasional paid recommendations near its signup. The [Editorial Standards](https://finalvestige.com/editorial-standards/) (ID 17; reviewed August 23, 2026) require original archival sources, clear distinctions between inference and fact, dated substantive corrections and disclosed commercial relationships. Proposed consent-alignment copy in prior draft #517 remains uninstalled.

**An enabled Jetpack sender is not a campaign authorization**. A manual per-post send switch can circumvent the global auto-send default, so unauthorized native preview/testing cannot be used as a workaround.

## Seller-specific claim verification (public seller copy, not evidence of results)

Zen12 official seller [About](https://zen12.com/about) describes twelve 12-minute audio levels with four versions and claims short sessions deliver an hour's advanced meditation. The same seller's [free-audio offer](https://zen12.com/freeaudio) collects email subscribers to its own newsletter; that is NOT permission to add anyone to either publisher's list, and bypassing Final Vestige's independent guide would violate the intended funnel. Format/features are seller-described; the equivalence and efficacy promises are NOT independently established for Zen12.

Hypnosis Live's [Total Focus](https://hypnosislive.com/mental-skills/total-focus) page describes a ~33-minute, 47 MB download and makes extensive concentration, productivity and “brain reprogramming” promises. The [official FAQ](https://hypnosislive.com/faq) describes a 14-day refund process and a five-session-per-year limitation; actual conditions and applicability at checkout remain unverified. Public offer prices have differed across captures. Do not quote current prices, discounts, refund guarantees, verified product effects or personal experience in a newsletter without additional accountable evidence. A merchant's posted address cannot satisfy Final Vestige's postal-address obligation.

**Named-product publisher affiliate approval; specific email-channel rights; creative reuse; earning-link format; product/price/refund terms; approved published independent guide; and actual commission tracking remain UNVERIFIED.** Public Inspire3 recruitment and seller marketing pages are not written Final Vestige permission. The Mind & Affiliate Studio owns the pre-sell guides; its draft source files are NOT live buyer-guide destinations. The original Issue 03's two seller citations still require independent quarantine before any commercial send.

## Concrete human verification plan — currently NOT authorized

1. Founder separately approves a safe, recipient-scoped native preview/test procedure. Until then, do not open an editor control requiring an email-send toggle, publish any post or test-send.
2. Privately obtain a genuinely received original RFC 5322/MIME email *only after* this permission. Analyze both HTML and text/plain with the offline inspector. Its result permanently returns SEND_ALLOWED=false; an “origin=received” string is not independent attestation.
3. Human compares subject/preheader/intro, early disclosure and single CTA across real email clients, mobile screens, zoom and screen readers. This is essential because code-generated HTML/static mockups do not simulate Jetpack excerpt rendering or client CSS.
4. Match Final Vestige's actual legally valid business postal address privately; verify its inclusion in the received commercial message, and perform an authorized, functional unsubscribe verification. FTC [CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful origin/subject, proper promotional identification, a valid postal address and a workable opt-out.
5. Reconcile unique email subscription/delivery status and exclusions privately; publish no subscriber PII, confirmation links or unsubscribe tokens.
6. Check the actual product-specific written affiliate email rights, seller creative claims and checkout policies, first-party approved live warm-up guides, exact verified earning URLs, and placement disclosures beside the recommendation.
7. Founder gives **separate final approval** for every actual issue, audience, destination and send date. No structural test result grants that approval.

## Source-controlled metrics plan; collection remains OFF

A future aggregate-only review ledger can contain issue number, editorial/commercial label, proposed destination, date range, observation source, aggregate guide views and CTA clicks **only when a genuine permitted measurement exists**, plus partner-reported sales *only if specifically verified*. All fields currently read NOT COLLECTED or UNKNOWN. Never infer a sale from a click. Do not include subscriber emails, private link IDs, unsubscribe tokens, raw UTM queries, orders, IP addresses or personal browsing traces. Do not derive campaign conversion rates, statistical tests or A/B success from a list of roughly two confirmed records. Use source-level aggregates only, and withhold public rates and variant comparisons at low n.

## Verification, limits and rollback

Run the committed 52 synthetic tests alongside the inherited 1,101 tests against the *exact final PR head* and read the real GitHub Actions result; expected total 1,153 assuming no external branch drift. This number is a target, **not a passing claim**. If a test fails, correct the implementation or legitimate expectation without weakening release controls. A passing run establishes source integrity, not legal or real-mail compliance. Undo by closing the unmerged draft PR. Nothing on the live site, newsletter, subscriber list, merchant account or homepage changes in this branch.
