# Final Vestige Labs — Desktop Utilities

**Pre-release engineering branch. Not production-ready.** Four free utilities and two premium product prototypes share a local-only deterministic engine. Nothing uploads user documents, calls an LLM, or makes an automated compliance decision.

| Executable name | Tier | Inputs | Output |
| --- | --- | --- | --- |
| LedgerDiffLite.exe | Free | left and right transaction CSV | matched, missing, duplicate-ID, variance report |
| InvoiceTwinScout.exe | Free | invoice CSV | exact/review duplicate candidates |
| SpendMapLite.exe | Free | vendor spend CSV | monthly spend by normalized vendor/category and spike flags |
| PolicyDeltaDesk.exe | Free | old and new TXT/MD/CSV | unified text diff |
| GrantAuditStudioPro.exe | Premium (internal preview) | claims, ledger, budget CSV | reconciliation, budget exceptions, evidence SHA256 manifest |
| ProcureGuardStudioPro.exe | Premium (internal preview) | PO, invoice, receipt CSV | three-way matching exceptions and SHA256 manifest |

## CSV headers

Headers are case-insensitive; spaces are accepted in place of underscores. The importer also recognizes common synonyms listed in fvs_suite/engine.py.

- LedgerDiff: transaction_id, amount
- InvoiceTwin: vendor, invoice_number, amount, date
- SpendMap: vendor, amount, date, optional category
- GrantAudit: claims (transaction_id, amount, program); ledger (transaction_id, amount, program); budgets (program, budget)
- ProcureGuard: purchase orders (po_number, line, quantity, unit_price); invoices (same); receipts (po_number, line, quantity)

Dates: YYYY-MM-DD or MM/DD/YYYY. Amounts: decimal strings; currency symbols, comma thousands separators and accounting parentheses accepted. Currency conversion, multi-currency, unconstrained allocation rules, fuzzy name matching, and OCR are **not** supported in v0.1. GrantAudit R6 supports explicitly linked split allocations under a limited documented CSV contract. Financial flags require human review.

## Local development

Python 3.12+ with Tkinter. From repository root:

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
    PYTHONPATH=products/desktop python -m fvs_suite.demo ledger

The six GUI entrypoints live under products/desktop/launchers. Windows CI uses PyInstaller and uploads **internal build artifacts only**; do not distribute or publish until tests, malware scan, clean-machine acceptance, release versioning, SHA256 and (preferably) code signing are complete.

## Invoice Twin Scout R4 candidate safety and scale

- Invoice exports with more than 200 transactions for one normalized vendor and amount are now supported when report density is manageable. Near candidates use a chronological seven-day inclusive sliding window, rather than comparing all rows across all dates.
- Exact normalized invoice-key occurrences are anchored to the first source row regardless of dates; same-vendor, same-amount near candidates use a seven-day window. No label implies a duplicate *payment* or fraud determination.
- Original vendor names, invoice numbers, dates, and CSV source row references are all exported. Independent review flags indicate normalized-key collisions, exact-invoice amount mismatches, or distant dates; all need human confirmation.
- A dense input producing more than 100,000 candidate review pairs is explicitly rejected **before saving any report**. Narrow the input by vendor/date; reports are never silently truncated.
- See [Invoice Scale R4 specification](docs/INVOICE_SCALE_R4.md) for complexity, test cases, scope and limitations.

## R10 optimization-safe smoke checks and mutation detection

All 30 packaged-engine smoke invariants now use explicit runtime failures rather than Python `assert`, which is discarded by optimized Python (`-O`). The candidate verifier re-hashes all six executables and its checksum inventory before and after every smoke invocation, rejecting persistent file changes even if a program exits zero. Smoke stdout and stderr are discarded rather than buffered without bounds. Added adversarial synthetic tests and a CI `python -O` test step. See [R10 security and verification notes](docs/SMOKE_INTEGRITY_R10.md). **This remains a development-only verification mechanism, not approval to distribute.**

## Packaged-executable smoke verification (internal CI)

Each portable Windows executable accepts `--smoke-test`. It runs its actual core workflow against disposable **synthetic test fixtures** under the system's temporary directory, validates a known exception or diff, deletes temporary data, and exits with status 0 only if all checks pass. GUI is never initialized and no network connection is used.

    .\dist\LedgerDiffLite.exe --smoke-test
    .\dist\InvoiceTwinScout.exe --smoke-test

CI launches **all six** EXEs as real processes after packaging, checks their exit codes and SHA256 fingerprints independently of the packaging step, and only then uploads a private short-retention artifact. This is a **packaging smoke check**, not yet a substitute for Windows 11 clean-machine/GUI testing or a malware scan.

## Import integrity and review policy

- Duplicate or blank normalized CSV column headers are rejected rather than arbitrarily choosing a column.
- A transaction/grant ID pair equal only after punctuation normalization (for example, `INV-100` versus `INV100`) receives `normalized_id_review` instead of `matched`; any simultaneous amount variance is separately retained. This protects against incorrect automated reconciliation.
- Case-only ID differences are treated as equivalent, but punctuation is **not** silently asserted to be the same real-world identifier.
- Amount parsing uses Python `Decimal`, not floating point; invalid and nonfinite amounts are rejected.
- CSV report cells beginning with spreadsheet formulas are neutralized to reduce formula-injection risk when opened in spreadsheet software.
- Duplicate IDs, ambiguous matches and all policy/audit flags require human judgment; the software does not authorize payments or certify compliance.


## ProcureGuard Studio Pro R5 — credits, returns, partial deliveries and reviewed tolerances

- Explicit positive `invoice` versus reversing `credit` and positive `receipt` versus reversing `return` events; negative numeric quantities are rejected. Untyped legacy inputs remain positive transactions.
- Optional invoice/receipt `event_type`, `document_id`, and `related_document` columns provide document-level review. Unlinked credits/returns, amount deviations, repeated invoice IDs and normalized-reference collisions remain visible as exceptions.
- Legitimate identical partial invoice amounts with **different, explicit invoice document IDs** are not automatically misclassified as duplicate entries. When document IDs are absent, conservative duplicate review stays enabled.
- Gross and net quantities and invoice values are reported separately, preserving audit trails. All credit memos and returns remain explicitly flagged for a human reviewer, even if arithmetic balances.
- Optional local price policy JSON is accessible from the **ProcureGuard Studio Pro** desktop GUI. Values are bounded, schema-checked, Decimal-exact and fingerprinted in the report/evidence manifest. Looser tolerances always produce a visible review flag.
- A complete synthetic pilot scenario, documentation, and source samples are in [PROCUREMENT_R5.md](docs/PROCUREMENT_R5.md). This is a **development prototype**, not an entitlement-protected commercial edition.


## GrantAudit Studio Pro R6 — linked split allocations and credit memos

- Optional claim-ledger source links enable **many claim lines across grant programs to reconcile to one ledger transaction**. This avoids incorrectly treating legitimate split reimbursements as missing records. Splits always remain flagged for human review.
- Use claims CSV headers `claim_id,amount,program,ledger_reference`; optional `claim_type` and `related_claim` support explicit credits (positive amount with linked original claim). The original three-file output and legacy single-ID matching remain supported.
- Claims are totaled per source ledger reference and program budgets per claim program, with gross/credit/net amounts, original row references, and source identities in the output. Ambiguous source links, repeated claim IDs, unlinked/cross-program/excessive credits, negative values and missing budgets are visibly reviewed or rejected.
- A credit-related column without a source ledger_reference is a fail-closed import error, preventing silent positive-credit accounting in legacy mode.
- Includes a synthetic two-program split + claim credit scenario in [R6 documentation](docs/GRANT_ALLOCATIONS_R6.md), 24 additional repository regressions, and a linked-mode packaged-executable smoke check. The R6 code has **not** passed full repository or Windows packaged-executable validation yet. Premium licensing remains unimplemented.

## R7 — Human exception review workbench (premium previews only)

- **GrantAudit Studio Pro** and **ProcureGuard Studio Pro** now expose a keyboard-accessible **Review exceptions (human only)…** window. A generated CSV report or previously saved report can be opened for operator review.
- Every exception receives an ID tied to the exact report SHA-256 and source-row position. An operator must explicitly record an identified reviewer, a substantive rationale and one of three choices: `needs_evidence`, `escalated`, or `reviewed`. None of these means compliant, approved or payable.
- Review actions are appended to a local, hash-linked JSONL journal. A separate sanitized register export shows unresolved / reviewed states without altering original reports. Modified source reports or broken journal hashes fail closed.
- The review journal is **plaintext, unsigned and unencrypted**. Its SHA-256 chain can detect many accidental changes, but is **not tamper-proof**, does not authenticate people and requires stronger protections before real sensitive data may be used. A stale lock file after a crash requires operator investigation.
- Unit regressions and packaged-EXE smoke paths are committed but **not yet verified on hosted Windows runners**. See [R7 review specification](docs/HUMAN_EXCEPTION_REVIEW_R7.md).


## R8 — Authenticated encrypted copies of premium review evidence

- Both premium review windows can now **Seal encrypted copy…** and **Restore encrypted copy…** using a user-entered, confirmed passphrase. The archive contains an authenticated AES-256-GCM encrypted snapshot of the exception CSV and (if present) its R7 human-review JSONL journal.
- The archive uses scrypt key derivation with a random salt, random AES-GCM nonce, versioned header/authentication, SHA-256 content fingerprints, exact product identity and original event count. The program does not upload or store passwords. Restores require successful decryption and R7 report/journal verification and are placed in exclusive new folders; existing evidence is never overwritten.
- Source and restored report/journal files remain **plaintext**; only the explicit `.fvault` backup is encrypted. This is not active encrypted storage, reviewer authentication, secure erase, or certification. Lost passphrases cannot be recovered.
- Install `cryptography==46.0.4` to develop from source; Windows CI installs this dependency before running the complete test suite and packaging. Packaged premium smoke checks now include encrypted backup/restore flows.
- The R8 module passed **12 isolated synthetic crypto/restore tests using a compatibility harness**, while full repository integration and packaged Windows smoke tests remain unverified due to hosted Actions runner failures. See [R8 encryption contract](docs/ENCRYPTED_EVIDENCE_R8.md).

## R11 offline premium entitlement verifier (development-only)

GrantAudit Studio Pro and ProcureGuard Studio Pro now verify distributor-signed,
product-specific Ed25519 entitlement files **before opening their GUI**,
generating reports or using the exception-review controls. The entitlement is
revalidated at each premium data action and rejects altered, expired,
cross-product, duplicated-field, unsigned or unrecognized-key licenses.
The four free tools remain free and do not require licenses.

**Current policy is fail-closed:** the production public-key map is
intentionally empty until a protected signing authority and key-rotation
policy are approved. Consequently, the premium GUI previews refuse access
in the current development build. Their explicit `--smoke-test` commands
still exercise only fixed synthetic data and never import real customer files.
This is *not* a finished checkout, activation, revocation or distribution system,
and the local verifier can be bypassed by modifying binaries. Do not publish
premium downloads without independently enforced server-side purchase access.
See [R11 entitlement contract](docs/OFFLINE_ENTITLEMENTS_R11.md).

## Release gates

1. Independent sample and edge-case test suite (money, CSV injection, encoding, duplicates, malformed input).
2. Binary smoke test on a clean Windows 11 machine; accessible keyboard UI.
3. Privacy and security review, including local file handling, report CSV injection mitigation, log redaction.
4. Premium entitlement / purchase workflow and license agreement before sales.
5. SHA256 checksums, release notes, support address and verified live download links.
6. Human approval through the Final Vestige site-layer QD/production process.

See [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).

## R12 operator-only offline license issuance (NOT a customer release)

The standalone `products/desktop/license_issuer.py` command can create
product-specific Ed25519 entitlements for GrantAudit Studio Pro and
ProcureGuard Studio Pro from an externally held **encrypted PKCS#8 private key**.
It never bundles the private key into any of the six executables, refuses
unprotected keys, requires a terminal passphrase and explicit issue
acknowledgment, never overwrites a license file, and verifies the result with
the R11 client verifier. **Nothing is activated:** `TRUSTED_PUBLIC_KEYS`
intentionally remains empty until approved production key custody, operator
registration, payment/download protection, security review and QD approval.

Local isolated R12 tests: **23/23 passed** on Python 3.13.5 with the exact
R11 verifier Git blob `587e30baa175aa399fe6e08093fbc93be66e66eb`;
full repository/Windows binary integration still unverified.
See [R12 issuer security runbook](docs/OPERATOR_ISSUER_R12.md).

## R13 operator issuance registry — unique IDs and local audit evidence (pre-release)

The offline premium license issuer CLI now requires a single persistent `--registry`
SQLite file in a protected operator-owned directory **outside Git**. It reserves
an opaque license ID before signing and prevents its reuse even following a
failure or crash. Cross-product duplicate IDs, concurrent issuers, symlinked
registry files, unsafe POSIX permissions and pre-existing output collisions are
rejected. A completed issuance records a SHA-256 of the verified license; the
registry stores a hash of the fulfillment path, not the plaintext path or holder.

**Limits:** this is one-machine local bookkeeping, not authenticated tamper-proof
logging, a customer database, payment processing, license revocation, a secure
multi-machine service, or release approval. All operators must use the same
protected registry and investigate uncertain `reserved` records manually.
The four free products and fail-closed premium verification keys are unchanged.
Twelve isolated SQLite tests passed locally on Linux Python 3.13.5 both normally
and under `-OO`; two additional real cryptographic CLI integration tests were
committed but have not yet run in the complete checkout. Windows CI and actual
six-EXE validation remain blocked. See [R13 runbook](docs/ISSUANCE_REGISTRY_R13.md).

## R14 operator registry schema guard — fail closed on schema drift (pre-release)

Premium license issuance now checks the **exact R13 SQLite registry schema**
inside each `BEGIN IMMEDIATE` reservation/finalization transaction. Missing
uniqueness or CHECK constraints, extra SQL tables/views/triggers/indexes and
failed SQLite integrity checks **block issuance**. Existing valid R13 registry
files require no migration; unsafe registries must be preserved for independent
review, never silently repaired or reset. This detects schema drift and
accidental manipulation, but cannot authenticate an administrator-controlled
database or prevent rollback/alternate registries.

Locally, **17/17 new R14 regressions passed** under normal Python and
**17/17 under `-OO`**, with four synthetic integration tests using a byte-exact
R13 source reconstruction. The full GitHub checkout and Windows builds remain
unverified until runner execution or trusted workstation verification succeeds.
See [R14 schema guard and recovery notes](docs/REGISTRY_SCHEMA_GUARD_R14.md).


## R15 operator licensing row-integrity safeguards (pre-release)

The R14 SQLite schema guard now runs alongside R15's semantic inspection of **all existing issuance rows** before each new premium license reservation or finalization. R15 rejects malformed license/key identifiers, noncanonical path/license SHA-256 digests, invalid or reversed timestamps, inconsistent reserved/issued states, and repeated destination hashes (including cross-product reuse). Repeated reservation of the **same output destination** now fails even under a different license ID; finalization refuses a backwards clock rather than recording an invalid chronology. The existing R13 table schema is unchanged. These checks do **not** prevent a privileged actor from coherently rewriting or rolling back a registry.

Seventeen focused tests passed locally under both normal Python and `-OO` with a reconstructed registry integration harness, including deliberate corruptions and no-write failure checks. The full branch test suite and packaged Windows executables have not run. See [R15 row-integrity guard and operator notes](docs/REGISTRY_ROW_INTEGRITY_R15.md). No premium distribution, production key activation, or QD publication authorization is implied.


## R16 signed-content finalization binding (pre-release)

The operator CLI now carries a SHA-256 receipt derived from its **original
in-memory signed entitlement bytes** into the issuance registry, rather than
allowing finalization to trust whatever file happens to be present after
signature verification. `finalize(..., expected_sha256=...)` requires a
canonical digest and compares the output bytes before recording `issued`.
A mismatch leaves the license ID reserved for manual investigation. R12's
Path-returning helper remains the default unless the CLI explicitly requests
the signed-content digest. This is not authenticated ledger storage and cannot
prevent an attacker changing files *after* finalization or replacing the entire
registry. See [R16 receipt binding and tests](docs/SIGNED_ISSUANCE_BINDING_R16.md).
No production keys, premium release or QD approval accompany this change.

## R17 Windows PE-image preflight (internal, pre-release)

The release candidate gate now validates the structural PE32+ AMD64 shape of all six files instead of accepting only MZ, PE magic and the machine value. It rejects malformed section tables, DLL/system images, missing entry points, invalid alignments or extents, and missing executable sections **before** the smoke phase. R9/R10 inert fixtures were updated for this stricter contract, and 13 focused R17 tests passed locally under ordinary Python and `-OO`. The full repository suite and six actual Windows binaries remain unverified while Actions jobs fail before running. This is a format sanity check, not code signing, malware clearance or permission to distribute. See [R17 PE preflight and Windows verification runbook](docs/PE_IMAGE_PREFLIGHT_R17.md).


## R18 PE entrypoint and section mapping preflight (internal, unreleased)

The six-EXE integrity gate now verifies that each AMD64 entry point is backed by
an actual executable section and that section file/virtual ranges do not
overlap or extend outside the declared image. It also rejects malformed
alignment and entrypoint locations while permitting one-file packager overlays.
R18 added 13 adversarial mapping tests and three full-catalog release-gate
tests; the prior 13 R17 cases still pass in isolated local Linux/Python
testing (including Python `-OO`). Actual Windows binaries, clean-machine
smokes, AV checks, signatures and QD approval remain outstanding. See
[R18 entrypoint mapping and evidence](docs/PE_ENTRYPOINT_MAPPING_R18.md).

## R19 CSV physical-line audit provenance and strict row widths (pre-release)

Shared financial CSV parsing now returns each record's **physical starting line**, even
when quoted text spans several source lines or blank source lines intervene.
LedgerDiff/Invoice Twin Scout and premium grant/procurement exception exports thus
reference the actual source-file location rather than a logical CSV row ordinal.
Strict CSV parsing also rejects truncated/extra columns and malformed quoting
before reports can be written; explicit empty trailing fields remain permitted.
The change does not alter Decimal money math, authorizations, human review or
QD publication. Twelve isolated parser regressions passed locally (also with
Python `-OO`); twelve new committed cross-app tests and Windows builds remain
unverified pending a working runner/checkout. See
[R19 provenance semantics and verification](docs/CSV_PHYSICAL_PROVENANCE_R19.md).

## R20 strict premium review CSV ingestion (internal, unreleased)

The human-only exception review queues for GrantAudit Studio Pro and
ProcureGuard Studio Pro now validate **every CSV record's exact field count**,
reject invalid quotes, and cite the **physical line where each record begins**,
including files with embedded newlines or blank lines. Badly formed `matched`
records also fail validation before any review journal is created.

**Migration caution:** existing journals for multiline/blank-line reports may
contain incompatible case identifiers and are deliberately rejected for human
inspection rather than silently rewritten. Single-line standard report case IDs
are unchanged. Seventeen repository regression tests were added; 15 isolated
CSV-intake checks passed locally under normal Python and `-OO`, but complete
repository/Windows verification remains pending. See
[R20 premium review intake contract](docs/PREMIUM_REVIEW_CSV_R20.md).

## R23 procurement quantity lexical integrity (internal, unreleased)

ProcureGuard Studio Pro no longer discards all comma separators or accepts
scientific-notation quantity strings when reconciling PO/invoice/receipt
movements. Only explicit, correctly grouped, nonnegative, finite decimal
quantities with at most eight meaningful fractional places are accepted.
The parser uses exact `Decimal`, does not echo malformed source text in
errors, and rejects invalid inputs **before** any reconciliation CSV or
evidence manifest is created. Explicit credit and return movements still
require human review and are never inferred from negative quantities.

The R23 branch adds 12 repository regression methods covering all three
import streams, source preservation, exact grouped quantities, no partial
audit files, and typed credits/returns; the new module is also included in
the Linux source CI optimized-Python test step. An isolated parser harness
passed 15/15 checks under normal Python and `-OO`; the connected repository
tests and real Windows x64 binaries remain **unverified** pending CI runner
availability. See [R23 procurement quantity input contract](docs/PROCUREMENT_QUANTITY_INTEGRITY_R23.md).


## R24 — ASCII financial/date inputs and confidential errors

All shared accounting amounts and invoice/spend dates now require ASCII digits, and direct binary-float amount inputs are refused rather than converted through text. Invalid date errors no longer display private input cells. This strengthens local financial accuracy for five apps while preserving explicit legacy two-digit date support (four-digit years recommended). See [R24 input contract](docs/ASCII_FINANCIAL_DATE_PRIVACY_R24.md). Four free and two premium applications remain **development prototypes**, not authorized downloads; Windows binary validation, premium fulfillment and independent QD approval are still required.

## R25 — financial CSV input bounds (development-only)

LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, GrantAudit Studio Pro and
ProcureGuard Studio Pro now reject financial CSVs larger than **64 MiB each**,
NUL characters anywhere in CSV headers/values (even ignored columns), and
malformed UTF-8 with generic errors. Import size is checked on the opened file
descriptor before and after parsing; these checks are not protection against
an adversary changing the file while it is being read. BOM/multiline physical
source citations, Decimal arithmetic, untouched originals and human review
remain. Partition exports over 64 MiB into reviewed batches rather than
silently truncating. Policy Delta Desk is text-only and unchanged.

See [R25 import-boundary specification](docs/FINANCIAL_CSV_IMPORT_BOUNDS_R25.md)
and the 15 source regression methods in
`tests/test_csv_import_bounds_r25.py`. Until the **full repository tests**
and **native six-app Windows x64 verification** run successfully, this is
not a released or certified desktop build. Independent site/QD approval and
premium access controls remain mandatory.

## Policy Delta Desk R26 — bounded text sources and digest-cited differences

Policy Delta Desk now reads the exact bytes of each local TXT/MD/CSV source through
a **10 MiB per-file guard** and rejects malformed UTF-8, NUL/control/bidi
characters, and more than 50,000 physical lines per source. The report records
**SHA-256 digests of the exact bytes read**, quoted/escaped source basenames,
and unified-diff line hunks. Unterminated final lines are explicitly marked
instead of concatenating conflicting evidence. Inputs are never rewritten;
invalid inputs produce no comparison report. See
[Policy Delta provenance R26](docs/POLICY_DIFF_PROVENANCE_R26.md).
These hashes are *fingerprints, not signatures or proof of legal correctness*.
The R26 helper regressions have run locally; full repository tests, true Windows
x64 smoke tests, QD approval, and release verification remain outstanding.

## R27 — complete, private financial CSV publication (development-only)

All five financial utilities now stage CSV output in a private, same-directory
temporary file and flush/sync it before making the final report visible.
On Windows an exclusive (non-replacing) rename publishes the file; on POSIX
an exclusive hard link prevents overwriting preexisting files/symlinks.
Conversion failures, filesystem errors, and duplicate report names leave no
new final CSV or abandoned staging file during normal exception cleanup.
The writer processes rows lazily and retains UTF-8 BOM and spreadsheet formula
neutralization. POSIX output permissions are owner-only.

**Scope:** shared `engine.save` CSV reports (LedgerDiff, Invoice Twin,
SpendMap, GrantAudit and ProcureGuard). This does **not** make an entire
multi-report grant package transactional, secure the separate premium review
journal/register or Policy Delta text report, or guarantee cleanup after an
abrupt OS/power termination. If the chosen filesystem does not support
exclusive publication, the operation refuses to publish rather than
overwriting another report. See [R27 design](docs/ATOMIC_FINANCIAL_CSV_REPORTS_R27.md).

The new helper regression suite passed locally on Linux; integrated repository
tests, native Windows filesystem behavior, six executable builds, QD review,
and guarded premium distribution remain release blockers.

## R28 — safe publication for policy diffs and grant hash manifests (development only)

Policy Delta Desk text diffs and GrantAudit Studio Pro SHA-256 inventories now
stage private UTF-8 text, flush/fsync, and publish with non-overwriting file
operations. This prevents normal I/O failures from exposing incomplete final
text evidence. Hash-manifest filenames are escaped to avoid forged lines from
tabs, newlines or bidi control characters. The existing policy source digests,
review-only conclusions and Decimal-safe financial computation are unchanged.
See [R28 design](docs/ATOMIC_TEXT_EVIDENCE_R28.md). Integration/Windows release
verification, protected premium access and independent QD review are pending.

## R29 — grant SHA-256 inventory provenance guard (development only)

GrantAudit Studio Pro now rejects ambiguous duplicate basenames, symlinks,
hard-linked aliases and modified/replaced evidence during SHA-256 inventory
creation. Each source is hashed from a bounded descriptor (64 MiB source, 256
MiB report cap) and every file is rechecked before the private, non-overwriting
inventory is published. Plain ASCII inventory lines remain compatible with
R28 for distinct filenames. This is not a snapshot, signature, authorization
or multi-file transaction. See [R29 design](docs/GRANT_INVENTORY_PROVENANCE_R29.md).

## R30 — verified CSV snapshots and consistent grant-mode selection (development only)

Five financial engines now parse a single bounded (64 MiB) local snapshot of each selected CSV after descriptor/path checks instead of streaming mutable source rows. This rejects common symlinks, concurrent edits, input growth and file swaps. GrantAudit derives its linked-claims header flags from those same validated claim bytes instead of reopening the file, preventing header/row version mismatch. The in-memory snapshot is not a filesystem lock or later source attestation; a changed source after parsing may still be inventoried in R29. The complete checkout, Windows x64 binaries and QD/premium distribution remain unverified and unreleased. See [R30 limitations and tests](docs/VERIFIED_CSV_SNAPSHOTS_R30.md).

## R32 — Complete GrantAudit evidence directories

Legacy and linked GrantAudit outputs now appear together in one private, timestamped `grant-evidence-*` subfolder under the operator-selected directory. If the SHA-256 inventory cannot be produced, neither report is published; existing reports and original CSV files remain untouched. This is **not** audit approval, a digital signature, or a release. See [R32 atomic bundle design](docs/ATOMIC_GRANT_BUNDLE_R32.md).

### R33: independent GrantAudit evidence consistency check (source-only)

R32 GrantAudit packages can now be checked again after export, without writing
or uploading the reports. With all three original inputs present and their
basenames preserved, run:

    PYTHONPATH=products/desktop python -m fvs_suite.grant_verify <grant-evidence-directory> <claims.csv> <ledger.csv> <budgets.csv>

The command returns 0 only when all five current source/report SHA-256 values
and the exact manifest layout match; it returns 1 on inconsistent or invalid
evidence. This is **not** a signature, historic authenticity proof, automated
compliance approval, release-ready Windows EXE, or replacement for human review.
See [R33 verifier threat model](docs/GRANT_BUNDLE_VERIFICATION_R33.md).


### R34: independently anchored GrantAudit inventory check (development-only)

The R33 offline verifier now optionally checks the published inventory against
an **independently retained** 64-character lowercase SHA-256 checksum. Capture
the inventory checksum at trusted publication time, then store it **outside**
the bundle in a separately controlled audit record. Later retrieve that
original pin; never calculate a purported "trusted" pin from a suspect copy.

    PYTHONPATH=products/desktop python -m fvs_suite.grant_verify --expected-inventory-sha256 "$SAVED_PIN_FROM_TRUSTED_REGISTER" /evidence/grant-evidence-dir /source/claims.csv /source/ledger.csv /source/budgets.csv

Success explicitly says **CONSISTENT (PINNED)** if the external checksum
matches. Omitting the flag remains backward-compatible but explicitly says
**CONSISTENT (UNPINNED)**: self-consistency is not authenticity. A mismatch or
malformed pin returns exit code 1. All results require human review. See
[R34 independent-inventory pinning](docs/GRANT_INDEPENDENT_PIN_R34.md).
There is no packaged verifier, Windows release, website approval, license
activation, or premium distribution change in this sprint.


### R35: source-bound ProcureGuard evidence bundles (development-only)

ProcureGuard Studio Pro now produces one **private two-file evidence directory**
instead of publishing an independent review CSV before its inventory. Every
PO, invoice and receipt is bound to the exact imported CSV snapshot digest;
an optional JSON threshold policy is read through a verified bounded descriptor
and its exact SHA-256 is also recorded and rechecked. A source or policy change
between parse and inventory publication aborts the entire package without
leaving a publishable partial report. The return contract still contains the
review CSV and its evidence-manifest `Path` objects. Existing exception review
and human compliance decisions remain unchanged. See
[R35 ProcureGuard source-bound evidence runbook](docs/PROCUREMENT_EVIDENCE_BUNDLE_R35.md).

This does **not** provide independent signature authenticity, continuing source
immutability, encrypted at-rest records, payment approval, a Windows x64 release,
or premium download entitlement. Keep both files and source data private.


### R36: independent offline verification of ProcureGuard evidence (development-only)

The R35 two-file ProcureGuard package can now be checked **without modifying
any financial records** by an independent, read-only CLI. It recomputes exact
SHA-256 fingerprints for the original purchase order, invoice, receipt,
optional custom price-policy JSON, and generated review CSV. Rejects malformed
packages, replaced/missing files, oversize inventory/policy, filesystem links,
and detected concurrent modifications. An optional SHA-256 digest saved
**outside** the bundle before later edits can anchor the inventory; an
unanchored inventory is merely self-consistent, not proof of authenticity.
The CLI distinguishes PINNED and UNPINNED results; all procurement findings
still require human review.

See [R36 ProcureGuard independent verifier runbook](docs/PROCUREMENT_INDEPENDENT_VERIFIER_R36.md)
for command syntax, pinned-value retention, risk limits and regression tests.
No Windows binary, premium distribution change, or website download is
approved by this development sprint.


### R37 — clean candidate distribution and safe checksum custody (development-only)

The internal six-EXE release gate now requires an **exact seven-file staging
directory**: the six named Windows x64 executables plus `SHA256SUMS.txt`.
Extra DLLs/scripts, hidden files, nested folders, accidentally copied private
license material, links/hardlink aliases, and size-unsafe candidates fail
closed **before any binary is run**. The gate uses descriptor-verified
SHA-256 reads and rechecks candidate membership across mocked/real smoke
phases; changes observed during verification are rejected. Evidence JSON is
now kept outside `dist` in the internal Windows script and CI flow.

[Read the R37 operator runbook](docs/CANDIDATE_DISTRIBUTION_INTEGRITY_R37.md).
This does not release software, prove malware safety/signatures, authorize
payments or compliance decisions, verify premium entitlement, or waive QD
approval. All six Windows executables remain unreleased.
