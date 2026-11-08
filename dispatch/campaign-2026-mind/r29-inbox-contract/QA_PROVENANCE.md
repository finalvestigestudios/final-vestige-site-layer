# R29 QA — verifiable local and GitHub-provenance separation

- Parent exact SHA: `6db066be8c479f17756406f39c429ba6c1b6dad2`; newly reviewed manifest and six manuscript sources were fetched directly from GitHub; six corresponding first Gutenberg blocks independently fetched at that SHA.
- New committed JS source was executed in read-only isolated V8 against those exact fetched GitHub sources: **40/40 source/guard checks passed**, including **17/17 deliberately unsafe mutations rejected**. Run the committed Node test with `node dispatch/campaign-2026-mind/r29-inbox-contract/tests/test_inbox_contract.cjs` in a complete checkout (Node test has not been run in a full checkout here).
- Existing Python baseline from source reconstructed from independently Git-blob-matched R28 archive: **134/134 passed** after restoring needed R25 Gutenberg fixture; initial incomplete reconstruction errored and is not counted as passing.
- Separate offline Python reviewer/auditor: **34/34 passed**. Offline **Chromium 6/6** viewport cases passed on local board at 320/360/390/768/1024/1440. Local board and GitHub board are distinct implementations; Chromium outcome should not be imputed to the committed HTML.
- Never treat local snippets as actual WordPress/Jetpack previews, nor model-only excerpt lengths as delivered email. Hosted CI to be inspected after PR creation; currently no received MIME, confirmed footer, postal, merchant approval or founder send approval.
- All six HOLD_UNSENT, 03/05 HOLD_MERCHANT. No sends, posts, WP changes, partner contact, list export, links or expense.
