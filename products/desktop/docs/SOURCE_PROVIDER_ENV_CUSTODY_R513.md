# R513 — Source-test cloud and package configuration custody (DRAFT / QD HOLD)

Scope: Issue #73, six standalone Windows x64 utilities; stacked on R512 draft #2948 (head `d6098ccfa44e1f8326d69fb3137f22fb26aaff63`). No changes to production `main`, app calculations, audit logic, premium licensing, packaging or catalog publication.

## Reproduced privacy gap
The R512 source-matrix child environment removes generic `*_TOKEN`/`*_KEY` credentials and Python/GitHub startup controls, but names such as `AWS_PROFILE`, `AWS_CONFIG_FILE`, `AWS_SHARED_CREDENTIALS_FILE`, `GH_CONFIG_DIR`, `DOCKER_CONFIG`, `KUBECONFIG` and `PIP_INDEX_URL` still pass to every scheduled Python test. Those values can be paths to host credential stores or URLs with embedded passwords. It is inappropriate to give financial source-test children ambient CI credentials, even though stdout/stderr are redacted.

## Change
- Deny inherited AWS, Azure, Google/Cloud SDK, GitHub CLI, Docker, Kubernetes, Python/npm/PyPI/Twine/Poetry/uv registries, GPG and Terraform environment namespaces, case-insensitively.
- Deny the two unsuffixed credential-store pointers `KUBECONFIG` and `GNUPGHOME`.
- Preserve only the existing `GITHUB_ACTIONS` public marker across GitHub names; preserve PATH, CI, locale and operating-system basics, plus reviewed deterministic Python overrides.
- Add ten R513 regression methods to the **already included** `test_source_evidence_runner_r509.py` source test. No manifest or CI workflow edits; all 416 SHA-pinned commands remain unchanged.
- No secrets, client records or real credential paths in test fixtures; the real subprocess test passes only synthetic data.

## Evidence and truthful scope
Local Linux standalone probe with the matching new `_child_environment` filtering logic: **10/10 normal**, **10/10 `-OO`**, 20/20 isolated executions, with one actual subprocess in each mode. This proves the isolated policy, **not** that the full committed Python regression suite or 416-command source matrix has run. Exact committed production code and newly committed test suite still require hosted Linux/Windows validation, including the new methods. A local clone/checkout was unavailable in the probe environment.

R512 exact-head GitHub Actions three workflows all reported failures before execution, **six jobs with no steps or assigned runner**, not failed tests. Repository admin should check Actions billing, spending limits, repository workflow policies and runner eligibility, then rerun full exact-commit matrix and native six-app Windows x64 release gates.

## Explicit limits
Environment minimization is **not a sandbox**: test code can still access files readable by the runner, and permitted HOME/PATH may indirectly reveal local environment. Do not mistake it for proof that no network or private files can be accessed. Any new filter-related test dependency must be reviewed explicitly; do not weaken protection to get CI green.

**HARD HOLD:** independent QD approval and explicit founder authorization are mandatory before merge/release. Do not publish unsigned/untested Windows executables or unrestricted premium downloads. Local-first processing, Decimal-safe amounts, deterministic audit provenance, and human-only compliance review are unchanged.
