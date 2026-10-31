# Dispatch R11 — protect the native-email reviewer from false source parity

**Unsent six-issue draft campaign · October 30, 2026 PT · master Issue #174 / Mind #171.**
**Parent:** draft PR #240 @ `e3e8c315af71b0c55c54850d2a4d60771df72178`.
**Scope:** read-only source-contract verification; no changes to original six letters, existing HTML previews, WordPress, subscribers, affiliate links, or homepage PR #49.

## Independently identified source-integrity defect

R10's `source_gate.mjs` validated the manifest, email manuscript, and proposed custom excerpts, but checked **only the length and HOLD flags** of the separate `NATIVE_DELIVERY_PARITY.json` preview rows. A misleading reviewer board could therefore display a different subject, preheader plan, commercial classification, excerpt, or CTA while the original gate still returned `SOURCE_ONLY_PASS`. This is a real source-contract weakness, **not** evidence that any genuine recipient received bad mail.

R11 adds exact equality to the canonical manifest and proposed excerpt for each of six unique issue IDs; ensures a commercial row's first-party guide is still **non-live**; and refuses to convert unverified welcome, native preheader, read-more, sender address, unsubscribe, received MIME, merchant permission, or founder approval into proof merely because a review JSON field was edited. The source-checker remains **never SEND_READY**.

**Tests added:** 12 Node mutation tests. The inherited 11 tests remain, for **23 committed Node declarations**. In a separate independent in-memory V8 check of actual current GitHub file contents, **8/8 original-campaign equivalent invariant groups PASS, 6/6 parity baselines match, and 14/14 injected false-proof or drift mutations are detected**. This is **not** execution of the committed Node tests; nor is it execution of the original Python suite on a complete exact checkout. A local container cannot resolve github.com, while previously observed GitHub Actions failures occur before executing steps. Mark both test suites **PENDING**, not green.

## Read-only source of truth snapshot: 2026-10-31 04:38 UTC

Authenticated WordPress site ID `256784396`: newsletter enabled, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, sender display `Final Vestige`, reply-to `no-reply`, no recent sends, welcome configured with the existing 52-page Focus Fieldbook. Counts: `total=2`, `confirmed=2`, `unconfirmed=2`, `imported_last_24h=0`. These internally inconsistent aggregates do **not** establish a recipient count; no list export/deduplication or new list was attempted. Welcome configuration is not delivery evidence.

Published `/dispatch/` (page 523), `/focus/` (1579), Editorial Standards (17), and Affiliate Disclosure (14) inspected read-only. We continue to prefer primary historical evidence, transparent uncertainty, corrected dates, and near-offer disclosure.

## Source-specific merchant position

- **Zen12, candidate issue 03:** seller states 12-minute sessions, 12 levels and four styles (guided, nature, music, white noise): https://zen12.com/about . The seller's **12 minutes = one hour of meditation** claim is **not independently proven** by the general research on meditation. Neither results nor checkout terms should be implied.
- **Hypnosis Live / Total Focus, candidate issue 05:** official SKU lists **33 minutes** and **47 MB**, plus a website-visible $2 promotion at this observation: https://hypnosislive.com/mental-skills/total-focus . Seller language promises remarkable concentration; do not repeat as verified efficacy. Prices, discounts, refunds and bundle choices are volatile; **omit fixed price and refund guarantees from mail**, and independently verify at checkout before recommending.
- **Partner eligibility:** https://affiliates.inspire3.com/ publicly recruits affiliates and says it issues special tracking links; it does **not** confirm Final Vestige account acceptance, eligible SKU, written newsletter/email promotion permission, approved creatives, approved earning URLs, or individual contractual conditions. A private Gmail search found product promotions and orders but no sufficient account-specific permission. Neither merchant URL is activated.
- Mind & Affiliate Studio controls unpublished evaluation guides and eligibility. Its draft PR #242 and earlier #188 / #229 **do not establish a published first-party destination**. Commercial issues #03 and #05 cannot point at guessed URLs.

## Hard release holds that cannot be solved by source-code tests

1. Identify **Final Vestige Studios' actual valid physical postal address** (street, registered PO box, or properly registered private mailbox) for qualifying commercial mail; the address appearing in a WordPress confirmation or the merchant's UK affiliate recruiting footer does **not** meet this evidentiary requirement.
2. In an explicitly approved WordPress editor workflow, inspect **native Preview email** (not a static generated HTML board). A *received* test MIME requires separately approved recipient and test-send authorization; never conflate preview with receipt. Validate accurate sender, exact article title/excerpt/Read More destination, disclosure visibility, postal details, unsub notice/link and mobile rendering. No test email is authorized now.
3. Reconcile contradictory aggregate counts in an appropriately private WordPress subscriber admin surface, without exporting personally identifying information to tickets or artifacts; confirm lawful permissioned audience.
4. Obtain authenticated partner approval, SKU/link and **email-channel permission** in writing; first-party guide must actually be published with compliant near-link disclosure; verify seller claims and terms.
5. Secure founder's distinct approval of final issue copy, approved recipient audience, timing and **sending**. Do not infer approval from this draft campaign brief.

WordPress currently uses **excerpt** delivery. Its documented default is about 55 words without a custom excerpt. The separate prepared preheader is a **plan**, not a verified native editable field. Do not treat authored 200–300 word HTML letters as the actual emailed content. No account, list, publication, sending setting or paid platform change is proposed.

## Human-first ethical conversion judgment

This 4-editorial / 2-commercial ratio remains correct. The original issue #05 describes an entire product catalog while the optional, still-unapproved PR #220 proposes a **Total Focus SKU-specific** alternative, which is a better reader promise if and only if merchant details and proper landing page are verified. It must not silently replace the founder's existing copy. Both sale candidates should lead to an independent, public, accessible Final Vestige evaluation **before** any verified affiliate click. Avoid testimonial inventions, urgency, price anchors, pseudo-scientific guarantees and A/B significance with two reported subscribers.

**What changed in R11:** only the read-only gate, its mutation suite, and this review note. No sending, publication, post draft, real email preview, signup import, vendor outreach or site settings edit. Every edition remains `HOLD_UNSENT`.

### Primary references

- WordPress excerpt configuration: https://wordpress.com/support/newsletter-settings/
- WordPress native preview (distinct from test sending): https://wordpress.com/support/newsletter/email-appearance/
- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- FTC endorsements: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- Editorial Standards: https://finalvestige.com/editorial-standards/
- Affiliate Disclosure: https://finalvestige.com/affiliate-disclosure/
