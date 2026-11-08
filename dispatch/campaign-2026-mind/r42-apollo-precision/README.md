# R42 — Apollo 1 source-precision editorial candidate (UNSENT)

Isolated optional editorial improvement for Issue #174, canonical six-issue PR #175, readiness PR #201; stacked on PR #448. Existing six newsletters, marketing allocation (4:2), WordPress pages and homepage PR #49 are not changed.

## Why this edition
PR #175's first-mile manuscript used a “Fourteen seconds” subject, but the CURRENT stacked canonical Issue 04 at our parent PR #448 has already been source-refined to **“Seventeen seconds. A much longer explanation.”** That 17.1-second interval is the first recorded fire transmission (23:31:04.7) through the final transmission's end (23:31:21.8), *not* the complete fire. R42 offers an independently written different narrative emphasizing the **~14-second interval from first report to cabin rupture**, the unproven initiating wire, and **six documented hazardous conditions**. This is an optional alternative to the existing stronger canonical treatment, not a repair of an uncorrected draft.

## Reviewed sources (November 1, 2026)
- Official NASA Apollo 204 Review Board report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- NASA Review Board summary: https://www.nasa.gov/missions/apollo/apollo-1/apollo-204-review-board-summary/
- Authenticated published Final Vestige article, WordPress post 434: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/
- Authenticated published site pages: /dispatch/ (523), /focus/ (1579), /editorial-standards/ (17).
- FTC commercial email compliance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## Native delivery is NOT proven
Read-only newsletter settings **2026-11-01T12:37:48Z**: enabled, new-post auto-email OFF, default excerpt, featured image ON, post date ON, custom preheader support not established; welcome copy points to the 52-page Fieldbook. Status **2026-11-01T12:37:46Z**: no reported recent sends (not necessarily zero lifetime sends). Subscriber counters total=2, confirmed=2, unconfirmed=2; unique consent-eligible recipients UNKNOWN, no PII retrieved. Business mailing address, actual received Jetpack unsubscribe and welcome delivery remain unverified.

## Contents and limits
The four candidate renderings are original manuscript Markdown, plaintext, a self-contained email-style HTML *static simulation* (not Jetpack output), and isolated Gutenberg-shaped blocks (not a WordPress draft). The same story and single article CTA appear in all. NASA links are primary-source citations, not second conversion buttons. Specific research statements are classified in `CLAIM_REGISTER.json`. All permissions and release attestations remain false. The optional candidate is NOT substituted into the canonical manifest.

**No send, test-send, WordPress post creation, settings changes, recipient contact, affiliate URL or new tracking.** Obtain founder editorial approval and actual inbox compliance tests before any edition could ever be released.

## CI identity defect found and repaired in this PR
The earlier Dispatch workflow used the label **“Checkout exact PR SHA”** but omitted `actions/checkout@v4`'s `ref` setting. On a `pull_request` trigger, checkout therefore tested GitHub's synthetic `refs/pull/.../merge` commit, not the exact PR head: hosted run #41308091851 logged merge commit `bf77111...` for requested head `a7f57aa...`. Its 518 passing Python tests demonstrated the merged tree, **not exact-head provenance**. R42 explicitly pins `ref: ${{ github.event.pull_request.head.sha || github.sha }}` and adds a fail-closed `git rev-parse HEAD` equality assertion; `workflow_dispatch` falls back to `github.sha`. Run success must be reverified after the change. This fixes the source-attestation weakness without changing production or sending any email.

The original R42 run had **two real test failures** because it expected PR #175's obsolete “Fourteen seconds” subject instead of the improved current stacked canonical “Seventeen seconds.” We corrected those assertions only after reading the exact current parent files. The source drift is recorded, not concealed.
