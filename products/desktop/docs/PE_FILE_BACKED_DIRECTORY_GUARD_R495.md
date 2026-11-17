# R495 — PE directory file-backing custody (draft / QD HOLD)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This is a source-only release-preflight change for the six standalone Windows x64 programs: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro.

## Defect and implemented invariant

R494 established that PE32+ data-directory RVAs fit in a section's mapped virtual extent, but `VirtualSize > SizeOfRawData` can create a *zero-filled* mapped tail with no corresponding on-disk directory bytes. A forged nonempty import/resource/etc. directory pointing entirely into that tail therefore passed the R494 structural test and could mislead artifact review.

R495 independently requires each nonempty non-certificate data directory to fit inside one **raw-file-backed virtual interval**, computed per section as:

```text
[VirtualAddress, VirtualAddress + min(SizeOfRawData, VirtualSize or SizeOfRawData))
```

The existing mapped extent, image bounds, header checks, section-overlap checks and same-descriptor manifest SHA-256 check remain in force. The PE security/certificate directory (#4) remains a **raw file-offset** reference and is not treated as an RVA. Its structural acceptance does not authenticate Authenticode signatures. Files are inspected, never executed, by this preflight.

This conservative pre-release policy rejects directory references in virtual zero-fill, even if a loader could map the location. It does not claim complete PE semantic validation, malware safety, signing, or executable compatibility.

## Test commands (trusted complete repository checkout)

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_guard_r494.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_guard_r494.py
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_binding_r494.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_binding_r494.py
```

The existing R494 step in both independent source and Windows internal workflows already invokes these two test modules in normal and optimized Python; R495 adds methods to those suites without a CI configuration rewrite. For the four new integrated tests, assert that a valid directory ending at the raw backing boundary passes, a zero-fill-only reference fails, a crossing reference fails, and the six-candidate release gate rejects a forged zero-fill directory with a valid inventory manifest.

### Release gate remains HOLD

- Local CPython execution on **synthetic fixtures** is not a native Windows x64 validation.
- GitHub Actions runner failures that occur before test steps do **not** count as passing or failing application tests. Inspect runner/billing eligibility and job annotations, then rerun exact-head jobs.
- Complete six-app source regression and Windows packaging, actual EXE launches, Defender scan, SHA256 receipts, keyboard/screen-reader accessibility, tested free downloads and authenticated premium entitlement remain mandatory.
- No binary, premium file, public download link, WordPress publication, or production merge is authorized. Keep **draft PR + independent QD review + explicit founder approval**; do not permit automated compliance/payment approvals.
- The guard does not read or upload real financial records. Preserve Decimal-safe money calculations, deterministic audit trails, local-first processing and redacted diagnostics.
