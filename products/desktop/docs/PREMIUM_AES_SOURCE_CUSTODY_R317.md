# R317 — Premium AES integration source custody (DRAFT / QD + founder HOLD)

Tracks [six-app desktop issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73), stacked on R316 draft PR #1814, **not production main**. All six Windows x64 utilities remain unreleased.

## Acceptance defect addressed

R316 required 22 genuine AES-GCM integration test methods to exist and execute without skips, but its test loader did not bind the discovered Python modules to unchanged source-file identities. A test module could be modified or replaced after preflight, including with byte-identical contents, and the gate could still report PASS. Python also caches imported modules in `sys.modules`.

R317 changes the **source-only** AES integration gate at `products/desktop/scripts/vault_crypto_gate_r316.py`:

- Snapshot each required test module with SHA-256 and `lstat` device/inode/mode/size/mtime_ns/ctime_ns; reject symlinks, nonregular files, empty files, and modules over 128 KiB.
- Verify all four modules before execution, again before individual import, after discovery and test run, and at the end of the batch. A source replacement, even byte-identical, forces HOLD.
- Evict a same-named cached test module before discovery; check that the imported module's file path resolves to the expected test file. Retain original zero-skip, redacted-error, fixed 22-case contract.
- No changes to AES-GCM algorithms, financial input handling, Decimal arithmetic, entitlement/licensing, review decisions, production, or WordPress.

**Boundary:** These snapshots are observations, **not** atomic file locks, not proof against transient changes between observations, and not attestation of Python bytecode caches or imported dependencies. Never mistake a source PASS for Windows executable acceptance or QD approval.

## Locally executed evidence (2026-11-09, Linux CPython 3.13.5)

Synthetic standalone fixtures only; no customer data. Source/test bytes verified as exact committed Git blobs:

| Gate | Normal `-W error` | Optimized `-OO -W error` |
| --- | ---: | ---: |
| R316 existing adversarial synthetic tests | 10/10 PASS | 10/10 PASS |
| R317 additional source-custody tests | 7/7 PASS | 7/7 PASS |
| **Total focused method executions** | **17/17 PASS** | **17/17 PASS** |

`python -m py_compile` passed for the changed gate and R317 regression module. R317 added seven methods: stable source twice, preloaded same-path module substitution, in-test source rewrite, byte-identical atomic replacement, later-module mutation, privacy/error suppression, and symlink rejection. **Three R317 methods failed, as expected, against the exact unmodified R316 predecessor blob** `5146b81b0e9d689f6bc54272fd2a3a765eab99b7`, reproducing earlier false-positive acceptance. New gate blob `39604e22bb19ec0e737d47b234862a52e5dac3c3`; R317 regression blob `659d32ed77ab49b01046d726c97063a4548ed409`.

Focused reproduction from repository root (the separate R316 true integration method is deliberately not counted in these synthetic-only results):

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_crypto_source_custody_r317.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_crypto_source_custody_r317.py'
PYTHONPATH=products/desktop python products/desktop/scripts/vault_crypto_gate_r316.py
```

The third command is expected to HOLD outside the genuine complete checkout; on the full checkout it must run all 22 actual AES-GCM cases and report zero skips.

## Still blocked / next release gate

Full private source integration, Ubuntu+Windows hosted CI, native Windows 11 x64 builds and six executable smokes are **not verified**. The preceding R316 run [#42725100029](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42725100029) had two failed jobs with no runner steps. The owner must inspect Actions billing/spending limits, runner allocation and workflow permissions and rerun on the R317 head, or execute complete source/crypto gates in a trusted full private checkout. Only after genuine integration evidence should an owner privately build six Windows x64 candidates, verify SHA-256, Defender, keyboard/screen-reader accessibility and access-controlled premium distribution.

**Independent QD review and founder authorization are mandatory before merge, release, publication or premium links.** Do not publish untested EXEs or expose premium binaries at public URLs.
