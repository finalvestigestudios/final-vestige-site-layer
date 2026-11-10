# R318 — Compile genuine premium AES integration test modules from source

**Status:** DRAFT, independent QD + founder HOLD. No release, publication, payment,
premium-link, WordPress, or production-branch changes.

## Defect / risk
The R317 22-case mandatory AES-GCM gate witnessed the disk identity and SHA-256
of four authentic test modules, but then used `unittest.TestLoader.discover`.
Python's timestamp/size-based `__pycache__` can still load older `.pyc` for
newer source having an identical byte count and recorded mtime. Consequently
the verified `.py` source could contain a failing critical test while older
passing bytecode ran. R317's filesystem source witness cannot detect that
discrepancy. This affects **test evidence integrity**, not AES-GCM cryptography.

## Engineering change
- `scripts/source_only_test_loader_r318.py` compiles verified `.py` bytes
  directly with `compile(..., dont_inherit=True)`, executes in a fresh
  module, then `unittest.TestLoader.loadTestsFromModule` enumerates the tests.
  It does not import the target from `.pyc` or delete/modify cache files.
- `vault_crypto_gate_r316.py` substitutes the source-only loader for
  `discover`. Its R317 per-file source/directory custody checks, four frozen
  module names, 22 required method IDs, failure/skip refusal, fixed redacted
  errors, and source-only/HOLD result are unchanged.
- `tests/test_vault_crypto_source_loader_r318.py` adds seven isolated
  synthetic regressions and one **mandatory full-checkout gate integration**
  test. The latter fails closed when the R316/R317 gate is missing or broken.
- No engine business calculations, entitlement flow, financial input handling,
  compliance decisions, Tk UI, or downloadable file changed.

## Local evidence and exact reproducible commands
Linux CPython 3.13.5; synthetic in-memory unittest cases in a temporary folder;
no real financial data or customers. `git hash-object` of locally executed
helper `49e2a99e3da72d4b741f8be006a554573f97be37` and
regressions `888ba2937c71eee4f28b4e7886896ac9cab46420` matches GitHub
committed blobs.

- **7/7 synthetic methods PASS** with `-W error`.
- **7/7 synthetic methods PASS** with `-OO -W error`.
- **14 total passing isolated method executions**. `py_compile` PASS.
- Reproduced real predecessor loader false positive: Python
  `unittest.TestLoader.discover` returned success from timestamp/size-compatible
  cached *passing* bytecode, while changed disk source contained
  `self.fail('PRIVATE BANK DATA')`. The new loader runs the disk source and
  fails it. Also confirmed stale *failing* bytecode cannot mask passing source.
- One additional **full R316/R317 gate integration method was committed but
  NOT executed locally**, because the private full checkout is unavailable in
  the local Linux runner. In the complete repo it is automatically discovered
  and cannot skip.

To run **all 8 methods and 22 actual AES integration cases** from a trusted
complete private checkout with cryptography installed:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_crypto_source_loader_r318.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_crypto_source_loader_r318.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_crypto_gate_r316.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_crypto_gate_r316.py'
PYTHONPATH=products/desktop python -W error products/desktop/scripts/vault_crypto_gate_r316.py
```

The existing desktop CI workflow already runs a complete source discovery
in normal and optimized modes; R318's integration test participates there.
**Do not report the 22 mandatory actual AES cases as passed until they run.**
Cached *dependencies*, interpreter integrity, and races between witness reads
are outside this source-only mitigation.

## Blocking release gates / next action
Prior [R317 Actions #42733546000](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42733546000)
completed failure: both source and Windows jobs recorded zero execution steps.
The root cause is not proven. Owner should inspect GitHub Actions billing/spend
restrictions, workflow permissions and runner allocation, then obtain actual
Ubuntu + Windows logs. Alternatively run the commands above in a trusted
complete checkout with `cryptography`. Next: privately build and smoke all
six Windows 11 x64 EXEs, capture SHA-256 and Defender/EDR/accessibility
evidence, and validate entitlement-gated premium delivery. **No merge or
release without independent QD and founder authorization.**
