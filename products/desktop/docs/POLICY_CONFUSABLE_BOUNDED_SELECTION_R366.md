# R366 — bounded Policy Delta look-alike citation selection

**2026-11-11 PST / 2026-11-12 UTC · DRAFT · QD + founder HOLD · Not approved for release**

## Problem and implemented correction

The R365 preflight caps optional direct-call Policy Delta inputs at 100,000 source row tuples and 8,388,608 Unicode codepoints. However, the look-alike renderer still constructed an in-memory **formatted citation tuple for every unique matching line pair**, sorted the entire match list, and finally displayed only 16 citations. A densely changed policy could therefore retain tens of thousands of unnecessary output tuples.

The real renderer now uses _retain_earliest_pair to keep only the **16 smallest (hunk number, before line, after line) citations**, incrementing an independent exact match count for the omission notice. Because the set-intersection candidate iteration depends on Python hash-seed order, merely taking the first 16 candidates would be incorrect; ordered bounded selection retains the same earliest physical citations across hash seeds. It does **not** discard later matches before counting their omission.

This reduces the additional **selected-output tuple storage** from O(number of matching pairs) to O(16), not the total renderer memory: existing source indexes and budget-validated staging still depend on the bounded input size. Neither source evidence nor byte fingerprints are modified. Ambiguous duplicates remain unpaired, malformed late hunks still suppress all optional review cues, and this report is navigation for independent human policy review, not legal or compliance interpretation.

## Executed local evidence

Isolated Linux Python 3.13.5 environment, synthetic inputs, locally reproduced relevant modules (not a full repository checkout):

- New R366 test module: **15/15 PASS** under normal Python -W error and **15/15 PASS** under optimized Python -OO -W error.
- Combined R366 tests plus nine existing R365 renderer integration cases: **24/24 PASS** normal and **24/24 PASS** optimized, **48 focused case executions** total (including the 30 new-case executions above).
- The 5,000-candidate helper stress tests assert selection storage never exceeds 16 tuples and that reverse/random ordering yields the correct earliest citations.
- Independent subprocesses with PYTHONHASHSEED=0,1,42,366 produced the same SHA-256 of the 100-pair review output: ec3a2570f591594f9d2c4987bcdb6ff2d5d3393c68dccb5629f8ed5dd0c15b67, with exactly 16 displayed cues for each.
- Syntax compilation of isolated Python source/tests succeeded.

**Evidence limit:** The local test modules were recreated from reviewed GitHub source rather than executed from a full exact-head repository checkout. The full inherited regression suite, actual Windows x64 build, the complete 22 genuine AES-GCM cases, source validators, Defender, screen reader/keyboard acceptance and premium entitlement validation were **not executed**. Do not represent these local checks as hosted CI or release acceptance.

## CI wiring, privacy and next gate

R366 is wired into the existing desktop workflow on both Ubuntu and Windows, normal and -OO optimized interpreters, with explicit Windows exit-code checks. Workflow source size is **212,068 bytes**, below the current finite **224 KiB / 229,376-byte** validation ceiling. The workflow and prior source validators must be executed on runners; local inspection is not a passing hosted check.

All six Windows x64 desktop applications remain **unreleased**: free LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk; premium GrantAudit Studio Pro and ProcureGuard Studio Pro. Local-first privacy, exact Decimal financial calculations, deterministic audit trails, human decisions and gated premium artifacts remain required. No production or WordPress changes, binary uploads, public premium download links, auto-merge, or bypass of QD/founder approval.

**Next highest-impact step:** Resolve the persistent 0-ms GitHub Actions runner failure, run exact-head Ubuntu/Windows R366 and inherited desktop regression gates including all 22 genuine AES-GCM tests, then native Windows 11 x64 packaging, PE/smoke, SHA-256, Defender, accessibility, and premium entitlement/download verification before requesting independent QD and founder approval.
