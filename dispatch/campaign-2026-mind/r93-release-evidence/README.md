# R93 — Dispatch proof escalation & first authorized native preview path (DRAFT ONLY)

**Recorded:** 2026-11-03 15:33 UTC. Dispatch owner [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), Mind/affiliate owner [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), original six-issue draft [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at SHA d57ccdba3aee8f065e143e101c2945f4f3d01647, release gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), predecessor excerpt adapter [#796](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/796).

**ZERO SENDS, ZERO TEST SENDS, ZERO WORDPRESS EDITS, ZERO LIST READS, ZERO MERCHANT/PAID LINKS.** Original six issue allocation 01/02/04/06 editorial, 03 Zen12 and 05 Hypnosis Live Total Focus reserved commercial. No substitution, staging approval, affiliate activation, CMS draft, sending schedule, extra ESP, list export, added tracker, or homepage PR #49 edit.

## Production verification, Nov 3, 2026

Authenticated Jetpack site ID 256784396: newsletter on and technically sendable, automatic new-post sends OFF, email content EXCERPT, sender display Final Vestige, replies NO-REPLY. Existing welcome config contains the 52-page Seven Day Focus Fieldbook link; **actual welcome receipt not established**. Five latest posts individually flagged never_sent_opted_out; this does **not** establish zero lifetime sends.

Two independent aggregate APIs disagree: newsletter reports total 2 / confirmed 2 / unconfirmed 2; Stats followers reports email 0 / WordPress.com 2. This is not four readers. **Actual eligible opted-in email recipients UNKNOWN**. A WordPress.com account can represent a subscribed visitor, and Reader followers can differ from email subscriptions; neither population is provably deliverable from those aggregates alone. Official WordPress guidance says to **filter by Email Subscription** and review aggregate states Subscribed, Not subscribed, Not confirmed, Bounced, Emails paused, Not sending. Link: https://wordpress.com/support/subscribers/ . Do so privately under owner authorization without exporting contacts; escalate if counts still conflict.

## Newly decisive preview limitation

WordPress official guide https://wordpress.com/support/newsletter/email-appearance/ explicitly says the post editor's **Preview email** button becomes visible when the **per-post Send this post to subscribers** toggle is ON. It also exposes **Send test email** alongside preview. The current read-only site connector cannot access that native editor email preview; obtaining it would require a separately approved WordPress draft and permission to touch a per-post setting in a nonpublished preview-only context. Such permission is **NOT granted**. The default-off sitewide setting is not equivalent to a prohibition on a manually opted-in post. Do not toggle anything now, and NEVER click Send test email without specific authorization. A static HTML preview is not evidence of Jetpack's delivered MIME, unsubscribe function, footer or mobile rendering.

Jetpack's October 28 customize guide https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ says a blank excerpt falls back to 350 characters; WordPress.com newsletter settings https://wordpress.com/support/newsletter-settings/ instead describes 55 words. BOTH support manual custom excerpts, so the ambiguity is avoidable when authorized; neither doc proves native results on finalvestige.com. In excerpt mode the native read-more CTA directs to the future newsletter **post permalink**, not automatically the original manuscript's editorial CTA. WordPress post title controls email subject. Native custom preheader setting has not been verified. R92 excerpts are optional candidates, NOT approved substitutions.

## Legal + product-specific truthfulness

FTC guidance https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business : valid publisher business postal address (qualifying registered USPS PO Box or registered private mailbox allowed), clear advertising identification, accurate subject/from and functioning opt-out. Automattic's address on an earlier confirmation message is **not the Final Vestige commercial sender address**. Never put a private home address or unsub token in version control. Need actual **received** commercial email showing publisher address + tested opt-out before release.

Official Zen12 actual sales https://zen12.com/hnp offers 12-minute sessions and asserts hour-equivalent meditation; latter is a **merchant claim**, not verified product-specific science. Official Hypnosis Live product https://hypnosislive.com/mental-skills/total-focus advertises a 33-minute 47 MB J.A. Amos recording and strong concentration outcomes; effectiveness claims are also seller assertions. Live and cached price snapshots visibly differ; no price, refund, guarantee or discount is safe to freeze into a draft. Companion Mind PR #800 remains a **draft guide**, NOT a live approved CTA. Official Inspire3 privacy policy https://inspire3.com/privacy/ allows referring affiliates access to purchase-related buyer data in some circumstances: Final Vestige will not ingest buyer PII. **Named account acceptance, written email-channel permission, merchant approved tracked URL/creative, current checkout/refund procedures, buyer-level data exclusion, two approved live warm-up guides NOT VERIFIED**. Zero commercial links.

A Gmail search through November 3 found a subscription *confirmation* but no authenticated custom welcome or signed Final Vestige-specific email rights. Confirmation ≠ welcome delivery, and an unrelated seller marketing message ≠ merchant authorization. No email or subscriber identities appear in these artifacts.

## Executable read-only proof classifier

Files: proofs.json is an ALL-FALSE, aggregate-only handoff; triage.py checks exactly five aggregate counters, 11 boolean evidence assertions with opaque proof IDs, original master SHA/4:2 mix, current excerpt/no-default-send transport, and no release or preview toggle permission. Even if someone claims all attestations, output **never** returns ready-to-send. No network, WordPress, Gmail, API, pixels, file writes or merchant requests.

Run from checkout:
- python -I dispatch/campaign-2026-mind/r93-release-evidence/triage.py
- python -I -m unittest discover -s dispatch/campaign-2026-mind/r93-release-evidence/tests -v

Local source-equivalent R93 Python test run: 33 / 33 passed. Hosted Actions pending new PR workflow; local results are **not native Jetpack email evidence**.

## Resolve blockers in highest-impact order

1. Founder privately selects qualifying Final Vestige postal address; confirm it is displayed in received commercial email, NOT just legal pages.
2. Owner privately filters subscriber Email Subscription statuses and reconciles opt-in eligibility; no list export. Draft support escalation in SUPPORT_HANDOFF.md remains UNSENT.
3. Separately authorize nonpublished WordPress post draft, per-post preview-toggle access, then inspect native rendered subject, excerpt, image, CTA, disclosure, legal address and unsubscribe. **No authorization yet.**
4. Separately approve a consenting controlled received-email test and inspect actual MIME/render/unsubscribe, if desired later. **No test email now.**
5. Mind owner resolves Zen12/Total Focus email rights, buyer privacy, checkout evidence and two approved LIVE buyer guides; only then review 03/05.
6. Founder explicitly approves exact creative/audience/send schedule before release. No prior draft approval authorizes sending.

**RELEASE: ALL SIX HOLD_UNSENT, 03/05 ADDITIONAL HOLD_MERCHANT.** Homepage is priority one; frozen PR #49 untouched.
