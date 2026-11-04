# R190 — Unicode compatibility-copy hard hold (DRAFT, six-app catalog)

Tracks [desktop issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacks on R189 draft [PR #965](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/965) at immutable parent `353eb51c67594881005d37b01ce3489328ce5785`; **not production/main**. This source-only change does not touch WordPress, launchers, binaries, private financial documents, premium payment/licenses, or download links.

## Reproduced acceptance gap and solution

The R188 visible-text and R189 HTML node-fragment scanners recognize literal ASCII release phrases, installer suffixes and URL schemes. However Unicode compatibility equivalents can visibly represent the same text while bypassing ASCII patterns: `Ｄｏｗｎｌｏａｄ ｎｏｗ`, `GrantAudit．ｍｓｉ`, `ｈｔｔｐｓ：//...`. These synthetic examples were **accepted under the R189 scanners but rejected by R190 locally**. This is a static draft risk, **not evidence of public release or an exploited live site**.

Refactor `catalog_visible_hold_r188.py` to reuse an offline, bounded scanner on (1) exact decoded HTMLParser text nodes and (2) NFKC-folded copies of each node. Retain original node boundaries for R189 fragment detection. Validate all inputs as exact built-in list/str before normalization; recheck limits and forbidden controls after normalization (which may expand text). Reject unsafe copy with generic diagnostic messages; never echo premium links, customer text or private paths. The original Gutenberg bytes are not modified. Normal Unicode accents and ordinary compatibility-styled informational copy remain allowed when safe.

## Evidence and scope (Linux local)

- Interpreter: local Python, isolated implementation and one exact-Git-blob-matched upstream R189 fragment module (`8dbc70208f04d99982da47caa0b442c24aa44699`).
- `PYTHONPATH=. python -m unittest discover -s tests -p 'test_catalog_compatibility_r190.py'`: **29/29 PASS**, no skips.
- `PYTHONPATH=. python -OO -m unittest discover -s tests -p 'test_catalog_compatibility_r190.py'`: **29/29 PASS**, no skips.
- `python -m py_compile catalog_visible_hold_r188.py tests/test_catalog_compatibility_r190.py`: **PASS**.
- Tested implementation Git blob: `61090987be80609a624b825e0618213d56d244bd`; tested 29-case file blob: `588beaeb00ddc39f11001ce98b068cc38a23dade`. Compare GitHub files on R190 branch to these hashes before relying on counts.

Synthetic tests include fullwidth/circled/mathematical letter forms, Unicode-equivalent punctuation, NBSP separation, split HTMLParser text nodes, digit/URL schemes, benign text, deterministic reuse, no source mutation, expansion bounds and privacy-safe errors. These tests **do not verify an actual browser's Unicode rendering, full source checkout, prior inherited suites or Windows binaries**.

CI now explicitly runs those 29 methods under normal and `-OO` Python and rechecks the tracked unchanged six-product Gutenberg draft in **both** Ubuntu and Windows jobs. Hosted execution must be observed, not assumed: R189 [run #41873237453](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41873237453) failed on both jobs with no recorded steps; root cause requires owner investigation.

## Review, blockers and next work

Maintain **HARD HOLD**. No production merge, publication, availability claims, public free binaries or unrestricted premium URLs. Do not infer security, payment entitlement, physical Windows accessibility, QD approval or founder permission from this preflight. The next highest-impact step is to restore GitHub Actions runner execution (inspect run failure banner, account billing/usage and runner provisioning); rerun R190 unmodified on Ubuntu and Windows, run inherited full-repo integration including pending Policy Delta real-file tests, privately build/checksum/scan/smoke-test six x64 programs, and obtain independent Windows 11 accessibility, Defender/EDR, signing, premium entitlement, QD and founder acceptance.