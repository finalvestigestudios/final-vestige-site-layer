# R183 — Policy Delta global physical source-coordinate custody

**Status:** draft engineering evidence only; HARD RELEASE HOLD. Tracks #73; stacked exclusively on R182 (PR #923), never production `main`.

## Defect and correction

R182 validated exact built-in row containers, positive physical source-line identifiers within 1–50,000, and duplicate positions **within one hunk**. Direct Python callers could still supply multiple individually valid hunks that claimed the **same before/after source line** or presented those line positions in reverse chronological order. The secondary cross-script look-alike navigator then emitted mutually inconsistent physical citations even though no original input was modified.

R183 hardens `fvs_suite.policy_confusables.render_local_confusable_evidence` to establish global physical-coordinate custody **before** generating any look-alike cue. Each side's row identities must be strictly increasing within a hunk, and the next well-formed hunk's first physical line must be greater than the previous hunk's last physical line on the same side. Empty sides do not reset their checkpoint. Every source row is checked, **including overlong lines that cannot themselves be rendered**. A cross-hunk conflict returns **no supplemental look-alike navigation**, rather than emitting a first plausible citation while suppressing only a later inconsistent one. A locally malformed hunk continues to be skipped without contaminating independent valid hunks, retaining the R182 behavior. A collection over 50,000 hunks is refused.

Valid, disjoint coordinates preserve the preexisting navigational evidence, numeric Unicode code points, spoken character names, source file SHA-256 fingerprints, original bytes, bounded output (16 pairs / 8 glyph details per pair), and deterministic ordering. Changed `_owned_rows` is an **internal** helper. This does not perform OCR, Unicode security classification, legal interpretation, fraud classification, or compliance/payment approval. The human reviewer must inspect the exact cited original policy lines.

## Files

- `products/desktop/fvs_suite/policy_confusables.py` — two-phase global provenance validation and within-hunk order checks.
- `products/desktop/tests/test_policy_global_source_custody_r183.py` — **25 deterministic synthetic unit tests**, including both-side collisions, reverse ordering, oversized hidden rows, empty sides, independence, boundaries, stable/private output, and existing output bounds.
- `products/desktop/scripts/safe_unittest_r183.py` — fixed inventory of exactly 25 names; fail closed on missing/extra/skipped/erroring methods, normal or `-OO`.
- `.github/workflows/desktop-build.yml` — Ubuntu `source-tests` and Windows `windows-build` invoke strict runner in both modes.

## Verification evidence and limitations

Local isolated Linux **Python 3.13.5**, using source and test contents with Git blob SHA matching the GitHub R183 branch: `PYTHONPATH=. python -m unittest discover -s tests -p test_policy_global_source_custody_r183.py` — **25/25 passed**; same with `python -OO` — **25/25 passed**. Total **50/50 focused method executions**, no failures/errors/skips. `python -m py_compile` also passed. These are not whole-repository tests; do not imply that inherited R178/R180 real-file tests, native Windows GUI, all six x64 executable builds, installation/smoke, or protected distribution have been verified.

Prior R182 GitHub-hosted workflow [41812725521](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41812725521) failed in both jobs **before allocating runners** (zero steps). Check R183's exact-head run and its job start/step evidence; if it also fails before runner allocation, owner must investigate GitHub Actions billing and usage, account/repo Actions permissions, GitHub-hosted runner entitlement/provisioning, and the Actions error banner. Never treat a pre-runner failure as application tests run.

## Release/QD gate

**No executable, installer, signing, public download URL, payment gate, WordPress publication or production merge** is authorized. Retain independent QD review and explicit founder approval. All four free apps (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and both premium apps (GrantAudit Studio Pro and ProcureGuard Studio Pro) remain **unreleased**. Before any release, restore CI; run complete inherited integration suites and Ubuntu/Windows tests; produce and smoke-test six actual private Windows x64 builds; perform physical Windows 11 accessibility checks, authentic Defender/EDR review, signing/checksum/provenance verification, premium access-control validation, independent QD, and founder decision.

**Highest-impact next step:** restore GitHub-hosted runner allocation and run the unchanged R183 draft head, especially the inherited **7 R178 + 7 R180 Policy Delta real-file integration tests**.
