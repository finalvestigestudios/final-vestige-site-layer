# Cluster notes: health (sections `health-sanitation`, `family-communication`)

Status: three articles **drafted, awaiting human review** (post-QD self-audit recorded at the end of this file). All `safety_review.state` are `pending`; none is published. Sources read live on 2026-10-29 (Firecrawl, `maxAge: 0`).

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

## Self-audit against the QD lessons (2026-10-30)

Scope: `medication-and-devices`, `emergency-hygiene-sanitation`, `warnings-radios-offline-maps` and `sources/fragments/health.json`. This is my own audit, not an independent review; it is not a QD pass and not an approval. `status.publish` is `draft` and `safety_review.state` is `pending` on all three.

| Defect class | Finding | Action |
|---|---|---|
| (a) Blanket discard/stop/skip about medication | Article 17 reproduced "discard refrigerated medication" (CDC, Ready.gov page) without a clear "do not stop or discard on your own". The Ready.gov web page (updated 2026-06-04) says *discard*; FEMA's December 2023 fact sheet says *replace* and *call your doctor or pharmacist*. | Read the fact sheet in full (new source `health-fema-power-outage-sheet`). Action box now says not to stop, throw out or ration a prescribed medicine on your own and to arrange a replacement. Comparison table shows both FEMA wordings. New editor's notes explain that discard/replace means replacement, not going without. Insulin above 86 F is framed as the FDA's last-resort acknowledgment with a tell-your-clinician line. Floodwater discard is paired with the FDA exception and a call-first-for-a-replacement line. |
| (b) Drills that interrupt life-safety or medical equipment | No drill switches off main power or medical equipment. Article 19 told readers to practice phone maps with the network off. | Added: use a spare or nonessential device, never disable a phone used for medical alerts, device apps or calling for help. |
| (c) Misclassified source kinds | All 21 fragment entries are `regulator` (federal or state agency) or `extension` (OSU). No Red Cross, AHA or other nonprofit is cited. The CDC archive page is a regulator page but archived; that is stated. | None needed. |
| (d) Legal duties, eligibility, regulatory claims inferred | None asserted. State refill laws, registries, utility priority speed and emPOWER enrolment are explicitly stated as unverified. WEA carrier participation and FCC rules are quoted from FCC and FEMA text only. | None needed. |
| (e) Partly read PDFs or long pages recorded as fully read | The Dec 2023 FEMA sheet could not be decoded by the first fetch tool; it was read in full by extracting text from the saved PDF (one page). FCC WEA page: archive list scanned by titles only. Linked sub-pages and PDFs on several sources were not opened. | Register `notes` now state the exact read scope for every affected source. |
| (f) Infant feeding, dosing, pregnancy, CO/fire | No infant-feeding, pregnancy or dosing statement is made. Insulin storage figures are the FDA's, with conditions and the product-label caveat; conversion tables not reproduced. CO rules quote FDA and CDC wording (never in an enclosed space, 20 ft from openings, detector, poison control). Oxygen/flame statement is the FDA's wording only. | Insulin wording strengthened as above. |

### Statements I could not verify to this standard
- Whether state emergency-refill laws, local registries and utility priority lists work as readers might hope: sources silent, stated on the page.
- The Ready.gov page vs fact-sheet wording difference is shown but not resolved; I cannot say which FEMA text the agency regards as authoritative beyond their dates (page June 2026, sheet December 2023).
- Offline map advice (editor's reasoning only, labeled).
- WEA-during-tower-outage limitation is our inference, labeled; the FCC item it points to was not opened.
- Red Cross/AHA first-aid guidance was not read and is only named as a pointer.

### Link checks
All sources in `health.json` remain `human_link_check: false`. No human has clicked these links.

## Live fidelity re-check (2026-11-01)
Method: `curl` each page, strip tags, exact-string match the figures used in the articles. This checks that quoted figures still appear on the live page; it does not replace a human reading.

| Source | Result |
|---|---|
| FDA insulin | Matched: 36-46 F, 59-86 F up to 28 days, two weeks, do not use (frozen), 48 hours, 98.6 F |
| FDA safe drug use | Matched: floodwater discard even in original containers, "appears unchanged", purified or bottled water, state emergency refill laws |
| Ready.gov power outages | Matched: "discard" wording and "more than a day" (page unchanged since read) |
| OSU EM 9334 | Matched: 13-gallon, 3-5 mil, half cup, half full, 100 feet, one-quarter full, under $20 |
| NWS NWR national | Matched: all seven frequencies, "more than 1000" transmitters |
| Ready.gov alerts | Matched: 10 minutes, repeated twice, no subscription, five locations |
| CDC power outage, FCC tips | **Not re-checked**: server returned HTTP 403 to scripted requests. Last read 2026-10-29 via Firecrawl. |
| Washington DOH toilet page | **Not re-checked**: connection failed from this machine. Last read 2026-10-29 via Firecrawl. |
| All other sources | Not re-checked (no distinctive figures used). |

No article text changed as a result. `human_link_check` remains `false` on every source.
