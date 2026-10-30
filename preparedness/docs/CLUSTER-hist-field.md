# Cluster notes: hist-field (lost-ways: #31, #32, #34)

Drafted 2026-10-29 on branch `claude/prep-hist-field-9db767`. All three are **drafted, awaiting human review**. Nothing is approved or published.

| Slug | n | Gate | safety_review | Words (validator count) |
|---|---|---|---|---|
| `fire-making-across-time` | 31 | yes | `pending` | ~3,270 |
| `navigation-before-gps` | 32 | no | `not-required` | ~3,050 |
| `pioneer-supply-chains-failed` | 34 | no | `not-required` | ~2,890 |

Sources: 29 entries in `sources/fragments/hist-field.json`; each fetched with Firecrawl on 2026-10-29. Two are upgrades of register placeholders (`loc-prairie-traveler`, `loc-pioneer-diaries`); the rest are new `hist-field-*` ids.

## What was read, and how far

* Read in full (page text): all NPS, USFA, Smokey Bear, NFPA, CDC CO, NWS, NOAA NCEI, NASA North Star, RMG (three stories), Science Museum Group overview, both Walker museum pages, NMAH tinder box, Smithsonian sextant, Utah History to Go, NPS Donner page, California State Parks Donner page, Britannica Donner.
* Read only in part: USGS "What is declination?" and USGS north-arrows page (long pages; explanatory text read, related-links boilerplate skipped); LOC *Prairie Traveler* (record, title page, preface, contents; **not** the chapters); LOC pioneer diaries (catalogue record only; **not** the diaries); McCurdy 1994 (**abstract only**, full text is scanned images).

## Source disagreements (all stated on the pages)

1. **Walker's first sale:** BBC-hosted Preston Hall record says 12 April 1827; Tees Valley Museums says 7 April 1827. Page says "uncertain".
2. **Outdoor-fire distances:** USFA 25 ft (campfire) / 10 ft (fire pit); NPS 15 ft; Smokey Bear 15 ft; NFPA fire pit 10 ft, NFPA 1 50 ft where adopted. Page tabulates and defers to the local authority.
3. **Lighter fluid:** NPS allows "only lighter fluid" where the park permits; USFA/NFPA/Smokey Bear say never use flammable liquids. Page follows the stricter statement.
4. **Donner party counts:** NPS 87 people / 40 deaths; Utah State History 47 of 87 reached Sutter's Fort; McCurdy 90 people / 42 deaths; Britannica 87 at peak, 42 deaths, 47 survivors (does not add up). Page tabulates and picks none.
5. **Departure date and claimed shortcut:** NPS April 12 from Illinois, saving "150-500 miles"; Britannica April 14 from Springfield, "more than 300 miles", and says the cutoff was actually 125 miles longer.
6. **Paiute role:** Britannica says Paiute warriors killed oxen; NPS quotes Sarah Winnemucca that her people would have helped but were afraid. Labelled "Disputed"; no contemporary Paiute account found.

## Claims I could NOT verify (and so did not make)

* Any sun/shadow-stick direction method or accuracy (no agency or museum source found). The nav article says so and teaches none.
* A Polaris accuracy figure; latitude by Polaris altitude (only an unvetted source found, not used).
* Walker's match-head quantities (deliberately not given); the "Wikipedia"-level details (equal parts, dimensions) were not used.
* The Pioneer Monument plaque wording (seen only on non-approved sites); not used.
* Breen's diary, Virginia Reed's letter and Hastings's *Emigrants' Guide* in the original: quoted only as reported by Britannica (four words at most).
* Indigenous and Polynesian wayfinding, and Paiute/Washoe perspectives on 1846: no sources read; the pages say so.
* Whether Smokey Bear's page is published by USDA Forest Service (the page text does not say; NPS refers to it as Forest Service / Smokey Bear material).

## Items for the human safety reviewer: `fire-making-across-time` (gated)

| # | Claim in the article | Where | Check against |
|---|---|---|---|
| H1 | No instructions for starting a fire by friction, flint-and-steel, or chemicals; Walker's match-head chemicals deliberately omitted | Whole page | Read it |
| H2 | Act box: check bans, never charcoal/camp stove indoors, no flammable liquids, never leave unattended | Read first | NPS campfires, NFPA, Smokey Bear, CDC CO |
| H3 | Distance table (10/15/25/50 ft) is reported by source, with "ask your local authority; larger is safer" (our reasoning, marked) | "Where the agencies differ" | USFA, NPS, Smokey Bear, NFPA. **Decision: is giving these figures acceptable, or link out only?** |
| H4 | NPS allows lighter fluid; we follow the stricter "never" line | Same section | NPS vs NFPA/Smokey Bear |
| H5 | CO paragraph: no generator or vehicle-exhaust numbers reproduced; NWS stuck-vehicle and "build a fire" statements named but not reproduced | CO subsection | CDC CO basics, NWS winter-before/during. **Decision: acceptable to cite NWS pages we deliberately do not summarize?** |
| H6 | Verdict panel: flint/steel "context-dependent", friction/fire piston "not validated", phosphorus matches "unsafe". The ratings are our reasoning; no agency rates these | Verdict | Science Museum, NPS Pipe Spring |
| H7 | Science Museum provenance caveat reproduced; peoples named as the museum names them, not independently confirmed | Skill section | Science Museum Group |
| H8 | Kind labels: NPS Pipe Spring is tagged `museum-object`, NFPA tagged `regulator` though it is a standards body | Fragment | Fragment notes |

## Notes for the other articles' reviewers (not gated)

* `navigation-before-gps`: NOAA sign convention for true bearing is reproduced (add declination; west negative) with the instruction to check the date and place. Dates and accuracy figures (3 s/day, within 1 degree, 1.5 degrees vs 10 degrees) are from RMG and are labelled as single-trial figures.
* `pioneer-supply-chains-failed`: please read the counts table and the winter/cannibalism paragraphs for tone. McCurdy is cited from the abstract only. The "chain" framing (food, animals, time, information) is our reading and is marked as an editor's note.

## Technical flags for the lead

* **Duplicate-URL risk:** other clusters may register the same CDC carbon-monoxide, NWS winter-storm, NPS campfire or LOC Prairie Traveler URLs under different ids; the validator rejects duplicate URLs at merge. If so, reconcile ids when merging fragments.
* `safety_review.state` is `not-required` for #32 and #34 (taxonomy `gate: false`). Change to `pending` if the lead wants every history piece reviewed.
* Build outputs under `preparedness/build/` were regenerated locally but not committed (hubs and landing are shared files).
* No new component or tool change was needed. The `kind` list has no clean fit for NFPA or an NPS interpretive page; a `standards-body` kind would help.
