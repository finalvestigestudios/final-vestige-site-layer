# Final Vestige Labs R146 — private Windows 11 witness CLI argument custody (DRAFT / HARD RELEASE HOLD)

**Scope:** The three established private, source-bound reviewer CLIs: `windows11_manual_acceptance_r109.py` (template/verify), `windows11_witness_writer_r122.py` (one-check human witness), and `windows11_review_progress_r123.py` (read-only 46-check progress). All six candidate applications remain unchanged; this does not add a bypass or license.

## Confirmed source defect and fix

Previously, all three used default `argparse.ArgumentParser` and called `parse_args()` **outside** their redacted HOLD handlers. A malformed invocation with an unknown option, invalid app/state, or accidental client filename as a flag could expose the rejected user-controlled value to stderr and automated support logs, despite each tool already redacting verification failures. Repeated custody flags could silently use only the final value; command-line abbreviations could select an unintended option.

R146 introduces one shared `PrivateReviewParser`, used by all three scripts. It rejects ambiguous duplicate long flags including `--flag=value`, disables prefix abbreviations, and raises a constant exception for argparse errors. Each main now parses **inside** its existing private HOLD boundary: malformed input returns **exit 1**, one exact `HOLD: Windows 11 manual source-to-witness acceptance unverified; release prohibited` stderr line, no stdout, and no access to candidate, witness, or review records. Unmixed `--help` remains static and returns 0. Correct complete commands still dispatch to the original custody code. `--help` mixed with other arguments now HOLDS rather than hiding an accidental review invocation.

**Privacy limitations:** This change cannot hide secrets from OS process lists, PowerShell history, upstream shell logging or endpoint monitoring. Operators must never put client material or secrets into command arguments or public support tickets. It does not establish genuine human execution of 46 checks, independent R9 authentication, actual Defender/EDR assessment, signing, premium access controls, QD approval or founder authorization. It does **not** modify the engine, Decimal money logic, customer inputs, audit reports, or financial exports.

## Strict reproducibility and CI

From repo root, with Python 3.12 and `PYTHONPATH=products/desktop`:

```sh
python products/desktop/scripts/safe_unittest_r146.py
python -OO products/desktop/scripts/safe_unittest_r146.py
```

Exactly **33** named synthetic tests must pass with no skips/failures in both modes on **both Ubuntu and Windows**: **132 mandatory named test executions**. Tests cover all three CLIs' unknown/missing/invalid/duplicate/abbreviated flags, secret-value redaction, fixed HOLD, no work attempted before parser rejection, static `--help`, valid dispatch continuity, and shared-parser behavior. Both CI jobs explicitly run this strict step, separate from the inherited complete normal/optimized source suite, six Windows candidate EXE builds and private native gates. A green CI result verifies this code change only, never actual physical Windows 11 acceptance.

## Review requirement

Feature branch only; PR stays **DRAFT/HOLD**, stacked on exact R145 SHA `9eb04a2caa1d33b58240dfa89b6484790575ce90` (not production `main`). No WordPress, site, license, premium distribution or public binaries changed. Independent QD review and founder authorization remain mandatory, and all six apps stay **UNRELEASED**.
