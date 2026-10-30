# Start Here contributor safety rebase — independently review before publication

**Issue:** #136 · **Existing integration:** PR #176 · **Evidence freeze:** PR #179 · **Independent QD:** PR #157 · **Food source-fixture fix:** PR #169

**Status: DRAFT / HOLD. No WordPress publishes, navigation edits or live-site changes.**

## Exact provenance and why a new draft was required

The integration input baseline was `c8df99cc661e518e93e58e1cc1ea3d7256f58643`; its evidence-lock parent was `a2618238ddcb3377a608b535577a5724a8cfd335`. The original independent Start QD safety fix used `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (PR #157). The contributor's Start branch subsequently advanced **three commits** from the initial `10f58fed1ba808056813064ca5f9680589db8da1` to **`2122d856fce9f64887c16df3d52e64be9f59a55b`**.

That newer revision materially expands infant, medicine, food-outage, housing and high-rise caveats and documents more precise reading depth. Simply relying on PR #157 and the original integration would silently omit that additional safety work. This branch copies the full updated source bodies rather than excerpting passages, while **retaining the integrated taxonomy's stronger safety gate** and all 31 other existing article bodies.

## Exact original content preserved

Four contributor-Start articles updated: `go-bags`, `household-emergency-plan`, `preparedness-real-households`, `three-day-kit`. There are seven changed HTML/metadata files (household plan metadata was unchanged), plus `sources/fragments/start.json` and `docs/CLUSTER-start.md`. The other six base drafts and the six other contributor clusters (shelter, food, health, three historical branches) remain untouched. Overall inventory remains **35 complete long-form draft articles and one local-only water planner**, with no publication or CMS writes.

The Start fragment now contains **27 source rows** rather than 26. It adds `start-fema-power-sheet`, which documents reading the **English pages 1–2** of the 34-page December 2023 FEMA V-1008 power-outage PDF, with pages 3–34 *unread*. Critically, that exact PDF URL already appeared in **three other contributor clusters** with their own notes. The crosswalk now preserves **all four distinct source rows**, with their individual support claims, not one falsely consolidated citation. Existing three Start shared-source entries also retain their newly revised claims/notes. ALL 30 duplicate-URL groups remain pending human reading-scope review.

Recomputed source inventory: **224 raw rows, 209 machine-marked verified, 15 unverified placeholder rows, 186 literal unique URLs, 30 repeated-URL groups, 15 repeated-ID groups, zero human-link-verified rows**. An unchanged count of distinct URLs despite one extra row is *expected*: the new row uses a previously observed URL. This is not a duplicate-content bug to fix by deleting rows; their individual reading depth matters.

## Specific substantive risk mitigations in the revised drafts

- **Medicine:** Unlike a blanket "discard after a day" instruction from an older FEMA source, the updated three-day kit includes the newer FEMA language about replacement, pharmacist/prescriber guidance, and avoiding unplanned interruption. These official sources still differ in wording; a qualified reviewer must resolve the interpretation.
- **Food:** The Start draft now explicitly presents the discrepancy between FEMA-associated two-hour versus four-hour advice for refrigerated food above 40°F. It attributes each to its actual source and does not declare both equivalent.
- **Combustion/CO:** Outdoor use and a stated 20-foot distance are tied to agencies, with an explicit caution that this distance is *not a guarantee of safety*.
- **Infant and pregnancy:** Kit lists now warn against unsupervised dosing of infant acetaminophen, clarify CDC's caveats for supplies needing clean water and put emergency birth supplies in context only, with no home-birth instructions.
- **High-rise evacuation:** USFA guidance is labelled fire-specific rather than universal. 
- **Housing:** The HUD multifamily template was **only partly read (12 of 79 pages)** and is no longer presented as a verified legal requirement; actual tenant duties are outside the verified source scope.
- **Household drill:** Simulate a power outage with nonessential devices; do not turn off the main breaker, alarms, refrigeration, sump pumps or critical medical equipment.

**These editorial improvements are not qualified clinical advice or proof of safety.** Human review of pediatric medication, refrigerated drugs, food temperatures, fire/CO, pregnancy and disability planning is still required.

## Governance / reproducible verification

The source-crosswalk file SHA and **all original 36 body/metadata pairs** remain pinned in the same Git input freeze: the seven changed Start file fingerprints were updated to the exact latest contributor Git blobs. That means an unexpected subsequent change fails verification instead of inheriting another version's approval. The original `integration_base_sha` is preserved as history, with a separate `reconciliation_20261030` provenance record.

All four revised articles are still `status.publish: draft`, `safety_review.state: pending`, and `taxonomy.gate: true`. Any future release must be validated against its own new claim and copy fingerprint, actual human URL reads and independent QD. PR #157, PR #169, PR #176 and PR #179 are **not** marked passed or merged by this rebase. A Git blob fingerprint is **not** a human signature, medical review or approval.

Run on a trusted checkout pinned to the exact head of this draft branch:

```bash
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/audit_integration.py --require-release-ready
```

The last `--require-release-ready` command **should fail** while 30 shared-source scopes, human link checks, source conflicts and independent safety/editorial/release authorizations remain pending. Test counts in a PR describe defined tests, **not executed tests**, unless execution on its exact SHA is separately evidenced. No live publishing or WordPress changes are authorized here.

## Full-corpus citation-use completeness pass

A dedicated scan of all 35 full articles plus the water planner found exactly **two** body citations missing corresponding article-specific `source_use` notes: `homemade-water-filters` / `cdc-find-clean-water` and `preparedness-real-households` / `start-ready-plan`. The original source IDs, evidence rows and article claims were already present; only the missing narrow descriptions of what each existing citation supports were added. We did not change their body copy or assert a fresh source read. Both affected articles remain unapproved drafts.

The validator now **fails closed** when an article cites a source without its own explicit reading-purpose note, as well as when it declares unused sources. Three additional unit tests cover the complete 36-item corpus and remove each note synthetically to confirm rejection. All 72 body/metadata inputs remain bound to their recorded Git blob SHAs (the two changed metadata SHAs have been re-pinned). This audit does not perform the outstanding human citation review.
