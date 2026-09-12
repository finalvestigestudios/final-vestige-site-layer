# Changelog

## 0.3.0 — FVSL-SCALE-BOARD-001

- Integrates the bounded FVF-21 Scale Board R7 executable repair into the governed Site Layer runtime.
- Preserves R6 publisher-DOM restoration while making `View in story` failure-atomic across dialog and focus state: scroll failures keep the dialog open; focus or highlight-scheduling failures reopen it and recover focus to the initiating jump control.
- Keeps successful story jumps closed-dialog + story-focused without persistent mutation of publisher-owned `tabindex`, id or class state.
- Adds exact browser assertions for `document.activeElement`, dialog state, absent/pre-owned/nondefault attributes, repeated interactions and timer cleanup.
- Preserves the R1–R6 extraction-truth, Sources-boundary, accessibility, privacy, no-network and no-storage contracts with exact-payload browser regressions.
- Extends deterministic release/package integrity checks to the exact R7 payload identity.
- Keeps merge, deployment, whole-site launch/indexing, and destination verification behind their existing governance gates.

## 0.1.0 — FVSL-BOOTSTRAP-001

- Introduces the governed Final Vestige Site Layer plugin runtime.
- Carries the exact reviewed Signal Finder, Evidence Map, and Detail Lens payloads.
- Verifies byte counts and SHA-256 hashes before emitting any payload.
- Adds deterministic CI for PHP syntax, payload integrity, and embedded JavaScript syntax.
- Establishes `production` as the WordPress deployment branch and requires live destination verification after deployment.
