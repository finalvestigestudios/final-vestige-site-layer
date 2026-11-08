# Labs R291 — premium review journal final-path custody

**Status: draft / unreleased.** Tracks issue #73; stacked on R290 commit
`3775164d24df2607f12126333c81caefb42c85f1`, not production `main`.
Independent QD review and founder authorization are mandatory before merge,
site publication, any executable release or premium delivery.

## Reproduced defect

Both GrantAudit Studio Pro and ProcureGuard Studio Pro append human-reviewed
JSONL records through `fvs_suite.journal_io.append_verified_event`. After its
final `fsync` and descriptor `fstat`, the implementation checked only that the
final pathname still referenced the same regular inode. A noncooperating writer
could grow or modify that inode **between final `fstat` and pathname `lstat`**.
In that observable case the old implementation returned success even though
pathname size or timestamps no longer matched the verified descriptor view.
This is an audit-custody/false-success defect; it does not establish that any
released customer journal was affected.

## Change

After the existing final pathname/identity verification, compare the
pathname's metadata against the already-pinned final descriptor using the
shared `_same_path_descriptor_signature` helper. Refuse to report a successful
append if identity, size or modification time differs. The helper avoids a
false rejection on Windows when creation time differs between `lstat` and
`fstat`. Keep the original evidence untouched after any uncertain append:
**no rollback, deletion, automatic approval, or successful audit claim**.
OS errors continue to use R290's context-free privacy error messages.

Tests inject controlled, real filesystem mutations precisely between the
final descriptor observation and pathname observation. Growth and same-size
in-place corruption both failed to raise on the original R290 source; patched
code raises and retains evidence. Other tests verify sanitized OS failure and
path-disappearance errors; Windows creation-time API-view disparity; existing
and new journal byte-exact success; invalid-event rejection.

## Reproduction

Run from repository root with the exact dependent source checkout:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_postappend_custody_r291.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_postappend_custody_r291.py' -v
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_io_privacy_r290.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_io_privacy_r290.py' -v
python -m py_compile products/desktop/fvs_suite/journal_io.py products/desktop/tests/test_journal_postappend_custody_r291.py
```

## Verified local evidence — 2026-11-08

Linux Python, actual temporary file I/O and injected final-stat races:

- New **8/8** tests pass standard, **8/8** pass `-OO -W error`.
- Inherited R290 **12/12** tests pass standard and **12/12** pass optimized.
- **40/40** focused test-method executions; Python compilation passes.
- Exact unmodified parent `journal_io.py` Git blob
  `1850df4c21412f579c7100d8697e8ed396bae7dd` reproduces **2/8** new
  test failures; restoring the fix passes 8/8. Unmodified dependency
  `csv_snapshot.py` Git blob `08c08598ac3575e3baf53ee3275db9aadc315f4d`
  and unmodified R290 test blob `749b1f064caf5bf1e234186020945cb4cb521ba4`
  were used for this limited local test checkout.
- Full inherited repository test suite, real native Windows execution and
  Windows filesystem/ctime behavior were **not** verified locally.
- Existing internal Actions workflow was extended with explicit normal and
  optimized R291 gates for both Ubuntu and Windows; runner execution is
  separately tracked and is not a local test pass.

## Boundaries and next release gate

This is a last-observation integrity check, **not** a lock against privileged
filesystem adversaries, concurrent writers editing after this function returns,
or malicious writers forging identical metadata. All cooperating writers must
still take the premium review lock; no automated compliance determination is
introduced. The four free utilities, local-first processing, Decimal-safe
money logic, paid access restrictions and user-controlled approvals are
unchanged.

The previous R290 Actions run
[42528619087](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42528619087)
failed before recording execution steps for both `source-tests` and
`windows-build` (root cause not confirmed). Owner unblock: review Actions
billing/spend restrictions, workflow permissions and runner allocation, and
rerun the exact R291 head. Then execute full integration and **genuine private
Windows 11 x64 six-EXE build/smoke/SHA-256/Defender**, physical keyboard and
screen-reader acceptance, and **gated premium** distribution verification.
Do not publish downloads or make production/QD changes on this draft branch.
