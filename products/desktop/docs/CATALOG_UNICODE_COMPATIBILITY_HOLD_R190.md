# R190 — Unicode compatibility-copy hard hold (DRAFT / HARD RELEASE HOLD)

Tracks [desktop issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacks exclusively on R189 draft [PR #965](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/965), immutable parent `353eb51c67594881005d37b01ce3489328ce5785`; **not main**. No production or WordPress changes, Windows builds, binaries, premium links, payment/licensing changes, or processing of private customer records.

## Gap reproduced and guard implemented

R188's literal/whitespace scanner and R189's node-fragment scanner can miss **Unicode compatibility** spellings of false release claims, installers, and URI schemes. In the exact R189 raw-scanner-equivalent path, four synthetic payloads passed: `Ｄｏｗｎｌｏａｄ ｎｏｗ`, `GrantAudit．ｍｓｉ`, `ｈｔｔｐｓ：//example.test/private`, `Ⓓⓞⓦⓝⓛⓞⓐⓓ ⓝⓞⓦ`. R190 rejects all four. This is a reproducible static preflight gap, not an observed public exploit.

In `catalog_visible_hold_r188.py`, run the existing bounded, offline, privacy-safe scanner on (1) the exact original HTMLParser text chunks and (2) NFKC-normalized copies of each chunk. Preserve node boundaries so the existing R189 fragment detector still catches split words. Retain exact built-in type checks before normalization and reapply size/control-character limits **after expansion**; an oversized normalized copy fails closed. Never alter source bytes or print hidden destinations.

## Executed local evidence — 2026-11-04

Isolated Linux Python verification against **exact Git-blob-matched** files. The following Git blob IDs were confirmed for the local inputs and correspond to committed GitHub files:

| File | Verified Git blob |
|---|---|
| R190 edited visible scanner | `61090987be80609a624b825e0618213d56d244bd` |
| R190 29 focused tests | `588beaeb00ddc39f11001ce98b068cc38a23dade` |
| R190 11 real-source integration tests | `c9b35371aadab683ef9703fb363c9109c12857e8` |
| Inherited R188 43-test module | `962d2d21c5228b537ad8c66d998ac8eb8bd6d249` |
| Inherited R189 fragment source | `8dbc70208f04d99982da47caa0b442c24aa44699` |
| Inherited R189 43-test module | `d0488e013fbd38c557150a02b9e7d5a041350c03` |
| R186 real Gutenberg preflight | `a64c109026742ce07d2e1debdb02ea67d43b82ef` |
| Real tracked six-card Gutenberg draft | `6ab8fc98223330caae28a9964f36ee8a0c9ce6af` |

Commands executed locally from `products/desktop` with `PYTHONPATH=.`:

```sh
python -m unittest discover -s tests -p 'test_catalog*' -q
# Ran 126 tests, OK
python -OO -m unittest discover -s tests -p 'test_catalog*' -q
# Ran 126 tests, OK
python catalog_preflight_r186.py site/software-catalog.gutenberg.html
# PASS_STATIC_DRAFT_ONLY: six unreleased apps, one contact link; QD/launch HOLD
python -OO catalog_preflight_r186.py site/software-catalog.gutenberg.html
# PASS_STATIC_DRAFT_ONLY: six unreleased apps, one contact link; QD/launch HOLD
python -m py_compile <seven applicable source/test files>
# PASS
```

**252/252 local method executions PASS**, no skips/failures. Breakdown per mode: R190 **29 new focused + 11 new full tracked-catalog integration**, inherited R188 **43**, inherited R189 **43** = **126 per mode**. Real tracked six-app draft remained unchanged, passed static draft preflight both modes, and the preflight result explicitly disavows downloads, entitlement, QD and publication approval. Synthetic negative cases prove the rejection path, not product distribution security or real browser accessibility.

The **complete repository test suite, R186's other 38 tests, R188/R189 other integration modules, Policy Delta real-file integration, native Windows execution, six private EXEs, signing, physical Windows 11 accessibility, Defender, premium entitlement and WordPress served-page QA have not been verified in this local reproduction**. Do not describe 252 method executions as full-repository tests. Every local byte used was checked against a Git blob, but this is still an isolated file-level checkout.

## Hosted CI and release hold

Added 40 R190 methods (29 focused plus 11 actual tracked-source integration) to **both** Ubuntu `source-tests` and Windows `windows-build`, running normal and `-OO` Python, followed by real draft catalog preflight. Prior R189 [Actions #41873237453](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41873237453) showed failure with zero executed steps in both jobs; the precise runner eligibility problem remains unconfirmed.

**Smallest owner action:** inspect the R190 Actions run failure banner if it also fails pre-runner, account billing/usage and runner provisioning; restore runners, then rerun the unchanged R190 commit. Follow with full inherited tests, private Windows x64 builds/smokes/checksums/scanning, Win11 keyboard/screen-reader/reflow acceptance, protected premium distribution, independent QD, and founder authorization.

**HARD HOLD:** all six applications remain unreleased. No production merge, download publication, public binaries, unrestricted premium files, automated legal/compliance approvals, or assertion of commercial readiness.