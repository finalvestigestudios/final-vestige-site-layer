# Final Vestige Labs R382 — Issued-license output FD custody

**DRAFT / NO MERGE / NO EXECUTABLE RELEASE / QD + founder HOLD.** Issue #73.
Base: R381 draft, not production main. Applies only to the *operator-side*
offline premium license issuer used for GrantAudit Studio Pro and
ProcureGuard Studio Pro. Never bundle issuer, registry, signing key or PEM
in a desktop executable. No customer inputs, network, entitlement release,
financial engines, site or WordPress are changed.

## Reproduced risk / corrective scope

Prior issuer wrote one signed .fvslicense via os.open(O_EXCL) and
os.fdopen(descriptor, "wb"). If fdopen raised, the raw descriptor was not
reliably closed. Raw OS creation/write/flush errors could retain confidential
operator paths in public exceptions. There was no explicit guard against
zero-progress/short writes or a post-write pathname-to-descriptor witness.

The replacement license_output_guard.create_issued_license:
- accepts exact bytes, 1–8,192 bytes, matching the existing verifier cap;
- uses one owner-only O_CREAT | O_EXCL write descriptor with no-follow where
  available; existing destinations and symlinks are never overwritten;
- handles short writes, rejects zero/invalid progress, fsyncs once, checks
  exact final length and pathname/descriptor identity, reparse flags,
  regular-file identity, one hardlink, and POSIX owner-only permissions;
- always closes an owned FD (including fstat, write, fsync and poststat
  failures), and raises fixed messages only after private handlers have exited;
- never retries an uncertain write or deletes a partially created output.
  Reservation stays under manual investigation and must not auto-finalize;
- leaves existing Ed25519 signing, R11 independent verifier, in-memory
  signed-payload SHA-256 receipt and the registry's manual authorization
  unchanged.

## Reproducible executed evidence (local Linux; not hosted CI)

Isolated helper + committed regression test sources, matched to their exact
GitHub blob IDs before reporting:
- license_output_guard.py: 9bec658c8cd3615cf9dab6423d49eaf524d8d13c
- tests/test_license_output_guard_r382.py:
  7972cf5109cbf6e889bf08459c517455368b6039
- Python 3.13, cryptography 46.0.4; no real credentials.
- Run from products/desktop with PYTHONPATH=products/desktop:
  python -W error -m unittest discover -s products/desktop/tests
    -p 'test_license_output_guard_r382.py'
  python -OO -W error -m unittest discover -s products/desktop/tests
    -p 'test_license_output_guard_r382.py'
- Result: **22/22 PASS** normal, **22/22 PASS** optimized
  (**44 focused method executions**); compileall PASS.
- Tests include real synthetic Ed25519 sign/verify for BOTH premium product
  identifiers, signature tamper denial, exact 8,192/oversize limits,
  collision/symlink no-overwrite, OS error canaries, FD close/fstat cleanup,
  partial and zero writes, fsync, in-place/path substitution detection,
  Windows reparse metadata simulation, private permissions, no auto-delete,
  and no console output. No key material was committed.
- Workflow adds four gated test invocations:
  Ubuntu and Windows, normal and optimized.

## Important evidence boundaries

The source/test pair was run in an isolated local tree. Its committed blobs
match the executed bytes. **The modified complete license_issuer.py was not
run in the full repository context, and neither the R12/R13/R16 integrated
Ed25519 tests nor all six source engines and 22 genuine AES-GCM cases were
executed on this exact branch.** No hosted Windows execution, PyInstaller
artifact, executable scan, keyboard-accessibility or real entitlement-delivery
verification is claimed. Synthetic Windows reparse tests do NOT establish
native Windows reparse protection or ACL policy.

TOCTOU after descriptor close, parent-directory replacement, and privileged
same-user races cannot be eliminated solely by the post-write witness. The
issuer's separate verifier and manual registry finalization are still
required. Windows native failure behavior remains a release blocker.

## Safe release gates / next

1. Resolve GitHub Actions allocation failures (recent Ubuntu and Windows jobs
   have zero recorded steps; inspect check annotations, billing/spending cap,
   runner eligibility). Re-run exact R382 HEAD.
2. Run whole exact-head suite, real R12/R13/R16 issuer+registry+verifier
   integration, genuine Ed25519 and 22 AES-GCM cases, including Windows x64.
3. Build *six distinct Windows x64 EXEs*, verify real PE/smoke/Defender,
   accessibility, SHA-256 manifests and premium license/controlled downloads.
4. Independent QD review AND founder approval before any site update,
   artifact sharing, premium fulfillment or production merge.

All six applications remain **UNRELEASED**. This is code and regression
coverage, not release authorization.
