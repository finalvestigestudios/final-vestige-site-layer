# R16 — PR #157 stale-safety-repair reconciliation / Preparedness Archive

**Issue #136 | 2026-10-31 | DRAFT / HOLD | may_publish=false**

## What the authenticated repository actually shows

PR #157 is a **draft, unmerged QA proposal** at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, based on the earlier START contributor branch. Its two proposed one-line article replacements are **not directly applicable** to current R15 integration `2492be67054ca1228752df64368ad75dec8dc586`: both *old* lines occur **zero** times in the actual integrated articles. Both QA *replacement* lines also occur **zero** times. Do **not** cherry-pick the patch or assume this proves the articles safe.

The current integrated `household-emergency-plan.body.html` (Git blob `8ca5c261dba56eeaf79c445332381a74867233de`) already describes a **simulated outage**, says to leave power running to critical equipment, and explicitly says **not to switch off the main breaker as a drill**. The current `three-day-kit.body.html` (Git blob `ef5463ca668166766ca3d868908bc0bcb6040a23`) already has an expanded medicine-refrigeration warning, clinician/pharmacist contact advice, a discussion of conflicting older and newer FEMA wording, and citations to the December 2023 FEMA sheet and Ready.gov. This is **content-provenance and text-presence evidence**, *not* a source-quality or medical-safety approval.

R16 independently counted **57** inline citation tokens in the integrated household-plan body and **75** in the integrated kit body (these are two articles only, not the full corpus). Their original Git blobs remain unchanged.

## Why a raw QA PR merge would be dangerous

The integrated `preparedness/taxonomy.json` Git blob is `eea601e53e16e36cd4fc890876bc249b39632370`, versus QA branch `d20ff18bc6f243e08796c0505981979a10fca2d9`. Five article `gate` flags already true in integration would be reverted to false if the QA version replaced the current file: `water-math`, `two-week-water-storage`, `pantry-rotation`, `family-communication-plan`, `warnings-radios-offline-maps`.

The integrated START source fragment blob `29574c328cbab0548e6e5d4a026694857d56b6b4` differs from the QA fragment `d5a5087042381227d840675d9eb08ddc375d21e8`. The authenticated per-source comparison found eight differing/missing source entries, including expanded reading-scope limitations and the newer FEMA power fact-sheet context. **Never overwrite the integrated source fragment with the old QA copy.** Source reading depth, page limitations, and exact citation explanations are evidence.

A machine-readable, source-pinned comparison lives in `preparedness/docs/R16-CURRENT-QA157-RECONCILIATION.json`. The separately drafted #157 changes require their own human disposition; the comparison does not close independent QA.

## R16 executable gate

`preparedness/tools/qa_current_copy_concordance.py` checks exact Git-blob parity for both current bodies, START source fragment and taxonomy, and 35 body/metadata pairs plus the exact slate URL set. It verifies specific already-present caution text and source tokens, rejects stale QA preimage/replacement strings and source rollbacks, and **always reports HOLD / may_publish=false**.

Run only against a trusted checkout with the full unpublished corpus:

```bash
python -I preparedness/tools/qa_current_copy_concordance.py --repo-root .
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The first command is read-only. The native build must remain local and draft-only; no CMS importer, public navigation, or WordPress API writes are authorized.

## Exact verification and release blockers

Locally executed **588/588 Python tests pass**, comprising 548 prior R10–R15 tests and 40 R16 adversarial tests. The two newly committed Python files have Git blobs exactly matching the locally tested bytes: R16 validator `f27fbde936c0aef132a46dfca09243c269432b43` and R16 test `aae4df947a06c663d975c4c4e7f7820015782e64`.

The local environment still cannot resolve `github.com`, so it cannot clone the private repository and run the native validator, build, and real 35-article R16 Python CLI. GitHub connector-based read-only checks **do not replace** those tests. No new hosted CI run is observed on the R15 HEAD.

Independent PR #169 is an **unmerged synthetic-fixture test proposal** at `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Consider it separately in trusted native integration; do not claim it is incorporated.

Seven Claude author branch heads were independently compared with their frozen SHAs on 2026-10-31 and found identical. Their Git graphs remain diverged; byte parity is not merge ancestry.

**Unresolved release blockers:** 30 shared-URL groups, 15 unread base placeholders, no independently documented source/claim verification of the 1,959 cited occurrences, qualified emergency/medication/water/food safety review, integrated native build and hosted CI, and independent QD. No source, site, navigation, WordPress, or article body was changed during R16.
