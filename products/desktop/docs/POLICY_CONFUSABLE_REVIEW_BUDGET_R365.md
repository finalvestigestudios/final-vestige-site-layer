# R365 — bounded Policy Delta Desk look-alike review navigation

**2026-11-11 · Draft / QD and founder HOLD · No release authorization**

## Defect and scope

The optional Latin/Cyrillic/Greek look-alike evidence renderer previously
accepted direct Python hunk collections totaling up to 50,000 physical source
rows **on each side**, and could build and retain skeleton indexes for almost
every 4,096-character line. This permitted roughly 400 million source
codepoints across both sides in the extreme, far beyond a small review hint,
even though the eventual human-readable output is capped at 16 pairs.
The normal file ingestion path has separate restrictions; this sprint
specifically hardens **untrusted direct helper calls**.

Before building any per-line skeleton indexes, the real
`render_local_confusable_evidence` entry point now validates the **entire**
collection using `within_confusable_budget` and rejects it without partial
hints if either inclusive aggregate limit is exceeded:

- **100,000 source row tuples** across both before and after sides combined.
- **8,388,608 Unicode codepoints** across all original source strings,
  including overlong lines that cannot be displayed or paired.
- Existing **50,000 hunk** ceiling stays in place.

The preflight rejects non-native container types, unsafe key types and
malformed row representations without invoking custom dict/list/tuple methods
or rendering source contents. Budget failure returns an empty optional
navigation string. Original text files, hashes, unified diffs and independent
human interpretation are not rewritten or suppressed. This is a defensive
memory/CPU budget for in-memory inputs, **not** a proof that direct-call
source records are authentic or a cap on already-allocated caller memory.
It counts Python Unicode codepoints rather than UTF-8 source bytes.

## Local test evidence (isolated Linux Python)

The standalone `policy_confusable_budget_r365.py` and direct-budget test
module were locally executed with synthetic data:

- `python -W error -m unittest discover -s tests -p test_policy_confusable_budget_r365.py`: **20/20 passing**.
- `python -OO -W error -m unittest discover -s tests -p test_policy_confusable_budget_r365.py`: **20/20 passing**.
- **40 focused case executions** total. Boundary inclusive/exclusive
  checks, aggregate side/hunk accounting, hostile subclasses, Unicode,
  long uncitable lines and no source mutation are represented.
- Exact local Git blob hashes:
  - `policy_confusable_budget_r365.py`:
    `d312ed251730b37ac72a401f963970b7839d63da`
  - `test_policy_confusable_budget_r365.py`:
    `7930d914e85d917695dd6820a44d3a3809c72441`

The **nine new real-renderer integration methods**, inherited R182/R364
regressions, full six-utility engine, four workflow source validators, all
22 genuine AES-GCM cases, native Windows build/PE checks, accessibility,
Defender scans, premium entitlement and full download verification **were
not run in the local test environment**. Mandatory normal/optimized Ubuntu
and Windows Actions test calls are committed, but must actually execute.
The updated workflow is **211,363 UTF-8 bytes**, below the finite
224 KiB (229,376-byte) ceiling. Do not call queued/failed CI passing.

## Safety, approvals and next acceptance step

All six apps (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy
Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro) remain
unreleased. No production merge, executable distribution, public premium
artifact URL, telemetry, automatic financial/compliance approval or live
WordPress publication. The branch stacks only on R364 draft and remains
subject to independent QD review and founder approval.

**Highest-impact next step:** Restore GitHub Actions runner assignment, then
run the exact-head R365 Ubuntu/Windows mandatory gates plus complete inherited
desktop and 22 genuine AES-GCM integrations. Validate Windows 11 x64
packaging, actual EXEs, file SHA-256, Defender, accessible keyboard/screen
reader use and premium download access controls before any release request.
