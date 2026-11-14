# Labs R421 — remove permissive unscoped review authorization

**DRAFT / SOURCE ONLY / RELEASE HARD HOLD.** Stacked on R420 draft PR #2442; no `main`, WordPress, or executable release modification. Issue #73.

## Reproduced defect and fix

R420 scoped the two real premium review GUI calls but retained a historical public helper behavior: calling `revalidate_or_revoke` without a `product` would apply `bool(authorize())`. A new caller could accidentally use that route and authorize on `True`, `"denied"`, or an unrelated truthy object. R421 **removes the compatibility route**. `product` is now mandatory and keyword-only; omission raises `TypeError` before calling the verifier or scrubber. Invalid/non-native product IDs deny and scrub without invoking the verifier. For valid `grants` and `procurement` IDs, exact `Entitlement` class and exact native proof product are required; a `str` subclass with overridden equality cannot spoof an app identity.

The trusted `authorize` callback must still call `verify_license` and cryptographically reverify the **current** local license on each operation. A valid-looking dataclass constructed by an untrusted callback is **not** cryptographic proof. No signing keys are bundled: `TRUSTED_PUBLIC_KEYS` remains empty before a separate distribution approval.

## Artifacts and compatibility

- `products/desktop/fvs_suite/review_target.py`: mandatory scoped review gate, fail-closed revocation.
- `products/desktop/fvs_suite/premium_launch_proof.py`: exact-native product field and malformed-property denial.
- `products/desktop/tests/test_review_scope_mandatory_r421.py`: **15** new regression methods covering both products, no scope, forged string equality, revoked/incorrect/hostile callback results, exception privacy, UI AST wiring and absence of the legacy gate.
- Existing R247/R248 tests now call the real scoped gate using synthetic `Entitlement` fixtures. R420's former legacy-acceptance test now asserts that omitted scope is rejected. Test fixtures remain unsigned; no false assumption of a valid signed license.
- `.github/workflows/desktop-source-evidence-r385.yml`: both Windows and Ubuntu request R421 plus inherited R247, R248, R252, R420 in standard and `-OO -W error` Python.

**Breaking helper API:** code that omits `product` must be upgraded explicitly. The actual premium GUI already passes `product=product` at both authorization sites, so it does not depend on the removed route.

## Evidence / limits

Local Linux Python 3.13.5 **extracted-scope fixture** ran 15 synthetic unit methods under normal and optimized Python: **15/15 + 15/15 PASS**; source compilation of the isolated model passed. The local fixture used the same authorization algorithm, synthetic `Entitlement` and a minimal two-call GUI AST, **not the exact full GitHub checkout, real signed-license verifier, inherited tests, or native Windows apps**. This is proof of isolated gate behavior only; a passing helper test is not a release result. The hosted workflow is the source of truth for exact committed integration. If CI cannot allocate a runner, mark tests **NOT RUN**, not failed tests or green release.

## Release acceptance / next step

1. Restore GitHub Actions runner allocation or supply a trusted Windows/Ubuntu checkout and execute the exact new 15 methods, inherited R247/R248/R252/R420, R419 journal integration, and all six engines' money/provenance/privacy/cryptographic regressions.
2. Validate authentic, current Ed25519 license checks including expiration, replacement, mismatched product, and deny after modal dialogs.
3. Build and inspect six genuine Windows x64 PE outputs; complete smoke tests, Defender, keyboard/NVDA/high-DPI, SHA-256 receipts, and actual denial of unauthorized premium downloads.
4. Require independent QD review and explicit founder approval before any merge, production release, WordPress publication, or premium asset exposure.

No customer data, ledger, premium EXE, signing secret, payment, authorization of reimbursement, or automatic compliance decision has been published.
