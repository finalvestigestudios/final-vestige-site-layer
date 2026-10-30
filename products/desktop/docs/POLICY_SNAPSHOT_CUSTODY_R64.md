# Labs R64 — Policy Delta Desk input snapshot custody (UNRELEASED)

## Product defect and user-facing correction

Policy Delta Desk previously checked an input pathname for a supported extension and
then opened a file descriptor for a bounded read. A local actor or concurrent
process could swap the pathname while the program read it. The report included
SHA-256 of the bytes actually read, but a replaced or concurrently modified
source could be accepted without warning. Additionally, two selections with
identical bytes reported only "No textual differences", making accidental
self-comparison easy to miss.

The R64 change reuses the **existing, previously tested**
`fvs_suite.csv_snapshot.read_csv_snapshot` on TXT, MD, and CSV policy inputs.
That helper verifies a regular-file `lstat` before opening, uses a bounded
single-descriptor read with `O_NOFOLLOW` where available, checks file identity,
size, timestamps, and path identity across the read, and fails closed for
observed mutations, symlinks, and swaps. Text is decoded and SHA-256
calculated from **the very same immutable bytes** that were read.

The existing 10 MiB per-file and 50,000-line caps, escaped source labels,
Unicode control rejection, UTF-8/BOM behavior, atomic non-overwriting
report publication, and exact before/after SHA-256 remain intact.

If both selected input snapshots have the **same byte digest**, the report
now visibly says to confirm that two intended versions were selected.
If the byte digests differ but decoded text has no differences (e.g. BOM-only
change), it instead explicitly requests human verification of that
discrepancy. The comparator never asserts legal compliance or approves
policy changes.

## Tests and verification boundary

Added `tests/test_policy_snapshot_custody_r64.py` with 17 focused
regressions: exact source digest and changed lines, identical path/content,
empty inputs, BOM-only differences, both input symlink positions, pathname
replacement before/after descriptor open, in-place mutation during read,
exact and over-limit size, unsafe controls, bad UTF-8 without private-value
echo, invalid extension/directory, and non-overwriting report publication.

Updated the **policy** packaged-engine synthetic smoke to verify both source
SHA-256 fingerprints and the accidental identical-input warning.

On a local Python 3.13.5 Linux reconstructed focused tree, the 17 new tests
passed with warnings as errors under both normal and optimized `python -OO`.
The tested R64 policy module, new test file, and reused R30 CSV snapshot/R28
atomic text modules are checked against their GitHub Git blob identities.
**This is not whole-repository verification.** The complete repository suite,
native Windows 11 x64 packaged binary, accessibility, malware scan and
independent QD approval remain unverified. Symlinks may be unavailable on
some Windows developer machines; focused symlink tests then skip explicitly
rather than falsely pass.

## Threat model and limitations

This guard detects common observable race and path-substitution scenarios,
not adversaries capable of changing metadata back exactly, modifying memory,
or replacing files **after** return. It does not prove independent origin,
authenticity, legal enforceability, or unaltered provenance over time.
SHA-256 is an identity fingerprint **not a signature**. Reviewers must
retain and secure original files separately; no source data is uploaded.

All six desktop programs remain development-only. Do not publish any of
their EXEs, expose premium builds without independent server-side access
control, or modify WordPress production/catalog availability. Complete
normal/-OO source suites and native Windows build + smoke acceptance are
required before any release. GitHub Actions upstream runner-start blocker:
[issue #75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75).
