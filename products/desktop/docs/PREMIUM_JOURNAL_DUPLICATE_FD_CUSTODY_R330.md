# R330 — Premium journal duplicate-descriptor cleanup on failed reader setup

**Status:** DRAFT / #73 / independent QD + founder **HARD HOLD**. No production merge, executable release, premium entitlement change, or automated compliance approval.

## Reproduced defect and scope

The common premium `journal_io.read_regular_bytes` previously used `with os.fdopen(os.dup(descriptor), "rb")`. If `os.dup` succeeded and `os.fdopen` (or stream context entry) raised, Python never entered the `with` block; the duplicated raw file descriptor remained open. An orphaned descriptor retains access to a private report or review journal and can accumulate on repeated failed reads. This is a **resource-lifetime / privacy hygiene defect**, not evidence of a customer leak, exploitation, or remote code execution.

## Code

- `fvs_suite/journal_fd_read.py`: new small owned-duplicate reader. It limits the read to `limit + 1`, preserves the original pinned descriptor, never reopens a pathname, and explicitly closes its duplicate if `fdopen` or `__enter__` fails. On ordinary successful reads, the stream context closes its owned descriptor.
- `fvs_suite/journal_io.py`: calls the helper inside the existing descriptor/path/size validation and OS-error redaction boundary. No changes to write/append logic, hash witnesses, Decimal arithmetic, review decisions, entitlement, website, or CI gate policy.
- `tests/test_journal_fd_read_r330.py`: **11 isolated regression tests** on normal reads, overflow, invalid limits, failed `dup`, failed `fdopen`, entry/read exceptions, privacy-safe non-path reopening, and original-FD preservation.
- `tests/test_journal_fd_read_integration_r330.py`: **3 full-suite integration tests**, including private-path-redacted public API failure and closure witness. **Not executed locally** without a complete private checkout.

## Executed evidence — 2026-11-10

Linux Python in an isolated temporary tree, exact helper/unit-test text proposed in this PR, synthetic data only: **11/11 standard PASS and 11/11 `-OO` PASS (22 passing method executions), zero skips**, Python compilation PASS. A separate fault-injection demonstration ran the exact old `os.fdopen(os.dup(fd))` expression: on injected `fdopen` error its duplicate survived `fstat`. The new helper closed its duplicate on the same error while keeping the original usable. No real financial records, network calls or customer data were involved.

**Not verified:** the 3 public-API integration methods; complete original private tree; Windows host; hosted CI; 22 genuine AES-GCM integration cases; six actual Windows x64 binary smokes, Defender, accessibility and protected premium distribution. Prior hosted run [#42820432995](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42820432995) concluded failure with both jobs lacking execution steps; infrastructure cause unknown.

## Trusted full-checkout replay

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_fd_read_r330.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_fd_read_integration_r330.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_fd_read*.py'
python products/desktop/scripts/offline_source_gate.py
```

**Next priority:** restore CI runner eligibility (owner: inspect Actions billing/spending, workflow permissions and runner allocation), execute full source tests + all 22 genuine AES-GCM cases with zero skips, then private Windows 11 x64 acceptance of all six utilities (build, smoke, checksums, Defender, keyboard/screen reader, entitlement gating). Independent QD and founder approval are necessary before merge, publication or distribution. All six remain unreleased.
