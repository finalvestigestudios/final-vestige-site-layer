# R409: offline six-app source-tree custody and zero-buffer child output

**State:** source-only safety increment, unreleased. Independent QD and explicit founder authorization remain mandatory. No production branch, customer data, site download URL, license check, or financial rule changed.

## Defects addressed

R408's offline_source_smoke_r408.py required regular *source files*, but did not verify the path components to those files. A symlinked desktop root, fvs_suite package directory, launchers directory, or nested package directory could therefore redirect source verification or execution outside the intended trusted checkout. Python's Path.rglob("*.py") may even skip a symlinked nested directory, leaving an imported source outside the SHA-256 inventory. On Windows, a junction/reparse directory can satisfy ordinary is_dir tests.

R408 also used stdout=subprocess.PIPE, stderr=subprocess.PIPE. Although those bytes were discarded from the final JSON receipt, subprocess.run() could still temporarily retain arbitrarily large private child output in memory.

## R409 implementation

- Before enumerating or executing sources, use lstat() to require real desktop, fvs_suite, and launchers directories; independently traverse nested package directories without following links. Reject symlinks, Windows reparse-point directories (including junctions), unreadable directories, and non-directory substitutions with fixed errors. **No child is spawned on invalid inventory.**
- Direct both child output streams to subprocess.DEVNULL, not Python pipes. Preserve isolated -I, no stdin, no shell, timeout, before/after SHA-256 inventory, fixed twelve statuses, deterministic JSON and explicit release_authorized=false.
- Update the inherited R408 invocation contract to assert OS-level output discard; add twelve R409 regressions and put both normal and optimized modes in the Windows + Ubuntu source workflow.

## Reproduction and evidence

On the exact upstream R408 runner blob 49be8b632e2e52c741ab42fb120e2d591d075a84, three selected new tests produced **2 FAIL + 1 ERROR** (nested symlink missed, stdout pipe remained, directory check absent). No private source or customer data was used.

On the R409 patched runner blob fc2b2974f1c6576ccbafdd7349f509f70516715d, updated inherited test blob 8191dae9fd89a6be40c02503715f9db403bb075a and new regression blob 1e6c0fb7db66c1ec69584d3ce7ac19a0c679db17, local Python 3.13.5 Linux execution produced:

| Source tests | Standard -W error | Optimized -OO -W error |
| --- | ---: | ---: |
| Twelve new R409 methods | 12/12 PASS | 12/12 PASS |
| Nine inherited R408 methods | 9/9 PASS | 9/9 PASS |
| **Total method executions** | **21/21 PASS** | **21/21 PASS** |

Python compilation passed. The test tree reproduces exact Git blobs for the three Python files, but is a **partial local reconstruction with synthetic launchers**. The tests include a 12-child synthetic launch with large stdout/stderr; they do not prove a complete source checkout, cryptographic suite, genuine Windows GUI/PE, NVDA, Defender, offline entitlement security or premium delivery.

## Full-checkout operator verification

From a trusted complete branch checkout, with its documented dependencies installed, run:

~~~sh
export PYTHONPATH=products/desktop
python -W error -m unittest discover -s products/desktop/tests -p test_offline_source_smoke_r408.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_offline_source_smoke_r408.py
python -W error -m unittest discover -s products/desktop/tests -p test_offline_source_privacy_r409.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_offline_source_privacy_r409.py
python -I products/desktop/offline_source_smoke_r408.py
~~~

Use native Windows and Ubuntu runners for independent confirmation. Source smoke 12/12 alone is **never** a Windows executable release gate or approval.

## Remaining release holds

CI-hosted execution has repeatedly failed before assigning runners, so the full-checkout and platform gates remain unverified. Diagnose runner allocation/billing eligibility, rerun the exact feature-branch commit, and complete inherited Decimal/cryptographic regression, six genuine Windows x64 PE launch tests, Microsoft Defender, keyboard/NVDA/high-DPI, SHA-256 distribution custody, premium anonymous-access denial, independent QD and explicit founder approval **before** publishing anything. Keep the four free and two premium utilities distinct.
