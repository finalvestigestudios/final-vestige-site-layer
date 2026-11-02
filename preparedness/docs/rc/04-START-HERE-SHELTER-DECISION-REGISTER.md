# Decision register (Start Here, Shelter and cross-cutting): founder or reviewer decisions required

**Status 2026-11-02. Nothing below is decided or approved.** "Release-blocking" = the item must be resolved before the affected page(s) can be published, regardless of passing tests. Recommendations are the AI lead's, not approvals. A general statement such as "I approve" is **not** treated as approval of any item here; each item needs an explicit, scoped decision recorded by a named person.

## A. Cross-cutting

| ID | Decision required | Options | Recommended | Consequence for publication | Blocking |
|---|---|---|---|---|---|
| X-1 | **Custody re-baseline.** The R22/R23/R53-R59 gates freeze the original 35 articles + 1 tool, 224 source rows and 30 shared-URL groups. Integrating the shelter, Start Here and later contributor work (35 articles + 6 tools, 244 rows, 32 groups) fails those gates by design. | (a) QD-reviewed re-baseline for all clusters once review edits settle; (b) apply a self-pinned draft now; (c) keep the frozen 35 and treat the continuations as separate later changes | (a). `docs/rc/simulate_custody_update.py` shows the exact delta; `docs/rc/CUSTODY-UPDATE-SIMULATION-2026-11-01.json` lists it. | Until done, the integrated tree cannot pass validate/build (it fails closed); only a simulated copy renders. | **Yes** |
| X-2 | **Founder "approved" (2026-10-29) for #6 `making-water-safer` and #21 `salt-beef-salt-pork-age-of-sail`.** Recorded from a one-word chat reply; no checklist items reviewed; reviewer name was taken from the About page. | (a) Confirm in writing what was reviewed and by whom, keep `approved`; (b) downgrade both to `pending` | (b) unless (a) is supplied. Records were qualified on this branch (name removed). | If left as `approved`, two pages would count as reviewed without evidence. | **Yes (these 2 pages)** |
| X-3 | **Health cluster "I approve" (typed in the health session).** Scope unknown: safety review of #17/#18/#19? editorial? publication? | State in writing which articles and which kind of review; otherwise treat as none | Keep `pending`. Three source conflicts remain open: FDA devices bleach dose vs CDC table; WA DOH vs OSU on bagged waste; Ready.gov "discard" vs FEMA Dec 2023 "replace". | No health article can publish on an unscoped approval. | **Yes** |
| X-4 | **Historical-source note.** The Simmons cookbook text read for `pickling-fermentation-old-recipes` is the **1798** printing (MSU Feeding America transcription), not the 1796 edition. MSU's own description (quoting the Longone collection note) says the 1798 second printing "follows word for word the text of the first printing" with some errata corrected; we have not verified that. | (a) Keep the article's statement that the 1796 text was not read; (b) also add the MSU note as an attributed statement | (a) now; (b) at editorial pass | Not blocking; wording is already accurate. | No |
| X-5 | **Reviewer roster.** No qualified human reviewer (clinician/pharmacist for medicine, fire-safety professional, extension/food-safety professional) is named anywhere. | Name reviewers per risk area | Name at least: a pharmacist or clinician (medicine, devices), a food-safety extension reviewer (canning, curing, jerky), a fire/CO safety reviewer | Without named reviewers no safety register row can close. | **Yes** |

## B. Start Here (PR #553, `claude/start-here-rc` @ `2af10621`)

| ID | Decision required | Options | Recommended | Consequence | Blocking |
|---|---|---|---|---|---|
| S-1 | **Refrigerated-medicine wording in `three-day-kit`.** Quotes FEMA 2020 ("discard") and FEMA Dec 2023 ("replace; call your doctor or pharmacist; use only until a new supply") side by side, says we do not know which governs. The RC had dropped the QD-required sentence "Do not stop, throw away or ration a medicine you depend on because of anything on this page"; **restored on the candidate branch** (`d44fc2c5`). | (a) keep both FEMA quotes + the restored guard; (b) remove the FEMA quotes and say only "ask your pharmacist or prescriber" | (b) is the most conservative; (a) is more transparent. Prefer (a) only if a pharmacist reviews it. | Medicine instruction; high consequence | **Yes** |
| S-2 | **FEMA 2020 "72 hours" claim C21b** needs a human reading of the rendered PDF (not machine-extractable). | Human confirms or the claim is reworded | Human confirm | Release-critical source | **Yes** |
| S-3 | **Plan builder "plan for" checkboxes and wallet-card note** (powered equipment, cold-stored medicine, optional card note). | Keep, or remove the card-note field | Remove the free-text card note until privacy reviewed | Printed output can expose personal data | Yes |
| S-4 | **Invented worked examples** (labelled as invented). | Keep with label / replace with generic text | Reviewer confirms none reads as an instruction | Low | No |
| S-5 | **WordPress strips `<script>`/`<style>` in `wp:html` for roles without `unfiltered_html`?** Untested: tools would be inert. Same pattern as the existing water planner. | Test in an installed WordPress draft | Test before any import | Tool functionality | **Yes** |
| S-6 | **Slug collision resolved on the candidate:** both Start Here and shelter built a tool named `reunification-plan`. Candidate keeps Start Here's household plan builder as `reunification-plan` and renames shelter's wallet card `family-reunification-card`. Two overlapping family-reunification tools now exist. | Keep both / merge into one / drop one | Merge into one at the editorial pass | Product overlap, not safety | No |
| S-7 | **hist-food source-ID retarget (not integrated).** `claude/prep-hist-food-b81f19` @ `67e116e5` replaces `hist-food-nchfp-jerky` with the base id `nchfp-jerky` (8 citation occurrences in `pemmican-and-dried-meats` and `pioneer-travel-rations`). The library refuses it (undocumented duplicate id), and R59-R61 say it must not silently inherit approval. | Accept retarget after human check / keep distinct ids | Keep distinct ids; revisit after re-baseline | Held back from the candidate | Yes (for those 2 pages' latest edits) |

## C. Shelter (PRs #521 `ac8625fa`, #554 `6a5998ea`)

Source: `SHELTER-FOUNDER-DECISIONS.md` on the follow-up branch. The shelter session's defaults are reproduced; all are **unanswered**. All are release-blocking for the four shelter articles and three tools.

| ID | Decision | Shelter session's default | Lead's note |
|---|---|---|---|
| H-1 | No indoor fuel-burning-heater procedure anywhere (leave if too cold) | Accept | Agree: no source gives a ventilation figure |
| H-2 | Generator at least 20 ft from windows, doors and vents, framed as a minimum with an "Uncertain" note | Accept | Agree; CDC cross-check recorded |
| H-3 | Stranded-vehicle engine "about 10 minutes per hour, window slightly open, exhaust clear" | Accept with attribution, or link out only | Needs a human: a number on a CO hazard |
| H-4 | Medication wording (FEMA Dec 2023 + "do not stop, skip or throw out") | Accept | Align with S-1 so the three pages say the same thing |
| H-5 | High-rise fire reading (stairs by default; defend-in-place undefined) | Accept | Ask a fire professional if possible |
| H-6 | Window wording when sealing in (documents differ; page tells no one to open a window) | Accept | Consider deleting the sentence |
| H-7 | Four-factor shelter-or-evacuate framing replaces "fast hazards mean shelter" | Accept | Reviewer should check the diagram |
| H-8 | Chemical shelter in place: prefer CDC 2026 wording, drop Ready.gov recirculation option | Prefer CDC | Agree |
| H-9 | Custody, pick-up and card privacy have no source | Accept after a child-safety professional reads it | Recommended |
| H-10 (added) | **USDA food-time wording in the outage planner** (follow-up PR #554): discard listed perishables after more than 4 hours without power; Ready.gov 40 F / 2 h shown as different. The FSIS emergencies page returned HTTP 403 even to a real browser, so its content is unverified. | Not raised by the shelter session | A human should open the FSIS pages |

## D. Open items by severity (summary)
1. **Blocking, no workaround:** X-1, X-2, X-3, X-5, S-1, S-2, S-5, H-1 to H-10, independent QD on the exact release commit, human safety review of 29 pending articles + 6 tools, human link check (0 of 244 source rows, 202 distinct URLs, checked by a human).
2. **Blocking until verified:** S-7, unreachable cited sources (see QA evidence report).
3. **Non-blocking:** X-4, S-4, S-6.
