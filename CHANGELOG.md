# Changelog

## 0.3.0 — FVSL-SCALE-BOARD-001

- Integrates the bounded FVF-21 Scale Board R7 executable repair into the governed Site Layer runtime.
- Preserves the R6 failure-atomic publisher-DOM restoration contract while adding deterministic interaction-state recovery: thrown scroll/focus operations cannot leave keyboard/screen-reader focus stranded after the Scale Board dialog closes.
- On a failed story jump, focus recovers to a feature-owned launcher when the dialog is closed, or to a feature-owned dialog control if it remains open; silent story-focus misses are treated as recoverable failures.
- Successful story jumps still focus the published paragraph without permanently rewriting publisher-owned `tabindex`, ids or classes; absent/pre-owned/nondefault tabindex values, repeated jumps and timer cleanup are regression-tested.
- Preserves the R1–R6 extraction-truth, Sources-boundary, Unicode/numeric-expression, accessibility, privacy, no-network and no-storage contracts with exact-payload browser regressions.
- Extends deterministic release/package integrity checks to the exact R7 payload identity.
- Keeps merge, deployment, whole-site launch/indexing, and destination verification behind their existing governance gates.

## 0.1.0 — FVSL-BOOTSTRAP-001

- Introduces the governed Final Vestige Site Layer plugin runtime.
- Carries the exact reviewed Signal Finder, Evidence Map, and Detail Lens payloads.
- Verifies byte counts and SHA-256 hashes before emitting any payload.
- Adds deterministic CI for PHP syntax, payload integrity, and embedded JavaScript syntax.
- Establishes `production` as the WordPress deployment branch and requires live destination verification after deployment.
