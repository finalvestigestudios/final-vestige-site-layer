# FVF-9 — Passage Kit R1

## Repair objective

Close the independent-QD defect in the original Passage Kit artifact without broadening the visitor job. Passage Kit still carries one published narrative passage into a reader's notes together with only the source notes already linked to that passage.

The original source derivation correctly uses the live `.fv-fn-ref[data-fv-fn]` citation contract, but v1 quote cleanup removed only the legacy `.fv-fn-mark` wrapper. A wrapper-free live citation anchor could therefore leak its visible marker text into the copied quotation before the resolved source note was appended.

## R1 behavior

R1 performs copied-passage cleanup on a detached clone and removes both the live `.fv-fn-ref[data-fv-fn]` anchor and the optional legacy `.fv-fn-mark` wrapper from the quotation. Source resolution still happens from the untouched published passage before quote cleanup.

Consequences:

- a cited passage copies clean narrative text and appends each resolvable linked source note exactly once;
- an uncited passage copies narrative plus article/section context with no invented source section;
- an unresolved citation marker is removed from copied narrative, but no source is invented or substituted;
- wrapper-present and wrapper-free live citations behave consistently;
- published passage and source-note DOM remain unchanged because cleanup happens only on clones.

## Preserved boundaries

- single-post longform gate, at least 12 qualifying narrative paragraphs and 3,000 narrative characters;
- at least two published source records;
- article title, nearest section heading and query-free same-origin article URL in the export;
- linked source-note derivation from existing `.fv-fn-ref[data-fv-fn]` relationships only;
- source backlink cleanup and existing clipboard/fallback behavior;
- no browser persistence, cookies, account/server state, analytics, fetch/XHR/WebSocket/sendBeacon or third-party scripts;
- 44px controls, labelled region, polite status, Escape focus return, 360px layout, forced-colors, reduced-motion and print cleanup.

## Exact payload identity

- Payload: `payloads/passage-kit-wp-block-r1.txt`
- Bytes: **8,001**
- SHA-256: **`9fd62e21ddc4b0673fc8287a536cc1c28f950e74b32febe373947e860baa7467`**
- Verifier: `tests/verify_passage_kit_r1.py`
- Workflow: `.github/workflows/passage-kit-r1-ci.yml`

The verifier browser-executes the exact payload against cited, uncited, unresolved-reference and legacy-wrapper cases, proves citation marker text never enters the quotation, proves resolvable sources are appended exactly once, proves unresolved references do not fabricate sources, and compares publisher passage/source innerHTML before and after each export.

## Governance boundary

This is a source/build repair candidate only. Green CI is evidence, not QD approval and not merge/deployment authority. Independent QD must review the exact frozen PR head and exact payload identity. Any code, test, workflow, contract or payload change after freeze creates a new review identity.

If QD passes this source/build artifact and the governing release record requires an executable integration, rebuild from then-current `production`, freeze a new executable SHA/package, rerun fresh feature and repository CI, and return that new identity to QD before any eligible FAST APPROVAL / FVS Execution Dispatch step. No WordPress write, whole-site launch/indexing, private-user processing, billing/spending, account/permission change, public Scout release or external commitment is authorized by this artifact.
