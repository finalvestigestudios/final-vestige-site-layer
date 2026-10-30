# R58 — CI source-gate execution contract

**Scope:** all six Final Vestige Labs desktop applications; no binary distribution or approval.

## Defect demonstrated

R57's CI preflight searched for the two-mode source-verifier command as an exact *line* inside a GitHub Actions step. It did **not** require that the step actually execute that line. In Bash or PowerShell, an unconditional `exit 0` preceding the literal verifier command could produce a green build preflight while bypassing the required regression suite. A literal command embedded inside a here-document was another plausible false positive.

## Fail-closed remediation

`ci_source_contract.py` now also calls `ci_gate_step_contract.verify_gate_step` for the Linux and Windows mandatory test steps. R58 recognizes precisely the reviewed GitHub Actions step shapes:

- Linux: `run: |`, create the private runner-temp evidence directory, run `offline_source_gate.py --report` to that directory, and nothing else.
- Windows: `shell: pwsh`, set the desktop-local `PYTHONPATH`, run `offline_source_gate.py`, then immediately throw when `$LASTEXITCODE -ne 0`. The quoted throw message cannot contain PowerShell interpolation or escape characters.

Extra shell commands, folded/altered YAML, repeated keys, step-level execution overrides, premature exits, and injected commands all fail the preflight. Future intentional modifications to these exact steps require review and updated tests; **do not weaken the validator to get a green build**.

## Verification and limitations

Run from a complete trusted checkout:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_ci_gate_step_contract_r58.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_ci_gate_step_contract_r58.py' -v
PYTHONPATH=products/desktop python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml
```

For a full acceptance test, also run `offline_source_gate.py` against the entire checkout in normal and optimized Python and execute the six native Windows candidate workflows.

This is **not a general-purpose YAML parser, a defense against a malicious upstream Python interpreter, or proof that GitHub Actions runners dispatched**. Existing controls still verify code, packaging inputs, dependencies, exact candidate identities, audit provenance, offline operation, and signed premium entitlements. Linux source evidence never constitutes executable validation.

## Distribution policy

All six utilities remain unreleased. No installers, public links, paywall endpoints, signing credentials, private financial files, or premium entitlements changed in R58. Windows x64 executable smoke, malware checks, accessibility and paid-access verification, green runner evidence, independent QD review and founder approval remain mandatory before publication.
