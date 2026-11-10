# Labs R334 — canonical six-app checksum inventory custody

**Status:** DRAFT / independent QD and founder approval HARD HOLD. Issue #73. No distribution or main-branch changes.

## Acceptance gap

The previous release gate parsed `SHA256SUMS.txt` with ASCII `splitlines()` and an unordered dictionary. Consequently, the gate accepted byte-distinct inventories with CRLF line endings, reordered rows or no final LF even though `build_inventory.py` emits an exact deterministic six-line LF format. The SHA hashes could still match, but the manifest's canonical audit evidence was not enforced.

## Code / contract

- `canonical_inventory_r334.py` checks the complete byte sequence, requires exactly the six `build_inventory.EXPECTED` filenames **in producer order**, 64 **lowercase** hexadecimal characters, two literal ASCII spaces and one final LF per line. No BOM, CRLF, extra/missing rows, Unicode normalization, additional fields or trailing whitespace.
- `release_gate._inventory()` reads through the existing bounded pinned-descriptor `read_checksum_candidate` and invokes the strict parser before the smoke loop. No new network use, entitlement changes or compliance auto-approvals.
- `.github/workflows/desktop-build.yml` places 25 regression methods in **both** source-test and private Windows-build jobs, under normal and `-OO` Python; existing checksums, native Win11 smoke, malware scanning, private premium delivery and QD approval remain separate release gates.

## Locally executed synthetic evidence (2026-11-10)

Linux CPython 3.13.5; temporary/synthetic SHA-only data; no executable was built or launched.

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_canonical_inventory_r334.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_canonical_inventory_r334.py'
```

25/25 PASS in normal mode; 25/25 PASS in optimized mode = **50/50 focused method executions**, zero skips. `compileall` PASS. Exact committed Python parser and test file Git blobs were re-run locally.

Reproduction using the inspected predecessor parsing semantics: all six rows with (1) CRLF, (2) reversed line order, or (3) missing terminal LF were **accepted** previously; all three are **rejected** by R334. These are canonicality failures, **not** demonstrated checksum collisions or malware bypasses.

## Holds / next action

No full repository suite or real Windows 11 x64 EXE acceptance was executed in this local slice. Hosted Actions has failed before step execution, cause not confirmed. Owner: inspect billing/spending limit, workflow eligibility, and runner availability; restore normal and `-OO` full tests including genuine AES-GCM integrations, then conduct private six-app Windows 11 x64 build/smoke, SHA-256/Defender/accessibility checks and premium entitlement verification. Do **not** publish binaries or remove draft/QD/founder HOLD.
