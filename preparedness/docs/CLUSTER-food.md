# Cluster notes: `food` (Food and Preservation)

Drafted 2026-10-30 by the `food` contributor session; QD self-audit 2026-10-30 (section 7). Sources fetched and read 2026-10-29 (two added 2026-10-30) (Firecrawl scrape, `maxAge: 0`, plus search for discovery). All four articles are **drafted, awaiting human review**. All four have `safety_review.state = "pending"` and `status.publish = "draft"`. Nothing is approved.

| # | Slug | Gate | Words | Sources cited |
|---|---|---|---|---|
| 8 | `pantry-rotation` | no (set to pending anyway, as it advises on discarding cans and botulism signs) | ~3,150 | 9 |
| 9 | `food-safety-power-outage` | yes | ~2,840 | 7 |
| 10 | `pressure-canning-low-acid` | yes | ~3,500 | 17 |
| 11 | `safe-jerky-dehydration` | yes | ~2,890 | 10 |

## 1. For the lead: test status after merging `origin/feature/preparedness-archive-v1` (ee591e2)

The merge was clean. The derived section test and the gating fixes resolved the landing-page failure. I did not edit `tools/`, `tests/`, `assets/` or `taxonomy.json`. Result of `python -I -m unittest discover -s preparedness/tests -v` on 2026-10-30: **Ran 36 tests, 34 passed, 1 failed, 1 errored, 0 skipped.** The two remaining problems have the same cause: the tests treat `nchfp-jerky` as a placeholder that will stay unverified, but the brief tells the jerky contributor to upgrade it (and I did).

1. `test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source` (ERROR): the test writes its own fragment that upgrades `nchfp-jerky`; with my real fragment already upgrading it, `build.Library()` raises `ValueError: duplicate source id 'nchfp-jerky' in food.json`.
2. `test_unverified_source_cannot_be_cited` (FAIL): it appends `{{cite:nchfp-jerky}}` and expects an "unverified source" error; the source is now verified, so no error is produced.

Suggested fix for the lead: use a synthetic fixture id (or a placeholder no contributor is assigned) in both tests. I cannot use a different id for the same page, because the validator rejects a second source with the placeholder's URL. `validate.py` and `build.py` both exit 0.

## 2. Sources verified (all in `sources/fragments/food.json`)

Upgraded placeholders (same ids): `fsis-power-failure`, `fsis-emergency-foods` (first fetch returned only the title; a second fetch with a 5 s render wait returned the text), `nchfp-jerky`, `nchfp-pressure-ground-meat`, `nchfp-home`.

New (prefixed `food-`): FSIS emergencies page; CDC "Keep Food Safe After a Disaster"; FoodSafety.gov power-outage charts; FDA power outages and floods; Ready.gov Food; FSIS Shelf-Stable Food; FSIS Food Product Dating; FoodKeeper landing; Illinois, Utah State and Oregon State Extension pages; FSIS Jerky fact sheet and Ask USDA jerky Q&A; Kansas State MF3173; five NCHFP canning pages (Using Pressure Canners, Ensuring Safe Canned Foods, Recommended Canners, Not Recommended, multi-cooker newsflash, dry-canning post, steam-canning statement); CDC Home-Canned Foods; USDA Complete Guide Guide 1 (PDF).

Already-verified register entries reused (never redefined): `cdc-botulism-prevention`, `fsis-home-cure-qa`, `nchfp-cure-smoke`.

## 3. Source disagreements found (all stated on the pages)

| Topic | Disagreement | Where shown |
|---|---|---|
| Refrigerator time limit | FSIS/CDC/FDA/Ready.gov: about 4 hours closed. FoodSafety.gov chart and Ready.gov: 2 hours above 40 F. FDA alone allows a measured 45 F pass. OSU Extension: 4 hours then 2 more | #9 "Two clocks" |
| Opened juice | FSIS: discard opened fruit and vegetable juices. FoodSafety.gov chart: keep opened fruit juice, discard vegetable juice | #9 |
| Bleach for sanitizing | FSIS 1 tbsp/gal for utensils, counters and cans; FDA 1 tbsp/gal for utensils but 1 cup per 5 gal for cans; CDC 1 cup per 5 gal throughout; Ready.gov 1 part to 10 for cans. **Not reproduced** | #9 |
| Dry ice | FSIS/FDA 50 lb / 18 cu ft / 2 days; Ready.gov 25 lb / 10 cu ft / 3 to 4 days. Different scenarios, not formulas | #9 |
| Home-canned food boil rule | FSIS shelf-stable page contradicts itself (text: 10 min + 1 per 1,000 ft, fruit never needed it; chart: 10 min high-acid, 20 min low-acid). CDC matches the text | #8, #10 |
| Tasting older canned food | Utah State Extension allows tasting a sample and suggests 165 F or 5 to 10 min boil; CDC and USDA say never taste | #10 |
| Jerky heating sequence | FSIS: heat to 160 F (poultry 165 F) before dehydrating. NCHFP/Kansas State: heat in marinade before drying or in an oven after drying | #11 |
| Jerky shelf life at room temperature | NCHFP 2 weeks; FSIS 1 to 2 months; Kansas State best within 1 to 2 months | #11 |
| Vacuum packaging | NCHFP calls vacuum packaging jerky "a good option"; OSU warns vacuum-sealed low-acid food at room temperature can foster botulism toxin | #11 |
| Raw poultry jerky | FSIS gives a 165 F procedure; NCHFP and Kansas State say raw poultry is generally not recommended (texture and flavor) | #11 |
| Steam canners | NCHFP "Equipment Not Recommended" page still says not recommended; NCHFP September 2026 newsflash endorses atmospheric steam canning for high-acid foods only | #10 |
| Minor internal NCHFP differences | Pressurizing time "3 to 10 minutes" (Using Pressure Canners) vs "3 to 5" (Recommended Canners) | #10 limits |
| Canned-food storage temperature | FSIS below 85 F best; CDC 50 to 70 F for quality, 95 F ceiling; OSU 95 F danger line | #8 |

## 4. Claims I could not verify, and things not read

* The two *Journal of Food Protection* studies (2004, 1998) on jerky are cited only **as FSIS summarizes them**.
* Not read: the full USDA Complete Guide (only Guide 1 was read as extracted text), the NCHFP drying, curing and smoking sections beyond the pages named, the NCHFP "Canning in Pressure Cookers" newsflash, individual FoodKeeper entries, the CDC "Eat Safe Food After a Power Outage" infographic, the Illinois Extension emergency-food PDF, the Utah State storage booklet.
* No national official figure for how many days or weeks of food a household should hold beyond Ready.gov's "several days". The Oregon two- and four-week figures are for the Cascadia hazard and are labelled that way.
* No source gave a ventilation rule for dry ice, a way to verify a dehydrator's actual temperature, pet or higher-risk-group guidance for outages or jerky, or any evaluation of smoke (cold or hot) as a pathogen control. The articles say so.
* No calorie or portion targets are given (none could be sourced without inventing).
* Process tables for pressure canning are **deliberately not reprinted** (link-out), as with the 1% bleach table in the model article.

## 5. Items for the human safety reviewer (same format as checklist section C)

| Article | What the reviewer must check | Against |
|---|---|---|
| `food-safety-power-outage` (#9) | The "two clocks" framing; the editor's conservative synthesis (treat 4 h as the outer limit, count time above 40 F separately); the editor's note that a post-outage fridge reading does not by itself rescue food; the excerpted keep/discard table (each row copied from the chart); the opened-juice disagreement and our "discard" lean; dry-ice figures presented as order-of-magnitude examples; the bleach link-out; our statement that dry ice ventilation is not covered by the sources | FSIS emergencies, FSIS Ask USDA, CDC, FoodSafety.gov chart, FDA, Ready.gov, OSU |
| `pantry-rotation` (#8) | Date-label table; FSIS shelf-life rows quoted in context; omission of the contradictory FSIS home-canned row; canned-goods discard criteria (deep dent, seam dent, rust); botulism symptoms line (12 to 48 h); the rotation-routine table is our schedule built from sourced intervals, labelled | FSIS shelf-stable, FSIS dating, Ready.gov, FSIS Ask USDA, Illinois, USU, OSU |
| `pressure-canning-low-acid` (#10) | No process times or pressures given; the 10-minute venting, restart-timing and "do not force-cool" lines (NCHFP); the CDC boil-before-eating rule with FSIS's qualification; our editor's reading that the boil is not a rescue; the shortcut table (each row cited); the 7 to 11 hour boiling-water figure quoted only to explain why it is not an alternative; omission of the detoxification steps; the statement that no source endorses improvised heat sources for canning | CDC home-canned, NCHFP (5 pages), USDA Guide 1, FSIS shelf-stable, OSU, USU |
| `safe-jerky-dehydration` (#11) | The 160 F / 165 F figures and 130 to 140 F dehydrator range with their context; NCHFP's 5-minute marinade boil and 10-minute 275 F oven step (as published, with the thickness condition); that we present both sequences and flag FSIS as the more conservative; the shelf-life disagreement and our lean to the shortest figure; the trichinella freezing rule (6 in, 0 F, 30 days) as NCHFP states it; no cure formula; smoke not treated as a safety step; vacuum-packaging caveat | FSIS jerky fact sheet, Ask USDA, NCHFP jerky, Kansas State MF3173, OSU, CDC botulism, FSIS home-cure |

## 6. Notes on method

* Every cited page was fetched and read in full on 2026-10-29 unless listed in section 4. `human_link_check` remains false everywhere.
* Quoted figures stay with their conditions. Where I summarize a number (for example the NCHFP boiling-water time range) the article says why it is quoted.
* No images are used.
* Related links to unbuilt articles (`outage-heat-cold-generators`, `pemmican-and-dried-meats`) degrade to plain text by design.

## 7. QD self-audit (2026-10-30), against the lessons from the Start Here review

Audit result: no article contained a blanket "discard medicine" instruction or a hazardous rehearsal. Targeted edits were made for the points below. All four articles stay `status.publish: draft` and `safety_review.state: pending`. **All sources in the fragment remain `human_link_check: false`.** I make no QD PASS claim.

| Class | Finding | Action |
|---|---|---|
| (a) Medication / medical instructions | #9 only said to ask a pharmacist or prescriber, but did not use the newer FEMA document. #8 repeated a secondary (Illinois Extension) statement that over-the-counter drugs should never be used past expiration. | Added FEMA fact sheet V-1008 (December 2023), read in full, as `food-fema-outage-sheet`, and quoted its medication wording in #9 with the qualification "call your doctor or pharmacist; do not stop or skip a prescribed medicine on your own". Removed the OTC-drug expiration claim from #8 and replaced it with "ask your pharmacist". I did not read the older 2020 FEMA wording, so the difference between 2020 and 2023 is not described. |
| (b) Hazardous rehearsals | None recommended. The only practical steps are freezing water jugs and using coolers. #10 says canning without standard equipment is outside the validated conditions. | None needed. |
| (c) Source kinds | `food-usda-canning-guide-1` was `extension` though its publisher is USDA NIFA. | Changed to `regulator`. FDA, CDC, FSIS, FEMA and FoodSafety.gov are regulators; NCHFP and university pages are `extension`. No nonprofits are cited. |
| (d) Secondary-summary claims | (1) Two jerky studies are known only through FSIS's summary. (2) NCHFP pages are adaptations of the USDA Complete Guide, not the Guide itself. (3) Kansas State cites an FSIS jerky fact sheet dated 22 September 2023 at a `/meat/jerky` path that I could not retrieve; the FSIS page I read still shows "Last Updated: Nov 03, 2016". (4) The FEMA discard rule differs between FEMA's Food page (2 hours above 40 F, updated March 2026) and its December 2023 fact sheet (more than 4 hours above 40 F). | (1) Already labelled "as FSIS summarizes". (2) Stated in the fragment notes. (3) Currency check done in a browser; the Ask USDA article (February 2025) gives the same figures; the possible 2023 FSIS version is recorded as unverified in the article's limits and the fragment. (4) Both FEMA statements are shown in #9's table, the newer one is identified, and the more cautious reading is stated. |
| (e) Partly read documents | USDA Guide 1 (40-page PDF) was only partly read; FoodKeeper only as a landing page. | Exact read scope is now written in the register `notes`: Guide 1 sections read are listed and the remainder is marked NOT read; FoodKeeper is marked "landing text and category list only". FEMA V-1008 is marked as extracted with `pdftotext` and read in full (one page). |
| (f) Food-safety figures and higher-risk groups | #9 and #11 said the sources do not break out higher-risk groups. I had not read the CDC page that does. | Added CDC "People at Increased Risk for Food Poisoning" (read in full, 2026-10-30; dated Jan. 31, 2025) as `food-cdc-risk-factors` and used it in #9 and #11, with an explicit statement that CDC's four "Safer Food Choices" pages were not read, so no food-specific rules for those groups are given. Older-vs-newer reconciliation: FSIS emergencies page (2013) vs FSIS Ask USDA (Dec 2024) vs CDC (Nov 2025) vs FEMA (Dec 2023) agree on 4 hours; the 2-hour and 45 F variants are stated as differences. NCHFP "Using Pressure Canners" (2014) and "Recommended Canners" (text revised 2009) differ on one minor timing (3 to 10 vs 3 to 5 minutes); both are stated and the manufacturer's manual is said to control. |

Statements I could NOT verify to this standard (all stated in the articles' limits sections):
* The two jerky journal studies (FSIS summary only); the possible newer FSIS jerky fact sheet.
* The older 2020 FEMA outage wording; CDC's "Safer Food Choices" pages for higher-risk groups; individual FoodKeeper entries.
* The unread parts of the USDA Complete Guide Guide 1 (and the rest of the Complete Guide).
* Any ventilation rule for dry ice; any way to check a dehydrator's real temperature; any official evaluation of smoke as a pathogen control.

Fetch notes for this round: Firecrawl ran out of credits, so the FEMA PDF was read with `pdftotext` from the locally saved file the web-fetch tool downloaded, and the CDC risk-factors and FSIS currency checks were read directly in the browser pane. The first CDC-risk-factors text I received came back through a subagent; I re-read the page myself before citing it.
