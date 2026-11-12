# Dispatch R293 — real audience provenance before revenue claims (UNSENT)

**Reference**: [Dispatch Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), master six-issue PR #175, per-edition guard PR #201, current stacked predecessor PR #2121. **Homepage PR #49 untouched.**

## New finding that changes the interpretation of the pilot

A fresh authenticated Jetpack Newsletter diagnostics snapshot at **2026-11-12T01:30:51Z** reports `total=3, confirmed=3, unconfirmed=2, suppressed=0`. The separate Jetpack Stats followers endpoint reports **WordPress.com=3 and email=0**, with `partial=false`. They are different counters/scopes; the two unconfirmed requests cannot simply be added to the confirmed or total figures. Importantly, the three confirmed in one endpoint must NOT be labeled three eligible email addresses. It is not proven that there are any emailable recipients. It is also not established that none of the WordPress.com followers receive notification emails. Actual eligible recipients remain **UNKNOWN** pending provider recipient classification and consent lifecycle evidence.

Full newsletter remains configured and enabled. The *automatic new-post email default* is OFF, but `site_can_send=true`; this is not a global outbound-mail disable. Five recent listed posts each reported `never_sent_opted_out`, NOT proof that no emails have ever been sent. The 52-page welcome URL remains configured; a received final welcome is not verified. An Oct 25 connected Gmail message was a confirmation request, not proof of completed welcome/Fieldbook delivery.

**This bundle makes no production change, does not export subscribers, invent a recipient count, send/test, activate commerce, edit WordPress or publish.**

## Exact read-only reviewer utilities

- `wordpress_aggregate_snapshot.json`: synthetic-safe **observed aggregate** counts/flags, no email addresses, user IDs, or conversion metrics.
- `aggregate_reconciliation.cjs`: deterministic scope-aware diagnostics, fail-closed release outcomes, separately gated authenticated revenue arithmetic; deliberately no send authorization.
- `test_aggregate_reconciliation.cjs`: synthetic tests; numbers in worked revenue fixture are **not actual FV events or purchases**.
- `RELEASE_AND_CONVERSION_DECISION.md`: issue-by-issue conversion priorities, source-of-truth owners and specific proof needed.
- `INBOX_AND_MERCHANT_SOURCE_AUDIT.md`: official merchant wording versus independent support; what a Jetpack preview **can and cannot** establish.

All six original editions remain **HOLD_UNSENT**. Commercial 03/05 remain **HOLD_MERCHANT**. Optional copy alternatives in previous PRs are **NOT_ADOPTED**. No new platform, signup list, email sequence beyond six drafts or expense.

Run read-only tests: `node dispatch/r293/test_aggregate_reconciliation.cjs`. This is an offline model; success is not a real consent or paid-revenue test.
