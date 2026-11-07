# R190 — Native source/citation + authentic six-tool privacy draft admission (DRAFT / HARD HOLD)

**Lane:** Preparedness Issue #136 only. Commercial coordination #820 and charter #818. **Parent:** R189 exact `84a4c3e47dae1a5a140316af363dc121f1a43fb0`. Entire PR draft only; no merge, release or CMS writes.

## Root cause and patch

1. R189's draft-HTML privacy scanner rejected **every native builder-inserted print button**: `build.py` adds `<button type="button" class="pa-btn pa-btn--ghost" onclick="window.print()">`, while R189 rejected *every* `onclick`. This creates a synthetic-green/authentic-red failure even when no exfiltration exists. The narrow correction allows **only that exact local button signature**, with exact handler text. All other onclick/event handlers remain prohibited; new R189 regression contains one builder-print positive and seven malicious/wrong-context negatives. This is a static HTML boundary, not a general client-side security or privacy PASS.
2. R188's whole-archive native preflight uses a disposable copy and deletes **its generated exports**. R189, run separately afterward on the original checkout, then cannot inspect the authentic six WordPress tool exports. R190 adds a source-pinned **joint diagnostic** that verifies all 16 original producer identities, runs the 12-step R188/native validator/build/test/source-citation pipeline, then performs a second build **only on a separate disposable copy** and runs R189 against the actual six generated draft HTML files. Original authored source is compared before and after, including a no-symlink and file-size bounded SHA256 inventory. The second build is necessary because R188 intentionally discards its own build outputs.
3. Strict receipt admission requires: 35 original articles; six companions; 41 unique draft canonicals, zero published; 12 complete native/source/citation/safety stages; nine inlined JS modules, six original tool bodies and six generated exports; no unsupported safety/QD/merchant clearance or claimed revenue. Any failed/missing or changed input is `INVALID_HARD_HOLD`; structural success is still **`DRAFT_HARD_HOLD`, exit code 2**.

### Execution evidence — Nov 7, 2026

- R190 local synthetic tests: **82/82 Python unittest methods PASS**, zero skipped; Python `-I -m py_compile` PASS. Tests run in the same `preparedness/tools` + `preparedness/tests` relative structure as the committed files, including 49 deliberately malformed receipt mutations, 12 skipped-stage mutations, and additional source tampering/symlink/size/false-clearance cases. No native full-tree source/citation/medical/food safety or WordPress acceptance claims.
- New R189 print-control test cases are **committed for independent execution**, **not executed against the authentic repo here**. Previously reported R189 57 synthetic tests were not re-run during this round. Do not confuse the R190 82 with the original repository 36+ test suite.
- Original repository cannot be cloned from this local environment (GitHub name resolution unavailable). The full native 35+6 build and 41 authentic export inspections, browser privacy/network/print/keyboard checks, 21 indexed unresolved source decisions, 58 tool-source rows, independent safety and QD remain **NOT TESTED / HARD HOLD**.
- GitHub readback identities (check from branch commit): R190 wrapper `cbf52dda1de707d17e516f4cd22432e1b0e20ea9`; R190 tests `b454cecb5b2f296cbc7c41f53ec34c31cc4c2a88`; R189 amended gate `b98fb8707459b0772ce93e232105d3dc5547bafa`; amended R189 tests `679d5c153d00714644b8b33120a5ad0662c278cb`.

### Trusted complete checkout diagnostic (source-only, does not publish)

```bash
python -I -m unittest discover -s preparedness/tests -p 'test_r190*.py' -v
python -I -m unittest discover -s preparedness/tests -p 'test_r189*.py' -v
python -I preparedness/tools/r190_atomic_native_privacy_preflight.py --repo . --timeout 300
# A fully structurally reviewed snapshot still exits 2 as DRAFT_HARD_HOLD.
```

This is **not** a hostile-code sandbox. Run only on independently reviewed source in an isolated environment. All generated WP drafts are disposable and not public CMS data.

## Exact contributor and agent custody (fresh connected GitHub comparison)

Seven original Claude refs: Start `2122d856fce9f64887c16df3d52e64be9f59a55b`; Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`. **All 7 / 7 compare identical (0 ahead / 0 behind).** Independent #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, stacked #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`: open draft, untouched. Homepage #1393 `94181f88f0de0a3b735ed125842205f38cc9eb1a`, Apollo #1390 `2f70c1161bb965725ebeb78c9bda78ba05847291`: read only.

## Conversion-first friction and acceptance

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (DRAFT ONLY) | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Public Legacy Triage listing → verifiable paid order | Unauthenticated seller ownership, license/rights, current PDF, signed-out buyer checkout, fulfillment/refunds/fees and product fit; about **financial paperwork**, not emergency school pickup | Independently inspect one actually purchasable owned product and merchant ledger; only then draft relevant, clearly optional records-continuity CTA | **COMMERCIAL HARD HOLD**; public listing is not a paid order | Founder / Commerce / Claude |
| Grok household-document video → source-backed free Household Emergency Plan | No authenticated exact published `asset_id`, allowed placement or canonical matching destination; original detailed guide not approved | Grok/Praxxis TASK-008 read-only handoff; suggested topic **“Which household documents would you lose if you had to leave tonight?”**. Until guide is independently cleared, public official-source gateway `/preparedness/` only. | **UNVERIFIED asset**, no production/post assignment | Grok production; Praxxis research/QA |
| Household Emergency Plan → free reader | Human source adjudication, safety, native build and QD pending | Preserve ungated free guide, accurate current-source dates, disclosure and high-intent free CTA in draft | **HARD HOLD** (structural synthetic only) | Preparedness / independent QA |
| Free guide → optional Family Reunification Card (FREE) | 11 unresolved source decisions, paper loss/privacy, printing, keyboard, network testing pending | On approved stage, test fake family entries at 360/390/768/1440px, print/export, no PII network egress; warn a lost card exposes printed details | **NOT TESTED** outside synthetic | Site QA |
| Qualified social session → CTA → lead / completed paid order → fees/refunds/net | No independently validated asset_id, qualified humans, confirmed signup, paid merchant orders, refunds or fees | Reconcile 7/30-day cohorts; net revenue / 1000 qualified human sessions only after all inputs independently verified; do not equate clicks or email interests with sales | **NOT COMPUTABLE (not zero)** | Claude analytics / Commerce |

Draft free-guide CTA (after qualified approval only): **“Plan for the people, contacts and records your household would need if you had to leave. Read the free Household Emergency Plan.”** Optional free tool: **“Print a Family Reunification Card. Protect personal information: printed cards can be lost.”** No paid link yet.

Preserve **Seven Day Focus Fieldbook as sole established lead magnet**, no retired water guide, no new offer. Grok alone owns social content and posting; Praxxis independent verification; Claude core site/measurement; founder all release/spending/merchant decisions. No WordPress, nav, public website, email, analytics script, affiliate or social changes.
