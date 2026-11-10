# Labs R322 — offline independent SHA-256 witness for restored premium bundles

**DRAFT / QD + founder HARD HOLD.** Issue #73. Stacked strictly on R321 draft PR #1846; no main, merge, publication, entitlement, customer files, or financial-rule changes.

## Why this matters

The R320–R321 read-only inspector checks that a restored evidence report, journal, and plaintext manifest are *internally consistent*. A person with write access to the folder can modify the report or journal and regenerate SHA-256 values inside the manifest. That forged folder could pass a self-consistency check.

R322 adds **opt-in independent witness comparison**: require the expected product, the SHA-256 digest of the report, and either a SHA-256 digest of the journal **or an explicit statement that no journal should exist**. The two digests must come from a separate, already trusted channel (for example, the authenticated original archive's verified custody record retained outside the restored directory). **Do not copy the expected digests from the same mutable restored manifest**; that defeats the purpose.

### Offline operator usage

From a trusted checkout, with `products/desktop` installed as the working tree, invoke the existing isolated CLI (SHA values below are placeholders, not real customer digests):

```bash
python -I products/desktop/scripts/verify_restored_bundle_r320.py /path/to/RESTORED \
  --expect-product grants \
  --expect-report-sha256 <64-lowercase-hex-from-independent-trusted-record> \
  --expect-journal-sha256 <64-lowercase-hex-from-independent-trusted-record>
```

For a bundle that must **not** contain a review journal, replace `--expect-journal-sha256` with `--expect-no-journal`. Use `--expect-product procurement` for ProcureGuard. SHA-256 inputs are digests, not passphrases. The operation requires no internet and never modifies a file. The original unanchored CLI remains available for its explicitly lower-assurance **consistency-only** check.

A partial set of witness flags **fails closed** with a fixed HOLD message (no automatic fallback). Invalid/wrong-format/wrong-product/wrong-file digest, unexpected journal presence, a missing journal, or a failed original R321 consistency check also HOLD. No customer path or expected digest is echoed on a failed witness check.

The Python API is `inspect_with_external_witness(folder, product="grants", report_sha256=..., journal_sha256=...)`. Pass `journal_sha256=None` **only** to require journal absence. On success, the original receipt is preserved with `external_witness_matched=True`. The original `source_authenticated=False`, `review_required=True`, `compliance_approved=False`, and `release_authorized=False` values remain unchanged.

## Threat boundary and human approval

A witness digest is meaningful only when verified independently from a trusted source; digest strings supplied by an attacker are not authentication. Matching SHA-256 checks proves no more than an observed byte match to the supplied values. It does **not** prove AES-GCM archive authenticity, entitlement, source provenance, genuine reviewer identity, event-chain semantics, approval, compliance, file locking against a hostile privileged concurrent writer, or release readiness. A malicious actor who controls the witness itself can bypass this control. Human compliance review and independent QD/founder approval remain mandatory.

## Reproduce / evidence (local Linux, November 9, 2026 PST)

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_restored_external_witness_r322.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_restored_external_witness_r322.py'
python -m py_compile products/desktop/scripts/verify_restored_bundle_r320.py products/desktop/tests/test_restored_external_witness_r322.py
```

Executed on a local reconstructed R321 inspector plus the R322 functional patch, synthetic CSV/JSONL and genuine temporary filesystem operations: **20/20 normal tests PASS, 20/20 optimized tests PASS (40/40 method executions), py_compile PASS**. The locally reconstructed base was not a complete private checkout. The R322 tests include a regression demonstrating that a completely rehashed report, journal, or product switch can pass the *pre-R322 unanchored consistency check*, while the new independent witness check refuses the same forged evidence. Other cases exercise both premium products, journal absence/presence, invalid digests,  isolated `python -I` CLI, privacy-safe HOLDs and no-write behavior. Hosted CI, actual AES-GCM restoration, signed Windows builds and malware/accessibility acceptance remain **UNVERIFIED**.

## CI / release hard hold

The existing desktop Ubuntu and Windows workflows now include both normal and `-OO` R322 regression commands, before source/packaging gates. Github Actions runner availability remains blocked: prior R321 [run #42760062056](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42760062056) failed before runner allocation. Verify R322 workflow status independently; do **not** interpret failed-before-run CI as a test failure or passing build.

**Next highest-impact milestone:** owner restore eligible GitHub Actions runner allocation or run a full private checkout with `cryptography` installed to execute all 22 mandatory genuine AES-GCM cases. Then privately produce and test all six native Windows x64 portable EXEs, collect SHA-256, Defender, accessible keyboard/visual smoke evidence, and confirm premium entitlement gating. No binaries or public download links are authorized by this PR.
