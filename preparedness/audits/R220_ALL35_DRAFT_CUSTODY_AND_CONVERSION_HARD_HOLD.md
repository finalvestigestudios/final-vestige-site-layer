# R220 — all-35 original/integrated-source and 41 WordPress draft custody (DRAFT / HARD HOLD)

**Governance:** Preparedness integration and citation safety #136; conversion attribution #820; business charter #818. **BUILT; 246/246 isolated synthetic unittest methods PASS; native repository validation/build NOT EXECUTED.** All release, independent-QD, human-source, medical-safety and merchant-acceptance states remain **HARD HOLD**. This is *not* an authorization to merge, publish, edit WordPress, navigate, activate commerce, send emails, post social content or spend.

## What changed (R219 → R220)

Prior R219 PR #1602 checks the 3 unresolved source uses and the transport of Articles #7/#20 to four WordPress/preview output files. R220 adds a broader **read-only, fail-closed all-35 article / 41 individual article-and-tool export gate** alongside R219, without altering R219 or the seven contributor branches.

New files:
- `preparedness/tools/r220_full_slate_draft_custody.py` — Git blob **25b76d731cc9e1cce2cece25444e14a7cb749c3f**, 15,223 UTF-8 bytes.
- `preparedness/tests/test_r220_full_slate_draft_custody.py` — Git blob **2abdf534a18a884068214900f83114960db91c25**, 11,315 UTF-8 bytes.
- This audit record only. No original article body, metadata, URL, source register, rendering engine, taxonomy, shared frontend, production integration, CMS or navigation changes.

The guard pins the R200 original 35-article custody manifest (Git blob `5822f9dfde21d1f3bdfc26658769d852c639438c`) and separately pins the **exact currently integrated R219 source identities**. It checks source provenance, seven original contributors, per-article slug/section/route ownership, article metadata and draft status, citation explanations, frozen internal-link target set, and authored HTML body-byte SHA identities. On a native build it additionally checks exactly 41 article+tool report entries, canonical URL uniqueness, ordered sources and word counts, and that the original fully resolved body occurs exactly once in *each* WordPress and preview export (82 individual HTML outputs). It rejects missing/mutated drafts, substituted SHA identities, duplicate JSON keys, symlinked input paths, duplicate URLs and unauthorized approval flags.

The generator also produces section hubs and the Archive landing output; **R220's count of 41 refers ONLY to the 35 articles + six tools**. Landing and section hubs are NOT covered by this gate. HTML semantic visibility, browser CSS, source factual accuracy, accessibility, crosswalk adjudication and independent safety review remain independent work.

## First authenticated integration census against R219

This run fetched **35/35 actual integrated body Git blobs and 35/35 integrated article metadata blobs** using the connected private GitHub repository. Compared with the immutable seven-contributor R200 originals:
- **14 / 35 article bodies have distinct integrated blob identities:** #1, #2, #12, #13, #14, #15, #16, #20, #24, #25, #27, #32, #33, #34.
- **21 / 35 article bodies still exactly match** the contributor snapshot.
- **12 / 35 metadata files have distinct integrated blob identities:** #2, #6, #7, #12, #13, #14, #15, #20, #21, #24, #25, #34.
- **23 / 35 metadata files exactly match** the contributor snapshot.

Every changed identity is now an explicit **custody receipt**, *not* an assertion that the change is correct, safe, or deeper. A later unreviewed byte change fails the guard rather than silently discarding the newer version or rolling back to a historic file. These integrated changes require qualified human semantic/diff review before merge. Metadata includes legacy `approved` labels on some draft articles; R220 never treats these as QD or contemporary medical-safety approval.

The original 3 unresolved article-level source uses remain a **HARD HOLD**: two `cdc-find-clean-water` uses in Article #7 and one `start-ready-plan` use in Article #20. Seven historical shared-source-ID reading-scope conflicts also remain pending. Do not interpret a citation appearing in a source register as verified support for the surrounding medical/water/food claim.

## Exact coordination snapshot, 2026-11-08

Seven source branch HEADS, rechecked on GitHub (unchanged):
```
claude/prep-start-bbfeb8       2122d856fce9f64887c16df3d52e64be9f59a55b
claude/prep-shelter-5e1e0e     5daeaf2dd5ab71806a6b73c91edfb1d8df5da976
claude/prep-food-ccdc55        f911ff7a655de8d81535ea86ec3d65a49ee76648
claude/prep-health-837444      d5ef5bafd68361434dd1cc9209915b8e8a4eaf17
claude/prep-hist-field-9db767  4e5caf812727953aa45e3bda2d382f2c67b6a09c
claude/prep-hist-food-b81f19   67e116e536c7410bed30f8f3b1bb8c166f3c223d
claude/prep-hist-home-0e0e38   7504a5f099594d635e3dd7332a33a2e1346c43a2
```
Independent QA #157 draft HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (older Start Here base, do not overwrite newer wording); food synthetic-fixture #169 draft HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`, follow-up #973 draft HEAD `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` (both unmerged). The home/EX2 lead has separate active PRs #1601 and #1607; no edits or unrequested merges performed. R220 stacked exactly on R219 #1602 at commit `94f5deaa4ed0f17dcee89e7a267440430ff43cac`.

## Tests — synthetic != authentic

Executed locally with Python:
```sh
python -m py_compile preparedness/tools/r220_full_slate_draft_custody.py preparedness/tests/test_r220_full_slate_draft_custody.py
python -I -m unittest discover -s preparedness/tests -p 'test_r220*.py' -q
python -I preparedness/tests/test_r220_full_slate_draft_custody.py -q
```
All **246/246 isolated synthetic tests PASS** via discovery and direct invocation; Python compilation PASS. Test methods exercise all 35 route-head checks, 35 body mutations, 35 metadata mutations, 41×2 WordPress/preview truncations and positive/negative custody cases. Tested file bytes match the two Git object identities above. **Tests do not include the original 35 articles or actual 41 exported WordPress files.**

Native `git ls-remote` fails locally with `Could not resolve host: github.com`, preventing obtaining the complete authentic repository in the execution runtime. Connected GitHub reads/writes do work, but they do not constitute a native `validate.py`, `build.py`, independent QD or checkout test. On a trusted checkout run the following, without any deployment:
```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r219_source_to_draft_chain.py --help
python -I preparedness/tools/r220_full_slate_draft_custody.py --root preparedness
```
The final R220 command must return `2 = DRAFT_HARD_HOLD` on held and structurally consistent inputs or `3 = INVALID_HARD_HOLD` on invalid/incomplete evidence. It never returns a publication PASS. Native repository scripts and all genuine exports remain **NOT EXECUTED** in this run.

## Conversion-first single-path acceptance (no activation)

**Verified topic intent to pursue, subject to asset matching:** household emergency contacts, insurance/financial documents and record locations before evacuation or a caregiver becoming unavailable. **Existing public free offer:** ungated `https://finalvestige.com/preparedness/`. Detailed new guides/tools remain unpublished and cannot serve as public campaign destinations. **One provisional commercial candidate only:** existing Legacy Triage `https://payhip.com/b/n1RhV` (publicly advertised $19 PDF by Vested Wisdom), not proven owned/rights-cleared, checkout-valid, secure in use or correctly fulfilled; no paid CTA permitted.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Grok's EXISTING relevant social asset → public free Archive | Actual immutable `asset_id`, post URL, platform, posted_at, hook, rights and link pairing are unverified | Match TASK-008 record to published real post and approved URL/UTM; do not fabricate IDs or alter Grok queue | **UNVERIFIED** | Grok / Praxxis |
| Public Archive → researched guide | Original claims and source exceptions have unreviewed safety and provenance gates | Source-adjudication, full native build, mobile accessibility, guide intent parity; preserve ungated emergency guidance | **HARD HOLD** | Preparedness / independent QA |
| Free record planning → optional Legacy Triage PDF | Merchant rights, completed-document privacy/security, PDF suitability and disclosures unverified | Independently inspect pack, rights, disclosure and safe-storage expectations before enabling sales language | **HARD HOLD** | Founder / Commerce |
| Disclosed optional product → confirmed order | Checkout, currency, tax/fees, refund and delivery not tested | Founder-authorized end-to-end receipt and download/fulfillment inspection | **NOT TESTED** | Commerce |
| Qualified human sessions → paid orders → net receipts | No authoritative accepted orders, fees/refunds, human-session or Grok `asset_id` attribution | Reconcile legitimate 7/30-day cohorts; calculate net revenue / 1,000 qualified human sessions only with denominator and merchant records | **NOT COMPUTABLE (not zero)** | Claude analytics / Commerce |

**Draft free CTA only, NOT live:** “Would everyone in your household know where to find emergency contacts and the essential records if you couldn't answer the phone? Start with our free Preparedness Archive.” Optional commercial CTA **disabled pending review**. Keep Seven Day Focus Fieldbook as the established site-wide opt-in, and do **not** restore retired water freebies or create unapproved products. No attributed paid sale, lead, merchant payout, click or net revenue is claimed.

**Strict governance:** Claude owns core production website/analytics work; Grok owns content creation/distribution; Praxxis handles independent research/asset QA; founder approves spending/production releases. R220 performs no CMS, navigation, homepage, analytics, social, email, affiliate, merchant or production writes. All 35 articles and 41 exports stay **DRAFT / HARD HOLD**.
