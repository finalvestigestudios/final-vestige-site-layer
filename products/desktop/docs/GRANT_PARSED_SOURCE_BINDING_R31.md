# R31 — Bind GrantAudit evidence manifests to the parsed CSV snapshot

**Status: source-only, pre-release, human review required.** This is not
an attestation of grant eligibility, an approval, or a signed audit document.

## The corrected failure mode

The R30 reader supplies a verified in-memory CSV snapshot for financial parsing.
Before R31, the GrantAudit manifest re-opened each source path and hashed the
bytes *at manifest time*, which might not be the bytes that drove its actual
reconciliation. A same-length change between parsing and hashing could result
in a superficially valid manifest of a **different** financial statement.

R31 binds the final manifest inventory to the SHA-256 digest of the **exact
source bytes** fed to CSV parsing. For both legacy and linked-allocation
GrantAudit modes, every input (claims, ledger and budgets) is included.

- `engine.table(include_digest=True)` returns the original parsed rows and a
  SHA-256 of its validated raw snapshot. With `include_headers=True`, it
  returns `(rows, headers, digest)` instead. Old callers retain their
  original return contracts when `include_digest` is omitted.
- The linked allocation path carries the already-parsed claims digest across
  the engine boundary; standalone callers without pre-parsed claims produce
  their own claim snapshot. Supplying pre-parsed claim rows *without* a digest
  now fails closed.
- `engine.manifest(..., expected_inputs=...)` delegates to
  `manifest_guard.inventory_text(..., expected_input_digests=...)` which
  rejects missing/extra/invalid source hashes, then rejects any evidence
  input whose current SHA-256 differs from the digest actually parsed.
- Existing deterministic ASCII basename-tab-SHA256 manifest rows, byte
  caps, symlink/alias defenses, no-overwrite atomic text publication,
  privacy-preserving errors, human-review wording and Decimal arithmetic
  are unchanged. Existing direct manifest callers lacking expected hashes
  still receive a **descriptive** inventory, not a provenance-bound one.

## Limits and necessary release gates

This is a **content consistency check** on disk before publication, not
digital signing, filesystem locking or a transaction across three output
files. The source files can change after the final inventory recheck;
generated exception/budget reports may remain when inventory generation
fails; and hostile writers could race a later operation. It does not
replace secure evidence vaults or human audit review. The content digest
does not record proof of who supplied the input.

Tests use synthetic CSVs; none of the premium binaries are publicly
accessible. Prior to release, execute the full repository test suite on
a trusted checkout, build all six Windows x64 launchers, smoke/AV/verify
and checksum their artifacts, independently review premium access and
complete the site's QD approval workflow.

## Tests and files

- `tests/test_snapshot_manifest_binding_r31.py`: real filesystem digest
  equality, same-size mutations, replacement, key coverage, malformed
  hashes and legacy descriptive manifest behavior.
- `tests/test_grant_manifest_binding_r31.py`: both legacy and linked
  GrantAudit engines, API compatibility, each of the three input mutation
  cases in each mode, and standalone linked-call fail-closed behavior.
- `.github/workflows/desktop-build.yml` runs both test modules with
  optimized Python on Linux plus the full regression suite on both jobs.

No source upload, telemetry, license change, payment decision, publication
or production-branch mutation is introduced.
