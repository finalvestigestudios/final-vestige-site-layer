# R342 — Native procurement source-reference custody (DRAFT / HARD HOLD)

**Scope:** ProcureGuard Studio Pro's local-only invoice-credit/receipt-return original-document-spelling review. Base: R341 (`4bdd7ce38db0e067ceaa0c6bc8d34bb3355261f8`), not `main`. No app builds, premium artifacts, production edits or release authorization.

## Reproduced defect

`source_document_spellings` and `has_original_spelling` previously called `str(value)` on arbitrary direct-API values. A custom object, `str` subclass or `int` subclass could execute a hostile `__str__` hook, forge a reviewer-visible source ID, or throw a private-path-containing error. A forged `frozenset` subclass could also override membership and decide an apparent original match. In `review_line`, two preparatory `str(...)` conversions bypassed any later helper boundary.

**Before-fix reproduction:** same 24-case R342 adversarial suite against the original R341 reference helper in an isolated Linux fixture: **8 failures, 7 errors**. Synthetic hostile strings only; no client files or Windows applications.

## Changes

- `fvs_suite/procurement_reference.py`: allow only **native `str`** and **native `int` up to 269 bits** for original reference labels; reject subclasses, `bool`, arbitrary object coercion, and oversized integers before calling `str`. Keep ASCII-only case comparison and original boundary whitespace semantics. Demand a native `frozenset` of native strings before set membership. No automatic compliance decision; source/reference mismatches remain review flags.
- `fvs_suite/procurement.py`: remove two pre-conversion `str(...)` calls feeding the source fingerprint guard. Ordinary CSV reader outputs remain native strings; numeric direct input compatibility remains for bounded native integers.
- `tests/test_procurement_native_document_r342.py`: **24** new cases covering hostile conversion hooks, membership spoofing, false numeric identifiers, Unicode distinctness, original whitespace semantics, determinism, and native numeric compatibility.
- `.github/workflows/desktop-build.yml`: require R75 historical 25-case original-identity suite plus R342 on both Ubuntu and Windows, standard Python and `-OO`, before packaging. No workflow permission or distribution change.

## Exact local test evidence and limits

- Local **Linux Python 3.13.5**, no network, isolated six-app helper package with `review.ascii_case_identity` copied from its real R341 implementation; real source/tests copied from R342 Git and checked using `git hash-object`.
- **24 R342 + 25 inherited R75 = 49/49 PASS** standard (`-W error`) and **49/49 PASS** optimized (`-OO -W error`), **98 focused method executions**. Python `py_compile` PASS. Zero skipped tests in this isolated execution.
- Git blobs: source `ef9b011033d6d80eab957435112b898915a902dd`; R342 regression `eb9c8fead05add322cc58c218ea8b9e3876275e7`. Existing R75 methods were re-created exactly as shown in R341 source for local replay; `review.py` dependency was a faithful minimal reconstruction **rather than the full repository package**.
- **Not locally executed:** whole-repository `fvs_suite.procurement.review_line` integration, all other desktop tests, 22 genuine AES-GCM integration cases, real Windows native binaries, Defender scan, accessibility testing, or protected premium delivery. The changed `procurement.py` call sites and CI remain awaiting actual hosted execution. Do not reinterpret 98 focused local executions as platform acceptance.

## Active blockers and next highest-impact step

R341 hosted [Actions run #42927571166](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42927571166) failed on November 10, 2026; Windows `windows-build` and Ubuntu `source-tests` had `steps=null` and `logs_url=null`. Root cause is **not confirmed**. Owner should inspect Actions billing, minutes/spend caps, runner allocation, workflow/check-run permissions and annotations to permit real runs. Next, execute R342's required cross-platform tests alongside the whole desktop suite and the 22 AES-GCM cases; then complete Windows 11 x64 binaries and independent QD/founder review. Premium access remains gated; all six apps remain **UNRELEASED**.

No source financial data, uploads, telemetry, customer content, download links, unrestricted premium executables, or compliance approvals were created.
