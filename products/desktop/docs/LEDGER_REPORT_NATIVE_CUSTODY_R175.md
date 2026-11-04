# R175 — LedgerDiff Lite report source custody (DRAFT / RELEASE HOLD)

## Threat and correction

The direct `attach_ledger_provenance()` API accepted Python `str` subclasses for left/right SHA-256 identities (`isinstance`), and expanded arbitrary report dictionaries (`**row`) without validating their underlying source values. Adversarial subclasses could misrepresent matching source digests via comparison hooks, create a false *identical input* review state, or forge financial display columns through custom mapping methods. Mutable nested values in an evidence-bearing report could be changed after issuance or execute a conversion hook during CSV writing. This is a **direct Python API trust boundary**, not a claim that hostile objects can originate from ordinary CSV files.

R175 requires built-in `str` for SHA-256 identities; validates the plain list container; reads each row from the base `dict` storage via bound `dict.keys`/`dict.items` instead of virtual methods; rejects non-native report field keys and values; then returns a fresh row with both verified snapshot digests and a human review flag for byte-identical inputs. Ordinary imported CSV strings and exact money text are unchanged. Raw customer input and existing rows are not modified or logged. Fingerprints prove bytes in the imported snapshot, not file authenticity or source independence. No approval or payment decision occurs.

## Verification contract

`python products/desktop/scripts/safe_unittest_r175.py` and `python -OO products/desktop/scripts/safe_unittest_r175.py`, with `PYTHONPATH=products/desktop`, require exactly **32 test methods** each, zero skips, and no unredacted financial values in diagnostics. The repository desktop CI includes an identical hard gate on Ubuntu and native Windows. Full cross-platform target: **128 focused method executions** (32 × 2 interpreters × 2 OSes) plus inherited source tests and six private Windows x64 candidate builds.

Tests use only synthetic digests and ledger rows; cover original cent strings, physical line references, caller row independence, duplicate input review, digest subclass attacks, fake dict views, bad keys/values, hidden mutable values, and stable deterministic repeats. Full historical suite and actual Windows packaging are required separately; local focused tests are not release approval.

## Release governance

Build candidates are internal-only. Never claim an unexecuted Actions run passed. Pending mandatory physical Windows 11 independent 46-observation accessibility acceptance, genuine Defender/EDR assessment, code signing, authenticated premium distribution, independent QD exact-head approval, and founder authorization. No production merge, publication, CMS edits, or unrestricted premium links without those gates.
