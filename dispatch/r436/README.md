# Dispatch R436 — public Fieldbook access ≠ confirmed consent (DRAFT)
Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Cross-owners: [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Revenue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).

**HOLD_UNSENT. Review-only source changes; no site writes, no subscriber contacts, no real test emails, no publication or affiliate link.** Isolated stacked branch on R435 PR #2935. The original six-issue campaign PR #175 remains canonical and untouched; PR #201's 4 editorial / 2 commercial gate remains authoritative; R434 alternatives have NOT been adopted.

## Specific P0 problem solved in source
The authenticated live WordPress /focus/ page (ID 1579; modified 2026-11-16T14:54:58) currently hides a free PDF panel until any not-blocklisted query value of `?subscribe=` or a class of `is-subscriber` appears. Neither is a provider-authoritative confirmation. This does not prove a data breach: the PDF is an already-public free asset. It **does** create misleading UX semantics (download shown “after signup”) and tempts analytics implementations to overcount leads.

R436 adds a **surgical, fail-closed, non-deploying patch generator** that swaps exactly the current gift panel and removes its query/class reveal script. The alternative keeps the real Jetpack form, the public PDF, one existing `focus_pdf_click` event, and the site style hooks. It makes the PDF visible without a signup and labels that download as **not a confirmed subscription**. Source contains no subscriber API, email sender or production writer.

## Files
- `focus_patch.mjs`: exact-version and exact-fragment guarded proposal for Claude review; it returns text only.
- `test_focus_patch.mjs`: synthetic original/duplicate/stale/error/consent regressions.
- `PUBLIC_PANEL_OFFLINE_PREVIEW.html`: accessible responsive **local offline** composition. Intentionally no real form, tracking or email.
- `CLAUDE_AND_FOUNDER_HANDOFF.md`: small-surface production acceptance checklist (approval required).
- `SELLER_AND_MAIL_RELEASE_GATE.md`: fresh official merchant/legal/platform source adjudication, no assumed rights.
- `CONSENT_TO_SETTLED_ORDER_CONTRACT.md`: one event and revenue measurement specification.
- `SOURCE_OF_TRUTH_SNAPSHOT.json`: aggregate-only diagnostic witness; no email addresses.
- `QA_RECEIPT.md`: exact-source checks and remaining proof boundaries.

## Critical distinction
**BUILT:** source-only panel replacement and non-sending preview. **TESTED:** pure patch checks on the exact read-only WP page and synthetic mutations. **NOT LIVE:** WordPress patch, recipient-verified consent analytics, new tracking, native Jetpack preview or email. **UNVERIFIED:** welcome delivery, unique eligible inboxes, FV publisher postal address, Jetpack footer opt-out, merchant EMAIL rights, cleared live guides, commission receipts and qualified sessions.

Recommended immediate action is a scoped Claude review of the patch before any additional email copy/experiment volume. Do not mistake PDF traffic or source tests for commercial success.