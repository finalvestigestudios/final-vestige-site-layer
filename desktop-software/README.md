# Final Vestige Studios — Desktop Software

**Status: development prototypes, not public products.**

This folder contains seven offline-first desktop tools. Each has a standalone
Python module with a Tkinter GUI and CLI, a unittest suite, and an Inno Setup
installer recipe. Windows CI artifacts are **unsigned private development
installers**, not public releases.

| SKU | License plan | Python entrypoint | Windows executable |
|---|---|---|---|
| FileProof | Free | fileproof/fileproof.py | FileProof.exe |
| Data Import Doctor | Free | data-import-doctor/data_import_doctor.py | DataImportDoctor.exe |
| Packet Preflight | Free | packet-preflight/packet_preflight.py | PacketPreflight.exe |
| Renewal Radar | Free | renewal-radar/renewal_radar.py | RenewalRadar.exe |
| Payment Sentinel | Premium, proposed $69 | payment-sentinel/payment_sentinel.py | PaymentSentinel.exe |
| Ledger Bridge | Premium, proposed $59 | ledger-bridge/ledger_bridge.py | LedgerBridge.exe |
| Reimbursement Auditor | Premium, proposed $79 | reimbursement-auditor/reimbursement_auditor.py | ReimbursementAuditor.exe |

The WordPress catalog is **draft page 1612** at
https://finalvestige.com/?page_id=1612&preview=true. Product names and
prices are hypotheses, not market-validated.

## Development

Python 3.11+; standard library only for app execution. Examples:

    python desktop-software/fileproof/fileproof.py
    python desktop-software/data-import-doctor/data_import_doctor.py
    python desktop-software/packet-preflight/packet_preflight.py
    python desktop-software/renewal-radar/renewal_radar.py
    python desktop-software/payment-sentinel/payment_sentinel.py
    python desktop-software/ledger-bridge/ledger_bridge.py
    python desktop-software/reimbursement-auditor/reimbursement_auditor.py

Each script opens a GUI without positional CLI arguments; use --help for CLI.

Run all suites from repository root (no third-party test library required):

    python -m unittest discover -s desktop-software/fileproof -p "test_*.py" -v
    python -m unittest discover -s desktop-software/data-import-doctor -p "test_*.py" -v
    python -m unittest discover -s desktop-software/packet-preflight -p "test_*.py" -v
    python -m unittest discover -s desktop-software/renewal-radar -p "test_*.py" -v
    python -m unittest discover -s desktop-software/payment-sentinel -p "test_*.py" -v
    python -m unittest discover -s desktop-software/ledger-bridge -p "test_*.py" -v
    python -m unittest discover -s desktop-software/reimbursement-auditor -p "test_*.py" -v

## Windows CI / artifact boundaries

- FileProof Windows workflow: .github/workflows/fileproof-windows.yml
- Three free apps workflow: .github/workflows/free-utilities-windows.yml
- Three premium prototypes workflow: .github/workflows/premium-prototypes-windows.yml
- Python 3.12, PyInstaller 6.16.0, Inno Setup 6, SHA-256 installer hashes.
- Each installer has a distinct Inno AppId to prevent cross-product upgrades.
- The matrix pipelines define silent installation, installed-file checks,
  and uninstallation. Defined checks are NOT evidence of passing.
- Never publish private unsigned CI artifacts or commit signing/payment keys.
- Initial FileProof installer build passed in Actions run 40617416676 on
  2026-10-27 Pacific, but independent install security and signing are pending.
- Subsequent Actions runs failed before job steps began (no step logs).
  Diagnose runner/account provisioning, quotas and policy; do not describe
  pre-step failures as application test failures. Avoid repeated retries.

## Release gates — all must be met before activating downloads

1. Verify outputs on realistic and adversarial data: broken input, duplicates,
   date boundaries, extreme values, Unicode and filesystem permission errors.
2. Run Windows GUI acceptance tests: first launch, import/export, Start menu
   shortcuts, Windows installer, uninstall, reinstall and upgrade.
3. Confirm Windows CI installer smoke tests pass; attach versioned binary,
   SHA-256 checksums, security scanning evidence and release notes.
4. Code-sign every direct-download installer using securely managed
   certificates or trusted signing. Do NOT ship unsigned direct EXEs publicly.
5. Validate offline function, no telemetry and no unauthorized file changes.
6. Configure premium payment and tested licensing/delivery before any sale.
   Premium prototypes currently have neither payment checkout nor
   license enforcement; never expose paid installers as public files.
7. Show genuine screenshots from tested binaries, requirements and limitations.
8. Validate buyer demand and realistic utility before claiming market fit.
9. Publish WordPress page only when a real, safe download is available.

## Honest feature boundaries

- FileProof compares recorded SHA-256 hashes and also flags added regular files, untracked links, and scan errors. A clean result requires all checks to pass. It is not a backup/recovery application, does not cover empty directory creation, and its unsigned manifests must be stored securely to prevent attackers from replacing them.
- Data Import Doctor diagnoses CSV issues, not guaranteed import compatibility.
- Packet Preflight checks folder metadata against a user-provided checklist,
  not application or regulatory eligibility.
- Renewal Radar is a local tracker. ICS exports fold long Unicode lines to the iCalendar standard and handle date boundaries. It does not run background notifications:
  ICS exports must be imported into a calendar. Invalid recurrence dates are
  skipped by RFC5545, e.g. monthly events on day 31 skip short months.
- Payment Sentinel flags patterns for human review, never proves fraud.
- Ledger Bridge quarantines duplicate exact reference/amount identities instead of arbitrarily pairing them. Date/amount-only matches remain review suggestions, dates outside tolerance trigger warnings, and blank standalone amounts are errors. Its HTML report includes all review warnings, candidate matches, ambiguous groups, excluded rows, and SHA-256 fingerprints of the original CSV inputs. See `ledger-bridge/samples/README.md` for fictional acceptance data. Manually verify sign conventions and all proposed matches.
- Reimbursement Auditor crosschecks user-entered evidence index and
  attachment presence; it does not read PDF contents or certify eligibility.

## Next milestone sequence

Restore GitHub runner execution; get matrix CI green; close test gaps; add
sample-data bundles and clear manuals; integrate signing; integrate payment
provider and controlled delivery; independently test Windows installers; then
publish individual catalog download buttons one product at a time.
