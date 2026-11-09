# R314 — packaged premium evidence bundle custody and manifest contract

**Draft / QD + founder hard hold.** Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Parent is R313 [PR #1798](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1798) at `2d612c73fb6da5767f40dbc76ad5e5c496ee05fd`, **not `main`**.

## Acceptance defect

R313 correctly made both packaged premium `--smoke-test` paths exercise the real product-bound restore call, but its scope-smoke helper only checked the restored report/journal bytes and the *top-level* temporary directory. A restore that left an unexpected decrypted file **inside** the restored directory, replaced a restored file with a symlink, omitted/corrupted the manifest, altered a source fixture, or modified previously-restored evidence while denying the opposite scope could still pass the original helper.

## Change

- Require exactly three regular, non-symlink files within a successful premium restore: `exception-report.csv`, `exception-report.review.jsonl`, and `sealed-evidence-manifest.json`.
- Parse manifest JSON with duplicate-key rejection; require the exact nine expected fields, version 1, correct product, source basenames and SHA-256 digests, true journal presence, a positive integer review-event count, and a nonempty timestamp.
- Reverify restored members **after the wrong-product denial**, not just before it; ensure source report and journal remain unchanged after both operations. Existing top-level leak, ciphertext, and wrong-scope checks remain enforced.
- Extend the existing R313 regression module from 16 to **28** test methods (12 new adversarial cases); keep its existing path in both the Ubuntu/Windows desktop CI steps, including `python -OO`. Neither premium production vault API, GUI, nor any of the four free engines is changed.

The packaged smoke uses synthetic fixtures and the actual restoration function through `smoke.run_smoke`. The new invariant is an **acceptance check**, not a substitute for vault authenticity, licensing, filesystem isolation or a malicious same-user race defense. It does not make real customer compliance decisions.

## Executed local evidence (not hosted CI)

Linux CPython 3.13.5; temporary filesystem; stdlib-only synthetic restore double:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_smoke_scope_r313.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_smoke_scope_r313.py'
python -m py_compile products/desktop/fvs_suite/vault_smoke_scope.py products/desktop/tests/test_vault_smoke_scope_r313.py
```

Results: **28/28 PASS normal, 28/28 PASS optimized; 56/56 method executions**, `py_compile` PASS. Byte-identical content verified with committed Git blob IDs: helper `28eb76cdb623674fffc730d70fb06d67320f98ec`, regression module `50905f110662f91f3083f62f8421f26fafdccb9e`. The local runner uses only a stub `fvs_suite/__init__.py` to import the dependency-free helper; that stub is **not committed**. This is focused synthetic regression evidence, **not** full repository or real AES-GCM, Windows x64 binary, NTFS, Defender, accessibility, QD, licensing or merchant handoff certification.

## Release hold and highest-impact next step

R313 GitHub Actions run [#42699568242](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42699568242) completed **failure** with Ubuntu and Windows jobs, but no recorded steps. Check this R314 branch's Actions separately; lack of hosted execution remains unresolved. Repository owner should inspect Actions billing/spend cap, runner eligibility and workflow restrictions, then obtain completed hosted normal/`-OO` full-source regression and actual AES-GCM integration evidence. Next, privately build and smoke-test **all six Windows 11 x64 portable EXEs** with SHA-256 hashes, PE architecture, Defender scan, keyboard/screen-reader checks and protected premium delivery. Require independent QD and founder approval before merge or publishing.

**NO production merge, site deployment, public binaries, premium file exposure or release claim.** Local-first processing, Decimal money, deterministic audit trails and human-review-only compliance remain unchanged.
