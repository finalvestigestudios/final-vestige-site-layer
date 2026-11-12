# Labs R368 — bounded Policy Delta NFKC evidence selection (DRAFT, QD HOLD)

**Issue:** #73. **Stack:** R367 draft PR #2130, head `22915e45ee0d53ef1c8bf548a5316de2c975f2db`. All six Windows x64 utilities **unreleased**.

## Defect and change

`policy_diff._local_compatibility_evidence` previously appended **every** NFKC-only substitution pair to `matches`, rendered the per-character compatibility codepoint cue for **every** candidate, sorted the entire list and displayed just the first 16. A legal/policy document with many independent NFKC-only lines could consume needless CPU/memory even though the final audit navigation was capped. This also made the truncation budget a display-only safeguard rather than a working-set bound.

R368 adds `policy_compatibility_selection_r368.earliest_nfkc_pairs` and calls it **only after** `owned_nfkc_hunks` validates original source-line custody and UTF-8 bounds. It preserves the distinct-candidate count and unique-pair/NFC tests, but retains at most **16 physical-coordinate-sorted** source tuples; expensive codepoint details are rendered only for the selected 16. It counts later candidates for a precise omission warning, independent of unordered dict/set traversal. It does **not** rewrite source bytes, SHA-256 fingerprints, money values, policies or compliance decisions. It does not weaken fail-closed malformed-hunk handling.

The mandatory `test_policy_confusable_bounded_selection_r366.py` gate now contains **21 added R368 methods** (14 selector methods, seven renderer/diff integration methods). Its existing normal and `-OO` invocations in **both** Ubuntu and Windows jobs pick up the additions without expanding the already large workflow, weakening permissions, or changing artifact visibility.

## Executed validation, with scope

- Local Linux Python **3.13.5**, exact new selector helper Git blob `ab23ffac30a91c1a6a935fc31394d636c17442da`: **15/15** isolated helper method tests pass under `python -W error`, **15/15** under `python -OO -W error` = **30 focused executions**. The local test file was separately constructed to exercise the same selector behaviors; it is **not** the committed 21-method integration module.
- Independent local synthetic **5,000 NFKC-only candidates** with distinct source coordinates: legacy full-sort output first 16 and new bounded output exactly equal; old and new count 5,000, while new retains exactly 16. Four `PYTHONHASHSEED` settings `0,1,42,368` produced the same selected cue SHA-256 `a7b0afc004f3c34a58c9b4f233bf293e902fcbaef07312615753c195a8d5df2a`. Synthetic fixture contains no private data.
- Four-run minimum on that **isolated** Linux synthetic selector comparison: eager **0.0284 s**, bounded **0.0024 s** (about **11.8x** faster). This is not a Windows, whole-application or production performance claim.
- Syntax/real source integration against complete repo, all pre-existing suite tests, the 21 appended R368 test methods, 22 genuine AES-GCM tests, native Windows x64 builds and signing/Defender/accessibility were **not executed locally**. Do **not** count added integration methods as passed.

## CI and release constraints

Last inherited [R367 workflow #43139110379](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43139110379) failed **before either hosted job recorded a step**. The exact infrastructure root cause is unknown; there is no evidence of a successful Windows build. Owner should inspect Actions billing/spending limits, hosted runner eligibility, and check failure annotations through GitHub UI. R368's exact-head CI result must be separately checked after opening the new draft PR.

**Next highest-impact gate:** restore Ubuntu/Windows step execution, run all inherited desktop source tests including the new 21 R368 cases, full six-app regressions and 22 authentic AES-GCM cases; then perform native Windows 11 x64 six-EXE build, signed/unsigned labeling, PE identity, smoke, Defender, keyboard/screen-reader, SHA-256 and authenticated premium entitlement/download acceptance. Do not distribute the two premium binaries at unrestricted URLs. Independent QD review and founder approval are required before merging, publishing, or presenting any app as downloadable.

**Privacy and safety:** offline/local-first financial data, original source evidence, Decimal-safe money rules and human-only compliance judgments unchanged. No new telemetry, public binary, site publication, or branch protection bypass.
