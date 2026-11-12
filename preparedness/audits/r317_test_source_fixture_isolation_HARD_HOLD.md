# R317 — Independent test-fixture source mutation sentinel (DRAFT / HARD HOLD)

Issue #136; conversion coordination #820 and charter #818. Draft-only, read-only test-source audit. Extends R316 PR #2192 without changing any authentic manuscript, source register, source fragments, taxonomy, metadata, WordPress outputs, CMS, or site route. No publication permission.

## Verified independent reviewer finding

PR #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` isolates the first synthetic source-upgrade test in a temporary checkout but **still writes and unlinks** `ROOT / sources / fragments / _dup_test.json` in `preparedness/tests/test_preparedness.py` lines 71–78. A documented non-approving PR review was submitted (review ID 5875156845); GitHub did not permit REQUEST_CHANGES on the reviewer's own PR, so COMMENT was used. Do not merge until the second fixture is isolated. PR #157 still draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; its proposed main-breaker wording change is editorial safety work but it is not an independent safety signoff.

## Gate and limitations

Read-only Python AST tool `preparedness/tools/r317_source_mutation_sentinel_hold.py` scans `test_*.py` without importing/executing any tests. It identifies statically evident direct calls such as `ROOT / 'sources' / 'fragments' / '_dup_test.json'` then `.write_text()`/`.unlink()`, plus test writes into canonical content/assets/tools/build and taxonomy files. It handles local aliases, literal slash paths, `joinpath`, `open('w'/'a'/'x'/'r+')`, and symlinked test files. Tests safely using `TemporaryDirectory` are not flagged. The gate hard-fails a missing test tree or missing core tests. It returns only DRAFT_HARD_HOLD or INVALID_HARD_HOLD—never QD PASS, merchant success, or publication approval.

**AST limitation:** dynamic paths, `os`/`shutil` writes, monkey-patching and generated code are not fully covered; a clean AST check is NOT permission to execute untrusted tests or proof of test isolation. Pair this with isolated checkout, review and full native execution.

## Locally executed scope

80/80 synthetic Python `unittest` tests pass in a local reconstruction, plus `py_compile`. Local checkout is incomplete; `--root /mnt/data/prep_r317` correctly returns INVALID_HARD_HOLD due to missing genuine `test_preparedness.py`. Full authentic 41 draft/41 preview outputs, complete native build and qualified source/safety/privacy/QD review remain **NOT EXECUTED / NOT APPROVED**. Prior R316 487 tests are historical prototype evidence, not rerun here.

## Conversion-first integration

ONE candidate topic: household emergency contact/reunification; only the existing public official-resource index `https://finalvestige.com/preparedness/` is a prospective free destination **after** Grok/Praxxis authenticate an actually published asset ID, the destination and mobile intent match. Original Article #15 and Tool #104 remain unpublished/hard held for 911/texting, child privacy, accessible print/no-JS. A currently purchasable, rights-cleared, deliverable Preparedness SKU, merchant transaction/refund, and attributed net revenue remain **UNVERIFIED**; no speculative CTA, retained water offer or new product. Owner: Founder/Commerce for paid offer; Grok/Praxxis for authentic asset; Claude for measurement and commerce-site engineering; Preparedness Integration for evidence and source gates.

## Integration handoff

Run `python -I -m unittest discover -s preparedness/tests -p 'test_r317*.py' -v` and `python -I preparedness/tools/r317_source_mutation_sentinel_hold.py --root .` inside a complete, *throwaway* authenticated checkout. AST failure is an integration blocker; successful AST results do not supersede R316 full export parity, safety adjudication, independent QD review or founder release approval. No CMS, publisher, post, analytics or merchant mutation.
