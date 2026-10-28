# R20 — Strict premium review CSV intake and physical-row provenance

## Why this matters

The **human-only** review queues for GrantAudit Studio Pro and ProcureGuard Studio Pro previously parsed reports with `csv.DictReader`, which counts *logical* records rather than the physical source-file lines printed in audit references. Quoted multiline text or blank lines could therefore misidentify the cited source row. The reader also tolerated truncated records and some invalid quoting. Those conditions should never lead to a review journal that appears to certify a trustworthy input.

## Implemented contract

`fvs_suite.exception_review.read_cases` now uses `csv.reader(strict=True)`. Before returning any queue, it:

- Decodes UTF-8 (including BOM), rejects NUL, enforces the existing 64 MiB cap, and checks normalized header uniqueness and required columns.
- Counts physical CSV lines, including continuation lines inside quoted records and blank lines; rejects malformed quotations, extra fields, and missing trailing fields.
- Counts the existing 200,000 **nonblank logical records** for the size cap, separately from physical source lines.
- Computes each case identifier from the existing file-hash-bound scheme and the **physical starting line**; normal single-line files retain their previous IDs.
- Leaves `matched` out of the review queue, but validates its field count and identifiers before skipping it.
- Keeps the existing append-only, hash-linked local journal and explicit `needs_evidence`, `escalated`, `reviewed` decisions. None authorize payments, expenditures, or compliance.

## Existing review journals: fail-closed compatibility warning

For ordinary reports with one line per CSV record and no blank lines, case IDs and `report_row` remain unchanged. **Any review journal previously created against an identical report containing embedded newlines or blank lines might now have incompatible row references or case IDs.** The journal validator intentionally rejects this mismatch; it **does not silently migrate, reinterpret or delete the evidence**. Preserve both originals, escalate to a human reviewer, and create a new journal only under an approved, documented evidence-migration procedure. Do not edit event hashes.

The physical reference is the first physical line of a record, not its final continuation line; numbers are one-based and include the header and blank lines.

## Reproduce tests after checking out PR R20

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_premium_review_csv_r20.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_human_review_r7.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

Local independent test environment for the R20 logic: Linux Python 3.13, **15/15 isolated CSV-intake checks passed normally and with `-OO`**, plus `compileall`. These local checks ran a manually reconstructed intake function with matching logic and helpers; they are **not** a complete checkout of the target repository. The **17 committed integration tests and full repository suite remain unexecuted** until a working runner or trusted local checkout is available.

## Release posture

R20 changes **only premium report ingestion, tests and documentation**; no production code is merged, no app is published, no signing or license credentials are issued. All six native Windows x64 executables remain subject to the prior six-app release gate: complete regressions, verified build, executable smoke, hashes, malware/signature checks, premium download authorization, and human QD publication approval.
