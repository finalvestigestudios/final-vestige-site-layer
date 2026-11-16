# Dispatch R392 — exact-source Chromium email-specimen QA

**Scope:** Static OFFLINE HTML only. This is NOT a WordPress Jetpack-generated newsletter, MIME message, inbox delivery, native preheader, sender address, unsubscribe test, accessible full-site certification, or approval to send.

## Inputs authenticated against GitHub at R392 commit

- `dispatch/r392/ISSUE03_ZEN12_OFFLINE.html` exact Git blob SHA-1: `70ef6ef717397b52e0d79cbe132799ce88245a56`.
- Independently re-read the GitHub file and computed identical local `git hash-object` before the browser run. Source HTML 3,331 UTF-8 bytes in local filesystem (reported content length depends on character encoding; Git blob is the byte identity).
- Chromium headless, Playwright, no JavaScript page execution, injected **exact** static HTML via `page.set_content`, no network requests, no live destination activation.
- Automated original source test harness and full JSON/screenshot artifacts kept in local evidence package. Not claiming GitHub-hosted CI or an externally received email.

## Nine actual offline browser cases

| Viewport CSS px | Browser zoom | Horizontal overflow | Source/legal marker/accessibility smoke check | Result |
|---:|---:|---|---|---|
| 320 | 100% | None | Three source-only links, `lang=en`, h1, commercial disclosure and inert CTA | PASS |
| 360 | 100% | None | Same, no scripts/forms/iframes or images | PASS |
| 390 | 100% | None | Same | PASS |
| 768 | 100% | None | Same | PASS |
| 1440 | 100% | None | Same | PASS |
| 320 | 200% | None | Same | PASS |
| 390 | 200% | None | Same | PASS |
| 768 | 200% | None | Same | PASS |
| 1440 | 200% | None | Same | PASS |

**9/9 PASS**: `documentElement.scrollWidth <= clientWidth+1` and `body.scrollWidth <= clientWidth+1`; zero page errors. No user message, image rights, hidden pixel or JavaScript tracking is involved. Screenshots of 320/390/768-pixel offline render were generated; no screenshots have been misrepresented as native Jetpack evidence.

## Exact native security/consent regression source run

- `release_gate.mjs`: `4d14ffd5006a7d4038c1bd47f18af7284c291ca5`.
- `release_gate.test.mjs`: `9c02fd89e8d22c4b650ffcd889878a15e2046a95`.
- `proof_ledger.json`: `822ebf182f91553b74f59f02451ffa7f09f886d5`.
- Source bytes independently matched all three GitHub blob SHAs; Node v22.16.0 `node --test release_gate.test.mjs`: **20/20 PASS, zero fail/skip**. Red-team bug documented in `GATE_REGRESSION_R392.md`: absent nonmerchant attestation keys previously allowed *human-review eligibility*, not sending; explicit 14-key required proof gate now fails closed. Unverified current-data revenue still NOT_COMPUTABLE.

## Actual missing release proof

Native WordPress non-sending *Preview email*, actual generated unsubscribe + qualifying FV postal address, consent-eligible recipients and received Fieldbook welcome, named Zen12 SKU-specific EMAIL acceptance + issued link/live reviewed guide, referred checkout/refunds and merchant settlement remain **UNVERIFIED**. Founder final campaign/send approval **NOT GIVEN**.

No WordPress/email/subscriber/affiliate changes, no production publish, no social task change, no spending.
