# R254 — Premium manifest/report byte custody (DRAFT; QD HARD HOLD)

Issue: #73. Baseline: R253 draft PR #1385 at `c6f546828de0c9903d58b15eb1114a29ec9db507`; isolated stacked branch. **Do not merge or publish.**

## Defect and resolution

R253 established correct output directories, file types and bundle filenames but did not inspect the **contents** of a premium evidence manifest. A report modified after generation, or an arbitrary nonempty manifest alongside the expected filenames, could still be announced as a complete package and implicitly selected for review.

`fvs_suite/premium_manifest_completion.py` now runs after R253 output-placement validation, before GUI success or implicit premium review selection. It:

1. Checks directory inventory equals exactly the expected reports + manifest; unexpected files fail closed.
2. Opens the manifest with a bounded (128 KiB), non-following descriptor, and verifies pre/open/post file identity, size and strict ASCII encoding.
3. Enforces the actual `manifest_guard.inventory_text` header/line format and bounded source-entry counts (GrantAudit: 3; ProcureGuard: 3 or 4 with optional policy).
4. Rejects malformed, repeated or ambiguous labels and invalid SHA-256 fields.
5. Uses the existing descriptor-safe `manifest_guard._hash_regular` to independently recompute report-byte digests (256 MiB per-report cap), matching the ordered report records in the manifest.
6. Returns no financial data or private paths to the GUI. A failed check leaves user files untouched and prevents automatic premium review selection.

Four free apps retain their existing one-file output validation. Premium entitlement verification and human-only review decisions remain unchanged.

## Reproduction and synthetic evidence

Before this change, an existing correctly named premium bundle with `evidence-manifest-*.txt` containing any nonempty text passed R253's path/size validation. Now it is rejected.

New test file: `products/desktop/tests/test_premium_manifest_completion_r254.py` — 13 methods. Included: GrantAudit, ProcureGuard with/without policy, changed report hash, mixed report/manifest, extra/missing files, over-limit inventory, invalid header/digest/count, duplicate source label, wrong product, symlink manifest, and no destructive cleanup. Updated inherited R251 GUI and R253 package fixtures to use valid synthetic SHA inventories.

### Verified in isolated Linux execution

CPython, isolated reconstruction of the new module plus a **local stand-in for existing `manifest_guard._hash_regular`** (using SHA-256 on synthetic files):
- `PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_manifest_r254.py'` — **13/13 PASS**.
- `PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_manifest_r254.py'` — **13/13 PASS**.
- Total **26 successful isolated test executions**. No genuine customer data, secrets, executables, browser interaction or network access.

**Not established:** running the committed tests against the full GitHub checkout and its real manifest_guard, inherited R251/R253 suites, hosted CI, Tk GUI, Windows 11 x64, portable EXEs, malware scan or screen readers. Isolated SHA stub does not substitute for real source-integrity verification. New source and regressions are committed for native CI when available.

## Reproducible exact-source commands

From the full repository checkout at this PR's head:

```powershell
cd products/desktop
py -3 -W error -m unittest discover -s tests -p "test_premium_manifest_completion_r254.py" -v
py -3 -W error -m unittest discover -s tests -p "test_report_destination_custody_r253.py" -v
py -3 -W error -m unittest discover -s tests -p "test_report_completion_r251.py" -v
py -3 -W error -m unittest discover -s tests
```

Check the R254 manifest against an actual GrantAudit and ProcureGuard publisher output with synthetic source CSVs. Do a Windows 11 x64 native GUI smoke test including tampering, failure messaging and premium auto-selection. Confirm `manifest_guard` hashes and optional procurement policy inventory before QD approval.

## Boundaries and release gates

Inventory hashes are **not signatures**, nor proof that imported source files remain unchanged since report creation; they describe the source snapshots recorded at build time. Post-generation checking is point-in-time, not race-free or power-loss durable. No compliance/payment approval is automated. Original inputs and existing published evidence remain unmodified. No public binaries or premium download URLs.

**Required independent QD:** review manifest format, Windows non-following descriptor behavior, very large output responsiveness, timeout/cancellation, accessibility, and inherited tests. Then private six-app Windows x64 build, independent checksum/scan/smoke tests, protected premium delivery and founder authorization. No production or WordPress changes.

**CI infrastructure blocker:** R253 Actions run #42358043490: Ubuntu `source-tests` and `windows-build` both concluded failure with no reported steps/logs. Check billing/usage, workflow permissions, hosted runner provisioning, then rerun the same R254 SHA unmodified.
