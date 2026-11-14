# Final Vestige Labs R432 — private SpendMap Unicode exception custody

**Status: DRAFT / NOT FOR RELEASE.** Issue #73. Feature branch stacked on
R431 draft #2508, not production `main`. `release_authorized=false`.
The six Windows x64 utilities remain unreleased. Independent QD review and
explicit founder authorization are required before merge, build distribution
or site publication. No executable, entitlement, checkout, license, download
or WordPress changes are included here.

## Actual defect and impact

Three independent SpendMap verifier paths could retain synthetic private
financial data in Python exception objects even if the displayed error was
generic:

1. `spend_label_verify._label_digest` raised a generic `ValueError ... from
   None` **inside** a `UnicodeError` handler. Python still populates the
   public exception's `__context__`; `UnicodeEncodeError.object` holds the
   original vendor label. This is reachable via the direct source-label
   verification API with an unpaired surrogate in a digest-required label.
2. `spend_report_envelope.NativeSpendCsvDigest.write` let the raw
   `UnicodeEncodeError` escape when given a non-UTF-8-encodable text cell.
   That exception can contain the entire untrusted financial report cell.
3. `spend_evidence_verify.verify_membership` converted malformed report
   Unicode/CSV errors to `ValueError ... from None` **inside** the exception
   handler. `UnicodeDecodeError.object` can contain the complete private
   report byte snapshot in its hidden `__context__`.

R432 records a failure flag and raises the fixed, nonsensitive `ValueError`
**after leaving each handler**. It does not echo values or paths in
messages; `__cause__` and `__context__` are empty for these paths.
This limits incidental exposure through exception-chain logging; it does
not promise to sanitize arbitrary debugger traceback frame locals, or
anomalous exceptions from unrelated modules.

Unpaired Unicode surrogates cannot appear in a valid UTF-8 CSV. The label
and writer cases defend the direct Python APIs; malformed report bytes
exercise the actual offline verifier path. This is a preventative privacy
hardening, not evidence of a customer breach.

## Changed, committed source

- `fvs_suite/spend_label_verify.py`: throw after the UTF-8 failure handler.
- `fvs_suite/spend_report_envelope.py`: same for the native report byte
  digest writer; invalid values never mutate its hash or byte count.
- `fvs_suite/spend_evidence_verify.py`: raise after the report decode /
  strict CSV reader handlers to avoid embedded raw report bytes in context.
- `tests/test_spend_private_unicode_custody_r432.py`: 16 focused unit
  methods on source-label evidence, digest and canonical CSV identity.
- `tests/test_spend_private_report_errors_integration_r432.py`: five
  real-engine source/export/verifier tests, including actual malformed
  UTF-8, unpaired surrogate and truncated quote report bytes.
- `.github/workflows/desktop-source-evidence-r385.yml`: Ubuntu 24.04 and
  Windows source-evidence runs, normal and `python -OO -W error`, plus
  inherited R430/R431 source verifier regressions.

## Precisely executed evidence (local, not full repository)

Linux isolated Python:
```sh
PYTHONPATH=products/desktop python -W error -m unittest discover \
  -s products/desktop/tests -p test_spend_private_unicode_custody_r432.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover \
  -s products/desktop/tests -p test_spend_private_unicode_custody_r432.py
```

Both modes completed **16/16 PASS**, total **32/32** focused executions,
with synthetic data. Locally reconstructed package files were verified
against their exact committed Git blob IDs: `spend_label_verify.py`,
`spend_report_envelope.py`, and the R432 unit test file. The changes
also passed Python source compilation. A controlled pre-fix run using
the exact R431 versions (also Git blob verified) produced **4 test
failures out of 16**, establishing that the tests detect the defect.
The detailed source privacy test creates no user files or network traffic.

**Not executed locally:** all five new full-engine integration tests,
the existing six-engine financial/cryptographic/entitlement regressions,
the Windows and Ubuntu hosted runners, and genuine Windows x64 binaries.
Do not count committed integration tests as passing.

## Safety invariants and next gate

This patch does not change Decimal computations, vendor matching, source
SHA-256 evidence, bounded label preview, CSV byte shape, license entitlements,
review decisions, local file ownership or the six separate launchers. It
never approves a claim, procurement exception, payment or compliance decision.

The prior exact-head R431 [source job](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43625190354)
and [Windows build job](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43625190353)
failed before recording execution steps or runner names. Root cause of
hosted scheduling is still unconfirmed. Check repository/org Actions
permissions, account billing/spending limits and GitHub runner eligibility;
then rerun the **exact R432 PR head** and require real success on both
operating systems, including this patch's five integration cases.

After source CI is genuinely green, validate each actual Windows x64 binary
on native Windows: executable launch/offline smoke, Defender scan, exact
SHA-256/versioned manifest, accessible keyboard paths, privacy and failure
handling, full financial/integrity suites, and separate access-controlled
premium download entitlement. Release stays on HOLD until independent QD
review and explicit founder approval.
