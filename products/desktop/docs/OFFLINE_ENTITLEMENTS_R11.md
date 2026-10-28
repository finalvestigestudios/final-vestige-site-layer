# R11 — Offline premium entitlements (development-only)

## Status

**Under development, not for production use.** This sprint introduces Ed25519
signature verification for GrantAudit Studio Pro and ProcureGuard Studio Pro.
Both premium GUIs are **locked by default** because the trusted distributor
public-key map is intentionally empty. This is a release gate, not a sales
integration. The four free utilities remain unaffected.

Neither a signed license nor a passing Windows executable smoke test authorizes
public distribution. Premium EXEs require controlled download delivery,
checkout integration, licensing terms, support, clean-machine verification,
security review and QD approval before release.

## Signed file contract

Extension: .fvslicense, UTF-8 JSON, <= 8192 bytes, exactly these fields:

- schema: fvs.entitlement.v1
- kid: signing authority key ID (4–64 ASCII letters/digits/_/-)
- product: grants or procurement (never interchangeable)
- license_id: a nonsecret unique ID (same character/length constraints)
- holder: nonblank string of up to 120 characters
- issued_at, not_before, expires_at: canonical UTC, e.g. 2026-10-28T12:00:00Z
- signature: canonical unpadded URL-safe base64 Ed25519 signature (64 bytes)

The signature covers the domain-separated byte stream
FinalVestigeLabs.entitlement.v1 + NUL + compact UTF-8 JSON of all fields except
signature, sorted by key, and with non-ASCII preserved. Any change to product,
holder, time range, issuer or license ID invalidates the signature. Duplicate
fields, unknown fields, malformed timestamps, invalid ranges, missing files,
symlinked files, oversized files, unknown kid, and wrong signatures fail closed.
Validity requires issued_at <= not_before <= current UTC < expires_at, with a
maximum 3660-day validity window. There is no embedded private signing key.

**Key custody:** Production public verification keys must be pinned in client
source only after separate protected key generation, a release review, and
documented rotation. Private signing keys stay outside distributable assets,
GitHub source, artifacts and CI logs; prefer HSM/KMS-based signing with an audited
issuance workflow. Ephemeral private keys in unit tests are test-only and are
never accepted by a production build.

## GUI behavior

- Premium app startup begins hidden and requires a valid signed entitlement.
  If a valid default file exists, it is used:
  %LOCALAPPDATA%\FinalVestige\licenses\grants.fvslicense or
  %LOCALAPPDATA%\FinalVestige\licenses\procurement.fvslicense.
- If production verification keys are configured but default entitlement is
  invalid/missing, the user may select a signed file for that session. Selecting
  a license does not automatically copy it or upload data.
- When no trusted production keys are configured (current R11), a warning is
  displayed and premium UIs are not initialized. No customer CSV is read.
- New report generation and opening the human review window revalidate the
  chosen entitlement. Every review-window data action rechecks the entitlement.
  Existing plaintext reports are not retroactively encrypted or removed.
- The six synthetic --smoke-test paths exercise core engines without a license,
  solely with fixed temporary synthetic data; they cannot import customer files.

## Limitations and risks

Purely offline activation cannot reliably prevent clock rollback, copying a
license to other machines, debugger/patch attacks, revoked or refunded licenses,
or access to software obtained from an unauthorized distributor. The signature
does prevent forging or modifying an entitlement without the signer's private
key, *assuming the packaged verifier and trusted keys remain intact*.

This implementation does not collect payments, generate or sell licenses,
operate a revocation service, establish real customer identity, lock down a
portable EXE against reverse engineering, sign the Windows binaries or protect
plaintext active working files. Never advertise production DRM or completed
premium access controls based on this implementation alone.

## Regression evidence

- 15 direct Ed25519 tests using newly generated ephemeral keys in
  test_offline_entitlement_r11.py.
- 4 headless premium UI tests in test_premium_access_r11.py.
- Independent pure verifier tests were run on Python 3.13.5 (cryptography 46.0.4);
  the complete checked-out repository and packaged Windows GUI tests remain
  outstanding pending a functioning runner or verified Windows workstation.

Run from repo root:

    PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p "test_*r11.py" -v

The unchanged internal build process still packages both premium apps to
private build artifacts only, never public downloads. Do not merge this stacked
PR into main or production before its parents are reviewed and QD gates pass.
