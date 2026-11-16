# R396 exact-source evidence and release result

**Scope:** source-controlled, unmerged, non-sending Dispatch pilot addendum. Original founder-approved draft in [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), guard PR #201, offline all-six reviewer PR #2703, previous source-only [R395 PR #2714](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2714). Frozen homepage PR #49 untouched.

## New independent finding
The **canonical commercial Issue 05** explicitly names **Hypnosis Live**, with destination `[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]`, while optional later R391 drafted around **Total Focus**, which is a particular Hypnosis Live recording. This is real parent-catalog→child-SKU scope drift, **not** two unrelated merchants. Seller sources: [Hypnosis Live catalog](https://hypnosislive.com/catalog), [official Total Focus](https://hypnosislive.com/mental-skills/total-focus) and [FAQ](https://hypnosislive.com/faq). No silent replacement or delegated founder approval. Source [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174).

## Actual source and native test evidence

New `dispatch/r396/offer_scope_gate.mjs` Git blob `893e881c575b6d7f3ba7f9a0ae571a2a27575ecb`; new `offer_scope_gate.test.mjs` blob `81faa20400b7c983687a2ae1d5192396507b0e69`. **Both match local git hash-object exactly.**

Actual locally executed native Node:
```sh
node --test /mnt/data/dispatch_r396/offer_scope_gate.test.mjs
git hash-object /mnt/data/dispatch_r396/offer_scope_gate.mjs /mnt/data/dispatch_r396/offer_scope_gate.test.mjs
```
**19/19 PASS, 0 failures, 0 skips** in native Node. Purely synthetic approval fixtures test failure states and REVIEW only; they are **NOT** actual merchant approval, real recipients, conversion data or a send operation. The implementation always returns `status=HOLD_UNSENT`, `send_enabled=false`.

Post-commit re-fetch of exact GitHub source, HTML, Markdown, plaintext and ledger: **9/9 static structural checks PASS** (4:2 mix, correct exact brand/SKU, all-false attestation, no actual active merchant CTA, legal placeholders, accessible HTML base, source trail). These are **static checks, NOT rendered email-client or native Jetpack screenshots**. The standalone HTML uses table layout, inline styles, meaningful heading and source links; dark-mode, responsive behavior and actual email client rendering still require authorized tests.

Original canonical PR #175 current head inspected at exact `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Its six original Python test conditions were **independently re-executed as V8 assertions against exact GitHub-fetched manifest and all six canonical Markdown issues: 6/6 PASS**. The native Python test runner was **not** executed this sprint; do not claim it was. Original test blob `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`, original manifest blob `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`.

## Authenticated WordPress as-of 2026-11-16 07:03:46Z

Newsletter enabled; technically sendable; new-post default auto-send **OFF**; 5 recent post emails `never_sent_opted_out`; full content; from name Final Vestige Studios; reply-to no-reply. **3 total, 3 confirmed, 2 unconfirmed** (not additive); follower WP.com 3 / email 0. Email-eligible recipient count unverified. Saved welcome contains 52-page PDF link; **actual received final welcome unverified**. No native preview, authenticated physical FV postal footer, unsubscribe action, issued Inspire3 earning link or settled commission. Connected Gmail targeted merchant/affiliate searches returned no matching named FV rights; absence of mailbox proof is not definitive absence of rights.

## Operator/owner release decision
Original 01–06 `HOLD_UNSENT`; 03 & 05 `HOLD_MERCHANT`; 04 `HOLD_COPY`; optional proposed Issue 05 here `NOT_ADOPTED`. No test email or send, subscriber or post creation, list import, settings change, outbound merchant activation, WordPress publishing, public link activation, PR merge or spend.

Owner assignment and next exact proof: **Mind** confirms Hypnosis Live catalog versus Total Focus SKU and issues offer-specific EMAIL permission/earning links; **Focus/Claude** privately checks unique eligible recipients and actually received welcome; **Dispatch/Founder** verifies native Jetpack preview, legal publisher address/unsubscribe and final creative; **Grok/Praxxis/Claude** jointly validate qualified visitor attribution against actual settled commissions, not clicks. Net revenue per 1,000 qualified human sessions = **NOT_COMPUTABLE** on real FV data.
