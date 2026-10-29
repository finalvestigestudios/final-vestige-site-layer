# R32 — All-or-nothing GrantAudit evidence publication

**Draft, source-only. No binaries approved or distributed.**

## Defect
Before R32, the legacy and linked-allocation GrantAudit engines individually
published the exceptions CSV and budget CSV *before* source-digest validation
could finish building the evidence manifest. A changed source, a failed
manifest write or a full disk could leave two plausible but **unendorsed**
reports in the chosen output directory. R27/R28 made each individual file
atomic; they did not provide atomic visibility for the three-file package.

## Implementation
Both GrantAudit paths now call `grant_bundle.publish_grant_bundle` with their
existing output writers. The helper creates a private, hidden, same-parent
staging directory; builds the exceptions CSV, budget review CSV and R31
source-bound SHA-256 inventory inside it; checks exactly three regular output
files with the expected names; and publishes the complete directory with a
single same-filesystem rename. It returns the same three Path objects in the
same order, now under `<chosen-output>/grant-evidence-<UTC>-<128-bit-token>/`.

On any validation, build, source change, or rename failure *before publication*,
the helper removes its private staging directory. It never removes existing
user exports or source data. Previous packages remain untouched. On POSIX,
the directory inherits the temporary directory's private 0700 mode. This
does not require networking, telemetry, account login, or a license change.

**Compatibility note:** report files now live in a unique package subfolder
rather than directly inside the selected output folder. UI consumers should
open the returned full paths, not reconstruct basenames.

## Threat-model limitations
The directory rename is atomic for observers on the same filesystem but is
not a transaction across disk controllers, a durable fsync of the parent
directory, a Windows installer/AV certification or a signed audit record.
An unpredictable target and a preflight collision check are not a guaranteed
no-replace primitive against malicious concurrent writers on all platforms.
Privileged local writers, subsequent edits, filesystem corruption and manual
approval remain outside this guard. Only GrantAudit uses this bundle helper;
ProcureGuard reports retain their separate publication strategy.

## Verification and release blockers
15 real-helper filesystem tests cover success, cleanup after exceptions,
manifest failure, disk-rename error, untracked files, nonregular files,
symlink output folders, destination collision, private permissions and
preservation of previously published evidence. Five additional full-engine
tests cover legacy, linked and source-change cases. CI runs both, including
optimized `-OO` Python source checks on Linux, and full suite on Windows.

No Windows x64 native binary was built, scanned or smoke-tested here.
Hosted Actions jobs have previously failed before step 1; integrated engine
tests and cross-platform packaging need a trusted runner before release.
The Final Vestige QD approval workflow and premium gated distribution are
untouched. All compliance/payment findings still require human review.
