# R133 — Immutable 35-article citation and source custody gate (DRAFT / HOLD)

**Scope:** Preparedness Archive only, Issue #136. Conversion coordination #820 and business charter #818. Review branch parent is R132 PR #1012 commit `5685b54796d520e8dd50e0cdf4d35e38c9cec7a4`; original release-candidate PR #584 commit `ddb3528ba6494dada1fa1c3a142ce746e3a67706`.

## What changed and what did not

An actual Git-tree read of the R132 head confirmed **35 article body HTML blobs + 35 corresponding metadata blobs + 8 source-register blobs + taxonomy + crosswalk = 80 immutable Git objects**. Those SHA-1 Git blob identities, including every article, are pinned in `locked_files.json`. `r133_snapshot_gate.py` re-reads local bytes and compares exactly to those entries. It checks full slate/route uniqueness, that every article remains in draft status, four Start Here safety gates, all 32 source-group review holds, source ID interpretation scoped to its author (or base), nonblank per-article source-use explanations, source verification-date presence, and **visible vs hidden citation tokens**. It refuses to treat citation tokens in comments, attributes, scripts, templates, inert or hidden elements as reader-visible evidence. It also rejects unmanifested article bodies, metadata and fragment registers.

**All evidence stays untouched.** The 35 articles, 35 meta records, eight source registers, crosswalk, taxonomy, WordPress builder, existing QA #157/#169, and homepage owners' branches are byte-for-byte unchanged. R133 creates only one manifest, one review-only Python gate, one isolated test module, and this documentation. Existing R132 crosswalk integrity checks remain authoritative for exact source variant content; R133 is an *additional* independent read-only gate, not a replacement for R124/R132 or a qualified reviewer.

Run in a **trusted full repository checkout of this draft branch**:
```bash
python -I preparedness/tools/r124_source_crosswalk_integrity.py --root .
python -I preparedness/tools/r133_snapshot_gate.py --root .
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```
The validator **returns structural status HOLD on a clean scan**, never QD PASS or publish eligibility. A true Python 0 exit from this gate only means its enumerated structural invariants held, not that health, food, fire, electrical or water advice is safe or that any link/claim was human reviewed. Positive existing `safety_review: approved` metadata is historical and does not constitute independent QD clearance.

## Evidence obtained this round

- **Exact branch heads rechecked via GitHub refs:** Start `2122d856fce9f64887c16df3d52e64be9f59a55b`; Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`.
- All seven Git refs are reported, **not** indiscriminately merged. The Food branch still diverges from the frozen candidate; S-7 jerky citation-ID conflict remains unresolved. The 32 crosswalk groups have structurally complete membership from R132 but **zero human adjudications**.
- QA PR #157 remains draft `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, with the independent electrical-drill and refrigerated-medication wording issues unresolved. PR #169 remains draft `e9cd7766dac59d47ab467d8945269b9146c2aef5`; shared-tree duplicate fixture is still present there, with proposed repair only in draft PR #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`.
- Homepage #49 `10495883299d53596992c26a8987f629b2904670` and flagship #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` were read-only checked.
- **60 isolated Python synthetic/adversarial tests passed locally**, plus Python compilation, using temporary 35-article fixtures only. They test 35 independent Git-blob tamper cases, source-use and source-check tampering, hidden citation laundering, false safety upgrades, malformed citations, duplicate routes, path traversal and unpublished states.
- **NOT TESTED:** the actual R132 35-article gate in a full trusted local checkout, complete native `validate.py`, WordPress draft builder, existing 36+ repository regressions, browser QA, GitHub Actions/integrity or qualified QD. Local git clone failed with `Could not resolve host: github.com`; the GitHub connector nevertheless provided the source file identities and permitted isolated draft-branch writes. Do not mislabel synthetic tests as full repository integration success.

## Conversion-first dependency and acceptance handoff

**Audience/intent:** households seeking a practiced emergency-contact, school pickup and reunification plan. **Proposed free destination:** the existing source-backed `Household Emergency Plan` article (`/preparedness/start-here/household-emergency-plan/`), **still DRAFT/HOLD**, not a live link. **Optional free tool:** previously drafted family-reunification printable only after its independent print/mobile/privacy review. Never require purchase or sign-up to access essential emergency information.

**The sole paid-offer candidate is a *slot* awaiting verification, not a newly claimed FV product:** choose ONE existing FV-owned and currently purchasable Preparedness SKU **only if** primary merchant listing, seller rights, exact price, checkout, license/disclosures, refund policy and downloadable delivery can be authenticated. None was verified in this run. Do **not** activate a product CTA, offer a price, reuse the retired water freebie, invent an affiliate approval or confuse third-party Payhip emergency planners with FV-owned inventory.

Draft CTA *for staged, nonpublic review only*: “Make a plan you can practice. Read the source-backed household guide and use the optional printable contact plan.” A **paid** CTA is **withheld** pending an authenticated product and founder approval. Sample future purchase description must state that it is an optional downloadable planning aid, *not official emergency or medical advice*, and that the free guide is available independently.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Existing Preparedness SKU → actual purchase | Product rights, seller SKU, checkout, delivery and refunds unverified | Merchant/product verification and real downloadable file QA; no invented SKU or price | **UNVERIFIED / HOLD** | Growth + Claude |
| Free Household Emergency Plan → useful read | 32 source interpretations, citation/medical/electrical safety decisions and full build unapproved | Run R124/R132/R133 on full checkout; human source/safety decisions, page preview, mobile and accessibility check | **60 local synthetic tests PASS; full checkout NOT TESTED** | Preparedness + independent QA |
| Grok social asset → correct landing | TASK-008 does not authenticate any Preparedness-specific asset_id, post URL or campaign | Praxxis/Grok provide actual asset_id, rights QA, platform-permitted CTA and final approved destination | **UNVERIFIED** | Grok/Praxxis |
| Guide → optional free printable | Existing printable not independently accepted | Test 360/390/768/1440 widths, keyboard use, print output, no server upload of family details, free access | **DRAFT, NOT TESTED** | Preparedness/Site QA |
| Guide → optional paid pack | No verified matching FV product; checkout friction unknown | Only after product confirmation, check descriptive/accessible CTA, accurate terms/price, merchant acceptance, download receipt and refund path | **HOLD** | Claude/Site QA |
| Paid order → realized net revenue | No reconciled merchant paid orders, human sessions, fees or refunds | Match immutable Grok asset_id/UTMs → landing → CTA → confirmed lead (if any) → merchant-confirmed order → refunds/fees; report 7/30-day cohorts with tiny-sample warnings | **NOT COMPUTABLE** | Growth |

**Revenue per 1,000 qualified-human sessions: N/A (missing source-of-truth numerator and denominator).** Views, clicks, signups and checkout starts never count as paid orders. Do not add measurement scripts or change the existing working Focus signup. Canonical handoff remains TASK-008 and dated Praxxis/Grok Drive, without claiming Grok production ownership.

**Release:** DRAFT / HOLD. No merge, WordPress/CMS write, page publication, nav, homepage, email, analytics, merchant, affiliate, social or spend change. Founder retains release approval.