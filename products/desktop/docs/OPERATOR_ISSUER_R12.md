# R12 — Offline operator-only premium entitlement issuance (PRE-RELEASE)

## Scope and release status

`products/desktop/license_issuer.py` is an **operator-side tool**, not a seventh
product and **not bundled with any of the six Windows executable launchers**.
It creates `.fvslicense` documents that the existing R11 Ed25519 client verifier
can validate. Only **GrantAudit Studio Pro** (`grants`) and **ProcureGuard Studio
Pro** (`procurement`) are eligible. The four free programs remain unchanged.

**Do not use this to sell or activate premium software yet.** Client
`TRUSTED_PUBLIC_KEYS` remains **empty**, so even properly signed entitlements do
not unlock the pre-release GUIs. No new production key was generated or pinned.
The repository does not provide protected checkout, proof of payment, secure
license delivery, license revocation, account recovery, or an approved production
signing authority. The site QD approval gate and all other release prerequisites
remain mandatory. Never attach an encrypted private key, passphrase, test license,
or a premium executable to a public release or issue comment.

## Required out-of-band preparation (not automated)

1. Obtain the business/financial/legal approvals for the license policy,
   entitlement duration, refund and revocation rules, and named custodians.
2. Generate an **Ed25519 private key in encrypted PKCS#8 PEM format** on an
   isolated, controlled machine using a reviewed security tool. Keep it outside
   **every** Git repository, CI runner, build artifact, or customer installation.
   The issuer rejects plaintext PEM, incorrect algorithms, oversized/symlinked
   keys, and a key inside a Git worktree. POSIX files must be owner-only (`0600`).
   Windows private-key ACLs must be reviewed separately by the custodian.
3. Protect signing material and its recovery method using approved offline/HSM/
   KMS custody and separation of duties. Record a nonsecret key identifier `kid`
   (4–64 `[A-Za-z0-9_-]` chars), and maintain a **separate protected registry**
   of issued unique IDs, customers, refunds, expirations, and key-rotation dates.
4. Through an approved, reviewed client-source change, distribute only the
   **32-byte raw Ed25519 public verification key** with the matching `kid`.
   Never pin test keys. Do not ship/publish until QD review, signed Windows
   binary testing, paid-download access controls, privacy review and user
   acceptance are complete.

## Operator use (only after authorization)

From a trusted Python 3.12+ environment with pinned `cryptography==46.0.4`:

```text
PYTHONPATH=products/desktop python products/desktop/license_issuer.py \
  --key /controlled/offline-signing.pem \
  --kid fvs-production-key-01 \
  --product grants \
  --license-id unique-approved-license-id \
  --holder "Authorized Customer" \
  --expires-at 2027-10-28T00:00:00Z \
  --output /controlled/fulfillment/new-license.fvslicense \
  --confirm-issue
```

Substitute real, authorized values when approved; the example illustrates the
interface and is not a usable customer entitlement. `--not-before` may specify a
**future** canonical UTC time, otherwise it starts at the issuance time. The
script derives `issued_at` from the current timezone-aware clock. The operator
must use a terminal: `getpass` prompts for the key passphrase without echo, and
**there is intentionally no** `--password` / environment / stdin-file option.
No private PEM bytes, passphrase or signed license contents are printed.

The issuer enforces strict R11 fields, maximum 3660-day lifetime, valid UTC
bounds, an existing output directory and exclusive `O_EXCL` creation (no
replacing a preexisting file or symlink). It writes a restricted-mode file,
flushes it to disk, then independently validates the resulting bytes against
the exact R11 client verifier using the corresponding public key. If an I/O or
post-write verification failure occurs, **inspect/quarantine** the new output;
it may contain partial data. Never blindly retry against or delete an existing
output. Maintain and back up the external issuance ledger to prevent duplicate
`license_id` reuse; this script cannot enforce uniqueness across operators.

## Security boundaries

- This is an **offline signer on a trusted operator machine**, not a hosted
  checkout, DRM, remote attestation, or proof a customer paid.
- Client validation remains disabled until authorized public keys are pinned.
  Public-key pinning **must not** be automated by this operator command.
- Python cannot guarantee memory zeroization or defend against compromised
  operating systems; key handling is bounded, but no hardware key isolation
  is claimed. Use HSM/KMS-backed authorization before production issuance.
- On Windows, filesystem ACL inspection and key use require independent review.
  POSIX checks are best effort; symlink races in parent directories and local
  administrator attacks are outside the current security boundary.
- Existing premium review journals and reports remain plaintext in working
  directories. R8 encrypted backups do not change that fact.
- Offline entitlements cannot guarantee revocation, refund enforcement,
  clock-rollback resistance, machine binding or protection from binary patching.

## Regression evidence

Run with `PYTHONPATH=products/desktop`:

```text
python -m unittest discover -s products/desktop/tests -p test_license_issuer_r12.py -v
```

The R12 suite checks real Ed25519/PBKDF-encrypted PKCS#8 issuance against the
**existing R11 verifier**, both premium products, future activation, signature
integrity, wrong algorithm and password, unencrypted and unbounded key files,
invalid UTC times, invalid identifiers, Git-worktree and symlink safeguards,
no-clobber output, POSIX permissions and noninteractive CLI refusal.

Local Python 3.13.5 + `cryptography==46.0.4`: **23/23** focused tests passed
against the independently fetched **exact R11 module blob**
`587e30baa175aa399fe6e08093fbc93be66e66eb`. The full GitHub checkout,
Windows CI, all-six packaged executable smoke tests, and distribution
integrations are **not verified**. This focused evidence does not authorize
production activation or software downloads.
