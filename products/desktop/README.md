## R137 — GrantAudit budget-source line and SHA custody (DRAFT / HOLD)

Both legacy and linked premium GrantAudit budget CSVs now identify the exact claim physical starting lines, authorized-budget physical line (or blank when missing), and the three original CSV snapshot SHA-256 hashes. Linked existing `claim_rows` stays stable. This shortens review without treating a match as eligibility or authorization. [18 synthetic integration methods and reviewer runbook](docs/GRANT_BUDGET_CUSTODY_R137.md) cover precision, BOM/quoted-newline citations, manifest custody and no-overwrite; Linux and Windows normal/`-OO` CI gates are required. **All six utilities UNRELEASED, premium locks retained, QD/founder approval and physical Win11/Defender/signing/gated distribution pending.**

## R136 — Policy Delta exact-line change index (DRAFT / HOLD)

Policy Delta Desk now places a **per-hunk before/after physical-line citation index** ahead of its existing fingerprinted, source-escaped unified text diff. The index records exact changed-line spans and counts for additions/removals, handles pure insertions, deletions and BOM-only zero-diff cases, and never interprets policy compliance. The original source SHA-256, Unicode visibility, no-overwrite behavior and local-first processing are preserved. See [R136 20-test operator runbook](docs/POLICY_CHANGE_INDEX_R136.md). Linux/Windows normal and `-OO` tests are mandatory; **all six apps remain UNRELEASED pending genuine physical Windows 11 review, Defender/EDR, code signing, gated premium delivery, QD/founder approval**.

## R135 — SpendMap Lite category-specific spend-spike evidence (DRAFT / HOLD)

SpendMap's original `review_spike` measured **vendor-wide** monthly spend and could miss category reallocations. R135 exposes separate `category_history_months`, exact `category_baseline_median`, and `category_review_flag` fields for **each vendor/category** without altering legacy vendor flags, physical source-row evidence, input SHA-256, Decimal precision, offline privacy or premium locks. The rule requires three previously observed months, a positive category median and current spend ≥2x that median. New [R135 synthetic regression suite and operator/release runbook](docs/SPEND_CATEGORY_BASELINES_R135.md) must pass in both Python modes on Linux and Windows. **Category spikes are human-review suggestions, never automated fraud/compliance judgments. All six programs remain UNRELEASED; QD/founder review, physical Windows 11 accessibility, real Defender/EDR, signing and gated premium distribution still HOLD.**

## R130 — finite-only private Win11 release evidence (DRAFT / HOLD)

The shared private R109 JSON intake now refuses nonstandard `NaN`, `Infinity` and `-Infinity` tokens, as well as exponent-overflow numbers such as `1e9999`; direct R9 verification rejects nonfinite in-memory smoke durations. SHA-256 custody alone cannot make such values meaningful. [R130 threat model, 18 synthetic regression methods and CI contract](docs/PRIVATE_REVIEW_NONFINITE_JSON_R130.md). Mandatory Linux/Windows normal and `-OO` verification; existing six native candidate build and evidence gates remain. **No physical Windows 11 checks, AV/EDR, signing, gated premium distribution or release authorization. All six apps UNRELEASED.**

## R129 — Windows 11 reviewer evidence ancestry (DRAFT / RELEASE HOLD)

Direct private R109 source and witness validation now rejects linked/reparse parent directories, checks directory identity before/after file reads, and validates even empty witness-folder ancestry. [R129 path-custody threat model and 16 synthetic tests](docs/PRIVATE_WIN11_PARENT_PATH_CUSTODY_R129.md). Linux/Windows normal and `-OO` source gates are mandatory; no synthetic test certifies human Win11 accessibility, malware clearance, code signing, protected premium delivery, independent QD or founder approval. **All six utilities remain UNRELEASED.**

## R128 — human-witness Unicode display integrity (DRAFT / RELEASE HOLD)

Local Windows 11 accessibility observations now reject C1 controls, hidden format marks, exotic spaces, blank/filler characters and Unicode variation selectors at both recording and revalidation of old v1/new v2 witnesses, even when evidence has a recomputed SHA-256. Ordinary multilingual letters, combining accents, spaces, tabs and newlines remain usable. [R128 engineering and limitations](docs/PRIVATE_WIN11_VISIBLE_OBSERVATIONS_R128.md). Fourteen synthetic regression methods must pass on Linux and Windows in normal and optimized modes. This does not constitute independent physical testing. **All six apps UNRELEASED; 46 human checks, real Defender/EDR, signing, protected premium delivery, independent QD and founder approval HOLD.**

## R127 — independent private human-observation file custody (DRAFT / HOLD)

The [R122 Windows 11 one-check writer](scripts/windows11_witness_writer_r122.py) now reads reviewer-authored `--observation-file` notes only from stable ordinary single-linked local UTF-8 files, rejecting symlinks/reparse ancestors, hardlinks, note paths inside executable/witness custody, paths to the raw R9 report or matrix, oversized and malformed inputs, and source replacement before/during read. The source-bound human PASS/FAIL matrix and six application engines are otherwise unchanged. [R127 operator and threat-model details](docs/PRIVATE_WIN11_OBSERVATION_CUSTODY_R127.md). Fourteen source-owned adversarial tests run in normal/`-OO` modes on both OSes, without physical Win11 review or release authority. **All six apps UNRELEASED; 46 human accessibility checks, real Defender/EDR, signing, premium access controls, QD and founder approval remain HOLD.**

# Final Vestige Labs — Desktop Utilities

## R126 — separate UTC capture timestamp for EACH private Win11 check (DRAFT / HOLD)

R122 previously reused a one-time session `observed_utc` for every witness note, making checks written days apart appear simultaneous. R126 records `recorded_utc` from the local UTC clock **separately for each new v2 witness**, validates the strict timestamp, chronology and future-date bounds on write and verification, and preserves historic v1 notes as legacy records without fabricating timestamps. This is *tool capture time*, NOT independent physical observation or trusted clock proof. [R126 operator runbook](docs/PRIVATE_WIN11_CAPTURE_TIME_R126.md). Sixteen focused synthetic methods run in Linux/Windows CI normal and `-OO`. **All six apps UNRELEASED; 46 physical checks, real Defender/EDR, premium controls, QD and founder release approval still HOLD.**


**Pre-release engineering branch. Not production-ready.** Four free utilities and two premium product prototypes share a local-only deterministic engine. Nothing uploads user documents, calls an LLM, or makes an automated compliance decision.

| Executable name | Tier | Inputs | Output |
| --- | --- | --- | --- |
| LedgerDiffLite.exe | Free | left and right transaction CSV | matched, missing, duplicate-ID, variance report |
| InvoiceTwinScout.exe | Free | invoice CSV | exact/review duplicate candidates |
| SpendMapLite.exe | Free | vendor spend CSV | monthly spend by normalized vendor/category and spike flags |
| PolicyDeltaDesk.exe | Free | old and new TXT/MD/CSV | unified text diff |
| GrantAuditStudioPro.exe | Premium (internal preview) | claims, ledger, budget CSV | reconciliation, budget exceptions, evidence SHA256 manifest |
| ProcureGuardStudioPro.exe | Premium (internal preview) | PO, invoice, receipt CSV | three-way matching exceptions and SHA256 manifest |

## R121 independently transmitted R9 pin required for physical Windows 11 QA (DRAFT / RELEASE HOLD)

The [local-only Windows 11 reviewer witness tool](scripts/windows11_manual_acceptance_r109.py) now **requires an externally supplied, exact lowercase 64-character SHA-256 of the original R9 report on both template and verify**. Previously it derived its template entirely from the local report, so a locally self-consistent but unrelated six-EXE/R9 pair could enter a 46-check manual review without a separate evidence anchor. Fifteen new tests cover malformed and missing pins, raw-report edits, changed candidate fingerprints, six-file inventory drift, and CLI refusal before intake; the source-owned diagnostics require all 70 synthetic methods. See [R121 custody protocol and limitations](docs/INDEPENDENT_MANUAL_R9_PIN_R121.md). A matching operator-provided pin is not proof of independent sourcing, Win11 human testing, malware clearance or release authorization. **The six binaries remain private and unreleased; QD/founder review remains mandatory.**

## R120 real positive controls for sixteen-entry tamper matrix (DRAFT / RELEASE HOLD)

The [R120 dual-control gate](scripts/sealed_tamper_matrix_r119.py) now proves the **unchanged** encrypted eight-record archive genuinely decrypts to the exact six native Windows candidate hashes **before and after** the R119 sixteen cipher/tag mutations. Seven added adversarial tests reject always-failing decryptors, fake success without bytes, corrupted/extra intake files, source drift, and missing final decryption. The existing CI privacy boundary is unchanged. [Threat model and test contract](docs/SEALED_TAMPER_POSITIVE_CONTROLS_R120.md). **No release authorization or physical Windows 11 acceptance.**

## R118 real six-binary encrypted CI roundtrip (DRAFT / RELEASE HOLD)

The [R118 source-owned integration harness](scripts/native_sealed_roundtrip_r118.py), its [15 fail-closed tests](tests/test_native_sealed_roundtrip_r118.py) and [limits/runbook](docs/NATIVE_SEALED_ROUNDTRIP_R118.md) exercise R117's AES-256-GCM seal/unseal against **all six actual Windows x64 R9-smoked EXEs** within the same ephemeral Windows Actions runner, preserve all eight exact source hashes, and require rejection of tampered real ciphertext. Temporary key/bundle/private plaintext are deleted and **never uploaded**. This is NOT physical Windows 11 acceptance, independent R9 evidence custody, malware clearance, premium distribution, signing, QD approval or a release.

## R117 private encrypted reviewer handoff (DRAFT / RELEASE HOLD)

The new [offline sealed handoff tool](scripts/sealed_candidate_handoff_r117.py) and
[operator runbook](docs/SEALED_WINDOWS_HANDOFF_R117.md) let an **authorized**
operator encrypt exactly six previously smoke-tested Windows x64 candidates,
their checksum inventory and independently SHA-pinned R9 evidence for controlled
physical Windows 11 reviewer intake. AES-256-GCM transfer and atomic no-clobber
intake protect custody; **the key must travel through a separate approved path**.
No executables, keys or encrypted envelopes are uploaded by CI. Local synthetic
cryptography regressions do **not** replace actual Windows 11 testing or QD
approval of premium-candidate transfer. All six products remain unreleased.

## R97 LedgerDiff and GrantAudit source-label visibility (pre-release)

LedgerDiff Lite and both GrantAudit Studio Pro reconciliation modes now display
original source-ID/program/reference labels with visible Unicode controls,
backslashes, and escaped literal semicolons. A source semicolon cannot pretend
to be an additional report-list entry; a typed escape differs from an actual
hidden character. The old casefold-sorted order and ordinary ASCII display
remain unchanged. This is **display-only**, not a new matching rule or approval.
Original CSV bytes/SHA-256, financial amounts, physical row references and
human-review obligations remain authoritative. See
[R97 threat model and pending release gates](docs/LEDGER_GRANT_VISIBLE_LABELS_R97.md).
All six EXEs remain **unreleased** pending complete source/Windows testing,
premium access control, independent QD and founder approval.

## R96 ProcureGuard human-readable document-list integrity (pre-release)

ProcureGuard Studio Pro now uses the same safe, **human-display-only** rendering
for five export columns: invoice documents, credit references, return references,
receipt documents and return documents. The new list renderer visibly escapes
bidirectional and invisible Unicode, source backslashes and literal semicolons
(which otherwise masquerade as separate list entries). It removes only ordinary
outer ASCII spaces; ambiguous Unicode spacing is retained as explicit evidence.
Original CSV snapshots, exact source SHA-256, line citations, matching keys,
Decimal arithmetic, human review flags and journal custody are unchanged.
See [R96 document-list threat model and verification](docs/PROCUREMENT_DOCUMENT_LIST_DISPLAY_R96.md).
Local isolated helper tests are not complete repository or native Windows proof.
All six products remain **unreleased**, with independent QD/founder approval
and premium access controls mandatory.

## R91 Policy Delta Desk invisible blank-filler display (pre-release)

Policy Delta Desk now visibly escapes seven non-control Unicode blank/filler
characters in added, removed and context lines of local policy diffs, using
the existing shared Unicode hazard predicate. Original policy bytes, exact
SHA-256 fingerprints and line positions remain authoritative, and literal
backslash-u sequences remain distinguishable from hidden source characters.
Twenty-two actual policy-module tests passed in a focused, exact-blob Linux
source workspace in both normal and optimized Python. Full-repository tests,
native Windows executables, distribution checks and QD/founder signoff are
still pending. [R91 specification and verification](docs/POLICY_BLANK_FILLER_CUSTODY_R91.md).

## R90 ProcureGuard receiving-document provenance (pre-release)

Even perfectly matched quantities can hide repeated receiving references. R90
flags duplicate normalized receipt IDs, duplicate return IDs, and return IDs
reused as receipt IDs for explicit **human review**. Two appended report display
columns expose original receiving/return labels with visible Unicode escapes;
the original source CSV and SHA-256 manifest remain authoritative. These are
not determinations of fraud or payment eligibility. [R90 review and test
evidence](docs/PROCUREMENT_RECEIPT_IDENTITY_R90.md) documents 19 committed
full-repository tests **pending CI**, plus 16 passing isolated source-equivalent
tests in each of normal and optimized Python. All binaries remain unreleased.

## R85 SpendMap Lite exact money and historical median (pre-release)

SpendMap's running median previously used Decimal unary minus, which can
silently round heap values under a caller's Decimal context. Monthly
aggregation inherited the same precision and exponent limits. R85 uses
context-independent heap negation, private-context midpoint averaging,
and a 64-digit isolated context for totals and spike comparisons.
Custom direct parsers now enforce the 1-trillion-per-row cent domain.
Focused source and maximum-cap synthetic stress tests passed locally;
full repository and Windows x64 testing remain pending. See
[R85 precision and release disclosure](docs/SPEND_DECIMAL_CONTEXT_R85.md).
**No downloads or releases are authorized.**

## R84 ProcureGuard high-precision audit arithmetic (pre-release)

The previous 28-digit ambient Python Decimal context could silently truncate
otherwise valid extended procurement totals with eight-place quantity and
unit-price fractions—even the R83 `*_exact` report fields. ProcureGuard now
uses a **scoped 64-digit minimum** for full three-way calculations and
cent displays, without mutating the process-wide Decimal context. For example,
quantity `999999999.99999999` × price `999999999999.99999999`
is now preserved exactly as
`999999999999999989990.0000000000000001` in the audit report.
Human decision flags and original report provenance remain intact.
See [R84 precision evidence and release caveats](docs/PROCUREMENT_DECIMAL_CONTEXT_R84.md).
These are draft code changes, not full-repository or native Windows proof;
the six executables remain unavailable pending QD/founder approvals.

## R83 ProcureGuard exact subcent financial display (pre-release)

ProcureGuard Studio Pro now explicitly uses `ROUND_HALF_UP` for its
gross, credit and net display-cent totals, in agreement with the suite's
existing financial input rounding. Previously, a quantity of 1 × unit
price 0.005 could show 0.00 under Python's default half-even display.
The report **appends** `invoice_total_exact`,
`gross_invoice_total_exact` and `credit_value_exact` containing
unrounded Decimal strings for human reconciliation and source verification.
Rounded gross minus rounded credits can differ by one cent from the
independently rounded net; the `*_exact` fields are authoritative for
that arithmetic. Original CSV inputs, policy fingerprints, provenance
and human-only exception flags are preserved. See
[R83 precision/runbook](docs/PROCUREMENT_EXACT_SUBCENT_R83.md).
These source changes are NOT evidence of successful packaged Windows
testing or authorization to release; QD and founder approval remain required.

## R81 premium source-reference display integrity (pre-release)

GrantAudit Studio Pro and ProcureGuard Studio Pro now visibly render
report-origin identifiers and flags in their human review queue and CSV
register. Invisible/bidirectional Unicode, non-ASCII spacing, variation
selectors and literal backslashes use deterministic ASCII escapes. Literal
Unicode escape text and actual hidden characters are distinguishable.
The register's source_key and original_flags columns are now human-display
representations, not byte-for-byte source data. Refer to the original report
and SHA-256 for exact evidence. Source cases, journal hashes, physical lines,
money arithmetic and review decisions remain unchanged. See
[R81 display-integrity notes](docs/PREMIUM_SOURCE_DISPLAY_R81.md).
This is pre-release source-only work, not native Windows verification.
Independent QD and founder approvals are still required.

## R80 premium raw-review boundary (pre-release)

The shared GrantAudit Studio Pro / ProcureGuard Studio Pro human-review validator
now checks original reviewer/rationale characters **before** trimming outer
whitespace. This prevents leading or trailing tab, CR/LF, C1 next-line and
Unicode line/paragraph separators from being silently discarded by Python's
`str.strip()`. The boundary applies both to new human-review actions and
revalidation of previously recorded journal events. Ordinary outer spaces
still trim, multilingual text remains supported, and neither source evidence
nor journal history is automatically rewritten. See
[R80 raw-review control custody](docs/PREMIUM_REVIEW_TRIM_BOUNDARY_R80.md).
Local extracted-function tests are **not** full app or Windows executable
acceptance; all six binaries remain unreleased and QD approval mandatory.

## R79 premium human-review Unicode custody (pre-release)

GrantAudit Studio Pro and ProcureGuard Studio Pro now reject hidden Unicode controls,
bidirectional display overrides/isolates, line/paragraph separators, malformed
surrogates and variation selectors in reviewer names or rationales before a
human review journal is appended. The same boundary checks existing journal
records, including events with recomputed SHA-256 chains, rather than allowing
misleading display text to be exported. Readable multilingual letters and
combining accents remain supported; no automated payment, grant eligibility,
or compliance decision is introduced. Older journals containing these characters
must be inspected manually, not silently rewritten. See
[R79 premium review text custody](docs/PREMIUM_REVIEW_TEXT_CUSTODY_R79.md).
Only the extracted text-validator boundary has passed isolated normal/-OO
Linux tests; full repository integration tests and Windows binaries are pending.

## CSV headers

Headers are case-insensitive; spaces are accepted in place of underscores. The importer also recognizes common synonyms listed in fvs_suite/engine.py.

- LedgerDiff: transaction_id, amount
- InvoiceTwin: vendor, invoice_number, amount, date
- SpendMap: vendor, amount, date, optional category
- GrantAudit: claims (transaction_id, amount, program); ledger (transaction_id, amount, program); budgets (program, budget)
- ProcureGuard: purchase orders (po_number, line, quantity, unit_price); invoices (same); receipts (po_number, line, quantity)

Dates: YYYY-MM-DD or MM/DD/YYYY. Amounts: decimal strings; currency symbols, comma thousands separators and accounting parentheses accepted. Currency conversion, multi-currency, unconstrained allocation rules, fuzzy name matching, and OCR are **not** supported in v0.1. GrantAudit R6 supports explicitly linked split allocations under a limited documented CSV contract. Financial flags require human review.

## R64 Policy Delta Desk source-custody hardening (pre-release)

Policy Delta Desk now processes TXT/MD/CSV policy inputs through the same
descriptor-verified, bounded raw-byte snapshot guard already used for the
financial CSV imports. Observed symlink/path swaps, in-place edits during the
read, and non-regular inputs fail closed *before report publication*. Policy
diffs also flag accidental identical-byte inputs and visually identical text
with different byte fingerprints (such as BOM-only changes) for human review.
Existing exact source SHA-256, line citations, size/line caps, and local-only
report behavior remain intact. See
[R64 Policy Delta source custody](docs/POLICY_SNAPSHOT_CUSTODY_R64.md).
Focused Linux helper verification does not establish successful complete
repository/Windows EXE verification or legal compliance certification.

## R77 Policy Delta Desk invisible Unicode review display (pre-release)

Policy change reports now visibly encode accepted zero-width Unicode format
characters, combining grapheme joiners and Unicode variation selectors as
ASCII \uXXXX or \UXXXXXXXX sequences. Literal source backslashes are doubled
so a source text containing a typed escape cannot masquerade as a hidden
character. Exact source SHA-256 fingerprints, original bytes, hunk references,
R76 CR/tab escaping and the human-only interpretation rule remain intact.
This mitigation does **not** detect every Unicode confusable. The report is
not a machine-applicable patch or a compliance determination. Twenty-seven
focused synthetic source-to-atomic-report regressions passed under normal and
optimized Python in an isolated Linux environment; full CI, all six Windows
executables, independent QD and founder review are outstanding. See
[R77 Unicode visibility engineering notes](docs/POLICY_INVISIBLE_UNICODE_R77.md).

## R76 Policy Delta Desk safe human-readable diff display (pre-release)

Policy text containing Windows CRLF or CR-only line endings could previously
emit raw carriage-return bytes into a change report, allowing some viewers
to obscure the visible starts of changed lines. Human-readable source lines
now show **literal backslashes as doubled backslashes**, horizontal tabs as
a visible backslash-t sequence, and carriage returns as a visible
backslash-r sequence. This also distinguishes an actual CR from a source
containing a literal backslash and the letter r. Original TXT/MD/CSV bytes,
source SHA-256 fingerprints, unified-diff hunk ranges, and human review
requirements are preserved. **The displayed diff is not a patch to apply
automatically.** Twenty-four local source/report regressions passed in normal
and optimized Python; full checkout, packaged Windows checks, and QD approval
remain pending. See
[R76 Policy Delta display safety](docs/POLICY_DIFF_VISIBLE_CONTROLS_R76.md).

## R60 SpendMap Lite scalable exact medians (pre-release)

SpendMap Lite now calculates prior-month anomaly baselines with a two-heap
**Decimal-only streaming median**, removing the repeated historical sorts that
became expensive on long vendor histories. Report rows, columns, exact half-cent
medians, vendor-collision review, and the human-only review policy are unchanged.
13 new regressions and the existing 20 R59 provenance regressions passed under
both normal and optimized Python locally; complete repository CI and native
Windows executable acceptance remain outstanding. See
[R60 streaming median engineering details](docs/SPENDMAP_STREAMING_MEDIAN_R60.md).

## R59 SpendMap Lite provenance and explainable spikes (pre-release)

SpendMap Lite now retains the **source CSV physical line numbers**, original
vendor labels per aggregate, vendor-month totals and the **exact Decimal median
baseline** behind each spike review flag. Since vendor normalization removes
punctuation, different spellings such as `A-CME` and `ACME` now trigger a
visible `normalized_vendor_collision_review` across all affected months, rather
than silently asserting that the businesses are identical. Existing report
columns and baseline review thresholds remain intact; six provenance fields are
appended. Every flag requires human judgment. See
[R59 SpendMap provenance details](docs/SPENDMAP_PROVENANCE_R59.md).
This is not an executable release or compliance certification.

## R57 verified complete CI source gate (pre-release)

Both desktop CI jobs now run the full offline source verification suite in **normal Python and optimized `-OO`**, compare exact test/skip identities, and execute all six synthetic source smokes before packaging. Linux retains the private, evidence-only `offline-source-suite.json` (no customer files, EXEs or premium downloads). The R57 source contract rejects missing, reordered, conditional or fail-open verification. This replaces the stale hand-maintained optimized-test selection; see [R57 CI source contract and limitations](docs/COMPLETE_CI_SOURCE_GATE_R57.md). **Hosted Actions and actual Windows x64 release tests remain unverified. No product is released.**

## R48 premium writer-lock custody (pre-release)

GrantAudit Studio Pro and ProcureGuard Studio Pro now create a private exclusive writer lock with a held descriptor while recording a human exception decision. The lock's identity and metadata are checked throughout the full report/journal revalidation and append process. An observed lock swap, hardlink alias, modification, or disappearance fails closed; foreign and stale locks are **never automatically broken**. Audit data stays offline, original CSVs are not edited, and no review grants payment authorization. See [R48 review-lock runbook](docs/REVIEW_LOCK_CUSTODY_R48.md) for recovery rules and limitations. These changes are not evidence of native Windows executable acceptance or permission to release either premium product.

## R44 keyboard-first GUI controls

All six Tk desktop applications now expose visible, local-only keyboard
shortcuts: Alt+1..3 to focus existing input fields, Ctrl+1..3 for file
pickers, Alt+O/Ctrl+O for output selection, and Alt+G/Ctrl+Enter to run the
existing review action. Premium windows also support Alt+R for human
exception review; the existing entitlement checks still run. Initial focus
is set to the first input. File and report dialogs are owned by the app.
These are source-level usability improvements, **not** Windows GUI or screen
reader certification. See [R44 keyboard-access checklist](docs/KEYBOARD_ACCESS_R44.md).

## Local development

Python 3.12+ with Tkinter. From repository root:

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
    PYTHONPATH=products/desktop python -m fvs_suite.demo ledger

The six GUI entrypoints live under products/desktop/launchers. Windows CI uses PyInstaller privately and uploads **evidence only, never executable artifacts**; do not distribute or publish until tests, malware scan, clean-machine acceptance, release versioning, SHA256 and (preferably) code signing are complete.

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


### R39 — independently pinned, read-only release-report recheck (unreleased)

`report_attestation.py` rechecks a previously retained R38 release-gate JSON against all six **current** Windows candidate files and its checksum inventory without executing binaries. It rejects malformed, oversized or linked reports, unsafe release assertions, contradictory smoke metadata and changed candidate fingerprints. An independently protected SHA-256 fingerprint of the original report can detect coordinated later edits to that report; without it, `UNPINNED` only means current consistency. **Historical smoke success is never independently proven by this check**, and release authorization remains false. See [R39 operator guide](docs/RELEASE_REPORT_ATTESTATION_R39.md). Full repo/Windows tests, malware scan, premium access controls and QD approval remain required.


## R40 — canonical no-clobber six-executable checksum inventory

Both Windows CI packaging and the offline Windows operator build now invoke `products/desktop/build_inventory.py dist` rather than inventing separate checksum inventories. The script requires **exactly six distinct, bounded Windows candidate file names**, hashes them twice before atomic, exclusive inventory publication, and checks all seven output files and all six hashes again. An existing manifest, extra binary, licensing secret, link or detected change fails closed. It does not execute images, certify provenance or approve release. See [R40 canonical inventory notes](docs/CANONICAL_CANDIDATE_INVENTORY_R40.md). All six products remain unreleased.


### R41 — CI evidence-only artifact export

Before R41, the Windows workflow uploaded `dist/*`, which could include all six release candidates (including premium binaries) as retrievable GitHub Actions artifacts. R41 restricts workflow artifacts to the source-only smoke report and the Windows SHA256 inventory/release-gate JSON, **never the EXEs**. A fail-closed, standard-library policy linter runs in both CI jobs, and 22 adversarial tests cover unintended upload expansion, duplicate/missing artifacts and unsafe retention. See [R41 artifact privacy runbook](docs/CI_ARTIFACT_PRIVACY_R41.md). This is artifact-scope hardening, not proof of a Windows native build, malware clearance, premium-fulfillment controls, or QD release approval.

## R43 complete Python source scope (pre-release)

Synthetic six-app source-smoke evidence now includes nested engine modules, top-level desktop Python helpers, scripts, and exactly six approved launchers. It detects observed same-byte source replacements through private file identity checks, and rejects unsafe source directory symlinks. This is **source-only** evidence, not native Windows EXE verification, entitlement validation, or release authorization. See [R43 source scope and limits](docs/COMPLETE_SOURCE_SCOPE_R43.md). All applications remain unreleased pending native smoke, malware/security and QD gates.

## R45 — Private GUI diagnostics

User-facing error dialogs never show raw Python exception text. Customer-controlled
CSV cells, original filenames, file paths, entitlement data and encrypted-vault
errors can appear in engine/OS exceptions. The six app launchers and premium
exception review workbench now present only fixed, operation-specific guidance
based on exception type; the renderer never stringifies the exception. A premium
review launch failure also receives a safe dialog instead of an unhandled Tk
callback traceback. This does **not** redact explicit input path fields or
paths a user intentionally selects; it protects error/status content.

Focused tests: `PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_ui_error_privacy_r45.py -v`.
See [R45 privacy notes](docs/PRIVATE_GUI_DIAGNOSTICS_R45.md). This is still
**pre-release**: Windows x64 native testing, malware scanning, premium access
control and human QD approval are required before distribution.

## R46 — Atomic premium human-review register custody

The GrantAudit Studio Pro and ProcureGuard Studio Pro human exception-review
CSV exports now use the shared atomic report writer rather than directly writing
the final filename. Before any final register is published, the exporter
revalidates **both the complete source report and the complete hash-linked
review-event history**. Observed mutations, interrupted serialization, disk
sync failures, existing filenames and symlink destinations fail closed,
without leaving a partial final report. The same source row citations, review
decision states, CSV field order and spreadsheet-formula neutralization remain.
These reports record human reviews only; no automated authorization occurs.

[Read the R46 premium register guide](docs/ATOMIC_REVIEW_REGISTER_R46.md).
The 20 focused synthetic tests do not establish complete GUI integration,
native Windows release readiness, historical authenticity or QD signoff.
All four free and two premium applications remain **unreleased**.

## R47 — Descriptor-bound premium human journal custody (pre-release)

Both GrantAudit Studio Pro and ProcureGuard Studio Pro now read local review
source CSV/JSONL evidence through a **bounded, descriptor-verified** reader
instead of trusting pathname stat checks followed by a separate open. The
human-only JSONL append checks the destination descriptor, source/report digest,
full prior journal chain and observed file identity before writing; it rejects
symlinks, hardlink aliases, swapped files and detected concurrent changes.
New journals are created with private POSIX mode 0600, without replacing other
files. An interrupted append can still leave a torn journal: subsequent
hash-chain validation fails closed, requiring manual incident review. This is
not an encrypted database, independent cryptographic attestation, or guarantee
against privileged filesystem races. See
[the R47 local review journal runbook](docs/DESCRIPTOR_REVIEW_JOURNAL_R47.md).

Focused R47 tests: `PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_journal_io_r47.py -v`.
Complete Windows/full-checkout integration, premium distribution entitlement,
malware scanning and separate QD approval remain required. **Nothing is released.**


## R49 — Post-write premium review commit confirmation (pre-release)

Both premium human exception-review workbenches now **re-read the original source CSV
and the complete SHA-256-linked review journal after the journal append has been
fsynced**, while retaining the descriptor-owned R48 writer lock. A review is
acknowledged only when the source batch remains identical and the journal
contains exactly the prior verified history followed by precisely the expected
new human event. Changes to a report, missing/altered/duplicate events, broken
journal parsing or lost lock ownership fail closed; the verifier never silently
repairs, retries or approves a financial/compliance decision.

**Important:** If this post-append check fails, the event may *already have
been written*. Do not blindly resubmit. Preserve the source/journal evidence
and have a human inspect the full history before any recovery. The local
readback is not a digital signature, encryption, or a guarantee against later
changes. See [R49 confirmation and incident runbook](docs/REVIEW_COMMIT_READBACK_R49.md).
The 16 synthetic helper tests passed locally (normal and `-OO`); four
committed real-module integration tests and the full repository/Windows
binary gates remain unverified due to CI infrastructure failures.
**No free or premium application is authorized for distribution without
native x64 smoke/AV/checksum, premium-access verification and QD approval.**

## R50 — Verified local premium license reads (pre-release)

GrantAudit Studio Pro and ProcureGuard Studio Pro now read offline Ed25519
entitlements through a bounded, verified file descriptor. This closes the
ordinary pathname-check-then-open gap: detected symlinks, hardlink aliases,
same-length file swaps, in-flight edits and oversized files are rejected before
parsing the signed bytes. Existing strict JSON, product/expiry checks and
signature verification remain in effect. Errors do not expose customer paths.
The two premium tools still have **no production signing trust anchor** and
remain locked by default. Free apps, financial calculations, human review and
production distribution were not changed.

See [R50 entitlement custody runbook](docs/ENTITLEMENT_CUSTODY_R50.md).
The 16 new R50 tests plus 15 original R11 Ed25519 tests passed locally
on Linux/Python 3.13.5 under normal and optimized `-OO` modes (**31/31 each**)
using a reconstructed focused source subset. Windows and whole-repository
integration, live entitlement issuance, six native EXEs and all release/QD gates
remain **unverified**. **Do not distribute either premium binary.**


### R51 — chronology-safe human audit journals (pre-release)

GrantAudit Studio Pro and ProcureGuard Studio Pro now refuse out-of-order
UTC timestamps across their complete local reviewer-journal histories, even
when the SHA-256 chain is internally consistent. Before recording another
human review, both applications reject a local clock that predates the latest
recorded decision. Equal-second events remain permitted. This is a consistency
check, **not** a trusted timestamp authority, signed audit trail, compliance
decision, or release authorization. Backdated records require manual
investigation; no automatic repair/replay occurs. See
[the R51 review chronology runbook](docs/REVIEW_CHRONOLOGY_R51.md).


## R54 exact active/skip test provenance (pre-release)

The runner-independent source gate now fingerprints not just discovered regression
IDs but the exact **executed** and **skipped** test IDs in normal and optimized
Python. Equal test counts with a different skipped set reject evidence, as do
entirely skipped test modules. No skip reasons, stack traces, customer inputs,
Windows binaries, or release authorizations are included in evidence. See
[skip-identity verification runbook](docs/TEST_SKIP_IDENTITY_R54.md).


## R55 pinned Windows build inputs (pre-release)

The runner-independent Windows candidate script and internal Windows CI now pin the
bounded SHA-256/metadata inventory of **all six apps' Python packaging inputs**,
the PowerShell build driver, and the CI workflow. They re-check this private
manifest before/after every PyInstaller operation and before/after the binary
candidate gate; observed source changes, injected modules, altered build
commands, same-byte file swaps or missing sources fail closed. This narrows
the risk of accidentally packaging six binaries from different source trees.
The manifest is stored outside the checkout and contains no customer records.
See [R55 build-input custody runbook](docs/BUILD_INPUT_CUSTODY_R55.md).
It is not an executable signature, clean-machine certification, premium
distribution permission or QD release authorization.

### R56 Windows packaging toolchain custody (draft / unreleased)

In addition to R55 source custody, [R56 operating procedure](docs/WINDOWS_TOOLCHAIN_CUSTODY_R56.md) pins the packaging Python interpreter, installed PyInstaller/hooks and relevant crypto/dependency files across all six Windows builds. Both the offline Windows driver and CI use isolated `python -I -m PyInstaller` to prevent checkout-root package shadowing. Source/toolchain validation never grants executable release, premium distribution or QD approval.

## R61 — SpendMap Lite source snapshot fingerprint (pre-release)

Each nonempty SpendMap CSV row now includes `source_sha256`, computed from the
**same verified source bytes** as the imported records. This binds physical
source-row citations to a precise input version; reviewers can verify the
preserved original with SHA-256. It does not certify authenticity, fraud, or
compliance. Empty imports have no report row to carry the fingerprint.
See [R61 source snapshot contract](docs/SPENDMAP_SOURCE_SNAPSHOT_R61.md).
The release/CI/Windows QD gates remain unchanged; no binary is published.

## R62 — LedgerDiff Lite dual-source SHA-256 and self-comparison review (pre-release)

LedgerDiff now attaches the **exact left/right imported CSV source SHA-256** to
every nonempty reconciliation row. The appended input_identity_review column
flags byte-identical snapshots (including accidental self-comparison), even if
the ordinary matching status is matched. The original nine CSV fields, Decimal
totals, collision review and physical source row citations remain unchanged.
Header-only inputs have no data row in which to carry fingerprints. See
[R62 LedgerDiff provenance runbook](docs/LEDGERDIFF_SOURCE_IDENTITY_R62.md).
No app is released, and premium-access, executable/QD and production gates
remain mandatory.

## R63 Invoice Twin Scout source custody (pre-release)

Invoice Twin Scout now hashes the **exact descriptor-verified input CSV snapshot**
used for candidate discovery. Existing report columns are preserved; two new
columns, `source_sha256` and `candidate_ref`, bind each duplicate-review
candidate to the imported bytes, physical source rows, and review status. A
deterministic, domain-separated candidate reference is a reviewer locator,
**not proof of fraud, authorship, or compliance**. Invalid source hashes,
physical row references, unsupported statuses, and duplicated candidate IDs
fail before a CSV is published. Header-only reports have no row-level hash.

See [R63 Invoice source identity runbook](docs/INVOICE_SOURCE_IDENTITY_R63.md)
for limits, independent source-byte verification and test/release gates.


## R65 — ProcureGuard Studio Pro pricing-policy input and confidential errors

- Optional local JSON price tolerances now require **ASCII fixed-point Decimal values** (up to eight fractional places). Scientific notation, non-ASCII digits, padded zeros and signs are rejected; maximum absolute tolerance remains 100.00 and fractional tolerance 0.10. Existing valid numeric JSON integers and standard fixed-point strings remain supported.
- Invalid invoice/receipt event kinds are reported with the parser-generated physical CSV row number **without echoing the confidential cell value**. Legitimate invoice/credit and receipt/return movements retain their existing human-review semantics.
- Twelve isolated input regressions passed on Python 3.13.5 Linux under normal and optimized (-OO) modes; six complete-engine integration tests are committed but unexecuted without a full checkout/working CI. See [R65 operator contract](docs/PROCUREMENT_INPUT_PRIVACY_R65.md).
- **Unreleased:** No paid executable, public download, checkout enablement, QD bypass, or production change. Windows binary/accessibility/malware testing, premium distribution controls and independent review remain mandatory.

## R66 — GrantAudit Studio Pro confidential claim-type error gate (pre-release)

- Unsupported linked-grant `claim_type` values can no longer be repeated in validation errors. The failure shows only a canonical physical CSV source row (or `?` for an untrusted row reference), with no private cell contents or control characters.
- Existing `claim`/`credit` classifications, optional/default behavior, Decimal-safe split allocations, source digests, human review flags and offline handling remain unchanged.
- Seventeen focused regressions passed in both normal and optimized (`-OO`) Python 3.13.5 Linux; five full-engine tests and the synthetic packaged smoke assertion remain **unexecuted** pending trusted complete-repository/Windows CI. See [R66 GrantAudit privacy runbook](docs/GRANT_CLAIM_TYPE_PRIVACY_R66.md).
- **Unreleased:** No premium binary or public download, no site change or production merge. Independent QD approval and full Windows x64 release gates still apply.

## R67 — Invoice Twin Scout direct-engine financial and audit input boundary (pre-release)

- Direct callers of the invoice candidate engine now must provide finite exact `Decimal` amounts, canonical unique physical CSV row references, real calendar dates, and normalized ASCII vendor/invoice keys. Invalid identifiers, duplicate rows, malformed values and data-bearing control text fail with fixed private-data-free errors before candidate report production.
- Boolean/float window or quota controls are rejected, and at most 200,000 imported records may be considered. Matching classifications, seven-day window, deterministic reviewer IDs, the 100,000-candidate default quota, and all existing valid CSV output fields remain unchanged.
- **20 isolated synthetic regressions passed in Python 3.13.5 Linux**, in both normal and optimized (`-OO`) interpreter modes, with warnings-as-errors; source and test blobs matched the tested local files. Full repository integration and native Windows x64 smoke/AV/accessibility gates remain **unexecuted**. See [R67 Invoice boundary runbook](docs/INVOICE_DIRECT_INPUT_BOUNDARY_R67.md).
- **Unreleased:** No executables, new download links, premium access changes, production edits, or QD bypass. Human review of all duplicate candidates is mandatory.

## R70 source-bound premium review exports (pre-release)

The premium review window now rechecks its selected report and journal before human review, register export, and encrypted backup actions. Both output APIs accept the opened report's expected SHA-256; a different valid report at the same path is rejected before publishing evidence. See [R70 review snapshot identity contract](docs/PREMIUM_REPORT_SNAPSHOT_R70.md). The 22 focused local tests do **not** establish complete-repository integration, Windows x64 acceptance, entitlement security, or release approval.

## R71 premium journal snapshot custody (pre-release)

The two premium exception-review windows now bind the selected **review journal's exact verified bytes** alongside the already source-bound report. Another local reviewer adding a valid event, file substitutions, disappearance or observed in-flight changes invalidate the selection and require an explicit reopen. The GUI refreshes its pinned journal only after its own successfully committed human review, without automatically approving grants, spending or procurement. See [R71 premium journal snapshot runbook](docs/PREMIUM_JOURNAL_SNAPSHOT_R71.md). **19 focused isolated synthetic tests passed in normal and optimized Python locally; full private-repository and Windows x64 tests remain outstanding.** No executable distribution or QD approval is implied.

## R122 — private Windows 11 physical-review witness recorder (draft / release HOLD)

Authorized reviewers can record one of the 46 physical checks at a time using a source-bound local observation file; the one-check recorder binds the selected app, check, human PASS/FAIL, six-candidate/R9 pin and session identity, and writes witness plus manifest without overwriting earlier evidence. It requires an actual Windows 11 workstation and independently sourced R9 digest; no automatic testing, independent certification, or release approval is implied. See [R122 operator instructions](docs/PRIVATE_WIN11_WITNESS_WRITER_R122.md). Linux/Windows synthetic regression CI cannot substitute for human NVDA/keyboard/contrast/scaling acceptance. **All six applications UNRELEASED; production unchanged; QD and founder approval required.**

## R123 — read-only independent Win11 reviewer progress queue (draft / release HOLD)

R123 provides a **local-only read-only 46-check progress summary** after native Win11 and independently authenticated R9 six-EXE custody verification. It reports fixed app/check identifiers, per-app PASS/FAIL/NOT_RUN counts and the next outstanding check, while rejecting orphan/unreferenced witness files, extra directory contents, prior R122 locks, altered evidence and source mismatch. No note text, private paths or hashes are printed, and it never grants release or premium entitlement. See [R123 physical reviewer progress runbook](docs/PRIVATE_WIN11_REVIEW_PROGRESS_R123.md). The 17 synthetic CI regressions do **not** represent actual Windows 11 physical reviewer acceptance. **All six unreleased; QD/founder hold remains.**

## R124 — fail-closed physical witness inventory before private manual review writes (draft / release HOLD)

R124 prevents the R122 one-check recorder from extending an already-dirty Windows 11 reviewer witness directory: every referenced human PASS/FAIL note must have exactly one ordinary file and **every unreferenced, hidden, temporary or other entry forces HOLD**. The writer checks before and after creating a note and rolls back only its own new note on post-write inconsistency; the R123 read-only progress queue shares the same inventory checks. No orphan is deleted automatically, and the matrix and witness directory must be separate. See [R124 private witness inventory/runbook](docs/PRIVATE_WIN11_WITNESS_INVENTORY_R124.md). Fourteen mandatory synthetic regressions run in both normal and optimized modes on Linux/Windows CI; they **do not** replace 46 real Win11 physical checks. **All six apps remain unreleased; no QD or founder approval bypass.**

## R125 — identity-preserving Windows 11 reviewer evidence cleanup (draft / HOLD)

R125 prevents the private R122 witness writer from deleting an independently replaced **byte-identical** note on failed write, and rejects an identically copied/replaced review matrix before commit. The original witness's open-handle file identity and digest must match before cleanup; unknown or substituted evidence is preserved for human investigation. [R125 operator runbook](docs/PRIVATE_WIN11_WITNESS_IDENTITY_R125.md) explains the limits (cooperative custody, not hostile-filesystem TOCTOU proof). Ten source-owned synthetic regression methods run in normal and optimized Python on Linux/Windows CI. **All six utilities remain unreleased; no QD/founder approval bypass or premium distribution.**

### R131 — LedgerDiff Lite independent CSV match columns (DRAFT / HOLD)

The free LedgerDiff Lite GUI now offers optional **left** and **right** match-key CSV header fields. This removes the requirement to modify source exports when their transaction identifiers have different headers. Each audited reconciliation row records the actual selected column names plus the existing original physical line references and per-source SHA-256. Explicit mapping refuses unsafe/missing/duplicate headers and disallows treating the amount column as identity. Fifteen synthetic integration methods and strict two-mode Linux/Windows CI gate are added; this is **not** a binary release or QD approval. [R131 operator and safety guide](docs/LEDGER_CUSTOM_KEYS_R131.md).

### R132 — LedgerDiff native keyboard, scale and shortcut regression repair (DRAFT / HOLD)

R131's two optional LedgerDiff CSV match-key fields added two legitimate Tab stops. R131 exact-head Windows CI **failed at R106 native focus**, despite passing Linux and earlier Windows source/build/smoke gates, because the R106/R107/R108 native observers still expected the pre-R131 three-entry form. R132 updates all three native gates to require five LedgerDiff editable controls and the original three Browse controls, preserves the two mapping fields as keyboard-focusable and visible at 200%/400%, and keeps cancelled-picker/blank-input safety enforced. It adds **21 exact, zero-skip source regressions** required on Linux and Windows in normal and optimized Python. First exact R132 CI passed R106 but **failed R107 native scaling**; fixed-code-only private diagnostic categories have been added for investigation, with release still blocked. See [R132 native LedgerDiff accessibility runbook](docs/LEDGER_NATIVE_ACCESSIBILITY_R132.md). These preflight changes do **not** establish the 46 independent physical Windows 11 checks or authorize binary distribution, premium access or production merge.


### R133 — LedgerDiff narrow viewport / 400% Tk reflow fix (DRAFT / RELEASE HOLD)

R132 exact-head [Windows CI #41419512396](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41419512396) passed R106 keyboard focus but **failed R107 native scaling** (`ledger/400%/unmapped`). The ledger's 65-character-wide editable fields next to very wide scaled labels forced their x-position outside the canvas. R133 replaces only LedgerDiff's three-column grid with a vertically stacked, full-width layout that preserves source controls and exact Tab creation order. Ten new zero-skip synthetic methods run in normal/`-OO` modes on Linux and Windows, in addition to the still-mandatory Windows native R107 and R108 probes. A local Xvfb synthetic reproduction supports the fix but does **not** prove native Windows or 46 physical Win11 accessibility checks. See [R133 reproducibility and safety runbook](docs/LEDGER_400_PERCENT_REFLOW_R133.md). All six apps remain **UNRELEASED**, with independent QD/founder release approval required.


### R134 — Invoice Twin Scout configurable near-match window (draft; unreleased)
The free Invoice Twin Scout screen now exposes a local-only **Near-match days (0-365)** setting (default 7). Exact normalized invoice-number anchors remain independent of the window; same-vendor/same-amount *near* candidates require the selected calendar-day window. `review_window_days` accompanies each review CSV finding alongside source SHA-256, physical source line references and stable candidate IDs. Invalid values fail closed without a partial report; no telemetry, automatic fraud determinations, or premium entitlement changes. See [R134 operator notes](docs/INVOICE_WINDOW_R134.md). Release is on HOLD pending physical Windows 11 acceptance, genuine Defender/EDR, signing, premium distribution access control, independent QD and founder approval.


### R138 — ProcureGuard source and offset-line custody (draft; unreleased)

The premium ProcureGuard Studio Pro three-way report now includes the exact snapshot SHA-256 for each purchase-order, invoice, and receipt CSV, plus deterministic physical-row candidate links from credit memos to source invoice documents and returns to source receipt documents. Ambiguous and missing links remain visible and carry the existing human-review flags; source identifiers are not copied into link JSON. No payment approvals, premium unlocks, money-rule changes, telemetry, or public downloads. The [R138 operator and review guide](docs/PROCURE_OFFSET_CUSTODY_R138.md) defines the limitations and the 22-method two-OS normal/optimized CI gate. **Release HOLD** until independent physical Win11/QD and founder gates pass.
