# R127 — QA #157 ↔ Preparedness RC #584: exact-source safety disagreement docket

**Status: DRAFT / HOLD.** Scope: [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), source/citation and high-consequence instruction adjudication only. Coordinates with [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and founder charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). This is **not** evidence of independent medical, fire, source-link, editorial or QD review. Never merge, deploy, publish, change WordPress/CMS/navigation, edit analytics, email, merchant or social content under this dossier.

## What was independently inspected (GitHub, 2026-11-04)

- Frozen integration candidate PR **#584**, head **`ddb3528ba6494dada1fa1c3a142ce746e3a67706`**.
- Independent safety QA PR **#157**, head **`7d1ae6b8ef93d10cfb6810987672360885e9c1aa`**, still draft/unmerged.
- Independent fixture test PR **#169**, head **`e9cd7766dac59d47ab467d8945269b9146c2aef5`**, still draft; its unsafe duplicate-ID fixture writes inside the source directory. **R125** draft PR #973 head `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` provides an isolated-test correction, not a tested/merged solution.
- R126 stacked author-source inventory PR #974: `c4ea5513aa0e04cacb736277e74c515c305df560`; 35 articles, 32 shared-source URL groups, 94 author-source bindings documented in R126, **not** human cleared.
- Homepage PR #49 `10495883299d53596992c26a8987f629b2904670`; flagship PR #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`; left untouched.

The new tool pins **eight independently fetched actual Git blob identities** across QA and RC: household plan body, three-day kit body, Start Here source fragment and 35-route taxonomy for each snapshot. Any changed raw byte forces HOLD, rather than silently re-accepting an updated source.

| Exact file | RC #584 Git blob | QA #157 Git blob |
|---|---|---|
| `household-emergency-plan.body.html` | `f81cd43516e8295104230412f18776919148f905` | `6407a31a882211e62c00f4e07ec7dc4d5abf99c6` |
| `three-day-kit.body.html` | `933f38ff3cd55a241cf9b392014fc52d4961e84f` | `f578cdbae602c1ad58a9237c8dea0fd74c99f7da` |
| `sources/fragments/start.json` | `96140d6d1872588e5d20d9052445c9157e88934d` | `d5a5087042381227d840675d9eb08ddc375d21e8` |
| `taxonomy.json` | `15c547bb3018ac182b12a51036389cfa39a59168` | `d20ff18bc6f243e08796c0505981979a10fca2d9` |

## Four independent review decisions: all OPEN, no automatic approval

1. **Electrical outage drill — `electrical_drill_wording`.** QA #157 changes the earlier risky main-power shutdown example to a lights-out simulation that keeps refrigeration, alarms and medical devices powered. The later RC independently uses a differently worded **simulated-outage evening** with an explicit “Do not switch off the main breaker as a drill.” Both contain cautionary wording, but the paragraphs are **not text-identical**. Review source support, special cases and final editorial wording; do not cherry-pick or equate the alternatives silently.
2. **Refrigerated medication — `refrigerated_medicine_product_specific`.** QA #157 includes an explicit caution not to stop essential treatment or discard limited medicine solely on a general webpage, and to promptly consult pharmacist/prescriber for product-specific instructions. RC instead advises asking a pharmacist about interim-use/replacement planning if a refrigerated medication warms up. **These are materially different answers to an urgent consumer scenario.** Neither automatically substitutes for named qualified medication review. Retain citations and do not silently remove either version's cautions during adjudication.
3. **Authority classification — `source_regulatory_classification`.** Both inspected source fragments label American Red Cross `start-redcross-older-adults` as `nonprofit`, not `regulator`. Both retain `human_link_check: false`. Machine classification parity is **not proof that the link or source claim was reviewed**. Preserve the author-scoped source evidence.
4. **Four Start Here gates — `four_start_here_safety_gates`.** Both taxonomies protect `household-emergency-plan`, `three-day-kit`, `go-bags`, and `preparedness-real-households` with `gate: true`. This check protects the entire 35-route roster from duplicate slugs or route drift. The gate flag is a structural blocker, **not a human safety receipt**.

**No QA decision is marked resolved.** No `safety_review`, `status.publish`, source register, canonical route, body, metadata, WordPress or article is modified here. Reviewer acceptance needs an explicitly identified qualified reviewer, evidence/decision record, current guidance, source-specific citation adjudication and separate independent QD release decision. Historical “approved” labels do not suffice.

## Executable deterministic cross-snapshot reviewer gate

- `preparedness/tools/r127_qa_safety_disagreement_gate.py` takes two **separate immutable checkouts**, `--candidate-root` and `--qa-root` (no write operations; no network dependencies); authenticates all eight raw blobs using Git's object hash, checks route roster parity (35 unique routes), Start Here gates, citation-preserving medication paragraph, protective breaker-drill language and accurate source classification, then returns **`HOLD_HUMAN_ADJUDICATION`** with four review items marked open.
- `preparedness/tests/test_r127_qa_safety_disagreement_gate.py` runs **71 local synthetic/adversarial tests**, including mutations on **both snapshots**; no source-directory fixture writes. The two committed Python blobs matched the locally tested byte-identities before PR creation. Compilation passed.
- Actual complete frozen checkouts are **not available in the Python environment**. Thus the executable against the two actual historical checkout trees, native `python -I preparedness/tools/validate.py`, `build.py`, the full regression suite, mandatory integrity, WordPress draft render, browser QA and independent QD remain **NOT EXECUTED / NOT VERIFIED**. Independent GitHub object reads show the input markers and pinned identities, but do not replace an actual executable run.

Proposed exact-checkout commands (for a permitted maintainer checkout; run in a read-only review worktree):

```sh
python -I preparedness/tools/r127_qa_safety_disagreement_gate.py --candidate-root /path/to/rc584-ddb3528 --qa-root /path/to/qa157-7d1ae6b
python -I -m unittest discover -s preparedness/tests -p 'test_r127_qa_safety_disagreement_gate.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

## Current seven-contributor exact refs (2026-11-04 GitHub read)

| Cluster | Current branch | Exact SHA | RC #584 policy |
|---|---|---|---|
| Start Here | `claude/start-here-rc` | `2af10621b0f4b5837f9224bf7f7163cc21590293` | integrated content, freeze for review |
| Shelter | `claude/prep-shelter-followup-evidence` | `6a5998ead97eca997e573ce8d3ceacf1c6aabad4` | integrated content |
| Food | `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | docs only |
| Health | `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | docs only |
| Historical food | `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | **not integrated**: citation-ID retarget requires S-7 human decision |
| Historical home | `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | integrated content |
| Historical field | `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | integrated content |

These exact refs matched the RC handoff's previously recorded “newest” heads during this run. **Do not automatically merge any contributor or reviewer branch**; the frozen integration candidate and its reviewed source provenance remain the target.

## Conversion-first #820 handoff: one true-intent free guide; paid offer intentionally absent

**Audience/topic hypothesis (not verified Grok traffic):** a household needs a printed contact, school pickup and meeting/reunification plan. Candidate source-backed free resource: draft `household-emergency-plan` at **proposed only** `/preparedness/start-here/household-emergency-plan/`. Do not call it live or safety approved. No Grok `asset_id`, platform post URL, actual clickable CTA surface, or matching Preparedness audience has been verified from TASK-008. Its live production priority remains Grok's, with Praxxis reviewing asset provenance. Do not write to or take over their Drive queue.

**Draft, disabled CTA:** “Make a contact and meeting plan your household can find. Read the free Household Emergency Plan.” Only surface after safety/source/route QA and release approval. Full free emergency steps must remain ungated. **Paid companion remains disabled:** no authenticated owned, rights-cleared and genuinely purchasable FV Preparedness SKU, real price, working fulfillment, rights license, refund policy or approved checkout was produced. No paid offer is invented or promoted. No retired water freebie.

| Offer | Funnel step | Blocker | Change / acceptance test | Evidence / owner |
|---|---|---|---|---|
| Existing verified Preparedness pack only | Payhip detail → completed checkout → usable download | Seller-owned SKU/rights/terms not authenticated | Growth obtains authenticated SKU, rights, price, terms, delivery proof; separate Site QA transaction/fulfillment test after permission | **HOLD / UNVERIFIED**; Growth/Claude |
| Free household plan | Grok asset → landing → complete ungated guide | #157 wording unresolved; article still draft; URL unapproved | Named safety/source review, real render at 320/360/390/768/1440 px, print and keyboard checks, exact destination validation | **HOLD / UNPUBLISHED**; Preparedness/QA |
| Social asset ID | Real permitted link → intended page | TASK-008 has no verified matching Preparedness published asset ID | Grok/Praxxis verify asset ID, channel, content rights and allowed link location, then Claude tests standard UTM mapping | **NOT VERIFIED**; Grok/Praxxis/Claude |
| Optional paid CTA | Relevant guide → checkout | Product authenticity, disclosure, mobile usability and delivery not demonstrated | Only after seller approval, test disclosure, correct price, real checkout, refunds and download on mobile | **NOT TESTED**; Site QA/Claude |
| Confirmed orders and revenue | Qualified human sessions → merchant-paid transactions | No first-party reconciled orders, fees/refunds or qualified audience denominator | 7/30-day source-of-truth cohorts; distinguish outbound link/start/signup from merchant-confirmed paid order | **N/A** net revenue per 1,000 sessions; Growth |

Do not add analytics scripts, spend, post, email or modify current `/focus/` signup. Existing Focus Fieldbook is the sole confirmed lead-magnet direction; this guide is proposed free **ungated**, not a retired water download. All order conversion and revenue numbers remain **UNOBSERVABLE**, not zero by assumption.

**Release status: HOLD, no merge or production changes.**
