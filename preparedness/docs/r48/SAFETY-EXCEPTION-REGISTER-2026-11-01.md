# High-consequence safety exception register (Deliverable C): HOLD

**Date:** 2026-11-01. **Base:** R47 `7b19198e` plus R48. **No exception below is closed.** Every entry is `OPEN` until a named qualified human reviewer records a decision. Nothing here approves, clears or publishes anything, and no article text was changed to produce this register.

**Machine authority.** Everything below is AI-assisted triage. Source text was fetched on 2026-11-01 (script, then a real Edge session for pages that refuse scripts; PDFs via PyMuPDF) and compared with article text by a model. "Supported" means *a cited source contains matching wording*. It does not mean the claim is correct in context, current, complete, or clinically safe.

## How the list was built

1. Ran the repo's own R13 triage (`high_consequence_claim_triage.py`) over all 36 draft items: **779 high-consequence action blocks, 237 with no citation in the same block**.
2. Read all 237. Most are labeled editor's notes, limitation statements, table-cell fragments, or "call your emergency number" pointers. **28 consequential uncited instructions or documented source disagreements** were selected for direct testing against the sources their own article cites (Appendix A; data in `r48/SAFETY-CANDIDATES-2026-11-01.json`).
3. Tested the quantified claims separately (see `FIGURE-TRIAGE-2026-11-01.json`: 178 of 186 fully confirmed, 0 contradictions).
4. Scanned all modern-track text for safety-assurance and absolute-claim language (63 sentences matched; none is an unattributed assurance; see SX-13).

Severity: **HIGH** = reader harm is plausible if the text is wrong or misapplied and a decision is unresolved; **MEDIUM** = source disagreement already handled on the page, or a single-source or unverifiable instruction; **LOW** = editorial or low-consequence.

## Register

| ID | Sev | Article / location (`preparedness/content/articles/`) | What is at issue | Evidence | Proposed correction / required action | Reviewer needed |
|---|---|---|---|---|---|---|
| SX-01 | HIGH | Citations across all clusters | **25 cited sources could not be read at all today** (of about 185 distinct cited URLs) (HTTP 403 to scripts *and* to Edge, or a PDF that would not parse). Claims resting only on them are unverified. They include `fsis-botulism` (cited by the **approved** salt-provisions article), `hist-food-fsis-smoking`, `hist-food-fsis-molds`, `food-foodkeeper`, `shelter-fcc-comms`, `health-fcc-wea`, 3 USGS/LOC/Smithsonian history pages and the Prairie Traveler. Full list: the 7 blocked sources in `SOURCE-ACCESSIBILITY-2026-11-01.json` (a subset) and the 25-URL list in this register's Appendix B | 403 recorded per URL. The FSIS botulism page *was* read on 2026-10-29 by a different retrieval route; it is not re-verified today | A human (or an authorized retrieval route) reads each page and records the supporting passage and date. Until then label dependent statements "unverified" in the review record. Do not treat the earlier 2026-10-29 read of `fsis-botulism` as current | Source reviewer |
| SX-02 | HIGH | All 35 articles | **Scope gap.** This register tests numbers and 28 hand-selected items. It did **not** evaluate qualitative accuracy of the **542 cited** high-consequence blocks, correct attribution among multiple cited sources, or whether wording is current | Triage counts above | Human claim-to-source review (the existing R33 priority order, 1,311 `REVIEW_FIRST` occurrences) remains the required work | Qualified human reviewers by domain |
| SX-03 | HIGH | `medication-and-devices` L61-62 `#cold`; `three-day-kit` L79 `#medicine` | **Refrigerated medicine in an outage.** Older wording ("discard") and FEMA's Dec 2023 sheet ("replace", call prescriber or pharmacist, interim use) differ. The text now says do not stop, discard or ration a medicine on the page's authority and defers to the prescriber or pharmacist. This was corrected after QD review 1 | Article states the discrepancy; FDA, CDC and Ready.gov pages in the article's own source set contain both "discard" and "replace" language | Keep deferral to prescriber/pharmacist as the lead instruction. A pharmacist or clinician must read the final wording. Do not soften to a bare "replace" or sharpen to a bare "discard" | Clinical (pharmacist or physician) |
| SX-04 | HIGH | `food-safety-power-outage` L41-42 `#clocks` | **FDA allows a measured 45 F, FSIS/CDC state a flat 4-hour limit.** The article takes the cautious reading as an *editor's note* | FDA page: perishable food at 45 F or below measured with a thermometer "should be safe", to be cooked and eaten promptly. FSIS/CDC pages state 4 hours and the 40 F line | Keep both figures and the disagreement visible. Ensure any summary or action box leads with the stricter reading. A food-safety specialist must confirm the editorial choice. Re-check the FDA page date before launch | Food-safety (USDA/Extension) |
| SX-05 | HIGH | `making-water-safer` L47 `#boil` (approved); `water-advisories-explained`, `homemade-water-filters` | **Boiling at altitude.** Agency cut-offs differ; the approved text retains the difference and advises 3 minutes at or near the higher cut-off | Verified in pages fetched 2026-11-01: CDC (both its pages) "above 6,500 feet"; NPS "below/over 6,500 feet"; EPA "above 5,000 feet"; Ready.gov: one full minute, **no altitude rule** | Retain the approved reconciliation exactly. Note in the review record that NPS agrees with CDC and that Ready.gov is silent. A water-quality specialist should confirm the "near or above 5,000 ft" advice | Water-quality / public health |
| SX-06 | MEDIUM | `making-water-safer` bleach table (approved); `medication-and-devices` L127 `#limits`; `two-week-water-storage`; `water-advisories-explained` | **Four bleach-dosing statements in four sources.** CDC table (5-9%): about 8 drops or just under 1/8 tsp per gallon, double if cloudy. EPA (6%): 8 drops per gallon. Ready.gov (5.25-6.0%): 1/8 tsp per gallon. **FDA device page (5.25%): 1/8 tsp (~0.75 mL) per gallon clear, 1/4 tsp cloudy** | Quoted from today's fetch of each page. Same structure, slightly different amounts because strengths differ | Keep the single pinned CDC table (test-enforced). The medication article correctly reproduces neither FDA nor CDC numbers; keep it that way. Propose a test that bleach drop/teaspoon quantities may appear only in the approved table and the CDC dish-soak line | Water-treatment specialist |
| SX-07 | MEDIUM | `pressure-canning-low-acid` L99 `#boil` | **Boiling home-canned low-acid food before eating.** Agencies differ on whether, and how it relates to tasting. The article's editor's note says the boil is an added margin, not a rescue for an unsafe jar | CDC: boil 10 minutes below 1,000 ft, add 1 minute per 1,000 ft; "when in doubt, throw it out" | Keep the note. NCHFP/Extension specialist to confirm that the page never implies boiling makes an untested jar safe | NCHFP / Extension |
| SX-08 | MEDIUM | `pemmican-and-dried-meats` L52 `#modern`; `safe-jerky-dehydration` `#storage` | **Jerky storage time.** FSIS: home-dried jerky "1 to 2 months"; NCHFP differs. Both give 160 F pre-heat. The jerky article follows the shortest figure | FSIS jerky page text fetched today | Keep the shortest figure and the explicit disagreement; no curing quantities appear (test-enforced) | NCHFP / Extension |
| SX-09 | MEDIUM | `emergency-hygiene-sanitation` L68 `#toilets` | **Urine disposal "on the lawn or ground, changing the spot".** Supported only by one extension page. No regulator or health-department page in the set says it | OSU Extension: add water to dilute and pour on the lawn or ground, change the spot each time | Add a second authoritative source or label it clearly as one extension's advice. Reviewer to decide whether a location caution (away from wells, water and food gardens) is warranted and, if so, find a source for it. **Do not add one from memory** | Environmental health |
| SX-10 | MEDIUM | `emergency-hygiene-sanitation` L59 `#toilets` | **Wet wipes/sanitizer when no running water.** Washington State DOH says they can be used; CDC's page says sanitizer must be at least 60% alcohol and applies where soap and water are unavailable | Both pages fetched today | Confirm the article's CDC 60% qualifier sits next to the DOH sentence, and that wipes are not presented as equivalent to soap and water | Public health |
| SX-11 | MEDIUM | `home-fire-escape-plan` L44 `#alarms` | NFPA's page states two effectiveness figures ("cut by 60 percent" and "cut in half") | NFPA page contains the 60 percent sentence; the article already marks this "Uncertain" | Keep as uncertain; do not state a single number as settled | Fire safety (USFA/NFPA) |
| SX-12 | MEDIUM | `family-communication-plan` L72 `#phones`; `warnings-radios-offline-maps` L83 | **Call-forwarding advice** ("forward your home number to your mobile before an evacuation") is uncited in its block and its likely sources (FCC pages) returned 403 | No source text retrievable; 0 supporting matches | A human confirms the FCC page says it, or add a citation, or remove. Low harm, but unverified | Source reviewer |
| SX-13 | LOW | Modern-track articles | **Assurance-language scan:** 63 sentences matched "safe/fine/guarantee/always" patterns across all tracks; 19 are on uncited lines (7 of those in modern-track articles, which were read individually). **None is an unattributed assurance** (all are hedges, "FDA says...", or "not a guarantee") | Scan script output | None. Re-run after any rewrite | Editor |
| SX-14 | LOW | `water-math` L40 and L69; `two-week-water-storage` L58; `root-cellars-cool-storage` L59 `#not-a-fridge` | **Our own physical-fact statements** with no source: water weighs a little over 8 lb a gallon; a water heater is "typically a few dozen gallons"; a space that keeps whole produce is not fit for cooked food, meat or dairy. All are labeled Editor's note | Editor's-note tags in text | Reviewer confirms each, or replaces with a sourced statement. The 8.34 lb/gal figure is standard physics; the water-heater and root-cellar statements need confirmation | Editor / domain reviewer |
| SX-15 | LOW | `homemade-water-filters` (whole piece) | The "not validated" stance on homemade sand/charcoal filters is **our inference** from what agencies require of filters, not an agency statement; labeled in-page | No official source evaluating homemade filters found in any cited page | Reviewer confirms the inference is fairly stated and consistent with the approved water guide | Water-quality |

## What was checked and found consistent (not exceptions)

Of the 28 tested items, **18 are supported by wording in a source the same article cites** (sentence-level check), **2 partially** (A10, A13), **6 only at keyword level** (weak; A05, A12, A17, A18, A19, A20), **1 could not be verified** (A15), and **1 is our own reasoning** (B08). See Appendix A. Examples: bucket-toilet steps (Washington DOH), refreeze if ice crystals or 40 F or below (CDC and FoodSafety.gov), feel the door before opening it (Ready.gov), jerky handling times, 1/4-inch slice limit and "don't save marinade" (FSIS, NCHFP, K-State), half-tank-of-gas rule (Ready.gov), let a pressure canner cool naturally (NCHFP). The weak and unverifiable items are marked as such in Appendix A.

## Appendix A: uncited-instruction and discrepancy checks

| ID | Article, line, anchor | Statement (short) | Supporting source in the same article | Finding |
|---|---|---|---|---|
| A01 | emergency-hygiene-sanitation L54 `#toilets` | Turn off the toilet water valve; flush out the bowl | `health-wadoh-toilet` | Supported (WA DOH) |
| A02 | same L59 | Wipes/sanitizer if no running water | `health-wadoh-toilet`, `cdc-hygiene-emergency` | Supported; see SX-10 |
| A03 | same L68 | Dilute urine, pour on ground, change spot | `health-osu-sanitation` | Supported by one extension source; see SX-09 |
| A04 | food-safety-power-outage L76 `#after` | Freezer food with ice crystals or at 40 F or below can be refrozen | `food-cdc-after-emergency`, `food-foodsafety-outage-chart` | Supported ("quality may suffer" appears in source) |
| A05 | same L77 | Check coolers the same way | n/a | **Keyword-level only (weak)** |
| A06 | home-fire-escape-plan L100 `#during` | Feel the doorknob and door before opening | `shelter-ready-home-fires` | Supported (Ready.gov) |
| A07 | safe-jerky-dehydration L76 `#handling` | Ground beef/poultry 2 days; whole red meat 3-5 days refrigerated | `food-fsis-jerky` | Supported (FSIS) |
| A08 | same L79 | Slice no thicker than 1/4 inch | `nchfp-jerky`, `food-ksu-jerky` | Supported |
| A09 | same L36 `#pathogens` | Marinate in the refrigerator; do not reuse marinade | `food-fsis-jerky` | Supported |
| A10 | shelter-or-evacuate L69 `#hazmat` | Chemical shelter-in-place: interior room, close vents and dampers | Ready.gov pages | Interior-room wording found on hurricane/tornado pages; **hazmat page wording not matched (weak)** |
| A11 | same L85 `#evacuate` | Full tank if evacuation likely; keep half tank always | `shelter-ready-evacuation` | Supported |
| A12 | same L68 `#hazmat` | Chemical evacuate/stay-indoors rule | n/a | **Keyword-level only (weak)** |
| A13 | pressure-canning-low-acid L53 `#outline` | Check gasket, vent pipe, level burner | `food-cdc-home-canned` | Gasket and venting supported; **"level burner" not matched** |
| A14 | same L58 | Let the canner cool by itself | `food-nchfp-using-pressure-canners` | Supported (NCHFP) |
| A15 | family-communication-plan L72 `#phones` | Forward home calls to mobile | FCC pages | **Not verifiable (403)**; SX-12 |
| A16 | pantry-rotation L58 `#chart` | Canned ham: 3-4 days refrigerated after opening | `food-fsis-shelf-stable` | Supported (row-specific, FSIS chart) |
| A17, A18 | same L59, L63 | Other refrigerator-time cells | `food-fsis-shelf-stable` and others | **Keyword-level only (weak)** |
| A19 | go-bags L65 `#babies` | Children's medicine dosing caution | Ready.gov pages | **Editor's note; keyword-level only** |
| A20 | three-day-kit L79 `#medicine` | Do not stop or discard a medicine | Ready.gov, CDC | **Editor's note; keyword-level only**; see SX-03 |
| B01 | food-safety-power-outage L41 `#clocks` | FDA 45 F | `food-fda-outage-flood` | Verified; SX-04 |
| B02 | same L42 | 4-hour limit | `fsis-power-failure`, `food-cdc-after-emergency` | Verified; SX-04 |
| B03 | pemmican-and-dried-meats L52 `#modern` | Jerky storage 1-2 months | `hist-food-fsis-jerky` | Verified; SX-08 |
| B04 | pressure-canning-low-acid L99 `#boil` | 10-minute boil | `food-cdc-home-canned` | Verified; SX-07 |
| B05 | home-fire-escape-plan L44 `#alarms` | NFPA 60% vs half | `shelter-nfpa-smoke-alarms` | 60% verified; SX-11 |
| B06 | medication-and-devices L127 `#limits` | FDA device bleach instructions differ | `health-fda-devices` | Verified; SX-06 |
| B07 | medication-and-devices L61 `#cold` | Discard vs replace | FDA, Ready.gov pages | Both wordings present; SX-03 |
| B08 | root-cellars-cool-storage L59 `#not-a-fridge` | Cool space unfit for perishables | FSIS, CDC | Editor reasoning; SX-14 |

## Not covered by this register
Clinical accuracy of any wording; whether any statement is complete for vulnerable households; qualitative statements in the 542 cited blocks; the 30 shared-URL source groups; the 25 sources that could not be read; rendered layout. No QD PASS, medical safety clearance or publication permission is implied.

## Appendix B: cited sources that could not be read on 2026-11-01 (25)

Retrieval attempted by script, then in a real Edge session. No header spoofing and no attempt to defeat a block page. Each needs a human read or an authorized retrieval route.

| source id | result | URL |
|---|---|---|
| `food-foodkeeper` | status 403, chars 227, blocked=True | https://www.foodsafety.gov/keep-food-safe/foodkeeper-app |
| `fsis-botulism` | status 403, chars 271, blocked=True | https://www.fsis.usda.gov/food-safety/foodborne-illness-and-disease/illnesses-and-pathogens/botulism |
| `health-fcc-wea` | status 403, chars 203, blocked=True | https://www.fcc.gov/Alerting/WEA |
| `hist-field-britannica-donner` | status 403, chars 264, blocked=False | https://www.britannica.com/topic/Donner-party |
| `hist-field-nmah-tinder-box` | status 403, chars 286, blocked=False | https://americanhistory.si.edu/collections/object/nmah_308548 |
| `hist-field-si-sextant` | status 403, chars 286, blocked=False | https://timeandnavigation.si.edu/multimedia-asset/sextant |
| `hist-field-usgs-declination` | status 403, chars 512, blocked=False | https://www.usgs.gov/faqs/what-declination |
| `hist-field-usgs-north-arrows` | status 403, chars 512, blocked=False | https://www.usgs.gov/faqs/what-do-different-north-arrows-a-usgs-topographic-map-mean |
| `hist-food-ce-pemmican` | status 403, chars 512, blocked=False | https://thecanadianencyclopedia.ca/en/article/pemmican |
| `hist-food-fsis-molds` | status 403, chars 292, blocked=True | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/molds-food-are-the |
| `hist-food-fsis-smoking` | status 403, chars 287, blocked=True | https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/smoking-meat-and-p |
| `hist-food-lc-salt-works-trail-alliance` | status 403, chars 0, blocked=False | https://lewis-clark.org/the-trail/fort-clatsop/the-salt-works/ |
| `hist-food-metis-fur-trade` | pdf not parseable | https://www.metismuseum.ca/media/document.php/00731.The%20M%C3%A9tis%20Fur%20Trade.pdf |
| `hist-food-monticello-meat` | status 403, chars 571, blocked=False | https://www.monticello.org/encyclopedia/preservation-of-meat |
| `hist-food-mv-smokehouse` | status 403, chars 265, blocked=False | https://www.mountvernon.org/the-estate-gardens/location/smokehouse |
| `hist-food-nk360-bison` | status 403, chars 286, blocked=False | https://americanindian.si.edu/nk360/plains-belonging/itbc.cshtml |
| `hist-food-si-cold` | status 403, chars 286, blocked=False | https://americanhistory.si.edu/explore/stories/keeping-your-food-cool-ice-harvesting-electric-refrigeration |
| `hist-home-loc-simmons-1796` | status 403, chars 257, blocked=False | https://www.loc.gov/item/96126967/ |
| `hist-home-monticello-cisterns` | status 403, chars 571, blocked=False | https://www.monticello.org/encyclopedia/cisterns |
| `hist-home-monticello-ice-house` | status 403, chars 571, blocked=False | https://www.monticello.org/encyclopedia/ice-house |
| `loc-pioneer-diaries` | status 403, chars 257, blocked=False | https://www.loc.gov/item/2002564479/ |
| `loc-prairie-traveler` | status 403, chars 257, blocked=False | https://www.loc.gov/resource/gdcmassbookdig.prairietravelerh01marc/?st=list |
| `shelter-co-oss-reunification` | status 403, chars 512, blocked=False | https://oss.colorado.gov/reunification |
| `shelter-fcc-comms` | status 403, chars 243, blocked=True | https://www.fcc.gov/reports-research/guides/tips-communicating-emergency |
| `si-nmah-life-aboard` | status 403, chars 286, blocked=False | https://americanhistory.si.edu/explore/exhibitions/on-the-water/online/fishing-living/commercial-fishers/atlan |
