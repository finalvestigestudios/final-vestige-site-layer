# R188 — executable producer custody before whole-archive native checks

**Scope:** Preparedness Archive #136 ONLY; commercial coordination #820 / charter #818. **UNMERGED DRAFT / HARD HOLD.** This is not qualified safety review, source-claim adjudication, independent QD, WordPress approval, merchant authorization or evidence of actual traffic/revenue.

## Concrete risk and fix

The previous R186/R187 integrated preflight checked 35 articles, six companion tools, 41 draft routes, native validation/build/36+ tests, nine review-gate receipts, source-citation integrity and explicit held status. However, a replacement native build/validator or one of the nine producer programs could emit a structurally plausible receipt while the reader assumed the correct tool ran. R187 bound **receipt shapes** but did not independently bind **the executables that produced them** to reviewed Git identities.

R188 introduces a **producer-code Git blob custody precondition** before importing/running R186. The pinned roster contains **16 independently fetched, authenticated original scripts** from the exact R187 parent commit `c881583358c485dcc02ca69e6cc275cd395a287a`: native `validate.py` and `build.py`, R161 original-body custody, R174/R175 citation/link custody, R176 prior native runner, R177/R178 safety-wording/state, R179 source crosswalk, R180 human-review docket, R181/182 independent PR reconciliation, R184/R185 exported article/tool gates, R186 integrated runner, and R187 strict receipt verifier.

The pin algorithm uses Git's **actual blob hash** (`SHA1("blob " + byte_length + NUL + bytes)`) rather than a plain SHA-1 or a file path alone. All paths must be in `tools/*.py`, be regular files, and reside under real, nonsymlinked Preparedness and tools directories. A missing, modified, replaced, oversize or symlinked script yields **INVALID_HARD_HOLD** before R186 is imported. Expected legitimate code updates require conscious review and repinning; there is no mutable runtime allowlist, environment bypass or automatic 'approved' state. The source bytes never leave the local machine in receipts.

**Recommended review-only command from a complete, trusted checkout:**

```bash
python -I preparedness/tools/r188_producer_bound_preflight.py --repo . --timeout 300
python -I -m unittest discover -s preparedness/tests -p 'test_r188*.py' -v
# Ordinary native validate.py/build.py/full suite are also invoked by R186
# only AFTER the R188 code custody precondition passes.
```

The command always exits **2**, on both valid structural hold and invalid hold. A valid structural packet is **DRAFT_HARD_HOLD**; it can never become a release pass. This is an integrity check in a trusted checkout, **not a sandbox against malicious Python, a self-authenticating root of trust, an independently audited source or a safety clearance**. The R188 entrypoint itself must be reviewed through the draft PR and GitHub commit, not presumed trusted simply because it runs.

## Exact local execution evidence, 2026-11-07 PT

- New code: `preparedness/tools/r188_producer_code_custody_gate.py` and `preparedness/tools/r188_producer_bound_preflight.py`.
- New tests: `preparedness/tests/test_r188_producer_code_custody_gate.py` and `preparedness/tests/test_r188_producer_bound_preflight.py`.
- **77/77 Python unittest cases PASS**, including **16 × 3 independent changed/missing/symlinked producer mutations**, 16 wrapper pre-execution corruption cases, invalid roots, wrong Git blob algorithm, malformed pin paths, symlinked tools dir, deterministic manifest, false approval and invalid timeout checks. **0 skipped**. Executed a second time under actual `preparedness/tools` and `preparedness/tests` layout. `python -I -m py_compile` PASS.
- Local incomplete-checkout execution correctly returns JSON `INVALID_HARD_HOLD`, exit 2, identifying the first absent pinned producer. **This is not authentic full-repo execution.**
- The complete repository cannot be Git-cloned in this runtime: `Could not resolve host: github.com`. Therefore the full 35-article/six-tool build, complete native suite, WordPress exports, staged browser/print/privacy QA and independent medical/food/source/QD reviews **remain unexecuted/unapproved**. Connected GitHub code readback can compare exact blob identities; it does not replace a native checkout.

## Seven frozen Claude contributor inputs / independent QA boundaries

Exact original contributor refs remained **identical, 0 ahead / 0 behind** against recorded SHAs on 2026-11-07:

| Cluster | Frozen original commit |
| --- | --- |
| Start Here | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Shelter / Heat / Power | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Health / Sanitation | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical Field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Historical Food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical Home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Independent draft PRs #157, #169 and #973 were inspected and **not merged**. Their R187-pinned heads remain `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, `e9cd7766dac59d47ab467d8945269b9146c2aef5`, `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`. Existing safety correction and fixture isolation remain separate independent review concerns. No original body, metadata, citation token, source register, canonical URL, publisher status, nav or other agent file was edited. Current home lead PR #1386 was read only.

## Conversion-first, evidence-qualified acceptance

**One candidate:** Existing public `Legacy Triage` Payhip listing (`https://payhip.com/b/n1RhV`), previously advertised as a $19 PDF about financial/accounts/records continuity. This is **not a child-reunification product**; seller identity, rights, downloadable contents, availability, checkout, refunds and payment settlement have not been independently authenticated. It must NOT be presented as a currently approved FV paid Preparedness pack or linked from an unreviewed emergency guide.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (not deployed) | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Legacy Triage → paid order | Product rights, SKU, genuine checkout, delivery, price/refund and audience fit unknown | Authenticate one genuinely purchasable, rights-cleared continuity pack with merchant receipts before any CTA | **COMMERCIAL HARD HOLD**; existing listing is only a candidate | Founder / Claude commerce |
| Grok family emergency content → landing | No verified published matching caregiver `asset_id`, post URL, rights packet, exact landing URL and attribution | Reconcile TASK-008; only use approved public `/preparedness/` official-source gateway until original guide independently cleared | **UNVERIFIED**; no published caregiver asset documented | Grok / Praxxis |
| Free original Household Emergency Plan → guide reader | Authentic source/food/medical/safety/QD review and native build outstanding | Keep ungated free advice; stage authentic approved draft and check mobile 360/390/768/1440, accessibility and citations | **DRAFT HARD HOLD**, no publish | Preparedness / independent QA |
| Guide → optional **free** Family Reunification Card | Eleven source judgments, print/lost-card privacy and keyboard/network tests unresolved | Use synthetic household data for private browser/print QA; never capture or transfer real child names or phone numbers | **HOLD**; no signup gate | Site QA |
| Confirmed merchant order → realized net revenue | No verified 7/30-day qualified-human session denominator, actual merchant orders, fees and refunds | Reconcile `asset_id` + `utm_campaign` → qualified landing → optional CTA → real merchant order → refunds/fees → net per 1,000 qualified humans | **NOT COMPUTABLE**, not zero | Commerce / Claude analytics |

**Draft CTA only, disabled until guide is cleared:** “Prepare a family contact and school pickup plan before a disruption. Read the free Household Emergency Plan.” Secondary optional card: “Print a simple family reunification card (free). Keep children's details private; a lost card can expose personal information.” Both must point to actual independently reviewed and approved destinations; no invented URLs, new email forms or new tracking scripts.

No retired water guide or freebie, speculative paid offer, rights-unchecked affiliate activation, new product, campaign post, CMS write, WordPress publication, analytics script, email send or spending. The sole established lead magnet remains the Seven Day Focus Fieldbook; do not gate emergency steps.

**Release decision:** DRAFT / HARD HOLD. Independently adjudicate source and safety decisions, inspect native build on trusted complete checkout, obtain staged QA and founder release authorization separately. Structural code identity alone cannot clear any of them.
