# R295 — Exact desktop CI events and read-only token custody

**Status:** DRAFT; independent QD and founder HARD HOLD. No production merge, builds, EXE uploads, premium distribution or approvals.

## Concrete gap addressed

R293/R294 restricted root and job mapping shapes, but the mandatory Python
source-contract did not inspect the *contents* of the GitHub Actions `on:`
event mapping or `permissions:` block. A workflow with a broader event
(`pull_request_target`, `push`, `workflow_run`) or an elevated
`contents: write` / `id-token: write` token could satisfy the prior
lexical source-contract while materially changing CI trust assumptions.

## Implementation

- `products/desktop/ci_event_permissions_r295.py`: exact, reviewed
  source preamble. Only `pull_request` scoped to desktop source or its
  workflow file, plus explicit `workflow_dispatch`, with
  `permissions: contents: read`. Duplicate keys, alternate key spellings,
  broad event/path settings, write tokens, and omitted permissions all fail.
  Whole-line comments and blank lines remain permitted.
- `ci_source_contract._jobs()` requires the new policy before examining
  job blocks. The obsolete permissionless root shape is no longer accepted.
- R57's historic GOOD fixture is upgraded to the real, read-only trigger
  preamble so prior source-contract tests remain meaningful.
- Both Ubuntu `source-tests` and Windows `windows-build` now call the
  30 regression methods under standard and `-OO -W error` modes.
- Financial parsers, Decimal arithmetic, customer files, runtime network
  fences, licensing, audit trails and human approval controls were not edited.

## Measured local verification

Tested with the byte-identical committed candidate module and regression
file on Linux CPython (not a full authenticated private checkout):

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover \
  -s products/desktop/tests -p 'test_ci_event_permissions_r295.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover \
  -s products/desktop/tests -p 'test_ci_event_permissions_r295.py'
python -m py_compile products/desktop/ci_event_permissions_r295.py \
  products/desktop/tests/test_ci_event_permissions_r295.py
```

- 30/30 standard methods PASS.
- 30/30 optimized methods PASS; **60/60 focused method executions**.
- Python compilation PASS.
- Committed/executed Git blob matches:
  - helper `b98db497bd1c22fd0a31b8e5e9bf0040f117e434`
  - tests `725dcbcc9d74da19558fcb5656403c84ccd3fff4`.
- Repository-wide inherited regression execution, full source-contract
  integration, YAML interpreted by GitHub, Windows builds, PE/smoke, Defender,
  accessibility and premium entitlement/distribution remain **UNVERIFIED**.
  A source guard cannot stop GitHub scheduling malicious YAML *before the
  guard is executed*; reviews and branch protections still matter.

## Operational blocker and highest-impact next step

The preceding R294 Actions run
https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42548679129
failed in **both** Ubuntu and Windows jobs **before recorded runner steps**.
The cause has not been established. Repository owner: inspect Actions
billing/spend limits, workflow permissions and runner availability, then
rerun the unmodified R295 head. If still blocked, execute the existing
private Windows 11 x64 offline candidate path on a trusted workstation
(without publishing); gather all six EXE hashes/PE validation, full source
suite, native smoke, current Defender, keyboard/NVDA and protected premium
access evidence.

**Release criteria:** independent QD review plus founder approval. The two
premium executables must remain access-controlled; never publish a public
artifact URL or infer application acceptance from these source tests.
