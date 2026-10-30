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
| R-12-6 | same | CDC's stranded-car instruction (run motor about 10 minutes per hour, window slightly open, exhaust clear) is reproduced with an editor's caution; confirm it should stay | CDC winter-storm |
| R-12-7 | same | Fan guidance: CDC "only below 90 F" and Ready.gov "do not rely on a fan"; both stated | CDC heat, Ready.gov heat |
| R-13-1 | `home-fire-escape-plan` | Two ways out, meeting place in front, practice twice a year, stay out once out | USFA, NFPA, Ready.gov home fires |
| R-13-2 | same | Sealing-in instructions reproduced from both sources; the window top/bottom difference flagged | NFPA, Ready.gov home fires |
| R-13-3 | same | Burn first step (cool water 3 to 5 minutes, clean dry cloth, 911) reproduced from Ready.gov only | Ready.gov home fires |
| R-13-4 | same | **High-rise and apartment:** USFA "leave" vs NFPA "defend in place"; our labeled cautious reading | USFA, NFPA, Ready.gov plan for locations |
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

## Items for the lead (not for the reviewer)

1. **Existing test now fails for any contributor who adds a new section.** `tests/test_preparedness.py::test_landing_lists_only_built_articles_and_no_empty_sections` hardcodes `populated_sections == ["water", "lost-ways", "field-tools"]`. With my articles the list is `["water", "shelter-power", "family-communication", "lost-ways", "field-tools"]`. I did not edit the test (shared). The brief says all tests must pass, so the lead should change the assertion to compare against the sections of the built articles (as `test_hubs_exist_only_for_populated_sections` already does). Every other check passes (validate: 0 errors; build runs; tests: 1 failure, this one).
2. **Source `kind` for NFPA.** NFPA is a nonprofit standards body, not a government agency. No allowed `kind` fits, so I used `regulator` and said so in the register notes. The lead may want a separate kind.
3. **Build outputs.** `build/` is tracked in the repo. I did not commit regenerated build outputs (they conflict across contributors); I restored the tracked files and removed my local build artifacts.
4. **No new components were needed.**
