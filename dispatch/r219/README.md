# Final Vestige Dispatch R219 — consent-path and paid-order truth pack (UNSENT)

**Status: DRAFT / NOT RELEASE AUTHORIZATION.** 2026-11-08 PT. Master [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), Conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Stacked on [R218 PR #1641](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1641). Canonical [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), readiness [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), frozen homepage [#49](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49) untouched. **All six letters HOLD_UNSENT; editions 03 and 05 additionally HOLD_MERCHANT.**

## New important WordPress product-truth distinction

WordPress.com's current Newsletter settings guide states: subscribers **without** a WordPress.com account receive a confirmation email before the welcome; subscribers **with** a WordPress.com account may *skip that confirmation email* and receive a welcome immediately. Thus a missing confirmation-email artifact does not, by itself, disqualify a provider-confirmed WP.com reader. Conversely an inbox *confirmation request* or a browser `?subscribe=...` flag does **not** prove completion. Authoritative subscription status and a distinct, confirmed status transition are necessary to count a **new** `confirmed_signup` event. WordPress.com source: https://wordpress.com/support/newsletter-settings/ (retrieved Nov 8, 2026). This clarifies R215–R218's double-opt-in verification without weakening consent.

## Read-only authenticated production snapshot (Nov 8, 2026, 22:33:53–54 UTC)

- Newsletter enabled; `site_can_send=true` indicates **technical capability, not legal/sender authorization**; `email_new_posts_by_default=false`; `email_content_format=full`; categories **disabled**; reply-to `no-reply`; sender name Final Vestige Studios.
- Subscriber counters total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**. Different endpoint: followers `wpcom=3`, `email=0`, `comment=0`, `partial=false`. **Do not add/merge those populations or infer actual email-eligible recipients.**
- Last five `recent_sends` reported `never_sent_opted_out` (posts 1917, 1920, 1922, 1924, 1926). No verified delivered Dispatch issue.
- Welcome **configured** to link to the 52-page Complete Fieldbook, but a **genuine received final welcome** and PDF open/byte integrity are not authenticated.
- Published WordPress pages read: `/dispatch/` ID 523 (2026-11-05 revision), `/focus/` ID 1579 (2026-11-05 revision), `/editorial-standards/` ID 17 (2026-09-09 revision). Dispatch signup omits the occasional affiliate recommendation sentence visible on Focus. Focus troubleshooting says to sign up again in a social in-app browser. R216 and R218 surgical fixes are still **draft**, not live.

## Why this is higher value than another newsletter draft

We lack proof of whom we may email, proof that the welcome reached an actual inbox, permission to promote the exact merchant offer via email, a verified Final Vestige mailing address/footer/unsubscribe in the received body, and paid-order settlement. The missing observations mean **net revenue per 1,000 qualified-human sessions = NOT COMPUTABLE**, not $0 and not a fabricated click-to-purchase estimate.

**No new signup list, paid service, merchant activation, tracking script, WordPress write or email**. The Python contract and HTML reviewer are offline, synthetic proof-handling and decision support. They cannot authorize distribution or authenticate an arbitrary input as a real provider record. Their explicit `send_authorized` result is always false, including when all test fields are true.

### Local reproducibility (standard library)

`cd dispatch/r219 && python3 -I -m unittest discover -p 'test_*.py' -v`

Browser reviewer QA may inspect `review_board.html` offline, but is not a Jetpack-rendered email. Legal footer and actual reply/unsubscribe behavior require separately authorized genuine received-message evidence. This draft does not modify the original six newsletters or other owners' work.
