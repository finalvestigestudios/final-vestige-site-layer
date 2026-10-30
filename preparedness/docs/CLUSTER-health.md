# Cluster notes: health (sections `health-sanitation`, `family-communication`)

Status: three articles **drafted, awaiting human review**. All `safety_review.state` are `pending`; none is published. Sources read live on 2026-10-29 (Firecrawl, `maxAge: 0`).

| # | Slug | Gate | Words (build count) | Sources cited |
|---|---|---|---|---|
| 17 | `medication-and-devices` | yes | ~3,700 | 8 |
| 18 | `emergency-hygiene-sanitation` | yes | ~3,300 | 7 |
| 19 | `warnings-radios-offline-maps` | no (set to `pending` anyway) | ~2,950 | 9 |

## What was verified
All 20 sources are in `sources/fragments/health.json`: CDC hygiene (upgrades placeholder `cdc-hygiene-emergency`), CDC power outage, CDC septic, CDC archived sanitation comparison, FDA safe drug use, FDA insulin, FDA medical devices, HHS emPOWER About, Ready.gov (power outages, people with disabilities, kit, plan, alerts), FEMA IPAWS, FCC WEA, FCC communicating-in-an-emergency, NWS NWR (upgrades `nws-nwr`, a Cheyenne office page) and NWS NWR national page, Washington DOH toilet page, OSU Extension EM 9334.

## Source disagreements found (all stated on the pages)
1. **Where bagged human waste goes.** Washington DOH: put bags in the garbage can. OSU Extension: do **not** put human waste in normal garbage or landfill; store until the sanitary system is repaired. Article 18 shows both and says to ask the local authority.
2. **Refrigerated medicine after an outage.** CDC and Ready.gov: discard after a day or more unless the label says otherwise. FDA: check the label or ask a pharmacist/manufacturer; life-sustaining drug may be used until replaced. FDA insulin page: vials/cartridges tolerate 59-86 F for up to 28 days. Article 17 sets them side by side and does not merge them.
3. **Bleach dose for device water.** The FDA medical-devices page gives its own dose (5.25% bleach, 1/8 tsp per gallon clear, 1/4 tsp cloudy) that differs from the CDC table in `making-water-safer` (8 drops/gal, doubled if cloudy). Neither is reprinted in the new articles; both link to the water guide and the device maker. **Lead to note:** the approved water article is unaffected, but a reader following the FDA page would use a larger dose.

## Claims and sources we could NOT verify
- American Red Cross and AHA first-aid pointers: not fetched; articles only direct readers to them without quoting.
- emPOWER: both pages read address public health agencies. We found no individual enrolment instructions and say so; we do not claim none exist.
- FCC text-to-911, FEMA "alerting people with disabilities", FEMA WEA public page, FCC WEA-capable-devices guide, CDC diapering fact sheets, CDC five-step handwashing page: not read, not cited, named as unread in the Limits sections.
- State emergency refill laws, local registries, utility priority restoration speed: sources are silent; articles say so.
- No official source evaluates offline map apps. Article 19 says so and labels its two sentences of advice as editor's reasoning.
- Weather watch/warning definitions: deliberately left to the local NWS office (not read).

## Date quirks (recorded as shown)
CDC hygiene shows Updated before Published. CDC power outage shows Updated Jan 2024 but Reviewed Aug 2026. FDA pages carry dates only in page metadata. NWS pages are undated; the NWR national page lists live outages and will change.

## Material deliberately NOT reproduced
- FDA's insulin unit-conversion/switching tables (clinical dosing; the page itself says to switch under a doctor's care).
- FDA's manufacturer telephone table (the page says numbers change).
- No bleach or disinfectant ratios for toilets/buckets (no page read gives one).

## Items for the human safety reviewer (same table shape as SAFETY-REVIEW-CHECKLIST section C)

| Article / tool | What the reviewer must check | Against |
|---|---|---|
| `medication-and-devices` | Insulin figures quoted with context (36-46 F fridge; 59-86 F up to 28 days for manufacturer vials/cartridges; diluted or decanted within two weeks; pump set 48 h; above 98.6 F discard; do not use frozen). Confirm the three-way refrigerated-medicine table reproduces each page faithfully and the "same direction, different emphasis" wording is fair. Confirm we are comfortable with the article giving **no** conversion or dosing and with the FDA-lifesaving-exception wording ("appears unchanged" is FDA's phrase). Editor's notes (marked) on priority lists being "a place in a queue" and apartment generators. Bleach-dose discrepancy is flagged, not reprinted. | FDA safe drug use, FDA insulin, FDA devices, CDC power outage, Ready.gov power outages and disabilities |
| `emergency-hygiene-sanitation` | Bag-toilet steps (WA DOH) and twin-bucket details (OSU: 13-gal bags 3-5 mil, about a half cup carbon material, poo bucket no more than half full, urine bucket about one-quarter full, 100 ft from water for burying) reproduced accurately. The unresolved garbage-disposal disagreement and our "ask local authority" handling. Use of an **archived** CDC page, restricted to the options table and two general principles. OSU's under-$20 cost figure (2021) labeled as an order of magnitude. | WA DOH toilet page, OSU EM 9334, CDC hygiene, CDC septic, CDC archive |
| `warnings-radios-offline-maps` | WEA statements (not affected by congestion; free; may need enabling), EAS (10-minute presidential access), NWR frequencies and features, FCC call tips reproduced accurately. Editor's note that WEA still depends on a working tower. The disclosed gap on offline map apps. FCC page is undated with older-technology wording. | Ready.gov alerts, FEMA IPAWS, FCC WEA and tips, NWS NWR pages |

## Notes for the lead (tooling)
- **Test failure outside my files.** `tests/test_preparedness.py::test_landing_lists_only_built_articles_and_no_empty_sections` hardcodes `populated_sections == ["water","lost-ways","field-tools"]`. It now fails because `health-sanitation` and `family-communication` are populated (the build also emitted new hubs for them, as intended). Validate and build pass; this one test needs updating by whoever owns `tests/`, and will fail for every contributor who adds a new section.
- `build/` outputs are tracked in git; I did not commit regenerated files, to avoid merge conflicts across the parallel branches. Rebuild after merging.
- `related` lists some slugs not yet built (`family-communication-plan`, `household-emergency-plan`, `go-bags`, `shelter-or-evacuate`, `navigation-before-gps`, `outage-heat-cold-generators`, `sanitation-before-germ-theory`); the validator only requires them to exist in the taxonomy. The article bodies link only to built guides, except plain-text mentions.
