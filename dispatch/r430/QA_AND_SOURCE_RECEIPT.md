# R430 execution truth, source snapshots and legal holds
## Existing canonical master: independently run
Verified PR [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) still points to exact HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`. The eight canonical manifest, Python test and six issue source files were obtained from an existing bundled source copy; `git hash-object` was computed independently and agrees with the exact GitHub source identities recorded in R429. Native `python3 -m unittest discover -s campaign-2026-mind/tests -v`: **6/6 PASS** (November 17, 2026). No changes to these files.

## New release and revenue evidence checks
Committed `consent_to_settlement_gate.cjs` and `test_gate.cjs` were fetched from their then-exact GitHub blob versions and executed **read-only in a V8 JavaScript isolate using a narrow Node assertion and URL-parser shim**: **69/69 PASS**. The implementation itself has no network side effects. This is **NOT a claim of native Node execution or the real Node URL parser**, browser QA, CI, actual merchant payments, or WordPress transport. Native Node execution remains a distinct outstanding gate.

Important adversarial coverage:
- source proof flags missing → `NOT_COMPUTABLE`, never made-up $0; deliberate complete zero is distinguished;
- bot sessions excluded, identical sessions/orders deduplicated, conflicting duplicates rejected;
- absent/incorrect campaign join or unmatched paid order → uncomputable;
- merchant confirmation/settlement missing → uncomputable;
- negative/fractional money rejected; refunds, fees and genuine negative net retained;
- subscriber confirmation is provider-authoritative and suppression/opt-out blocks leads;
- private email/IP/PII rejected from aggregate fixtures;
- exact-first-party HTTPS only for proposed 01/02/04/06 CTA UTMs, with merchant 03/05 inert;
- post title/preheader not conflated, offline HOLD text flagged as potential snippet risk;
- even hypothetical full evidence makes founder review possible **but never releases a send**.

## Fresh authenticated WordPress read-only source
- `wpcom_jetpack_newsletter(status)` as of `2026-11-17T19:38:12Z`: subscribers total 3 / confirmed 3 / unconfirmed 2 / suppressed 0, provider send capability true, latest five posts `never_sent_opted_out`, recent actual recipient counts null.
- `wpcom_jetpack_newsletter(get_settings)` as of `2026-11-17T19:38:13Z`: subscriptions ON, `email_new_posts_by_default=false`, `email_content_format=full`, From display Final Vestige Studios, `reply_to=no-reply`; configured 52-page Fieldbook PDF welcome.
- `wpcom_jetpack_stats_followers`: wpcom 3 / email 0 / partial false; don't sum those with newsletter dashboard counts.
- [Dispatch page](https://finalvestige.com/dispatch/) ID 523, [Focus page](https://finalvestige.com/focus/) ID 1579, [Editorial Standards](https://finalvestige.com/editorial-standards/) ID 17 retrieved from authenticated WordPress, unchanged.
- [Mind owner #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) newest R450 draft [#2903](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2903) still reports 28 closed commercial gates. Grok/Praxxis TASK-008 and handoff Google Docs read-only; no task queue change.
- Targeted Gmail searches for merchant-specific affiliate authorization and received Fieldbook welcome returned no responsive proof in searched messages; **limited search only**, not proof about any other recipient or merchant account.

## Proof levels
**BUILT:** source-only revenue/consent/preheader gate and review materials. **TESTED:** 6 native master Python tests; 69 source-exact V8-shim assertions. **LIVE:** original Jetpack settings and pages only. **NOT VERIFIED:** native Node tests for new gate, email editor Preview, received welcome, real inbox unsubscribe/postal, merchant permissions/pricing/refunds/referral link, lead attribution, paid orders, realized revenue, qualified session denominator.
No number from synthetic test fixtures can appear as a real KPI. Master campaign and homepage PR #49 remain untouched.
