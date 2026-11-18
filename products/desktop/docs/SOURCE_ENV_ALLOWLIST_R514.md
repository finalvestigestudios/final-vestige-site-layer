# R514 — Fail-closed child environment for six-engine source CI

**Scope:** issue #73; stacked on R513 draft PR #2954. This is an internal read-only test runner improvement, NOT a Windows executable release or QD approval.

## Defect and change

R513's case-insensitive blacklist filtered known cloud, package, and secret-related names, but any previously unknown environment key without a recognized prefix or suffix still reached the 416-command Python source-test subprocesses. Examples include \`FINANCE_VAULT_URL\`, \`CLIENT_BILLING_ENDPOINT\`, and \`FV_LICENSE_FILE\`. The R514 boundary instead inherits only an explicit inventory of required Python bootstrap OS paths and public CI/locale variables, and always sets reviewed \`PYTHONPATH\`, \`PYTHONDONTWRITEBYTECODE=1\`, and \`PYTHONHASHSEED=0\`. Case-folded duplicates are dropped entirely to avoid Windows ambiguity. Host mappings are never mutated.

Files:
- \`products/desktop/scripts/source_child_env_r514.py\`: standalone allowlist boundary.
- \`products/desktop/scripts/source_evidence_runner_r509.py\`: existing \`_child_environment\` API now delegates to R514 policy.
- \`products/desktop/tests/test_source_evidence_runner_r509.py\`: ten new regression methods already covered by both pinned unittest invocations; one inherited assertion updated because arbitrary benign-looking variables are now intentionally dropped.

The 416-command SHA-pinned inventory, original 414-command prefix, compact source workflow, Windows build safeguards, six financial engines, audit trails, license gates, and production branch are **unchanged**.

## Measurable verification

- A byte-identical local copy of \`source_child_env_r514.py\` was executed on Linux CPython: **10/10 normal + 10/10 optimized (\`-OO\`) pass**, including a real subprocess. Verify the new file's Git blob SHA matches the tested local copy before citing exact parity.
- An unknown-key synthetic sample was inherited under R513's blacklist by design, but dropped under R514's allowlist. This is not a claim of real-world credential exposure.
- The 10 methods were committed into the existing matrix-listed R509 test module. **The complete committed module and 416-command matrix have NOT run** locally/hosted; neither has Windows x64 packaging or Defender, keyboard, checksum or premium-entitlement testing. Test logs contain synthetic values only.
- Allowlist behavior is intentionally restrictive: a legitimate future source test needing an additional host variable must receive an explicit reviewed allowlist amendment, not arbitrary pass-through.

## Limitations, approval, next gate

Environment filtering is **not** a filesystem sandbox. Home/profile paths remain permitted where necessary for Windows/Python bootstrapping. No compliance or payment decisions are automated.

**HARD HOLD:** independent QD review and founder approval before merge/release. No production branch, WordPress publication, executable or premium download was modified or exposed.

**Next highest-impact step:** resolve GitHub Actions job startup failure (billing/spend cap, runner eligibility and workflow policies), execute both OS matrix jobs at exact commit, then full six-app Windows x64 packaging, Defender, checksums, accessibility, premium access checks and independent QD approval.
