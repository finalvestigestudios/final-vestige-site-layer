# R442 — Premium license holder invisible identity boundary

**DRAFT; RELEASE HARD HOLD.** Issue #73. Scope: shared offline holder validator for **GrantAudit Studio Pro** (grants) and **ProcureGuard Studio Pro** (procurement). Stacked on draft R441 PR #2567 at pinned parent `97f4d5314122b88bdda4c73bf43ef8c097689326`, not production main.

## Reproduced failure and minimal fix

The R441 validation correctly rejected Unicode controls, bidi formatting, surrogates and line separators, but admitted visually ambiguous internal Unicode Zs spaces (such as U+00A0 NBSP, U+202F narrow NBSP and U+3000 ideographic space), invisible variation selectors (U+FE0F and U+E0100) and Unicode noncharacters (U+FDD0, U+FFFE and 17 planes' FFFE/FFFF values). Thus two different signed holder strings could appear indistinguishable in a human review. This is a synthetic input-custody weakness, **not evidence of license forgery or a customer incident**.

The production `fvs_suite/holder_identity.py` validator now:
- accepts ordinary internal U+0020 spaces and visible French, Arabic, Japanese and combining-accent names;
- rejects non-ASCII `Zs` separators, Unicode variation-selector ranges U+FE00–U+FE0F and U+E0100–U+E01EF, and noncharacters U+FDD0–U+FDEF plus FFFE/FFFF in all 17 Unicode planes;
- retains R441 control/bidi/surrogate refusal, exact built-in `str` type check, 1–120 codepoint bound and no leading/trailing whitespace;
- never silently normalizes, translates, infers legal identity, contacts a server or modifies an audit/financial record. Money remains Decimal-safe and premium human decisions remain manual.

**Compatibility note:** Names genuinely containing non-ASCII spacing glyphs or CJK variation selectors previously accepted by R441 will now be refused, including already-signed synthetic examples. Do **not** edit signed files, auto-reissue an entitlement, bypass verification or silently remap an organization name. Human operator must inspect original identity and plan an explicitly approved migration/reissue before adoption. Independent QD review must assess the strict display policy.

## Exact committed artifacts

- `products/desktop/fvs_suite/holder_identity.py` — Git blob `e97dbd844ad9912a060c5558d6d468c10d6f3319`
- `products/desktop/tests/test_holder_display_boundaries_r442.py` — Git blob `589ad31eaf3370a1c1ed6d1147c0d70a5e2a4b96` (9 pure regression methods)
- `products/desktop/tests/test_premium_holder_boundaries_r442.py` — Git blob `08aae9266828dfd4906efc966234add47add5cdb` (4 full-module methods with ephemeral Ed25519 signatures and synthetic issuer inputs for both premium products)
- `.github/workflows/desktop-source-evidence-r385.yml` — four new normal/optimized invocations across Ubuntu and Windows, retaining R441 and inherited source gates

## Locally executed evidence — precise limits

Linux CPython 3.13.5 with exact production and test blob content reconstructed in a **partial isolated source subset**, using the actual R441 pure test file as an inherited regression:
- New R442 pure tests: **9/9 PASS** in `python -W error`, **9/9 PASS** under `python -OO -W error`.
- Inherited R441 pure tests: **4/4 PASS** in both modes.
- **26/26 total focused test-method executions PASS**; Python compilation of changed production, new pure tests and new integration file PASS.
- Independently verified the three new/changed Git blob SHA-1 values against exact files after GitHub publication.
- Controlled **pre-fix** test run with exact original R441 helper blob `23bea5b0401b8525ebb83c58e007b6335620b251`: **338 assertion/subcase failures** across 5 of the 9 new methods; the corrected helper passes them.

**Not executed locally:** The 4 full-module R442 Ed25519/issuer integration methods, all six desktop engines as a complete checkout, native Windows Tk, native Windows x64 packaging, Defender, product entitlements, premium gated delivery or end-user accessibility. CI registration is not CI success. No release gate is satisfied by these local focused tests.

## CI, QD and next step

Prior R441 exact-commit [source run #43674973552](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43674973552) and [desktop build #43674973521](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43674973521) failed before any recorded steps, 4 failed jobs without a runner assignment. The underlying cause has **not** been established. Examine the R442 exact-head runs and GitHub check annotations; an authorized repository owner must inspect account/organization Actions billing/spending limits, repository Actions policy and runner eligibility. Once execution is restored, run the full R442/R441 and inherited license/Decimal/audit suites on exact head, package six real Windows x64 binaries internally, smoke/scan/checksum, verify premium download restrictions, then independent QD review and explicit founder approval.

**release_authorized=false.** No merges, public executables/downloads, real licenses, premium files, site publication, or automated compliance approvals.
