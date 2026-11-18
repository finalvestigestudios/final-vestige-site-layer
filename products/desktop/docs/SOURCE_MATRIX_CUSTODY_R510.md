# Labs R510 — Independent source-matrix execution custody

Status: **DRAFT / HARD HOLD**, issue #73. This is not a native Windows build, QD acceptance, or production approval.

## Defects and fixes

The R509 independent workflow was compacted beneath its inherited 8-KiB ceiling by moving its full 416-command test inventory to a Git-blob-pinned file. Two custody gaps remained.

1. The R385 test asserted the compact YAML still contained an obsolete phrase about 22 AES-GCM tests. R510 replaces the stale text check with *exact normal and optimized vault crypto test commands*, each required exactly once in the immutable inventory.
2. The R509 runner rejected a symlinked test file but accepted a regular file reached through a symlinked parent directory. R510 rejects symlinks at every required test-path component (products, desktop, tests and the test leaf), before launching anything.
3. The runner now strips GitHub environment/output command-file handles, askpass helpers and common cloud credential environment variables from subprocesses, reducing accidental exposure of workflow metadata to source tests.

## Evidence and limitations

Five new methods extend the already-scheduled R509 regression test module from 11 to 16: valid local-file acceptance, symlinked tests-directory rejection, symlinked products-directory rejection, credential/environment-handle isolation, and repair of the AES custody contract. All 16 inherited R385 test methods remain. On hosts where symlink creation is restricted, the two corresponding synthetic tests can be skipped; report actual skips and never count them as passes.

The pinned manifest Git SHA a55a9b5bcbee5b9f075a39fc581ed5a4716eaca3, its 414-command inherited prefix, all 416 ordered commands, both CI workflows and their approved size/time limits were untouched. No engine, financial logic, packaging, distribution or WordPress change was made. Actual GitHub Actions and full native Windows execution are still required.

## Next highest-impact step

Repo owner checks Actions billing/spend limits, private repository eligibility, runners and restrictions. Rerun R510 exact SHA and confirm all 416 test subprocesses run under the existing 20-minute limit on Ubuntu and Windows, including both Python modes; distinguish passes from skips. Then run all six real Windows x64 native EXEs, SHA-256 and Defender scans, keyboard accessibility, and premium entitlement checks. Independent QD review and explicit founder approval are mandatory.

**Hard HOLD:** no merge, public executable, premium download, release approval or customer data movement. Local-first privacy, Decimal-safe money and human compliance review remain unchanged.
