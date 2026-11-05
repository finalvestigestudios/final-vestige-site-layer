# Labs R218 — NFKC compatibility-form formula prefix custody

**Status:** DRAFT / QD HARD RELEASE HOLD. Tracks #73. No production merge, WordPress publication, public binaries, paid downloads, or claim of Windows acceptance.

**Parent:** R217 draft #1150 at immutable \`b83a3ee81b76d994711e30a19e6255f2824af0a1\`.
**Feature:** \`feature/labs-r218-nfkc-csv-prefix-20261105\`. Stacked on R217, never on \`main\`.

## Reproduced gap

The R217 shared CSV publisher correctly rejected literal ASCII \`= + @\` and nonnumeric \`-\` at the first meaningful source-cell character, including previously guarded whitespace/control/combining prefixes. But spreadsheet software can also apply Unicode compatibility folds during import: U+FF1D FULLWIDTH EQUALS SIGN and U+FE66 SMALL EQUALS SIGN each NFKC-normalize to \`=\`; U+FF0B/U+FE62 normalize to \`+\`; U+FF20/U+FE6B normalize to \`@\`; and U+FF0D/U+FE63 normalize to \`-\`. R217's predicate returned false for these forms, permitting direct \`cell=str\` callers to publish them in headers, rows, and ignored extra fields.

**No claim that a specific version of Excel, LibreOffice, or other importer executed a payload.** The risk is cross-importer interpretation ambiguity. CSV quoting alone is not a formula neutralizer.

## Change and safety bounds

\`fvs_suite.csv_formula_guard.has_unescaped_formula_prefix\` now inspects the **NFKC normalization of the first meaningful character**, after the existing leading-format/space detection. It rejects compatibility forms whose normalized first character is \`= + @ -\`, while preserving the original cell text unchanged for approved, escaped values. Only actual **ASCII \`-\`** followed by canonical ASCII Decimal digits/periods remains exempt. Compatibility-form minus must be explicitly escaped by the caller, even with a numeric tail. This is conservative: a reviewer may see additional escape apostrophes on non-ASCII minus labels.

The shared \`atomic_reports._render_cell\` already calls this guard before CSV publication for sanitized **headers, all data cells, and extra ignored mapping values**. Inherited publication rules remain: local-first/no network, no automatic decisions, Decimal-safe amounts, UTF-8 BOM, 64 MiB output and cell-size bounds, source originals unchanged, same-directory stage, exclusive no-overwrite publication, static privacy-safe failures and removal of incomplete stage files. The code does **not** attempt to normalize all Unicode strings, diagnose legal compliance, or certify spreadsheet importer behavior.

## Evidence actually executed (2026-11-05)

Environment: Linux x86_64, CPython 3.13.5; disposable temp directories and synthetic values only; no source financial records or premium outputs.

Local reconstructed *source files* matched Git blobs: parent R217 \`atomic_reports.py\` \`085cf2ffb7db7b9efb6c750feea28034de6cd6c7\`, parent guard \`6819a16c8a65d597a800837dd65a9e2e680cf626\`. Proposed guard \`79e49395947db9bf5f2ea26a323243c73968a1b1\`; new R218 test \`abcbfb69fed1b607cdba5af9ad74d733c71ea1f9\`. Both proposed blobs were confirmed on GitHub after commits.

- **RED:** 20 new R218 test methods on the original R217 guard: 27 assertion/subtest failures + 1 exception (count is per subtest/error, not distinct test methods).
- **GREEN:** 20/20 R218 methods, 17/17 exact-blob inherited R217 methods, 21/21 manually reconstructed R216 methods, 11/11 exact-blob inherited R27 methods. **69/69 normal + 69/69 with \`python -OO\` = 138 successful focused method executions**, with \`PYTHONWARNINGS=error\`, 0 skips and \`compileall\` passing.
- The inherited R216 test file was manually reconstructed for this local run and **was not byte-identical** to its GitHub blob. Therefore no claim is made that the entire exact inherited R216 test file or full project suite ran.
- The tested new guard, the R217 shared CSV writer, the new R218 tests, the R217 and R27 tests *were* byte-identical to GitHub source blobs. Native Windows execution and executable verification were **not** performed.

Minimal exact-repo reproduction after a future runner/checkout:

\`\`\`sh
export PYTHONPATH=products/desktop
export PYTHONWARNINGS=error
python -m unittest discover -s products/desktop/tests -p 'test_atomic_nfkc_prefix_r218.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_atomic_nfkc_prefix_r218.py'
python -m unittest discover -s products/desktop/tests -p 'test_atomic_negative_formula_r216.py'
python -m unittest discover -s products/desktop/tests -p 'test_atomic_pair_shape_r217.py'
python -m unittest discover -s products/desktop/tests -p 'test_atomic_reports_r27.py'
\`\`\`

## Hosted CI, gates, next action

\`.github/workflows/desktop-build.yml\` adds explicit Ubuntu source-tests and Windows build job **normal + \`-OO\`** regression steps for R218, without uploading customer records or premium outputs. The prior R217 Actions #42109040058 concluded **failure** with \`steps:null\` for both Ubuntu and Windows, so no hosted step success can be inferred from that run.

**Next highest-impact step:** owner inspects the new R218 Actions run and any pre-execution failure banner, GitHub Actions permissions/billing/usage and runner provisioning. Restore running jobs and rerun the unchanged R218 head. Next complete the full inherited six-engine tests, private Windows x64 builds, SHA256, Defender/EDR, Windows 11 accessibility/manual smokes, encrypted premium handoff, QD and founder approval. **Do not merge or publish binaries or unrestricted premium URLs** before all release gates pass.
