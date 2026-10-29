# R34 — independently pinned GrantAudit evidence inventory

**Development-only, no Windows release authorization.** GrantAudit Studio Pro
still requires a human reviewer. This enhancement extends R33's read-only
offline verification with an *optional out-of-band trust anchor*.

## Why an external pin matters

R33 verifies that the current claims, ledger, budgets, and two reports
exactly agree with a plaintext SHA-256 manifest. An actor able to rewrite
the entire evidence directory and its manifest can make forged content
appear internally consistent. R34 optionally compares the **exact original
manifest bytes** against a **separately recorded SHA-256 checksum**.
A rewritten manifest will then fail even when all five new file hashes agree.

**The pin must be captured at trusted publication time and retained outside
the package** in a separate, access-controlled audit register or immutable
record. Reading the checksum from the suspect package at verification time
does **not** establish an independent trust anchor. This is not a digital
signature, a reliable timestamp, an identity assertion, or payment approval.

## Operator procedure (source checkout; no packaged binary yet)

**At publication, while the complete R32 bundle is under trusted control:**

On Windows PowerShell, immediately after export:

```powershell
$manifest = 'C:\Evidence\grant-evidence-EXAMPLE\evidence-manifest-EXAMPLE.txt'
$publishedSha256 = (Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant()
# RECORD $publishedSha256 and the bundle identifier *outside the bundle*
# in your separately controlled audit register. Do not store the only copy
# in the bundle or replace the recorded checksum later.
```

On Linux: `sha256sum -- /trusted/bundle/evidence-manifest-EXAMPLE.txt`.
Record the first (64-character) lowercase hex field separately.

**At subsequent verification, retrieve the previously recorded checksum
from the independent trusted register; do not recalculate it from a suspect
copy.** From the repository root:

```powershell
$env:PYTHONPATH = 'products/desktop'
$savedPin = '<64 lowercase hex characters from separately controlled register>'
python -m fvs_suite.grant_verify --expected-inventory-sha256 $savedPin 'C:\Evidence\grant-evidence-dir' 'C:\Source\claims.csv' 'C:\Source\ledger.csv' 'C:\Source\budgets.csv'
if ($LASTEXITCODE -ne 0) { throw 'GrantAudit evidence is invalid; manual investigation required' }
```

Linux:

```sh
PYTHONPATH=products/desktop python -m fvs_suite.grant_verify \
  --expected-inventory-sha256 "$SAVED_PIN_FROM_TRUSTED_REGISTER" \
  /evidence/grant-evidence-dir /source/claims.csv /source/ledger.csv /source/budgets.csv
```

The pin is exactly 64 **lowercase ASCII** hexadecimal characters with no
whitespace; malformed pins fail closed. Original CSV basenames and the
claims/ledger/budgets argument order remain mandatory.

Exit 0 with **`CONSISTENT (PINNED)`** confirms that the five *current*
files match the current manifest *and* that the manifest matches the
independently retained SHA-256 anchor. Exit 0 with
**`CONSISTENT (UNPINNED)`** is an explicitly weaker self-consistency result
(for callers not providing the new option). Exit 1 / **`INVALID`**
requires manual investigation. Messages omit source paths, data and raw
pin values. None of these statuses constitutes financial approval.

## Fail-closed scope and limitations

- Reuses the existing R33 path/link/hardlink checks, bounded source/report
  hashing, 64 KiB inventory cap and post-check re-read; no network or
  additional cryptographic dependency.
- Tests cover deliberate same-size source edits, full coordinated
  file-plus-manifest rewrites, invalid pins, unchanged read-only behavior,
  CLI status and output privacy, and simultaneous inventory modification.
- An independent pin protects against *undetected manifest replacement only
  as long as the separately stored checksum remains trustworthy.* A
  privileged actor who can rewrite both the evidence and trusted record,
  or a trusted operator who pins already-forged bytes, defeats this control.
- This is a point-in-time check. It does not authenticate the original
  creator, prevent future edits, guarantee clock accuracy, preserve
  confidentiality through disk encryption, or automatically assess grants.
- The pin is a digest rather than a password, but command-line arguments
  may be visible to local observers. Do not supply secret tokens or
  customer data as the pin.
- Neither premium file distribution nor WordPress/QD approval is modified.

## Local regression evidence and outstanding release gates

Run both modes:

```sh
PYTHONWARNINGS=error PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_grant_anchor_r34.py' -v
PYTHONWARNINGS=error PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_grant_anchor_r34.py' -v
```

The 17 targeted tests passed locally in both modes using the actual
committed helper/verifier source and exact committed R33 dependencies
reconstructed for the isolated local checkout. This does **not** replace
a complete repository test run, Windows x64 build, GUI smoke, AV scan,
checksum inspection, premium entitlement enforcement or site QD review.
Keep all six EXEs unreleased until every release gate passes.
