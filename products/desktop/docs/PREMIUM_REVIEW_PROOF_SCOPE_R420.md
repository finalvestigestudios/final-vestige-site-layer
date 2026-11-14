# Labs R420 — product-scoped premium review entitlement proof

Status: **DRAFT / SOURCE ONLY / NO RELEASE AUTHORIZATION**. Parent: R419 draft PR #2437 at `1dbda29ba3b942efb41e8c49e38930471844e584`. No production `main` modification.

## Defect and impact

The premium human-review window previously called `revalidate_or_revoke(authorize, clear)` and accepted `bool(authorize())`. A verifier callback accidentally returning `True`, `"denied"`, a truthy sentinel, an entitlement for the *other* premium product, or a custom object with `__bool__` could allow the review workbench to open or keep local review actions enabled. This was weaker than the separately checked premium app-launch proof. No assumption is made that the product currently ships valid signing keys (the embedded signing authority is intentionally empty); the issue matters before any future trusted launch.

## Fix

- The **actual premium review GUI** passes its product at *both* authorization boundaries: before constructing a Tk window and for each revalidation prior to review/export/seal/restore actions.
- The scoped revocation helper demands the exact `offline_entitlement.Entitlement` class and matching native product via the existing `has_verified_premium_proof` predicate. A mere truthy callback return, a subclass, a mismatched product, and a hostile `__bool__` cannot grant access.
- Verifier errors cause denial and sensitive review-view clearance without printing private filenames or license identifiers. Failed UI clearing remains visible as an error, never a permit.
- The real GUI callback continues to call `verify_license(entitlement_source, app_id)` on each check. **Shape validation does not replace Ed25519 verification, expiry checking, or live license-file readback.** Direct callers can still forge a dataclass if they control the verifier callback; the callback itself is a trusted boundary.
- Two-argument `revalidate_or_revoke` preserves old non-gating test/API semantics so historical headless helpers do not silently break. It must **never** be used to authorize a premium GUI. A later QD-reviewed breaking API cleanup can remove that compatibility path.
- R248 pre-window tests now reject a plain user-defined `Proof` dataclass as insufficient, while retaining synthetic real-type shape checks.

## Evidence and test boundaries

New `test_premium_review_revalidation_r420.py` has **13 committed methods**: two product positives, opposite-product denial, truthy sentinel rejection, hostile string/truthiness hooks, wrong/non-native product denial, private verifier exception, revocation on subsequent callback failure, one verifier call per check, scrub failure and legacy semantics, plus AST inspection that both actual GUI call sites pass `product=product`.

Reproduction before fix: `bool("denied") is True`; a truthy sentinel from an incorrect product would also be accepted. With the scoped helper, both fail and trigger scrubbing.

**Local evidence:** Linux, isolated package shim with an `Entitlement` dataclass (not real cryptography), the implementation-equivalent scoped guard, and synthetic UI wiring: **13/13 standard Python + 13/13 optimized `-OO -W error` passed**; Python source compilation passed. The synthetic GUI is **not** actual `review_ui.py`; the full repository, real `offline_entitlement.py`, and exact committed 13-test file have **not** been executed in a trusted full checkout. Do not claim integration or native Windows success from these results.

The [desktop source evidence workflow](../../../../.github/workflows/desktop-source-evidence-r385.yml) now requests normal and optimized runs of R420 plus inherited R248, R247 and R252 proof/revocation contracts on Ubuntu and Windows. As of the R419 parent, hosted Actions had **no recorded job steps** in either [source #43564094561](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43564094561) or [Windows build #43564094526](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43564094526). Runner/billing root cause remains unconfirmed. New exact-R420 run status must be inspected separately.

## Explicit acceptance before shipping

1. Restore GitHub Actions runner allocation (owner checks Actions billing/spending cap, repository permissions and job annotations), or use a trusted full Windows/Ubuntu checkout. Run **exact R420 tests**, inherited R247/R248/R252, real R419 premium journal tests, complete six-engine Decimal/provenance and AES-GCM/Ed25519/entitlement suites.
2. Confirm the authentic `verify_license` returns the proof shape only for valid, non-expired, same-product signatures. Exercise expiry, wrong-product, license replacement and denial before Tk construction and after modal dialogs.
3. Build and smoke-test six actual **Windows x64** portable EXEs; perform native keyboard/NVDA/high-DPI checks, Windows Defender scan, SHA-256 receipts, licensing validation, and unauthorized premium download denial.
4. Enforce independent QD review and explicit founder approval before merges, publishing or releasing any binary.

**No** file containing a customer ledger, journal, private signing key or premium executable was added. No orders, payments, eligibility decisions, website changes, public download links, or production updates are part of R420.
