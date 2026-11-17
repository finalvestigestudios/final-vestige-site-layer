# R506 — exact SHA-256 stream read receipts (six Windows x64 candidate gate)

**Status:** source-only DRAFT / QD and founder HARD HOLD. Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Based exclusively on R505 draft PR #2909, not production main.

## Scope and correction
The R493 same-descriptor SHA-256 verifier ignored the return value of its reset `seek(0)`, and accepted a bytes receipt without confirming the file position advanced. A direct-call wrapper could return an apparently correct byte stream while ignoring the requested absolute offset, or return more bytes than requested. In R506, each digest stream:
- requires an **exact plain-int zero** reset position before hashing;
- requires **plain immutable bytes**, no more than the bounded requested chunk;
- requires an **exact plain-int cumulative `tell()` receipt after every read, including EOF**;
- retains existing fstat identity, expected digest and size checks; private exceptions remain fixed and unchained.

This is defense-in-depth for a release preflight, **not** an Authenticode signature check, malware clearance, proof of hostile-stream authenticity, or authorization to distribute.

## Locally executed reproducible focused evidence
Inert synthetic data on Linux CPython with real file descriptors; focused `test_pe_digest_receipts_r506.py`:
- `PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_digest_receipts_r506.py`: **12/12 PASS**
- `PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_digest_receipts_r506.py`: **12/12 PASS** (24 focused test-method executions total)
- `python -m py_compile products/desktop/pe_digest_custody_r493.py products/desktop/tests/test_pe_digest_receipts_r506.py`: **PASS**
- Same tests against original R505/R493 verifier blob `c02c3192ded832a50d5356042e860bf4154acde8`: **7 expected failures / 12** (negative control).
- Exact tested SHA Git blob hashes: verifier `4b8ec54f1aafbea6e44ae303dbaf55ef7e490d36`, new tests `ba6eae835419344f9adc496c61e2b2b9399f9a54`.

Both internal build and independent source workflows request this focused suite in normal and optimized Python. Hosted CI, full inherited tests, six-app financial engine validation, Windows x64 packaging, smoke tests, Defender, a11y, codesigning and authenticated premium delivery **have not been verified for R506**. Do not infer pass from scheduled steps.

## Hold and next gate
GitHub Actions had repeated pre-step failures in R505 ([internal build #44166721322](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44166721322), [independent source #44166721332](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44166721332)); infrastructure root cause is not confirmed. Smallest unblock: owner checks Actions billing, runner eligibility and policy, then reruns exact-head workflows or runs a trusted full checkout on native Windows x64.

All six candidates stay unreleased; no premium executable or unrestricted URL is provided. Preserve local-first financial privacy, Decimal-safe calculations, deterministic audit trails, human compliance review, independent QD and explicit founder approval.
