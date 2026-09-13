# Changelog

## 0.3.0 — FVSL-VESTIGE-ASSEMBLY-001

- Adds the Vestige Assembly payload: a decorative, homepage-only intro curtain that plays a short
  fragment-assembly choreography (~8.6s) and then dissolves to reveal the real, already-rendered
  homepage underneath.
- Runs at most once per browser session (`sessionStorage`), never on non-home pages, and is
  immediately dismissible by any scroll, keypress, or pointer input anywhere on the page.
- Fully skips itself under `prefers-reduced-motion: reduce` and `forced-colors: active`; is
  `aria-hidden` and `pointer-events:none` throughout so it never hides content from assistive
  technology and never blocks or delays interaction with the real page.
- Carries only the four brand lines given in the design brief; introduces no fabricated
  citations, no new dependencies, no network calls, and no persistence beyond the one-time
  session flag. Includes a hard 12s failsafe removal so the curtain can never get stuck.
- Adds `tests/verify_vestige_assembly.py` (exact payload identity, gating/timeline behavior via
  an extracted, unit-tested pure-function seam, and the same adversarial-safety checks used for
  Case Search) to CI.

## 0.1.0 — FVSL-BOOTSTRAP-001

- Introduces the governed Final Vestige Site Layer plugin runtime.
- Carries the exact reviewed Signal Finder, Evidence Map, and Detail Lens payloads.
- Verifies byte counts and SHA-256 hashes before emitting any payload.
- Adds deterministic CI for PHP syntax, payload integrity, and embedded JavaScript syntax.
- Establishes `production` as the WordPress deployment branch and requires live destination verification after deployment.
