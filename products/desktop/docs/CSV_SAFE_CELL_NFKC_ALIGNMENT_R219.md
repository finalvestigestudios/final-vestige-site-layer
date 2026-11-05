# R219 — Shared CSV sanitizer and compatibility-form formula alignment

**Status:** Draft only; independent QD + founder **HARD RELEASE HOLD**. Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on immutable R218 `c0b321983c1056e313c17dc84bcf4042d9eec2f8`, not `main`.

## Actual production defect and correction

R218's last-line CSV publisher rejects spreadsheet-compatible Unicode operator prefixes using `has_unescaped_formula_prefix`. The higher-level `engine.safe_cell` sanitizer was still limited to ASCII `= + @ -` and ignored prefix characters. Consequently a **valid, local financial source label** such as `＝LEDGER-1`, `＠ACME` or `＋ACME` could get through `safe_cell` unchanged, only to be rejected by R218's hardened publisher. This turned a safely renderable record into a failed export and could interrupt reconciliations without any unsafe output being published.

R219 makes `engine.safe_cell` use the **same shared predicate** from `csv_formula_guard.py` as the publisher. It prepends a literal ASCII apostrophe to a formula-like *original* value. It does **not** NFKC-normalize or change source amounts, matching keys, input digests, row coordinates or compliance findings. Existing sanitizer behavior remains: it escapes ambiguous invisible prefixes, leaves canonical negative Decimal literals unchanged, respects already apostrophe-escaped text, and preserves benign nonleading Unicode. The stricter CSV publisher remains the independent fail-closed boundary.

## Regressions and execution evidence

New `products/desktop/tests/test_safe_cell_nfkc_roundtrip_r219.py` defines **17** synthetic offline regression methods: all eight compatibility-form operators, numeric minus, exact Decimal, ASCII formulas, apostrophe idempotence, invisible prefixes, source text identity, direct CSV writer sanitization of headers and ignored values, byte-deterministic UTF-8-BOM output, no-overwrite, and real CSV engine report paths for LedgerDiff Lite, Invoice Twin Scout, and SpendMap Lite with SHA-256 source provenance. No premium materials or private customer data are used.

CI updated `.github/workflows/desktop-build.yml` in **both** Ubuntu `source-tests` and Windows `windows-build` to execute the new exact file in normal and `python -OO` modes, failing the job on test failures. These are **proposed** CI checks, not a claim of hosted execution.

**Local execution completed:** a **source-extracted 10-method predicate/sanitizer contract harness** constructed from inspected R218 `engine.safe_cell` and `csv_formula_guard` logic was executed on the local Linux Python environment:
- normal Python: **10/10 PASS**
- optimized `python -OO`: **10/10 PASS**
- 20 focused method executions across both modes.

The isolated local harness substitutes a simplified `_escape_source_character` helper for the tested prefix symbols. The **17 committed in-repository tests, inherited regression suite, six app launchers and actual Windows x64 executables were not executed locally**: the repository is private and its GitHub URL cannot be resolved from the local container. The GitHub connector was used to inspect and modify exact repository source and tests. Do **not** treat isolated harness results as full source-integration or Windows acceptance.

## Privacy, audit integrity and release conditions

- No network I/O, customer data or automatic audit/compliance decisions introduced.
- Source bytes and SHA-256 provenance remain authoritative. New escaping affects only the exported visible representation.
- No changes to Decimal parsing, financial tolerances, premium entitlement or file publication semantics.
- No production branch changes; do not merge or publish any free or premium executable from this draft.
- Hosted GitHub Actions has repeatedly reported Ubuntu/Windows zero-step failures, including R218 [run #42119130750](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42119130750). Root cause not independently determined. The owner must inspect Actions billing/usage, permissions and runner provisioning; restore execution and rerun the **unchanged R219 head**.

## Highest-impact next gate

Execute R219's 17 committed tests plus **all inherited tests** on Ubuntu and Windows. If green, privately build, SHA-256-checksum, Defender-scan and smoke-test all six Windows x64 launchers using independent accessibility/keyboard observation; maintain protected premium distribution, QD review, and founder approval. Do not create public download links or release claims until every required artifact and acceptance record exists.
