# Dispatch R351 — conversion-critical guest sign-up and subscriber retention
**Status:** SOURCE ONLY · UNSENT · NO LIVE CHANGE · FOUNDER APPROVAL NOT GIVEN.
**Parent:** R350 draft PR #2450 at 0b286c920be00c4cccdc714a6d3c719633f50a78; master six drafts PR #175; owner Issue #174; Mind partner #171; Focus #129; revenue #820.

## What is genuinely new
1. A native-Python-tested, offline **anonymous signup markup classifier** that distinguishes an actual email form from an editor/API fallback self-link without fabricating a guest-browser failure or completed signup. Supports locally saved HTML only; it cannot send, subscribe, fetch a site, or contact subscribers.
2. A source-of-truth decision memo distinguishing overlapping Jetpack status counts from WordPress.com follower counts, with actual first-click QA acceptance and provider-confirmation steps assigned to Claude/Focus.
3. An optional reader-retention rewrite of original Issue 06 with HTML and plaintext companions. Primary CTA goes to the already-configured *existing* Fieldbook PDF rather than the /focus/ acquisition page, subject to destination check. It is **NOT adopted** and must not be published or emailed.
4. Exact-product Inspire3 evidence/rights ledger that treats public price, product advertising, checkout price, affiliate acceptance and EMAIL rights as distinct propositions.

## Non-negotiable states
All original issues 01–06 = HOLD_UNSENT. Issues 03,05 = HOLD_MERCHANT. Issue 06 alternative = NOT_ADOPTED. Homepage production takes priority; PR #49 untouched.
No subscriber exports/emails, no website edits, no schedule or send, no new platform, no list import, no merchant links, no paid acquisition, no merges or releases.

## Test
`python -m unittest -v test_guest_snapshot_classifier` from this directory; fixture-only 17/17 assertions passed locally on verified Git blob source. The original master PR #175 test suite passed native Python 6/6 after the eight latest Git blobs were matched. These tests demonstrate classifier behavior, **not real guest UI, double opt-in, welcome delivery, unsubscribe or paid orders**.

## Useful source links
- [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201)
- [Live Dispatch](https://finalvestige.com/dispatch/), [Focus](https://finalvestige.com/focus/), [Editorial Standards](https://finalvestige.com/editorial-standards/)
- [WordPress native Preview email](https://wordpress.com/support/newsletter/email-appearance/), [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
