# Cluster notes: `food` (Food and Preservation)

Drafted 2026-10-30 by the `food` contributor session. Sources fetched and read 2026-10-29 (Firecrawl scrape, `maxAge: 0`, plus search for discovery). All four articles are **drafted, awaiting human review**. All four have `safety_review.state = "pending"` and `status.publish = "draft"`. Nothing is approved.

| # | Slug | Gate | Words | Sources cited |
|---|---|---|---|---|
| 8 | `pantry-rotation` | no (set to pending anyway, as it advises on discarding cans and botulism signs) | ~3,150 | 9 |
| 9 | `food-safety-power-outage` | yes | ~2,840 | 7 |
| 10 | `pressure-canning-low-acid` | yes | ~3,500 | 17 |
| 11 | `safe-jerky-dehydration` | yes | ~2,890 | 10 |

## 1. For the lead: things outside my ownership that block "all tests pass"

I did not edit `tools/`, `tests/`, `taxonomy.json` or `register.json`. `validate.py` and `build.py` pass. `python -I -m unittest discover -s preparedness/tests` shows **3 failing tests**, none caused by an article defect:

1. `test_landing_lists_only_built_articles_and_no_empty_sections` hard-codes `["water", "lost-ways", "field-tools"]`. Any contributor who adds a `food`, `shelter-power`, etc. article breaks it. Suggest computing the expected list from `lib.articles` and the taxonomy order.
2. `test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source` writes its own fragment that upgrades `nchfp-jerky`. Once any real fragment (mine) upgrades `nchfp-jerky`, the test's fragment becomes a duplicate of a verified id and raises `ValueError`. The brief tells contributors to upgrade `nchfp-jerky`, so this will always fail after the first one does. Suggest the test use a placeholder nobody is assigned (for example `nws-nwr` is assigned too, so a synthetic fixture id is safer).
3. `test_unverified_source_cannot_be_cited` appends `{{cite:nchfp-jerky}}` to expect the "unverified source" error. Same cause: `nchfp-jerky` is now verified. It needs a placeholder that will stay unverified or a fixture-injected unverified entry.

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
