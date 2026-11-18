# Labs R524 — Native UTC review clock custody

**DRAFT / QD HARD HOLD.** Tracks [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on [R523 draft #3008](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3008), not `main`. All four free and two premium Windows x64 utilities remain **unreleased**.

## Defect, scope, impact

Both premium products use `fvs_suite.review_chronology` to assess ordering of hash-linked, **human-authored** review records. The source previously used `isinstance(value, datetime)` for caller-supplied previous/clock values and called `.utcoffset()` / `.astimezone()` on them. An attacker-controlled `datetime` subclass could forge a future current clock or a past previous event and therefore bypass a chronological rejection in **direct Python API calls**. A native datetime carrying arbitrary custom `tzinfo` could execute user code, raise a private exception, and leak source-specific details.

This change rejects nonnative datetime instances and nonnative timezones **before calling** timezone methods. Only `type(value) is datetime` with `type(value.tzinfo) is datetime.timezone` reaches comparison. We preserve zero-offset native clocks (including explicitly named UTC); native fixed-offset historical previous records still convert to UTC; non-UTC *new* clocks still fail. Canonical persisted string parsing and immutable hash-chain semantics are unchanged. These checks do **not** make the machine's clock trusted or constitute an electronic signature.

## Reproduction and code

- Exact unmodified R523 `review_chronology.py` was loaded from Git blob `a837df908cc4f5d40da7d05cd1d81d51a816eb20`. A synthetic 16-method test harness showed **4 FAIL and 2 ERROR**: two forged subclasses could evade chronology checks, and two custom `tzinfo` cases invoked a callback raising `PRIVATE-CUSTOMER-CLAIM-123`.
- [Updated shared premium chronology guard](../fvs_suite/review_chronology.py) makes those paths fail closed with existing constant, privacy-safe `ValueError` messages and no linked exception chain.
- **16 regressions** appended to existing already-pinned [R51 test module](../tests/test_review_chronology_r51.py), with no new command or source-manifest modification. They exercise forged clocks, overridden `astimezone`, hostile tzinfo with a call counter, UTC accepted, earlier clocks rejected, compatibility with historical native nonzero offsets, fractional chronological rollback, and deterministic error privacy.

## Executed evidence and boundary

- Local Linux CPython focused **16/16 PASS normal**, **16/16 PASS `-OO`**, **32/32 executions**, 0 skips; `py_compile` PASS.
- Tested production code's Git blob is `65a1ed17acc6a74e40d02796b1000e54d9a423cb`, identical to the updated repository production file blob. The focused harness exercised functionally identical 16 scenarios; the complete committed R51 test module and repository-wide 416-command source matrix **were not executed**.
- No premium journal, customer data, CSV input or on-disk evidence was altered. No financial arithmetic, payment authorization, compliance decision, telemetry, site/catalog switch, binaries, entitlement issuer or access controls changed.
- **No Windows x64 build, six-image launch, malware scan, GUI/accessibility acceptance, checksum, signing, live free download or paid entitlement test has passed here.**

## Review/CI blockers and next steps

GitHub Actions for [R523](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3008) repeatedly failed before step execution; see [runner blocker #75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75). Check **this R524 head** independently. A GitHub administrator should examine Actions billing/quotas, repository workflow permissions and runner eligibility; prove the smallest job can start before rerunning the 416-command matrix and Windows build/release checks. Verify the connected test suite (R51, R395 and both-premium integration), independent QD review, and explicit founder approval before any merge or release. Do not announce/download premium artifacts publicly.
