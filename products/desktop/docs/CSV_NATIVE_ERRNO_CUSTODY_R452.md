# Labs R452 — native errno custody in shared CSV publication

**Issue:** #73 · **Status:** DRAFT / release HARD HOLD · **Parent:** R451 draft PR #2629 at exact commit `2d6290ea58d17d112ac190aae1cad3f214498978`. Neither branch nor commit is production `main`.

## Defect and impact

The six desktop financial utilities use a shared CSV publication guard. Its `private_csv_failure(error)` builder previously accessed `error.errno` **three times** through ordinary Python attribute lookup. An `OSError` subclass can override `__getattribute__` or `errno` with a property that throws a confidential exception or forges a different errno. That can bypass the fixed-message privacy boundary or misclassify an actual error. This is a focused defensive correctness bug, **not** evidence of an observed customer exploit.

## Change

The builder now retrieves the CPython-native `OSError.errno` member descriptor **once** using `OSError.errno.__get__(error, OSError)`, bypassing subclass getter hooks. Only exact positive `int` values survive; boolean, string and negative errno values fall back to `errno.EIO`. `FileExistsError` retains the existing path-free collision message. Callers must continue raising the sanitized result **outside** the original exception handler, so hidden `__context__` does not retain private paths.

No input CSV files, originals, Decimal calculations, audit evidence, compliance judgments, premium licenses or publication workflows are modified.

## Reproducible focused evidence — 2026-11-15

Environment: isolated Linux CPython **3.13.5**, minimal source package, synthetic financial identifiers and simulated error subclasses, no customer files, no installer, no network.

- Controlled pre-fix run against the inherited R451 guard: **8 of 9 test methods failed** (6 errors / 2 assertions); one collision test passed.
- With the patched shared production guard and R452 test file: **9/9 PASS** with `python -W error -m unittest discover -s tests -p test_csv_errno_descriptor_custody_r452.py`.
- Same focused suite under `python -OO -W error`: **9/9 PASS**. Total **18 focused passing executions**.
- Local `compileall`: **PASS**.
- These are focused *minimal-package* executions, not complete repository integration or native Windows verification. Host CI must execute the committed test and inherited R237/R451 integration before merging.

## Release/QD gates

R452 is a stacked **draft**, not a published executable. Do not merge, publish Windows binaries or link premium downloads. Do not change the live site. Require independent QD review plus explicit founder authorization after working CI proves six-app tests, Windows x64 packaging, Defender, keyboard/accessibility checks, SHA-256 verification and gated premium distribution.

**Known blocker:** recent GitHub Actions Windows and Ubuntu jobs have exited with **zero recorded steps**; runner allocation or policy failure cause unconfirmed. Repository owner should inspect Actions run annotations, account billing/spending limits and runner permissions, then rerun the exact-head workflows. No hosted or Windows result may be inferred from local passes.
