# The Dispatch — R53 founder evidence and release-authority pack (DRAFT / HARD HOLD)

**2026-11-01, 23:35 UTC source snapshot.** This is a **read-only production review + isolated source-controlled development**, not a published email or an authorization to send.

## Scope, ownership, and branch safety

- Master six-letter original draft: [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174).
- Offer and buyer-guide owner: [Mind & Affiliate Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Its newer Zen12 guide drafts (including [PR #519](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/519)) are NOT approved/live.
- Stacked directly on Dispatch R52 [PR #517](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/517) at exact parent SHA 16668c36c779e2c243c50b631f7abc20f4006173. No existing manuscript, main, homepage, frozen PR #49, WordPress content, Jetpack, or any list changed.
- Original balance intact: issues **01/02/04/06** editorial, **03/05** potential commercial. Optional alternatives are NOT selected by default.

## Actual source checks this sprint

Authenticated WordPress **finalvestige.com** site ID 256784396 at 23:34–23:35 UTC: Newsletter enabled; site can technically send; global new-post auto-email **OFF**, but per-post send remains possible. Email format is **excerpt**. Welcome is **configured** to deliver the same 52-page Focus Fieldbook, but receipt was **not** verified. Recent send list empty (NOT proof of zero lifetime sends). Subscriber counters **total 2 / confirmed 2 / unconfirmed 2** remain nonadditive; no uniquely consent-eligible count established.

Published read-only WordPress pages: **/dispatch/** ID 523, **/focus/** ID 1579, **Editorial Standards** ID 17. Dispatch still has no near-form commission notice, while Focus ALREADY does. Final Vestige's own standards require separating historical evidence from commercial relationships and disclosing financial ties. Previous R52 proposed uninstalled corrective copy. No page change authorized or made.

Read-only Gmail search: **no qualifying publisher-specific Zen12 or Total Focus affiliate acceptance/email-channel authorization established**. An October 25 WordPress **subscription confirmation** is not a successful final Fieldbook welcome, a commercial Dispatch send, or proof of Final Vestige's own mailing address. Consumer marketing email, product purchase receipts, and public merchant swipes are not permission to market products through email. **No subscriber's address or private link is stored in the repo.**

Primary official merchant pages rechecked **2026-11-01**: https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus ; https://inspire3.com/ll/ . Product formats are vendor descriptors; claims of enhanced focus, hour-equivalent meditation, automatic brain changes and advertised efficacy are not independently established product outcomes. Public **Limitless Labs** swipe material is not named-product authorization for Zen12/Total Focus.

Provider: https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter/send-newsletter-emails/ . Federal compliance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business and https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .

## Files, what they actually accomplish

1. **merchant_authority.json** — privacy-safe dated source/permission snapshot. All rights and eligibility unknown; every issue held.
2. **merchant_authority_gate.py** — fail-closed independent *attestation-shape* gate. It rejects wrong publisher/product, email scope missing, consumer receipt, public swipe, missing private proof reference, expired terms, absent human review and invalid link/creative/checkout attestations. Even a hypothetically well-shaped synthetic proof returns **MANUAL_AUTHORITY_REVIEW_REQUIRED** and global **HOLD_UNSENT**. It cannot authenticate an issuer or award an actual release.
3. **PARTNER_AUTHORIZATION_REQUESTS_NOT_SENT.md** — two precise, original merchant-facing draft requests to obtain the **named product + publisher + EMAIL channel** permission, link format, creative rights, terms, and product-specific claim support. They have NOT been sent.
4. **JETPACK_NATIVE_PREVIEW_EVIDENCE_HANDOFF.md** — separate authorization protocol for native preview and *later* actual received MIME QA; explicitly handles the WordPress per-post preview/send hazard.
5. **COPY_CONVERSION_HARD_AUDIT.md** — issue-by-issue review grounded in the original six manuscripts; separates real top-risk commercial clickpaths from copy-quality questions. Notes that R50 quarantined merchant source citations but original Issue 03 still has active vendor citations.
6. **ATTRIBUTION_MEASUREMENT_SPEC_NOT_ACTIVE.md** — minimum privacy-safe, *unimplemented* first-party measurement definitions coordinated with Mind #171, anti-PII rules and tiny-audience no-A/B protection.
7. **review.html** — static accessible reviewer board; NOT a Jetpack email and not approved for public website use.
8. **Two R53 Python regression files** — guard source invariants and preview safety, using entirely synthetic proof input. Total run count must be taken from **actually executed** tests, not from this document.

## Commands (source-level, no email/network writes)

From repo root, with Python 3.11+:

    python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
    python dispatch/campaign-2026-mind/r53-release-evidence/merchant_authority_gate.py

The gate's JSON should always return global **HOLD_UNSENT**. The complete CI pipeline should check exact pull-request head before passing; passing tests are **not** legal certification or inbox delivery evidence. Reviewer HTML must be checked in a real browser before claiming device/accessibility pass; source-level a11y checks alone cannot guarantee WCAG compliance.

## What actually unlocks a release

1. Private, source-of-truth acceptance and **EMAIL** permission for Final Vestige for each named offer, correct earning URL, current seller terms and creative use.
2. Approved LIVE first-party independent buyer guides from Mind #171; inspect their actual clickpaths and early disclosures; **never** use a guessed /mind/... URL.
3. Private subscriber-category reconciliation (avoid 2+2=4), confirmation and consent eligibility, no address exposure.
4. Valid **Final Vestige** physical mailing address and functioning unsubscribe verified in an **actual received** commercial email, plus post-specific commercial-primary-purpose/FTC QA.
5. Genuine WordPress native preview and separately authorized received test email, controlling the dangerous per-post-send toggle.
6. Final founder authorization covering each issue's exact creative, audience and dates; homepage flagship and PR #49 remain untouched.

No mail was sent/test-sent, WordPress content/settings edited, subscriber or merchant contacted, link activated, list exported/imported, analytics enabled or new email platform/expense incurred. **All six HOLD_UNSENT; #03/#05 HOLD_MERCHANT.**
