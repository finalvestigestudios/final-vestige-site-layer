# R242 — Six-app SHA256 inventory staging custody

**DRAFT / independent QD + founder HARD HOLD.** For issue #73. Stacked only on R241 [draft PR #1305](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1305) at exact head 471e0aa29b27eebb45d06943e35e404f91a23c63. Never production main.

## Before and after

The shared six-EXE inventory builder previously leaked the raw mkstemp descriptor if fdopen failed. A stream context-entry failure could also strand a descriptor; unexpected exceptions could expose private customer paths. Short writes or same-size corrupted staged bytes were not checked before hardlink publication. They might briefly become the published inventory before post-publication rollback.

R242 introduces a dedicated descriptor-to-stream ownership handoff that closes raw handles on all failures, including KeyboardInterrupt and SystemExit. A guarded staging writer closes on failed context entry and redacts unexpected ordinary exception messages. It requires a native integer write count equal to the canonical manifest byte length. Most importantly, before link publication, the existing bounded read_checksum_candidate guard independently verifies staged bytes match the exact canonical six-entry ASCII manifest. Existing post-publication drift checks, atomic exclusive link, original files, no telemetry, premium restrictions and human approval remain unchanged.

## Reproduction and observed evidence

Recovered exact R241 source blobs: build_inventory.py 44edcfd9b192cc950fbcdac36882797094ae96df and candidate_guard.py cc92c58246196f284ea12659621a347bd96e4fe9, locally validated by git hash-object. The 19 new fault tests against the unfixed original produced **11 failures and 6 errors**; 2 passed.

On isolated Linux x86_64 Python 3.13 using actual local file descriptors and synthetic non-executable bytes, fixed source yielded **19/19 PASS** standard and **19/19 PASS** optimized Python, zero skips, total **38/38 executed test methods**. Compileall PASS. Tested conditions: fdopen error and interrupts; stream-entry failure; write short/wrong/bool/None counts; unreported appended bytes; same-length corruption; write/flush/fileno/exit exception privacy; exact success; originals preserved and no premature manifest/link.

Local commands (repository root):

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_inventory_staging_custody_r242.py'
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_inventory_staging_custody_r242.py'
    python -m compileall -q products/desktop/build_inventory.py products/desktop/tests/test_inventory_staging_custody_r242.py

GitHub submitted blob identities match the locally executed source/test exactly:
- build_inventory.py: e5e559016778326dc3957639034f5e6b70e6d2de
- test_inventory_staging_custody_r242.py: 163a4ae329017fb57d8d0db36fd659177ade207a

Both independent Ubuntu source-tests and Windows windows-build workflows now include these tests in standard and -OO mode before packaging. Hosted CI execution is NOT established by these local results. Previous [R241 Actions run #42293861011](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42293861011) failed with no recorded execution steps; cause unconfirmed.

## Hard hold / next acceptance

Full inherited six-engine regression, native Windows 11 x64 EXE builds, checksum / Defender / EDR, functional Windows smoke, NVDA / keyboard / high-DPI, protected premium delivery, code signing, independent QD and founder approval remain unverified. Four free and two Pro apps all remain unreleased. No production merge, site publishing, unrestricted premium downloads or public binaries.

**Next highest-impact action:** restore hosted Actions runner execution (inspect failed-run banner, billing/spend, workflow permissions and runner provisioning), rerun unchanged R242 head, then complete the entire six-app suite and actual Windows 11 validation. This sprint makes no release claim.
