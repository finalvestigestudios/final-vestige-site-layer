# R13 — operator-side unique entitlement ID registry (PRE-RELEASE)

This sprint adds `products/desktop/license_registry.py` and makes `--registry`
**mandatory for the R12 operator CLI**. The four free applications are unchanged.
The premium customer apps remain fail-closed because `TRUSTED_PUBLIC_KEYS = {}`.
This is **not** a production billing, authorization or distribution system.

## Scope and safe operation

The operator supplies **one persistent, shared, protected, local SQLite database**
for all authorized operators on the **same trusted host**. Do not create a fresh
database for each issuance, share it over network filesystems, or use replicas
without controlled reconciliation. Back it up through a separately approved
process; reconcile backups before restoring. An administrator can still edit,
replace, or copy a database: this registry is **not cryptographically
authenticated** and is not an anti-tamper audit archive.

1. Obtain separate human approval, an externally held encrypted Ed25519 key,
   and a genuinely unused opaque `license_id`.
2. Create a local restricted directory **outside every Git repository**.
   On POSIX use `chmod 700 /controlled/entitlements`. On Windows have a custodian
   verify equivalent NTFS ACLs independently. Do not place it in the website,
   build artifact, CI environment, customer device, synced/public folder or
   cloud download bucket.
3. Run the original issuer with an **absolute** `--registry` path, for example:

```text
PYTHONPATH=products/desktop python products/desktop/license_issuer.py \
  --key /controlled/offline-signing.pem \
  --registry /controlled/entitlements/issuer.sqlite3 \
  --kid approved-key-id-001 --product grants \
  --license-id unique-opaque-id-001 --holder "Authorized Customer" \
  --expires-at 2027-10-28T00:00:00Z \
  --output /controlled/fulfillment/unique-opaque-id-001.fvslicense \
  --confirm-issue
```

The tool prompts interactively for the signing-key passphrase. No automated
passphrase, key, customer license, personal financial record, or checkout token
is stored in the registry. The registry holds an opaque ID, product, public
key identifier, SHA-256 hash of the **absolute output path** (not its plaintext),
reservation timestamp, and later the entitlement's SHA-256 and issue timestamp.

## Fail-closed states and recovery

**reserved**: The database transaction committed before any attempt to sign or
write the customer file. If decryption fails, the output collides, a write is
interrupted, post-write verification fails, or the process crashes, the ID
remains reserved. Do **not** automatically delete or recycle this row. Review
the operator's source/output/evidence before any separately authorized
correction; generate a new unique ID when uncertain.

**issued**: The R12 issuer created and independently cryptographically verified
the file; the registry recorded a SHA-256 of those bytes with the same ID,
product, `kid`, and output path hash. Issued rows cannot be finalized twice.
The tool prints the nonsecret SHA-256 for external fulfillment evidence. Treat
the entitlement itself as sensitive customer material.

SQLite `BEGIN IMMEDIATE` and the primary-key constraint serialize concurrent
local processes; the license ID is unique **across both premium products within
this one database**. A second database can still issue the same ID. The
reservation and customer file are two distinct filesystem resources: this
is *not* an atomic distributed transaction. On an uncertain intermediate state,
stop and investigate instead of retrying blindly.

## Guardrails and limitations

- Registry must be an absolute `.sqlite3` path in a pre-existing non-symlink
  folder outside Git. On POSIX, parent and file must be operator-only, the file
  owner must match the process, and database creation uses mode `0600`.
  Windows ACLs and local administrator attacks require independent review.
- No symlink registry/file or clobber of an existing `.fvslicense`. Hashing of
  finalized file is bounded to 8192 bytes, with regular-file checks.
- The issuer API remains a low-level, testable signing primitive; the
  **interactive CLI** enforces registry reservations. Do not import the low-level
  API into unapproved alternative fulfillment services.
- No live signing keys, test trusted keys, payment integration, premium public
  download, code signing or QD/production approval are created by this sprint.

## Test evidence

```text
PYTHONPATH=products/desktop python -m unittest discover \
  -s products/desktop/tests -p test_license_registry_r13.py -v
PYTHONPATH=products/desktop python -OO -m unittest discover \
  -s products/desktop/tests -p test_license_registry_r13.py -v
```

12/12 **isolated local SQLite registry tests passed** on Linux/Python 3.13.5,
both normally and under `-OO`: duplicate IDs across products, competing
reservations, reserved-after-failure, hash finalization, output mismatch,
symlink protection, path privacy, file permissions, no-clobber, and invalid
inputs. These tests use synthetic data and do **not** prove Windows/NTFS
behavior, full R12 CLI integration, actual packaged EXEs, hosted Actions, or
distribution. The full suite remains mandatory before release.

**Next gate:** obtain a functional Windows runner or run the offline Windows
candidate script on a trusted clean x64 workstation at the exact PR SHA,
review NTFS key/registry ACLs, verify six EXEs and their smoke checks, and
preserve the site's QD approval process. Do not publish or sell these builds.
