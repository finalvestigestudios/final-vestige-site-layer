# Independent local Playground provenance preflight — RELEASE HOLD

Read-only independent QA stacked on the homepage's draft PR #265. This branch changes no homepage source, WordPress site, page, subscriber, installed plugin, frozen PR #49, or live configuration.

## Confirmed source-level gap

PR #265 identifies the supplied Assembler theme ZIP by an editable `Theme Name: Assembler` header and records the archive SHA-256 **after accepting it**. It does not compare that hash against an independently authenticated publisher digest. Its generated CLI command also specifies `@wp-playground/cli@latest`, not a reproducible fixed package version. These are **local developer-preview provenance and reproducibility gaps**, NOT evidence of compromise, production exposure, or browser failure.

## Run before launching local Playground

The independent validator requires a complete, UNSTARTED local stage from PR #265, the exact tested Git commit, an unmodified official Assembler ZIP, and the ZIP's SHA-256 obtained through a trusted independent channel. Recomputing the checksum from an arbitrary downloaded archive and treating it as its own independent trusted value defeats the guard.

```sh
python -m unittest discover -s qa/independent_playground_integrity -p 'test_*.py' -v
python qa/independent_playground_integrity/verify.py \
  --stage-dir /tmp/fv-ex2-local-stage \
  --assembler-zip /trusted/assembler.zip \
  --trusted-assembler-sha256 '<trusted-64-digit-hex-digest>' \
  --expected-head '<exact-40-character-commit>'
```

The validator checks the externally trusted archive SHA, every prepared theme-mount file against the archive, exact Git HEAD, release HOLD receipt, local-only/no-import Blueprint requirements, and an exactly version-pinned Playground CLI package. All failures are nonzero and fail closed. It performs no network requests or WordPress operations.

**Current PR #265 output is EXPECTED TO FAIL the pinned-CLI check** because its command uses `@latest`. The homepage lead should independently select and verify a fixed package version and then correct the existing builder under its own review/QD governance. This QA PR does not invent or install one.

## Evidence and release

The two exact GitHub-committed Python files were byte-for-byte matched to the local files tested on Python 3.13: **13/13 tests PASS**; `py_compile` PASS. All fixtures are synthetic. Neither the actual WordPress Playground CLI nor an official Assembler ZIP is available in this runtime. No genuine WordPress, mobile browser, image-transfer, axe, Lighthouse, Jetpack, or production Cloud/Atomic parity acceptance has passed; NASA/NYPL rights and QD/CI remain HOLD. This new validator can only return `SOURCE_INTEGRITY_ADMITTED_ONLY` while release stays HOLD.
