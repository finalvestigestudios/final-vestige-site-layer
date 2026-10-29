# R38 — exclusive atomic verifier evidence (internal only)

The six-app offline Windows x64 release gate now **refuses `--report` paths in
or below the candidate `dist` directory**. This check happens before any
`--smoke` execution. Verification JSON belongs in a separate, existing operator
folder, for example `build/candidate-evidence`. The Windows operator script and
CI already use an out-of-tree evidence location.

The gate writes UTF-8 JSON to a new private temporary file in the report
folder, flushes and synchronizes the complete bytes, and uses an exclusive
same-directory hardlink to publish the finished report. It never opens the
final name for incremental writing and never overwrites an old report or a
preexisting dangling symlink. An unsupported hardlink filesystem is an error,
not permission to fall back to unsafe writing. Failed publication removes the
staging file on a best-effort basis and returns a nonzero exit status. Files
are mode 0600 on POSIX hosts; operator ACL management is still required on
Windows. Sensitive caller paths are not copied into new error messages.

This is an **evidence-completeness safeguard only**, not a signed attestation.
It does not eliminate filesystem races or guarantee persistence after sudden
power loss, prove code authenticity, inspect malware, validate premium buyer
entitlements, approve compliance decisions, or authorize release. Retain a
separate independent SHA256 evidence receipt if chain of custody is necessary.

## Reproduction (synthetic/local tests; no Windows EXEs run)

```bash
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p 'test_release_report_r38.py' -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p 'test_release_report_r38.py' -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p 'test_release_report_cli_r38.py' -v
```

Run full source regression, trusted native Windows smoke, malware scanning,
checksums, premium access-control checks and QD review separately. **All six
executables remain unreleased.**
