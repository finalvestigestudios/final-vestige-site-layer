# Dispatch R398 — exact-source, native, non-sending QA receipt

**2026-11-16 10:49 UTC, SAFE HOLD.** All testing local/offline. Neither WordPress nor merchant was written to. No subscribers or inbox recipients were contacted. No new script/analytics deployed. Six canonical drafts and their release status unchanged.

## Initial source-of-truth checks

1. Read GitHub master Issue #174 newest comments, companion #171 (including Mind R418 draft #2727), Focus #129 and revenue #820, and read existing draft PR #201 metadata. Inspected current R397 draft PR #2724 (head `9f9e04f1ddb5d28c2e36c3d9ee571478323780b1`) before creating isolated branch `dispatch-r398-focus-consent-source-qa-20261116` from its SHA. Homepage frozen #49 untouched.
2. Read authenticated WordPress Newsletter settings/status and published /dispatch/, /focus/ and Editorial Standards. At 10:35 UTC, enabled, default sending OFF, full-text email; total 3/confirmed 3/unconfirmed 2, 5 latest posts `never_sent_opted_out`, 52-page welcome configured. Actual eligible receiving inboxes, welcome delivery and native preview remain unknown.
3. Read official Zen12 and Hypnosis Live sales pages and WordPress/FTC compliance docs; no approved affiliate EMAIL rights or issued FV earning URL was authenticated. Gmail read-only search did **not** find an affirmative FV-specific merchant approval or the actual Fieldbook welcome. Vendor promotional emails are not publisher-rights evidence.

## Native suites (real executions, not simulated web output)

- **Original PR #175:** exact eight canonical source blobs were already independently matched to GitHub in R397 QA package. Reused those same unchanged bytes and independently executed `python -m unittest discover -s tests -v` with **6/6 PASS**, exit 0, Python 3.13.5. Current master head still `d57ccdba3aee8f065e143e101c2945f4f3d01647`.
- **R398:** `node --check focus_consent_gate.mjs` PASS; `node --test tests/*.mjs` **26/26 PASS**, exit 0, Node 22.16.0. Tests include 15 individual bad provider states, fake email/Reader/confirmation-only clicks, duplicate signup signal, all-false commercial holds, all-true but no permission to send, and five separate native `vm` reproductions of live /focus/ inline-JS behavior.
- Four R398 executable/fixture files used in the native tests **match GitHub's blob SHA-1 exactly**, verified via `git hash-object` and GitHub `fetch_file` on the new branch:

| File | Git blob SHA-1 |
|---|---|
| `focus_consent_gate.mjs` | `969084cfcec518d9d19c1af771d34df3961512f0` |
| `tests/focus_consent_gate.test.mjs` | `5cbe3ec305419f7e1f71938d339527b9bc998bc6` |
| `focus_live_js_excerpt.txt` | `4ba08134ca4586e0d7b3c420020f98571277754e` |
| `tests/live_focus_ui.test.mjs` | `605ee40073f85bcb1509f0e047fa704dc59d1435` |

**A genuine native Jetpack email preview, Chromium email viewport, received-message/unsubscribe test, checkout and revenue test were NOT performed.** Node VM is not a browser and cannot prove actual email-client appearance or delivery. This sprint adds an independently actionable production fix proposal to Claude/Focus; it does not claim to have repaired the live webpage.

## Source-falsified state

The exact inline snippet from `/focus/` uses a denylist for `subscribe` URL values and displays the “Your fieldbook is ready” panel when any other nonempty value occurs. `is-subscriber` class also displays it. The download anchor is annotated `data-fv-location="after_signup"`, which could cause reporting confusion **if** an analytics consumer interprets it as confirmed lead. No evidence of such an analytics consumer was established. Thus R398 implements a narrow fail-closed acceptance contract without asserting that actual inflated lead events exist.

## Final risk and approval matrix

**PASS (tested):** independent source and 26 native QA checks, unchanged original 6 source tests, real connected read-only WordPress settings/count snapshot. **HOLD:** actual unique eligible recipients, confirmed welcome receipt, native WP email rendering, qualifying FV postal + working unsubscribe, exact SKU EMAIL grant and accepted earning URL, approved live Mind guide, settled paid commissions, audited qualified-human sessions. **All canonical issues remain HOLD_UNSENT; 03/05 HOLD_MERCHANT, 04 HOLD_COPY; optional copies NOT_ADOPTED.** Six-issue 4:2 pilot preserved. Revenue per 1,000 audited qualified-human sessions **NOT_COMPUTABLE**.

Owner handoff: Claude + Focus #129 owns any narrowly reviewed CMS UI fix and provider-confirmed signup integration; Mind #171 owns SKU rights and guide; founder approves mail/legal/send; Dispatch #174 coordinates non-sending proof; Grok/Praxxis + Claude #820 supply genuine attribution and paid settlement chain.
