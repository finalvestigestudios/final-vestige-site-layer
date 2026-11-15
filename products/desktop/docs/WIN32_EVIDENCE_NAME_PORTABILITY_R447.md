# R447 — Windows x64 premium evidence filename portability (DRAFT / HARD RELEASE HOLD)

Related to [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R446 draft PR #2600, pinned parent 942772a1098353421efa1b2df2acf4dbd20134fd. No production main changes or release.

## Defect and change

R446 excluded invisible control labels and noncanonical JSON spellings, but accepted filenames that normal Windows APIs cannot safely resolve. Examples: ledger:2026.csv (alternate-data-stream separator), CON.csv / COM¹.csv / LPT1.csv (device aliases), names with leading or trailing ASCII spaces, terminal periods, Windows reserved punctuation, and overlong NTFS components. Such labels can appear valid in a manifest generated outside Windows but not carry reliably into the Windows x64 workflow. This is not a demonstrated checksum forgery or license bypass.

The common fvs_suite.evidence_label.canonical_evidence_label now rejects these names before any private source/report hashing by manifest_guard.inventory_text. premium_manifest_completion.verify_premium_inventory also rejects each decoded row before report hashing. This covers GrantAudit Studio Pro and ProcureGuard Studio Pro without changing Decimal arithmetic, SHA-256 digest semantics, original bytes, entitlement logic, telemetry, or human compliance review.

The validation refuses the Windows reserved path punctuation (angle brackets, colon, double quote, slash, backslash, pipe, question mark, asterisk); leading ASCII space; terminal period/ASCII space; CON/PRN/AUX/NUL/CONIN$/CONOUT$; COM1–COM9 and LPT1–LPT9 including Windows-recognized superscript ¹²³ aliases and extension forms; and basenames above 255 UTF-16 code units. Existing invisible/format/noncharacter refusals remain. Visible international names and interior spaces remain reversible and canonical.

Microsoft references: [Naming Files, Paths, and Namespaces](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file) and [File System Functionality Comparison](https://learn.microsoft.com/en-us/windows/win32/fileio/filesystem-functionality-comparison). This is a conservative Windows-first portability policy, not universal filesystem certification.

## Artifacts

- products/desktop/fvs_suite/evidence_label.py — common producer/verifier basename contract
- products/desktop/tests/test_windows_evidence_basename_r447.py — 5 pure helper regression methods (unsafe devices, punctuation, Unicode, UTF-16 length, custom string subclasses)
- products/desktop/tests/test_windows_manifest_integration_r447.py — 3 integration methods: prehash refusal for inputs and outputs; reader refusal for tampered input rows on both premium product layouts and optional fourth procurement input; reader refusal for report labels, preserving report bytes
- .github/workflows/desktop-source-evidence-r385.yml — Ubuntu/Windows normal and optimized R447 tests plus inherited R446/R254/R255
- this reviewer runbook.

## Execution evidence and limitations

A local isolated Python package with exact proposed helper logic and synthetic names passed 5/5 in standard Python and 5/5 with -OO -W error; source and tests passed compileall and AST parse. This is NOT a full GitHub checkout or native Windows execution. The 3 new full-module integration methods and inherited R446, R254, R255, six-engine suite are committed but not locally executed against the complete repository; do not count those as passing.

R446 CI failed before any recorded test steps: [source workflow #43697416239](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43697416239), [Windows build #43697416238](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43697416238). All observed jobs had no assigned runners; infrastructure cause unconfirmed.

## Compatibility and release hold

An existing evidence manifest with a newly prohibited name is held for human review. Do not silently rename or edit original evidence. If authorized, make a clearly tracked copy using a portable name, rerun the financial reconciliation and inventory, and retain the unmodified original for audit. Older mismatched inventories do not become authenticated.

**release_authorized=false**. No public EXE, ZIP, premium file, unrestricted premium URL, entitlement, website deployment, telemetry, payment approval, or main-branch merge. Genuine Windows x64 builds and smokes, Defender scans, checksum validation, protected premium delivery, independent QD review and founder approval remain necessary.

**Next action:** inspect failed-job annotation details and GitHub Actions billing/spending limits, repository policy and hosted-runner eligibility. Restore runners, execute R447 exact-head tests including full-module methods, then finish the six-app Windows release gates.
