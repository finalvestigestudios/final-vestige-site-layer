# R512 — Source child-environment custody (draft / QD hard hold)

Issue: #73. Parent: R511 draft PR #2943, commit \`4eed3c2001acf8786494ce3591957962304f2f44\`. Scope: shared read-only source-verification runner for all six Windows x64 desktop utilities, NOT any executable or production financial logic.

## Reproduced exposure
The runner filtered named secrets and a limited set of Python and loader variables. It still passed through additional \`PYTHON*\` startup switches (for example \`PYTHONSAFEPATH\`, \`PYTHONUTF8\`, \`PYTHONIOENCODING\`, \`PYTHONHASHSEED\`), GitHub command-file handles (\`GITHUB_STEP_SUMMARY\`, \`GITHUB_STATE\`), event paths, and \`GIT_CONFIG_*\` / \`SSH_AUTH_SOCK\`. This allowed surrounding job state to influence source-test behavior or be observed by test subprocesses.

## Change
- Filter all case-insensitive \`PYTHON*\`, \`GIT_*\`, \`SSH_*\` environment names and all \`GITHUB_*\` names except the public \`GITHUB_ACTIONS\` CI marker, in addition to existing token/credential suffixes and dynamic-loader checks.
- Reconstruct only \`PYTHONPATH\` (reviewed desktop module root), \`PYTHONDONTWRITEBYTECODE=1\`, and deterministic \`PYTHONHASHSEED=0\`.
- Preserve nonsecret CI, PATH, locale and operating-system variables to avoid intentionally changing Windows system bootstrap.
- Extend the already-pinned \`test_source_evidence_runner_r509.py\` with eight R512 regression methods. The immutable 416-command matrix, manifest SHA pin, 8-KiB source workflow limit, and internal release guards stay unchanged.

## Test evidence and limitations
A local Linux standalone probe of the *exact new environment function*, with eight equivalent synthetic regression cases, passed 8/8 standard and 8/8 optimized Python (16/16), including a genuine child process. That isolated probe is not a whole-repository run of the committed R512 module; the new committed methods and inherited suite still require hosted execution. No native Windows smoke, Defender, licensing or accessibility gates have passed here. No binaries were generated.

## Risks and follow-up
Some source tests may intentionally depend on unreviewed \`PYTHON*\`, \`GITHUB_*\`, \`GIT_*\` or \`SSH_*\` variables. A hosted exact-commit run must reveal and adjudicate any such dependency rather than loosening controls silently. Restore GitHub Actions runner execution (billing/eligibility/repository settings) and run Linux/Windows 416-command source matrix, Windows x64 six-app builds, Defender, accessibility, entitlement checks and SHA256 custody before independent QD review and founder approval.

**HARD HOLD:** no merge, deployment, signing assertion, public EXE links, or unrestricted premium downloads. Local-first privacy, Decimal money calculations, deterministic audit evidence, and human compliance review remain untouched.
