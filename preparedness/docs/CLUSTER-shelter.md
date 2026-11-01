# Cluster notes: shelter (sections `shelter-power`, `family-communication`)

Drafted 2026-10-29/30. All four articles are **drafted, awaiting human review**. #12, #13 and #14 are gated (`safety_review.state: pending`). #15 is not gated in the taxonomy; it is also recorded as `pending` because it concerns children's reunification and leans on one state-specific school page and one undated FCC page. Nothing is `approved` or `published`.

## Articles

| # | Slug | Gate | Words (validator count) | Sources cited |
|---|---|---|---|---|
| 12 | `outage-heat-cold-generators` | yes | about 3,980 | 15 |
| 13 | `home-fire-escape-plan` | yes | about 3,530 | 9 |
| 14 | `shelter-or-evacuate` | yes | about 3,420 | 13 |
| 15 | `family-communication-plan` | no | about 3,110 | 14 |

## What I verified (all fetched 2026-10-29 with Firecrawl, `maxAge: 0`, and read in full)

29 sources are in `sources/fragments/shelter.json`. Two upgrade register placeholders (`usfa-fire-escape`, `cdc-co-generators`); 27 are new, prefixed `shelter-`. Pages: CDC (CO basics, CO PSA, power outage, winter storm, heat, reunification), CPSC (CO center, portable heaters), USFA (escape plans), NFPA (escape planning, smoke alarms), FCC (communicating in an emergency), NWS (NOAA Weather Radio), Colorado Office of School Safety, and Ready.gov (power outages, extreme heat, winter weather, home fires, shelter, evacuation, tornadoes, hurricanes, floods, wildfires, hazmat, make a plan, plan for locations, plan form, people with disabilities).

## Placeholders not upgraded

* `ready-are-you-ready` (PDF): the scraper could not read the PDF, so it is **not** upgraded and not cited.
* `nws-nwr` (`weather.gov/cys/nwr`, a Cheyenne office page): I did not read that URL. I verified the national page `https://www.weather.gov/nwr/` and registered it as the new `shelter-nws-nwr`. The old placeholder is untouched.

## Source disagreements found (all stated on the pages)

1. **CO alarm placement.** CDC CO basics: "near every sleeping area." CPSC: every level and outside sleeping areas. Ready.gov: every level, central locations. Not contradictory; the article states all three and the editor's reconciliation (cover both).
2. **CO death figures.** CDC PSA "more than 500 a year" (scope not stated), CDC basics "more than 400" non-fire, CPSC "more than 200" consumer-product non-fire, "more than 100" generator. Shown side by side with their scopes; not combined.
3. **Heat-stroke temperature.** Ready.gov sign "above 103 F"; CDC power-outage page says body temperature "may rise to 106 F or higher within 10 to 15 minutes". Different statements; flagged as uncertain.
4. **Kerosene and unvented heaters.** CDC lists "portable space heaters or kerosene heaters" as backup heat and says "make sure you have proper ventilation if you must use a kerosene heater"; Ready.gov and CPSC give kerosene-fuel rules; the same agencies warn about CO from fuel burning. **No source gives a ventilation figure.** The article gives no instruction for running a fuel-burning heater indoors and says why. See reviewer item R-12-5.
5. **High-rise fire.** USFA: leave, close the door, pull the alarm, use the stairs. NFPA: high-rise and apartment residents "may be safer defending in place." The article states both and gives a clearly labeled editor's judgment (the more cautious reading is USFA's). See R-13-4.
6. **Sealing yourself in.** NFPA: open windows at the top and bottom if possible; Ready.gov: no mention of opening windows. Flagged uncertain.
7. **School reunification.** CDC: faster reunification is better. Colorado (state-specific): do not rush to the school. FCC: text. Colorado: limit calls and texts. Presented as applying at different moments, with "your school's plan governs."
8. **NFPA smoke-alarm effect.** The same NFPA page says working alarms cut the risk of dying in a home fire "by 60 percent" and "in half." Neither figure is quoted.
9. **Page dates that look wrong.** CDC PSA: Updated (2023-11-01) earlier than Published (2024-05-15). CDC reunification: Reviewed (2021-01-06) earlier than Published (2024-11-15). Ready.gov plan form shows "Last Updated 10/30/2026", a day after I read it (probably dynamic). All recorded as shown.

## Claims I could NOT verify, or deliberately left out

* **No numbers or practices that no source gives:** generator size, run time, fuel-storage quantity, wiring or transfer-switch methods, ventilation for any heater, how long a sealed room stays safe, escape-ladder ratings or heights, drill target times, how far "out of the area" the contact should be. The articles say these are not covered.
* Not read: USFA handouts and pictographs, NFPA tip sheets (including the high-rise sheet), Red Cross pages (generator, winter storm, Reconnecting Families), FEMA reunification-support fact sheet, NCMEC, the I Love U Guys Standard Reunification Method, CDC teen-preparedness page, EPA power-outage and indoor-air page, NWS heat and winter pages, CPSC safety-alert PDFs.
* Not covered: earthquake, tsunami, radiological or nuclear emergencies, wells and septic after floods, state or local alarm laws, tenancy law, evacuation-zone data for any area.
* Editor's reasoning not from sources (all labeled in-page): why an out-of-area contact works; a three-level meeting-place structure; keep a paper copy and think about what a child's card reveals; renters should ask landlords in writing; sources are silent on shared custody; the "design for the slowest person" advice; the stay-or-go five-question checklist; the "pattern" that fast local hazards mean shelter and slower wide hazards mean leave.

## Items for the human safety reviewer

(Same format as section C of `SAFETY-REVIEW-CHECKLIST.md`.)

| # | Article | What the reviewer must check | Against |
|---|---|---|---|
| R-12-1 | `outage-heat-cold-generators` | Action box and generator section: 20 ft from windows, doors, vents; exhaust away; never in garage, basement, carport even with doors open; long heavy-duty cord; dry; cool before refueling; never connect to house wiring | CDC power-outage, CDC CO basics, CPSC CO center, Ready.gov power outages and evacuation |
| R-12-2 | same | CO alarm placement reconciliation (alarm outside each sleeping area **and** on each level) is our judgment | CDC CO basics, CPSC, Ready.gov |
| R-12-3 | same | The three-source CO death-figure table is faithful and not misleading | the three pages |
| R-12-4 | same | Heat and cold first actions reproduced from Ready.gov and CDC (heat stroke: 911 plus cooling steps; frostbite: no massage or heating pad; hypothermia: below 95 F is an emergency); we add no treatment of our own | Ready.gov heat and winter weather, CDC winter-storm and power-outage |
| R-12-5 | same | **Kerosene heater handling:** do we want to keep the "we give no instruction for indoor fuel-burning heaters" position? Sources conflict in emphasis and give no ventilation numbers | CDC winter-storm and power-outage, Ready.gov home fires, CPSC heaters |
| R-12-8 | same | Medication wording: FEMA Dec 2023 sheet ("replace ... call your doctor or pharmacist ... use only until you have a new supply") vs CDC and Ready.gov "throw away / discard"; our text defers to the prescriber or pharmacist and never says stop or discard | FEMA V-1008, CDC power-outage, Ready.gov power outages, CDC heat |
| R-12-6 | same | CDC's stranded-car instruction (run motor about 10 minutes per hour, window slightly open, exhaust clear) is reproduced with an editor's caution; confirm it should stay | CDC winter-storm |
| R-12-7 | same | Fan guidance: CDC "only below 90 F" and Ready.gov "do not rely on a fan"; both stated | CDC heat, Ready.gov heat |
| R-13-1 | `home-fire-escape-plan` | Two ways out, meeting place in front, practice twice a year, stay out once out | USFA, NFPA, Ready.gov home fires |
| R-13-2 | same | Sealing-in instructions reproduced from both sources; the window top/bottom difference flagged | NFPA, Ready.gov home fires |
| R-13-3 | same | Burn first step (cool water 3 to 5 minutes, clean dry cloth, 911) reproduced from Ready.gov only | Ready.gov home fires |
| R-13-4 | same | **High-rise and apartment:** USFA high-rise page (posted 2022, reviewed May 2026) makes stair evacuation the default and limits shelter in place to people who cannot self-evacuate; NFPA general page says "may be safer defending in place". Both stated; we read USFA as more specific; NFPA high-rise tip sheet not read | USFA high-rise, USFA escape plans, NFPA, Ready.gov plan for locations |
| R-13-5 | same | Escape-ladder paragraph gives no product or height advice, only NFPA's practice rules | NFPA |
| R-14-1 | `shelter-or-evacuate` | Hazard table rows are faithful to each Ready.gov page; our "fast local = shelter, slow wide = leave" pattern is labeled as ours | Ready.gov tornadoes, hurricanes, floods, wildfires, hazmat, winter weather |
| R-14-2 | same | Tornado vehicle advice reproduced as the page words it (no safe option; drive at right angles only if far, visible, light traffic) | Ready.gov tornadoes |
| R-14-3 | same | Hazmat shelter-in-place and decontamination steps reproduced from an April 2023 page; confirm they are current | Ready.gov hazmat (oldest source here) |
| R-14-4 | same | "Sealing a room is temporary" and our statement that no source gives a duration | Ready.gov shelter and hazmat |
| R-14-5 | same | "Households that cannot easily afford to leave": editor's note only, no program verified | none |
| R-15-1 | `family-communication-plan` | Out-of-area contact recommendation and FCC network-congestion tips (the FCC page is undated and partly outdated) | FCC, Ready.gov evacuation |
| R-15-2 | same | Reunification: CDC vs Colorado emphasis; Colorado is one state's guidance and is labeled as such; confirm that is acceptable | CDC reunification, Colorado Office of School Safety |
| R-15-3 | same | Editor's suggestions about children's contact cards (do not reveal more than needed), paper copies, three-level meeting places, custody note | none (labeled editor's) |
| R-15-4 | same | NCMEC hotline 1-800-THE-LOST is reproduced from the CDC page and has not been called or checked on NCMEC's own site | CDC reunification |

## Self-audit after the first independent QD review (2026-10-30)

Merged `origin/feature/preparedness-archive-v1` (head ee591e2) into this branch (merge commit 75d21d5), with no conflicts. I did not edit `tools/`, `tests/`, `assets/` or `taxonomy.json`; an earlier uncommitted edit of mine to a test was discarded before the merge, so the lead's derived-sections test is the only version.

Audit of each defect class, with what I changed (targeted edits, no rewrites):

| Class | Finding | Action |
|---|---|---|
| (a) blanket discard/stop/skip about medication or medical care | **Found, #12.** I had reproduced the CDC's "throw away refrigerated medication" wording. The newer FEMA fact sheet (V-1008, December 2023, read in full, 2 pages) says "replace ... unless the drug's label says otherwise," "call your doctor or pharmacist" and "use the medicine only until you have a new supply." | Rewrote the bullet to lead with the FEMA wording, note that the CDC and Ready.gov outage pages say throw away or discard, and say plainly that none of this is a reason to stop, skip or throw out a medicine without asking the pharmacist or prescriber (citing the CDC heat page's "don't stop or change your medicines until you talk to your doctor"). A search found no other medication, "discard" or "skip" instruction in the four articles. |
| (b) drills or actions that interrupt life-safety or medical equipment, or create smoke or fire | **Found, #13 and #14.** The fire-drill advice (dark, eyes closed) had no caution against real smoke, flame or cutting power. #14 repeated Ready.gov's "shut off water, gas and electricity" with no medical-equipment caveat. | #13: added a labeled editor's note: simulation only, no real smoke, flame, heat or fog, nothing lit, no switching off power or any safety or medical equipment, clear trip hazards first. #14: added an editor's note that the shut-off applies only if the home is damaged and you are instructed, and that anyone relying on electrically powered medical equipment should not cut power on their own judgment and should plan with their provider. |
| (c) misclassified source kinds | **Found.** NFPA (two entries) was `regulator`. | Changed to `nonprofit`. All other kinds are government bodies (CDC, CPSC, USFA, FCC, NWS, FEMA/Ready.gov, one state office). The Colorado Office of School Safety is a state office, kept as `regulator`; its parent department was not confirmed. |
| (d) legal duties or regulatory claims from templates or secondary summaries | **None found.** Landlord and tenancy points are labeled editor's notes saying we did not research tenancy law. The flood-insurance 30-day statement and the voluntary registries are attributed to Ready.gov; "authorized adults" is attributed to Colorado; "check that kerosene heaters are legal" is the CDC's. No NFPA 72 or code citations. | None. |
| (e) partly read PDFs or long pages recorded as fully read | **Found, register notes.** Notes did not say how much was read, and the plan form was fetched at an old PDF address whose PDF was never read. | Every entry now carries a "Read:" note (page text as rendered by Firecrawl; videos, images, linked PDFs and handouts not opened). The plan-form note says only the web form's field labels were read. The two new entries state exactly how they were read (below). |
| (f) CO, generator, heating, high-rise shelter-in-place and evacuation wording | **Found.** (1) CO distance: pages say "at least 20 feet" (Ready.gov, CPSC), "more than 20 feet" (CDC basics) and "less than 20 feet" as the forbidden zone (CDC outage); FEMA's December 2023 sheet says "at least 20 feet away from any building openings like windows, doors or garages." (2) Nothing said 20 feet is only a minimum. (3) High-rise: #13 relied on a general USFA escape page and one NFPA line; USFA's dedicated high-rise page had not been read. (4) FEMA's newer sheet says alarms on every level **and** near sleeping areas, and adds gas stovetop/oven/grill/dryer, gas stoves and candles for heat, and the vehicle-in-garage rule. | #12: added FEMA's wording of the distance, a labeled editor's note that 20 feet is a minimum and not full protection by itself, a FEMA row in the alarm table, and FEMA's heating and vehicle sentences. #13: replaced the "two agencies" box with the current USFA high-rise page (stairs by default; shelter in place only for people who cannot self-evacuate; keep stair doors closed and never propped open; no elevators) and a labeled difference from NFPA's "defending in place." |

Reviewer table changes: R-13-4 now describes the USFA high-rise page versus NFPA; new R-12-8 covers the medication wording.

### New sources added in this pass (`shelter.json`, now 31 entries)

* `shelter-fema-power-outage-sheet`: FEMA V-1008, December 2023. Firecrawl credits ran out, so a web-fetch subagent downloaded the PDF (its own text extraction failed); I extracted the text locally with PyMuPDF and read both pages in full. `verified_on` 2026-10-30.
* `shelter-usfa-high-rise`: USFA blog page, posted 2022-01-12, last reviewed 2026-05-01. Read through a web-fetch subagent's extraction (about 19,000 characters, no sign of truncation). Quotes were returned verbatim by the tool but not independently checked against the live HTML; the handout PDF, images and pictographs were not opened. `verified_on` 2026-10-30.

All 31 sources remain `human_link_check: false`. Every article remains `status.publish: draft` and `safety_review.state: pending`. I am not claiming QD pass or approval.

### Statements that could not be verified to the QD standard

* The 20-foot figure is quoted from four official sources, but none says why 20 feet or that it is sufficient; our caution that it is a floor is an editor's note.
* The CDC "run the motor about 10 minutes per hour" instruction is the CDC's alone; FEMA's newer sheet gives only the general "well-ventilated place outside" rule. Kept with a caution (R-12-6); a reviewer may prefer to cut the number.
* Hazmat steps come from an April 2023 Ready.gov page and were not cross-checked against a newer document.
* Colorado school-reunification guidance is one state's; no second state source was read.
* The FCC emergency-communications page is undated and partly outdated.
* NFPA's high-rise tip sheet, USFA handouts, Red Cross pages and FEMA's reunification fact sheet were not read.
* The USFA high-rise page was read through an extraction tool, not in a browser.

## Items for the lead

1. `preparedness/build/` is no longer tracked; I committed no build output.
2. No new components were needed.
3. The earlier NFPA `kind` request is resolved by the new `nonprofit` kind.

## Sprint 2 (2026-11-01): evidence pass, tools, review package

Branch `claude/prep-shelter-continuation`, started from review candidate `5daeaf2` (that branch is untouched). Details: `SHELTER-SOURCE-LEDGER.md`, `SHELTER-QD-PACKET.md`, `SHELTER-QA.md`.

**Resolved or narrowed**
* High-rise: NFPA's high-rise tip sheet and USFA's handouts were read. NFPA's general "may be safer defending in place" is not repeated in NFPA's own high-rise sheet; the three documents agree on stairs as the default and sealing in only for people who cannot get out. #13 now says so, tells no one to defend in place on their own judgment, and sends readers to their building's plan.
* Stranded vehicle: the CDC's 10-minutes-per-hour instruction is corroborated by the NWS (same figures, window slightly open, clear exhaust); kept with attribution and caveats. A reviewer may still prefer to drop the number (R-12-6).
* Shelter versus evacuate: the "fast hazards mean shelter" shorthand was removed from the body, dek and meta description; replaced by four deciding factors, a diagram, and "official order first."
* Chemical shelter in place: CDC's June 2026 page read and compared with Ready.gov's April 2023 page; differences shown; no sealed-room duration is given anywhere.
* NCMEC: the CDC's 1-800-THE-LOST and NCMEC's own site's 1-800-843-5678 are the same number. Not call-tested.
* Texting: Ready.gov's March 2026 page now leads; the FCC page is demoted to older, flagged detail.

**Still open (for the human reviewer; see the QD packet)**: kerosene and indoor fuel-heater handling; the numeric vehicle instruction; combined medication wording; high-rise reading; window wording when sealing in; four-factor framing; CDC versus Ready.gov hazmat steps; custody, pickup and card privacy; USDA food-safety pages unverified; only one state's school reunification example.

**New**: 3 tools (`home-fire-escape-worksheet`, `power-outage-planner`, `reunification-plan`), generated by `tools/gen_shelter_tools.py`; 10 new sources (fragment now 41, all `human_link_check: false`); 2 diagrams; 28 new tests.

**For the lead**: `taxonomy.json` gained two tool rows and a retitled `reunification-plan` row (all three gated, status drafted-pending-safety-review); the section hubs for `shelter-power` and `family-communication` are the shared template and list only articles, so they do not show the tools (the tools appear in the `field-tools` hub and are cross-linked from the articles); a "related free tools" row on section hubs would need a `build.py` change. `docs/qa/` also holds two stale untracked page images (`card-print-page1.png`, `worksheet-print-page1.png`) that I could not delete (the shell blocked the removal); they are not committed and can be deleted.
