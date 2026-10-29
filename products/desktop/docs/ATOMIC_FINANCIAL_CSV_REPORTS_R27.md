# R27 — complete, exclusive local CSV report publication

**State:** source-only prototype, not a verified Windows release; issue #73.

## Risk and affected applications

Previously `fvs_suite.engine.save` wrote directly into the final .csv
destination. A disk-full condition, row conversion exception, or interrupted
write could leave a truncated file carrying a convincing finished-report name.
A report-name collision also needed consistent no-overwrite semantics.

The shared writer serves **LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite,
GrantAudit Studio Pro and ProcureGuard Studio Pro**; it leaves policy text
comparison and premium review journal/register separate and unchanged.

## Implementation

1. Create a cryptographically unpredictable same-directory staging file using
   `tempfile.mkstemp`; POSIX files are private (0600) by default.
2. Stream deterministic CSV records without an additional copy of all rows;
   preserve UTF-8 BOM, original column order, quoting and the existing
   `safe_cell` spreadsheet-formula neutralization callback.
3. Flush and `fsync` the complete staged file, closing its handle.
4. Publish using `os.rename` on Windows (which refuses preexisting targets)
   or exclusive `os.link` on POSIX (where rename might overwrite). The
   staging file and final report live in the same directory/filesystem.
5. Clean temporary staging files through `finally`, including when row
   iteration, conversion, write, fsync or publication fails. A rejected
   destination is never overwritten or dereferenced.

A filesystem that disallows the selected exclusive publication method causes
a visible error. No unsafe overwrite fallback is attempted.

## Evidence / limits

Eleven new real helper tests exercise UTF-8 BOM and multiline records, POSIX
0600 permissions, symlink and collision resistance, failing generators/cell
converters, simulated fsync/publication failures, ignored fields and a
5,000-record lazy stream. Three additional engine-wiring tests were committed
for CI (not run locally). The helper passed on Linux Python 3.13.5 in normal
and `-OO` execution with warnings treated as errors.

The test fixtures are synthetic, never customer financial data. Failures after
a system crash or forced process termination may leave a private staging file.
Multi-file outputs (e.g., GrantAudit's two CSV files plus its manifest) are
**not** an all-or-nothing transaction; separately written manifest and premium
review register paths are **not** hardened by this sprint. Power-loss directory
durability and native Windows behavior remain unverified.

No monetary calculations, source imports, review decisions, entitlement
checks, production site, QD workflow or premium download controls were changed.

## Remaining gates

Restore runnable CI or execute full repository tests on a trusted checkout,
then build, inspect and smoke-test all six Windows x64 executables, preserve
checksums, security/AV results and operator evidence. Keep premium files
behind effective access controls; obtain human QD approval before site release.
