# Final Vestige Labs R456 — zero-copy shared CSV sanitizer

**Issue:** #73. **Parent:** R455 stacked draft PR #2650 at `66cb9064d55cf456cf3e98b22b6189d6cd677b15`. **Status:** DRAFT ONLY / QD and founder hard hold. No production, website, entitlement, license or binary operations.

## Concrete defect

The R455 source-level numeric-prefix guard was changed to use `Pattern.fullmatch(value, pos)` rather than an almost 1 MiB suffix copy. However, the normal shared `engine.safe_cell` caller *still* unconditionally performed `token = s[index:]` before checking operators and negative Decimals. For a valid 950,000-digit ASCII negative amount prefixed by a single ASCII space, that redundant slice allocates about 950 KiB per call. The same occurs for a benign long text cell preceded by spaces. Every one of the six desktop programs routes saved report values through this shared sanitizer.

R456 inspects the original owned string at its offset using `str.startswith(prefixes, index)` and a compiled `Pattern.fullmatch(s, index)`. The established exact ASCII negative grammar `-[0-9]+(?:\\.[0-9]+)?` remains unchanged, as do imported source values, deterministic CSV byte witnesses, SHA-256 evidence, Decimal accounting, offline behavior, and human review. This is an allocation reduction, not a change in compliance classification or allowance for unsafe formulas.

## Artifacts

- `products/desktop/fvs_suite/engine.py` — source fix (no suffix allocation).
- `products/desktop/tests/test_csv_safe_cell_zero_copy_r456.py` — ten synthetic regression methods for 100,000 seeded old-vs-new parity examples, confusable signs, invisible prefixes, native Decimal, no attacker-defined coercion, exact source fidelity, and two large-allocation boundaries.
- `.github/workflows/desktop-source-evidence-r385.yml` — standard and `-OO` source test registration on both supported CI OS lanes.
- `.github/workflows/desktop-build.yml` — Windows standard and `-OO` regression gates before packaging.

## Local evidence and verification limits

On Linux Python with a separately reconstructed sanitizer projection, a deterministic corpus of **100,000 examples** matched the previous implementation in normal and `-OO` modes. A single-space-prefixed 950,000-digit safe negative had a local tracemalloc peak of **951,424 B before** versus **1,382 B after**; a 950,000-character plain-text label had **950,204 B before** versus **163 B after**. These are narrow, synthetic projection measurements, **not** a full repository test or Windows evidence. The committed ten regression methods and all six installed applications require CI/full-checkout verification.

## Release policy / next action

Do not merge, publish, expose gated premium installers, sign, offer download links, or change WordPress. Inspect the exact-head CI run and its job failure annotations. Prior R455 Windows and source workflows both failed before any steps or runner assignment (run IDs `43744921757` and `43744921783`); root cause remains unconfirmed. Restore runner eligibility/billing/policy, run committed R456 and inherited six-app suites on native Windows x64, then independent QD review, accessibility, Defender, checksum, protected premium distribution and explicit founder approval.
