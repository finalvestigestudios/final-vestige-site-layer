# R448 — premium evidence hard-link custody (DRAFT / HARD RELEASE HOLD)

Issue [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R447 draft [#2604](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2604) at exact parent `2cfe9fb8cca8a014951fa42fcaf93329f78b3909`; **not** production `main`. No premium binaries, public downloads, entitlement changes, WordPress changes or release authorizations.

## Defect and bounded fix

`manifest_guard._hash_regular` checked ordinary file mode, descriptor/path metadata and content stability, but not the file's `st_nlink`. Two pathname aliases to one inode could be created by an operator or another local process, allowing edits through the second name while the inventory still described a single named evidence file. The five-field metadata signature intentionally omits link count, so link-only changes could escape those comparisons. This is a **local evidence provenance/custody gap**, not a demonstrated SHA-256 collision, remote exploit, or approval bypass.

The R448 patch reuses the established `premium_link_custody.require_single_link` predicate, requiring exactly one link at **five** observation points: (1) before opening each input/report, (2) immediately after descriptor adoption, (3) after descriptor reading, (4) at the final pathname view of that digest, and (5) across the final all-file recheck immediately before publication of inventory text. Source and report bytes remain read-only. Earlier R447 Windows-safe labels, bounded streaming and SHA-256 rules remain unchanged. If a hard link is present or appears during hashing, the writer fails closed; it never returns a partial inventory.

The verifier already requires exactly one link for published reports and its inventory file. This change aligns the *writer* with that custody rule and covers **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. It does not guarantee against privileged concurrent edits, inode reuse, future mutations after the final check, or aliases invisible to filesystem link counts; no invented tamper-proofing claim is made. Legitimate evidence with multiple links requires a reviewer-approved **separate copy** and full reconciliation/re-inventory, preserving original evidence.

## Committed artifacts

- `products/desktop/fvs_suite/manifest_guard.py` — writer-side five-stage single-link verification.
- `products/desktop/tests/test_premium_manifest_link_custody_r448.py` — **6** full-module methods, synthetic files: pre-existing external aliases (sources/reports), alias created between stat/open, alias at postread pathname recheck, alias after earlier source hash but before final sweep, unmodified positive SHA-256 inventory.
- `.github/workflows/desktop-source-evidence-r385.yml` — executes R448 and inherited R254/R255 manifest tests, standard and optimized, on both Ubuntu and Windows. Adding tests does not repair hosted-runner eligibility.
- This review document.

## Executed local evidence (limited, not full checkout)

A **reconstructed isolated projection** of the targeted production functions, local synthetic fixtures and three minimal dependency projections passed:
- `python -W error -m unittest discover -s tests -p test_premium_manifest_link_custody_r448.py`: **6/6 PASS**.
- `python -OO -W error -m unittest discover -s tests -p test_premium_manifest_link_custody_r448.py`: **6/6 PASS**.
- `python -m compileall -q`: PASS.
- Controlled pre-fix projection with the five single-link checks removed: **7 failed assertions/subcases across 5 methods**; one positive case passed. This is a before/after synthetic demonstration, **not a complete repository regression run**.

The committed new test source has **not** been executed against a full GitHub checkout, and the existing repository's inherited tests and native Windows x64 build checks have **not** passed for R448. Do not count projected passes as CI or distributable verification.

## Exact-current inherited CI blocker and next step

R447 parent run [#43702115135](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43702115135) (Ubuntu/Windows source) and [#43702115165](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43702115165) (internal Windows build) each failed on 2026-11-15 around 10:02 UTC in seconds, **four failed jobs with zero recorded steps and no assigned runner**. GitHub reports one check annotation per job, but the available connected API cannot fetch those annotation endpoints; **no root cause is verified**.

**Smallest unblock:** the repository owner should open each Actions run's failed job UI and read the first annotation, then check Actions billing/spending caps and runner/policy eligibility. Once runner allocation is restored, rerun the exact R448 head and inherited six-app suites, genuine Windows x64 EXE builds, Defender scans, keyboard/accessibility smokes, SHA256 and protected premium delivery verification. Retain **QD review + explicit founder approval** before any publication.

**Release state:** `release_authorized=false`, draft-only. No executable, premium artifact, download URL, license, deployment, merge or payment approval.
