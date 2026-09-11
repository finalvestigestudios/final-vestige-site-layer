# Changelog

## 0.3.0 — FVSL-SCALE-BOARD-001

- Integrates the exact QD-passed FVF-21 Scale Board R4 payload into the governed Site Layer runtime.
- Preserves the reviewed Scale Board payload identity: 17,520 bytes, SHA-256 `ecd9a6aed288061abd2ec55d53a049595174f8579178be773802d8ce7b325fee`.
- Adds the R4 browser/adversarial verifier and fixtures to the executable integration candidate.
- Extends deterministic release/package integrity checks to include Scale Board.
- Keeps merge, deployment, whole-site launch/indexing, and destination verification behind their existing governance gates.

## 0.1.0 — FVSL-BOOTSTRAP-001

- Introduces the governed Final Vestige Site Layer plugin runtime.
- Carries the exact reviewed Signal Finder, Evidence Map, and Detail Lens payloads.
- Verifies byte counts and SHA-256 hashes before emitting any payload.
- Adds deterministic CI for PHP syntax, payload integrity, and embedded JavaScript syntax.
- Establishes `production` as the WordPress deployment branch and requires live destination verification after deployment.
