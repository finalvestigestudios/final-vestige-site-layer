# R16 — bind premium issuance to the exact signed bytes

**Scope:** Operator-side premium entitlement issuance; GrantAudit Studio Pro and
ProcureGuard Studio Pro only. This is an internal development control, **not**
production approval, software licensing activation or a commercial payment gate.

## Threat and improvement

Previously, `IssuanceRegistry.finalize(...)` re-read the output file and
stored the SHA-256 of *whatever* bytes existed at that path. The operator CLI
had already called the entitlement signature verifier, but a file replacement
after verification and before finalization could make a different document's
bytes appear in the issuance record.

R16 changes the call contract:

1. `issue_entitlement(return_digest=True)` signs the canonical R11 payload,
   writes it exclusively, independently validates the created license through
   the existing Ed25519 verifier, and returns `(Path, sha256)`. **The returned
   SHA-256 is of the original signed byte string still in memory.** The default
   `issue_entitlement(...)` return is still a Path for R12 callers.
2. The CLI carries that specific receipt to
   `IssuanceRegistry.finalize(..., expected_sha256=receipt)`.
3. The registry **requires** a lowercase 64-hex expected digest and compares
   it to a bounded, no-follow read of the current output before changing
   `reserved` to `issued`. A missing, malformed or mismatched receipt leaves
   the reservation unchanged for manual investigation.
4. Existing R13–R15 synthetic tests now pass explicit fixture-derived
   fingerprints. R16 tests include real temporary Ed25519 signing, both premium
   products, same-length corruption, valid alternate-license swapping, and an
   injected replacement *between* verifier acceptance and receipt handoff.

The receipt is not itself an authenticated proof to outsiders. The registry
trusts the issuer process to supply the expected hash; if that process is
compromised, or an attacker has control of registry files or machine time,
this control cannot establish authenticity. The registry continues to store
no plaintext holder, customer financial records or signing keys. The
pre-release client public-key map is **still empty**.

## Local regression commands

At the exact feature-branch checkout, with `cryptography==46.0.4` installed:

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_signed_issuance_binding_r16.py -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p test_signed_issuance_binding_r16.py -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

For a genuine six-app candidate on a trusted Windows x64 workstation use
`products/desktop/scripts/verify-windows-candidate.ps1 -Build`.
Successful Python tests **do not** prove executable compatibility,
genuine license payment, protected distribution, malware clearance or QD signoff.

## Operational boundaries

- Do not recycle a reserved license ID after a failed signing or tamper event.
- Preserve the registry and affected file for a qualified operator's review.
- Never put a production signing PEM, production passphrase, or issued customer
  license in a repository, workflow artifact, test log or public URL.
- Keep signing authority, paid fulfillment, premium download access, code
  signing, Windows ACL verification and QD publication approval as distinct gates.
- No application or download is authorized for release by this change.
