# R208 — Strict rendered CSV evidence custody (DRAFT / HARD RELEASE HOLD)

Tracks [Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This change is on an isolated feature branch **stacked on R207 draft PR #1081**, starting at immutable `17c0927e3306c00a4d8f103f989d8e2f78c6f6ad`; never target or publish to `main` without independent QD and founder approval.

## Defect and behavior change

The shared six-app CSV writer `fvs_suite.atomic_reports.write_csv_report` accepted the sanitizer callback's row output without type or safety validation. Python's `csv.writer` silently coerces `None`, raw `Decimal`, integers and byte strings to CSV representations; a sanitizer returning `=SUM(...)`, `+...`, or `@...` can bypass obvious formula safeguards, and NUL can create ambiguous spreadsheet evidence. These issues also applied to otherwise-ignored extra row columns. R207 validated rendered *headers* but not returned row-cell types, NUL or blatant formula prefixes.

A private `_render_cell` helper now calls the existing sanitizer **exactly once** and requires a **native `str`** without NUL and without bare leading `=`, `+`, or `@`. It is used on **headers and every row item (including ignored extra fields)**. A malformed result raises a **static, privacy-safe** `ValueError` and the existing atomic publication logic removes the staged partial file; existing output remains untouched. Positive cases preserve UTF-8 BOM, line breaks in values, signed negative Decimal amounts stringified by `engine.safe_cell`, lazy rows, exclusive publication, and original row source keys.

**Scope:** This is defense-in-depth, not a replacement for `engine.safe_cell`'s more extensive invisible-prefix formula policy. It neither changes Decimal computations nor interprets compliance / approves payments. It is not a general sandbox or a claim about spreadsheet importers.

## Executed test evidence

On Linux local Python, from **exact committed-source Git blobs** reproduced in an isolated minimal test directory, using synthetic financial fixtures only:

- **Red phase against exact R207 writer blob** `59af5aa1c6a57770844a3fef07693b01815fd969`: the new 18-case R208 suite failed with **12 failures and 6 errors**. This demonstrates the missing callback-result contract.
- **Green normal Python:** R208 **18/18**, exact inherited R207 **14/14**, exact inherited R27 **11/11**; **43/43 PASS**.
- **Green optimized `-OO`:** same three exact suites **43/43 PASS**; **86/86 total test-method executions**, zero skips.
- `python -m py_compile` for changed production/test modules: PASS.
- Git blob identities locally checked: updated writer **`b761fa16dada427da99eac5ad952a21b7daf9715`**, new R208 18-method tests **`26452413760d70b5c296465b6b643d7d99e45b20`**, inherited R207 tests **`42474f9e0649c81651e2874207c2f53909cfaa2e`**, inherited R27 tests **`3e9d020f527771dd768fd4af49dbfa091d4db8fb`**.
- CI workflow receives an explicit new 18-case normal/`-OO` step in **Ubuntu source-tests** and **Windows windows-build** (4 Python invocations, two Windows exit-code gates). This confirms **configuration**, not hosted execution.
- Tests cover formula prefixes in headers and cells, malicious `str` subclasses, `None` / bytes / numeric / Decimal sanitizer results, NULs in included and ignored fields, old evidence non-overwrite, failed second row cleanup, BOM, physical multiline records, one-call sanitizer behavior, and safe signed amount output.

Local verification is **not** the entire inherited desktop source suite or native Windows execution. The other six application engines, real Windows x64 executables, Windows 11 accessibility, signing, Defender scan, and premium license/download isolation have **not** been accepted or released.

## CI/release/QD constraints and immediate next step

Prior [R207 GitHub Actions #42016100084](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42016100084) reported failed `source-tests` and `windows-build` jobs, each with **no available step records**; the underlying runner/quota failure remains undiagnosed. **Do not** interpret as executed Python failures or successful Windows builds.

**Smallest owner unblock:** inspect the run's GitHub Actions failure banner and billing/usage permissions, runner provisioning and repository Actions policy. Restore hosted execution and rerun the **unchanged R208 head** on both Ubuntu and Windows; record actual job steps and full suite results. Run private six-EXE packaging, checksum verification, native Defender scanning, Windows 11/NVDA keyboard/high-DPI smoke and accessibility acceptance. Secure premium downloads behind genuine access control and obtain separate independent QD/founder release approval before any site or main merge.

All work here is branch-local. No public downloads, no premium artifact distribution, no WordPress publication, and no production changes.
