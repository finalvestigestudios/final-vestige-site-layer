# R177 — Hazard-Critical Draft Wording Custody (DRAFT / HARD HOLD)

Scope: Preparedness Archive #136 only. Conversion attribution coordination #820; business charter #818. Parent: **R176 PR #1307**, exact base commit `73fe9e2d7ca434288f30027e8cde71de65c8fcf2`. Additive changes only: this reviewer record, a pinned JSON contract, a read-only gate and synthetic tests. No edits to any of the 35 originals, source register, taxonomy, site navigation, CMS, homepage, merchant, analytics, content distribution or signup flows.

## Finding: independent safety PR #157 and the current draft are not identical

Read independent QA PR #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`: it proposes not turning off the household main breaker in a rehearsal and requires clinician/product-specific context before medicine disposal decisions. Its patch is based on the older Start Here branch. **The R176 original draft already carries different, more detailed nonessential-only simulated-outage wording and an expanded, explicit discussion of conflicting FEMA medication guidance.** Thus #157 must be independently reconciled rather than blindly cherry-picked or called merged. Fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` and follow-up #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` remain separate and unmerged.

The authentic R176 blobs checked read-only via GitHub were `f81cd43516e8295104230412f18776919148f905` (Household Emergency Plan) and `933f38ff3cd55a241cf9b392014fc52d4961e84f` (Three-Day Kit). All contract fragments were observed in these source files, including the instruction not to shut off the breaker and the warning to consult a clinician about refrigerated medicines. This is **source-text presence inspection only**, not a pass from executing the authentic Python gate or the WordPress renderer, and cannot confirm medical safety.

## What the gate checks

`preparedness/tools/r177_safety_wording_gate.py` reads the pinned contract at `preparedness/review/r177/safety_contract.json`. The tool hard-pins the manifest's SHA-256, so removing any of its required safety phrases or article scope without code review is rejected. The manifest identifies the two already-existing safety-critical draft articles, visible HTML sections, and specific existing warning fragments. The structural gate rejects missing or duplicated passages, concealed HTML nodes, unexpected source/export substitutions and recognized contradictory instructions to switch off main power as a drill or blindly discard refrigerated medication. It emits only SHA-256 file identities and diagnostic errors, not personal data.

Use it read-only on a trusted exact checkout:

```bash
python -I preparedness/tools/r177_safety_wording_gate.py --repo .
python -I preparedness/tools/r176_native_review_preflight.py --repo . --timeout 300
python -I preparedness/tools/r177_safety_wording_gate.py --repo . --check-export
python -I -m unittest discover -s preparedness/tests -v
```

The second R177 command requires authentic prior `preparedness/build/wp/` drafts. Execute R176 natively before the export check; R176 itself copies and checks an isolated corpus and does NOT populate the original checkout's build directory. If no local WP drafts exist, the optional R177 export check **correctly rejects missing files**. Both R176 and R177 intentionally exit **2** even for structurally intact drafts. Read their JSON and error counts; a held draft is never an authorized release. R177 is not an OS/network sandbox, browser accessibility audit, human source or safety adjudication, or substitute for R174/R175 whole-corpus citation/link gates.

## Evidence

- Local Python compilation PASS; **54/54** synthetic unittest cases PASS, no skips. Includes every required fragment removed from source and/or rendered mock HTML, hidden/commented wording, duplicate blocks, unsafe positive main-power instruction, false commercial/safety approval flags, missing exports, and weakening/tampering of the pinned manifest. Python exact committed Git blobs: gate `febf37090e00c82700da4cf228ba900983bf15ec`; tests `54fb6b6a314645f21a037f9cc010a2a9b0ec5c07`; pinned JSON `6b44d02b067f8393541e16e31a03284bf8df91eb`.
- GitHub clone remains unavailable to this local runner (Nov 6: `Could not resolve host: github.com`). No authentic 35-article validation/build/unittest or authentic WordPress export gate executed. Prior R176 and R175 synthetic evidence is not retroactively promoted to real corpus PASS.
- R161 original custody manifest at `fede4222c796d92798eff7cf0dcb225c291f7d61` still declares **35** originals, **2,000** citation occurrences and **385** article-specific source relationships, but does not establish this round reran the complete corpus. Existing 75 source decisions, 32 shared-URL groups, 11 Family Card source decisions and 10 jerky-claim decisions remain human HOLD. Do not equate historical safety with current advice.

## Seven contributor heads (fresh exact-GitHub comparisons, all identical, 0 ahead / 0 behind)

| Cluster | Current branch | Current SHA |
|---|---|---|
| Start Here | `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Food | `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Shelter | `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Health | `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical Field | `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Historical Food | `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical Home | `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Homepage lead PR #1300 at `b03ced998272a8dec5a70c5f6a48b31d54fe6599` was reviewed as separate ownership and left untouched.

## Conversion-first, one audience, one honest free-to-paid path

Audience: caregivers organizing emergency school pickup and family reunification. **Authentic existing free DRAFT**: Household Emergency Plan, proposed `/preparedness/start-here/household-emergency-plan/`; not live and not a lead gate. Optional existing free Family Reunification Card remains source/privacy/print held. Draft caption/on-site CTA, NOT approved for publication: “How would your household reconnect if schools and phones were disrupted? Read the free Household Emergency Plan, then prepare a contact card.” No instructions or gate behind a merchant CTA.

**Do not introduce a paid pack** until Commerce independently verifies one existing rights-cleared genuinely purchasable Preparedness SKU, merchant acceptance, pricing and terms, source provenance, actual download delivery, and refund/fee handling. None was authenticated this round. The active TASK-008 social pilot is Mini Museum-first and no published Preparedness Grok asset_id, actual post URL or approved destination was present in reviewed handoff. This proposal is not a new Grok assignment. Do not alter the existing free Focus Fieldbook offer or resurrect a retired water freebie.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Owned Preparedness paid pack → settled order | Rights, authentic offer, checkout, fulfillment and refunds unverified | Verify ONE existing listing + real delivery/refund terms before drafting paid CTA | HARD HOLD; no authenticated order | Commerce / Claude |
| Household Emergency Plan → free reader | Sources/safety/QD and native build unresolved | Independent adjudication; execute R176 + R177 against real output; mobile review | 54 synthetic tests PASS; authentic NOT RUN | Preparedness / Site QA |
| Free guide → optional Family Card | 11 source decisions, privacy/printing and browser checks open | Test real staging at 360/390/768/1440 with synthetic data only | HARD HOLD | Site QA |
| Grok asset → matching free guide | Creator-owned asset_id/post/destination not authenticated | Reconcile TASK-008 with Praxxis/Grok, protect Mini Museum priority | UNVERIFIED | Grok / Praxxis |
| Qualified-human session → net paid revenue | No verified creator-campaign denominator, transactions or refunds/fees | Use approved existing consent-respecting measurement; reconcile asset_id/UTM → landing → CTA → confirmed lead → settled order → net in 7/30-day cohorts | NOT COMPUTABLE; small-sample warnings mandatory | Claude / Commerce |

**FINAL: BUILT / SYNTHETICALLY TESTED / DRAFT / HARD HOLD.** No release approvals, source or medical safety determination, paid CTA, affiliate activation, public WordPress/CMS/navigation writes, posting, email, analytics scripts or spending.
