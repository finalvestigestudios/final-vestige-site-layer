# R417 — File-descriptor custody for the six-app offline source evidence runner

**Internal engineering-only; release HOLD.** Stacked on R416 draft PR #2421, tracked by issue #73. The working branch is not production main. No binaries, customer data, licenses, download URLs or website routes changed.

## Defect and patch

The R416 source_digest() verified each file using lstat() and subsequently read bytes through Path.read_bytes(), opening the pathname again without tying that new descriptor to the earlier checked inode. A file replacement or last-component symlink insertion in between could cause the runner to hash **unverified bytes**. The same risk applied to local CSV/JSON templates under both import roots, not just Python files. A post-process digest comparison does not repair an invalid initial digest.

R417 now uses _read_verified_source_bytes(): (1) reject non-regular, linked/reparse and empty/oversized files; (2) open a read-only descriptor with POSIX O_NOFOLLOW where available; (3) compare path lstat identity with descriptor fstat identity before reading; (4) read at most the announced size in bounded 64 KiB blocks and reject unexpected extra bytes; (5) compare the descriptor identity and pathname identity again **after** reading, including same-view change timestamps; and (6) close the descriptor on every outcome. This prevents known path-to-descriptor substitution, inode-replacement and in-flight rewrite cases from being certified.

Windows Python 3.12 can report different st_ctime_ns values for lstat versus fstat for the *same* file. Cross-API comparison omits that one field on Windows only, while same-API before/after comparisons retain it. This follows the existing products/desktop/scripts/source_smoke_gate.py Windows compatibility contract. All diagnostics remain fixed, no private paths or subprocess outputs enter receipts, and source receipts remain release_authorized=false.

**Boundary:** The runner is NOT a hardened OS sandbox; the POSIX last-component O_NOFOLLOW defense is not available on every platform, ancestor components can still be swapped by a hostile local actor, and local source evidence is not signed source provenance. This patch improves source-measurement custody, not runtime process isolation or executable verification.

## Exact artifacts and evidence

- Modified: products/desktop/offline_source_smoke_r408.py
- Added: products/desktop/tests/test_source_descriptor_custody_r417.py (12 regression methods)
- Updated: .github/workflows/desktop-source-evidence-r385.yml to run all 12 tests on Ubuntu 24.04 and Windows latest, both normal Python and -OO
- **Local test evidence:** Python 3 on Linux executed an independently recreated copy of the new descriptor-reading helper against 12 synthetic adversarial checks in normal mode (**12/12 PASS**) and -OO mode (**12/12 PASS**). These 24 executions are **extracted-helper probes**, not the exact committed 12 regressions, a complete repository checkout, the six real financial engines or Windows package tests.
- The new committed test covers six real synthetic launcher calls in both modes, descriptor redirection, same-length in-flight rewrite, inode replacement, symlink insertion, short reads, appends, private error redaction, nonregular handles, Windows timestamp comparison and stable source SHA256.
- Repro commands from a **trusted full checkout**:

  ~~~sh
  # from repository root
  PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_source_descriptor_custody_r417.py
  PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_source_descriptor_custody_r417.py
  python -I products/desktop/offline_source_smoke_r408.py
  ~~~

## CI and release HOLD

At R416 head 9ad241ab245c44fe44dd232968420716407bc418, source run #43549527769 and Windows build run #43549527738 both failed **before steps** (each job's steps=null and logs_url=null). No assertion about application quality can be drawn from a non-executing job. Inspect R417 exact-commit CI as it becomes available; do not represent the extracted-helper evidence as native Windows validation. Verify GitHub Actions runner/billing/eligibility with the repository owner.

**Next highest-impact acceptance:** Execute the exact committed tests and inherited financial/Decimal/provenance, AES-GCM, Ed25519, premium approval-queue suites on complete Windows+Ubuntu checkouts; build and natively smoke all six real Windows x64 PE executables; complete Defender and keyboard/NVDA/high-DPI acceptance; independently checksum binaries and verify gated premium downloads deny unauthorized access. Require independent QD review and explicit founder approval before merge, distribution or any website publication.
