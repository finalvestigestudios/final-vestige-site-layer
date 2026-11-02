# Final Vestige Labs R124 — fail-closed physical reviewer witness inventory

**DRAFT / RELEASE HOLD · Issue #73 · stacked on R123 draft PR #529, not production.**

## Why this matters

The R122 one-check Windows 11 recorder verified the 46-slot matrix and all
**referenced** witness notes before recording another result. The R123
read-only progress tool subsequently began rejecting **unreferenced/orphan**
notes and unexpected directory entries, but the R122 writer could still
append additional evidence into that already-contaminated review folder.

An interrupted R122 attempt can leave an unreferenced file, or a reviewer
may accidentally place a different file in the dedicated witness folder.
Continuing to record human PASS/FAIL decisions into a dirty folder risks
concealing a custody incident until the next read-only progress check.

## Implemented behavior

The new scripts/windows11_witness_inventory_r124.py shares a single
strict manifest-vs-directory contract between the R122 writer and R123
reader. It enumerates exactly the filenames corresponding to matrix slots
whose state is human-recorded PASS or FAIL. Every such entry must be an
ordinary, single-linked, non-symlink, non-junction, non-reparse file. Every
NOT_RUN slot must have no witness digest, and unexpected entries are fatal.

The **R122 writer now checks the complete witness inventory twice**, both
under its cooperative lock *before* reading the new observation and
*after* writing the new witness but *before* atomically replacing the
matrix. An unexplained orphan, temporary file, directory, hardlink or
missing referenced note raises HOLD. If a second-check inventory failure
occurs, R122 preserves the unchanged matrix and removes only the new
witness it created when the bytes still match; **it does not remove any
unexplained orphan or third-party file**. It also rejects placing the
matrix and witness folder together, because the reviewer lock/matrix are
not witness notes.

**R123** uses the same inventory validator both before and after its
revalidation of referenced witnesses. Its output remains counts and fixed
check IDs only; no observation text, private path, SHA pin, reviewer ID,
financial content or human finding is printed. Both tools retain
RELEASE_HOLD regardless of recorded PASS count.

## Operator handling

Continue using the R122 and R123 runbooks with a **dedicated witness
directory** that is different from the directory holding matrix.json.
If either tool returns its redacted HOLD, **stop recording immediately**.
An authorized human reviewer must investigate the unexpected local entry,
determine whether it represents interrupted or conflicting evidence,
preserve a private incident record according to the organization's
custody procedure, and only then decide whether to restore a known-good
matrix/witness pair or restart the review under new custody. Do **not**
delete or reclassify mysterious files automatically, suppress the HOLD,
or use an unattended cleanup script.

The R9 digest must still be authenticated out of band and pinned to the
exact six privately retained, Windows-smoke-tested EXE bytes. The R124
module does **not** authenticate the human reviewer or make hostile
filesystem access impossible. Its lock is cooperative, not a substitute
for OS access controls or independent attestation.

## Tests and deployment gates

tests/test_windows11_witness_inventory_r124.py provides **14 source-owned
synthetic regressions** for clean progress, preexisting orphans, hidden
files, extra directories, missing notes, simulated hardlinks/symlinks,
same-folder rejection, rollback when an orphan appears between inventory
checks, preservation of other files, and explicit recovery after human
investigation. scripts/safe_unittest_r124.py fails for any missing,
duplicate, failed or skipped method and redacts fixture/user content.

The workflow runs the 14-method suite in **normal and -OO optimized modes
on both Ubuntu and Windows**, in addition to inherited source, native
six-EXE, encryption, GUI and source-provenance gates. Synthetic fixture
tests are not evidence of physical accessibility or actual Defender scans.

**All six apps remain unreleased.** No production/site content, financial
Decimal engines, licensing, customer data or premium binary distribution
is changed by R124. QD review, founder approval, independent physical
Windows 11 accessibility checks (46), Defender/EDR review, signing and
premium access controls are still required.
