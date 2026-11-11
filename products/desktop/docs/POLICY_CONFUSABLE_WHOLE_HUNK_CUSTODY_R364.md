# R364 — Policy Delta Desk all-or-nothing look-alike source citations

**2026-11-11. Draft engineering change; NO release authorization.**

## Concrete defect / before-and-after

The Policy Delta Desk's supplemental Latin/Cyrillic/Greek look-alike
navigation accepted a list of already-constructed diff hunks. Before R364,
`render_local_confusable_evidence` used `continue` on an invalid hunk and
could still emit authoritative-looking physical source-line cues from earlier
and later hunks in an incomplete, untrustworthy direct-call collection.
The NFC and NFKC supplemental navigation helpers instead reject the whole
collection. The core source-byte SHA-256 and unified diff remained separate.

R364 changes the malformed-hunk branch to **return no supplemental look-alike
navigation for the entire collection**. It validates all hunks before emitting
cues, retaining the established rejection of repeated/backward coordinates,
hostile container subclasses, unsafe source field keys, and invalid source
types. It retains independent bounded omission of **valid** overlong lines;
such lines do not invalidate correct, short candidates. Real file-based
unified-diff input is ordinarily well formed; the principal affected
boundary is direct helper use or a regression in hunk assembly.

This change deliberately revises one R182 legacy expectation: skipping a
malformed hunk is no longer considered safe. The old test now requires
global suppression. It is not a new legal interpretation, fraud flag, or
change to source bytes, financial data, premium access, or QD policy.

## Exact local evidence (Linux, isolated module)

- Executed the complete **new** 16-case R364 test file using Python with
  `-W error`: **16/16 pass**; repeated under `-OO -W error`: **16/16 pass**,
  **32 passing case executions** total.
- Exact helper and test Git blob SHA-1 identities reproduced by local
  `git hash-object`-compatible calculations:
  - `fvs_suite/policy_confusables.py`: `1dd991854cd7a671a24d5f7899b9b8a44ed303c4`
  - `tests/test_policy_confusable_whole_hunk_r364.py`: `dc1f9b0302f57709da557523223388736e9d5f1f`
- Reverted that local helper to the **exact pre-change Git blob**
  `0f89919bd07d48d1694e06f1035f501d1761eb08`: the same new tests
  reproduced **10 expected failures of 16**, showing the previous
  partial-navigation behavior (not a hosted CI result).
- Added mandatory existing R182 + new R364 normal and optimized test
  invocations to the **Ubuntu and Windows** desktop workflow, with Windows
  `$LASTEXITCODE` fail-closed checks.

**Not executed:** R182 full legacy file, the complete application integration
suite, the four workflow validators, 22 real AES-GCM integration cases, or
Windows-native packaging / GUI / Defender / entitlement acceptance. The
isolated local copy is byte-identical only for the two cited files; this
does not establish full-repository correctness.

## Gates and next action

All four free and two premium standalone apps remain **unreleased**. No
executables, site publishing, public premium URLs or production changes.
This PR stacks on R363, stays draft, and requires independent QD review and
founder approval before any merge or distribution.

Restore GitHub Actions runner allocation, execute the R182/R364 changes
together with the inherited suite and 22 genuine AES-GCM cases. Only then
move toward native Windows 11 x64 build/smoke, hashes, Defender scanning,
keyboard and screen-reader checks, entitlement verification and QD signoff.
