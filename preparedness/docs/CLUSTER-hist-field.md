# Cluster notes: hist-field (lost-ways: #31, #32, #34)

Drafted 2026-10-29 on branch `claude/prep-hist-field-9db767`. All three are **drafted, awaiting human review**. Nothing is approved or published.

| Slug | n | Gate | safety_review | Words (validator count) |
|---|---|---|---|---|
| `fire-making-across-time` | 31 | yes | `pending` | ~3,270 |
| `navigation-before-gps` | 32 | no | `not-required` | ~3,050 |
| `pioneer-supply-chains-failed` | 34 | no | `not-required` | ~2,890 |

Sources: 28 entries (after the audit below removed the Smokey Bear page) in `sources/fragments/hist-field.json`; each fetched with Firecrawl on 2026-10-29. Two are upgrades of register placeholders (`loc-prairie-traveler`, `loc-pioneer-diaries`); the rest are new `hist-field-*` ids.

## What was read, and how far

* Read in full (page text): all NPS, USFA, NFPA (the article only, not the NFPA 1 code), CDC CO, NWS, NOAA NCEI, NASA North Star, RMG (three stories), Science Museum Group overview, both Walker museum pages, NMAH tinder box, Smithsonian sextant, Utah History to Go, NPS Donner page, California State Parks Donner page, Britannica Donner.
* Read only in part: USGS "What is declination?" and USGS north-arrows page (long pages; explanatory text read, related-links boilerplate skipped); LOC *Prairie Traveler* (record, title page, preface, contents; **not** the chapters); LOC pioneer diaries (catalogue record only; **not** the diaries); McCurdy 1994 (**abstract only**, full text is scanned images).

## Source disagreements (all stated on the pages)

1. **Walker's first sale:** BBC-hosted Preston Hall record says 12 April 1827; Tees Valley Museums says 7 April 1827. Page says "uncertain".
2. **Outdoor-fire distances:** USFA 25 ft (campfire) / 10 ft (fire pit); NPS 15 ft; NFPA fire pit 10 ft, NFPA 1 50 ft where adopted (NFPA's summary of the code). Page tabulates and defers to the local authority.
3. **Lighter fluid:** NPS allows "only lighter fluid" where the park permits; NFPA says never use gasoline or other flammable or combustible liquids. Page follows the stricter statement.
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
* Who publishes the Smokey Bear page: the text did not say and a follow-up fetch was blocked (Firecrawl credits exhausted), so the source was removed instead of kept as `regulator`.

## Items for the human safety reviewer: `fire-making-across-time` (gated)

| # | Claim in the article | Where | Check against |
|---|---|---|---|
| H1 | No instructions for starting a fire by friction, flint-and-steel, or chemicals; Walker's match-head chemicals deliberately omitted | Whole page | Read it |
| H2 | Act box: check bans, never charcoal/camp stove indoors, no flammable liquids, never leave unattended | Read first | NPS campfires, NFPA, CDC CO |
| H3 | Distance table (10/15/25/50 ft) is reported by source, with "ask your local authority; larger is safer" (our reasoning, marked) | "Where the agencies differ" | USFA, NPS, NFPA. **Decision: is giving these figures acceptable, or link out only?** |
| H4 | NPS allows lighter fluid; we follow the stricter "never" line | Same section | NPS vs NFPA |
| H5 | CO paragraph: no generator or vehicle-exhaust numbers reproduced; NWS stuck-vehicle and "build a fire" statements named but not reproduced | CO subsection | CDC CO basics, NWS winter-before/during. **Decision: acceptable to cite NWS pages we deliberately do not summarize?** |
| H6 | Verdict panel: flint/steel "context-dependent", friction/fire piston "not validated", phosphorus matches "unsafe". The ratings are our reasoning; no agency rates these | Verdict | Science Museum, NPS Pipe Spring |
| H7 | Science Museum provenance caveat reproduced; peoples named as the museum names them, not independently confirmed | Skill section | Science Museum Group |
| H8 | Kind labels: NPS Pipe Spring is tagged `museum-object`; NFPA is now `nonprofit` | Fragment | Fragment notes |

## Notes for the other articles' reviewers (not gated)

* `navigation-before-gps`: NOAA sign convention for true bearing is reproduced (add declination; west negative) with the instruction to check the date and place. Dates and accuracy figures (3 s/day, within 1 degree, 1.5 degrees vs 10 degrees) are from RMG and are labelled as single-trial figures.
* `pioneer-supply-chains-failed`: please read the counts table and the winter/cannibalism paragraphs for tone. McCurdy is cited from the abstract only. The "chain" framing (food, animals, time, information) is our reading and is marked as an editor's note.

## Technical flags for the lead

* **Duplicate-URL risk:** other clusters may register the same CDC carbon-monoxide, NWS winter-storm, NPS campfire or LOC Prairie Traveler URLs under different ids; the validator rejects duplicate URLs at merge. If so, reconcile ids when merging fragments.
* `safety_review.state` is `not-required` for #32 and #34 (taxonomy `gate: false`). Change to `pending` if the lead wants every history piece reviewed.
* Build outputs under `preparedness/build/` were regenerated locally but not committed (hubs and landing are shared files).
* No new component or tool change was needed. The `kind` list has no clean fit for an encyclopedia (Britannica, tagged `scholarship`) or an NPS interpretive page (tagged `museum`); a `reference` kind would help.

## QD self-audit (2026-10-30, after merging `origin/feature/preparedness-archive-v1` at ee591e2)

Merged cleanly (no conflicts). Fixes were targeted edits; `status.publish` is `draft` everywhere; #31 stays `safety_review.state: pending`; #32 and #34 keep `not-required` (taxonomy `gate: false`). **All 28 sources remain `human_link_check: false`.** No QD pass or approval is claimed.

| Defect class | Finding | Action |
|---|---|---|
| (a) Instructions harmful if followed literally (fire) | No how-to for any fire-starting method; match-head chemicals omitted. One sentence told readers to "get into fresh air and call for help" for CO symptoms, which the CDC page we read does not say | Reworded to the CDC's own symptom list. Safe-practice section now rests on USFA, NPS, NFPA and CDC wording with the hazard qualifications (bans, never indoors, CO, supervision, no flammable liquids) |
| (b) Misclassified kinds | NFPA was `regulator` (validator now rejects it); McCurdy was `scholarship`; Smokey Bear page tagged `regulator` with an unverified publisher | NFPA -> `nonprofit`; McCurdy -> `journal`; Smokey Bear source removed and its few claims re-based on NPS and NFPA. Still imperfect: Britannica (`scholarship`) and NPS interpretive pages (`museum`), flagged for the lead |
| (c) Claims inferred from a secondary summary | NFPA 1 "50 ft" and permit statements come from an NFPA blog about the code; Marcy handbook sentence inferred its approach to direction-finding from a contents list; the nav article cited a Smithsonian sextant page for a chronometer sentence it does not contain | Reworded as "NFPA's summary, code not read"; handbook inference deleted; chronometer sentence deleted |
| (d) Partly read sources recorded as fully read | LOC *Prairie Traveler*: only OCR of the first 25 of 398 page images; McCurdy: abstract only; USGS pages: long page, explanatory text read; NFPA 1 never read | Register notes now state exactly this. Not read at all: Marcy chapters, LOC diaries, Breen, Reed, Hastings, Walker's day book, NFPA 1 |
| (e) Donner figures, dates, causation | Dek and one editor's note stated causation as fact ("information failure before food failure"); "Paiute leader and writer" and "men with ... reasons of their own" went beyond the sources; Then panel claimed "months from anyone who could help"; the intro listed Smithsonian material not used | Causation softened to what the sources locate and an explicit "we cannot weigh" statement; unsupported descriptors and motives removed; Then panel limited to Britannica/NPS statements. Counts remain tabulated by source, none chosen; disputed points already tagged `Uncertain`/`Disputed` |
| (f) Navigation accuracy | "Believable figure" gloss on the 10-degree dead-reckoning error was our inference; an editor's note claimed the problem "had no good answer" | Both removed or limited to what RMG says. Accuracy figures remain only as single-trial RMG figures with the caveat box; no accuracy stated for Polaris or the compass |

### Statements I could not verify to this standard (still in the articles, labelled)
* `fire-making-across-time`: the distance figures and "larger is safer" (our reasoning, tagged); the verdict ratings for flint/steel, friction and phosphorus matches (our reasoning, no agency rates them); that Walker's 1826 date is right (three sources agree; first-sale date disputed).
* `navigation-before-gps`: that no official or museum source exists for sun/shadow methods (a statement about our search, which ended when Firecrawl credits ran out); the "dead reckoning" definition (editor's note).
* `pioneer-supply-chains-failed`: all Britannica-only figures (125 miles longer; five days vs two; relief-party dates; 2010 excavation), McCurdy beyond the abstract, the Paiute disagreement, and the "four-part chain" framing (editor's note).

### Commands run from the repo root (after the fixes)
* `python -I preparedness/tools/validate.py` -> `0 error(s), 0 warning(s)`
* `python -I preparedness/tools/build.py` -> completed, exit 0 (outputs are git-ignored now)
* `python -I -m unittest discover -s preparedness/tests -v` -> `Ran 36 tests ... OK` (no failures, no errors, no skips reported)

## Follow-up pass (2026-11-01): primary sources attempted

Firecrawl credits were nearly exhausted, so each attempt was kept small. Still `publish: draft`; #31 still `pending`; all 30 sources `human_link_check: false`.

| Item | Result |
|---|---|
| Breen diary | **Added** `hist-field-oac-breen-diary` (Bancroft Library finding aid via OAC), read in full as prose. The diary's own entries and transcription were NOT read. Finding aid adds a useful caveat (early printed versions "considered to be corrupt") and does not say the diary is "the only contemporary record" (that claim stays attributed to Britannica). Breen's first name is now sourced |
| Hastings's 1845 guide | **Added** `hist-field-ia-hastings-guide` (Internet Archive OCR). Full text fetched, but only the passages around printed pp. ~137-139 and the Bear River valley were read. States about 2,100 miles / about 120 days "exclusive of delays" and Fort Hall as the supply point. The cutoff passage OCR is too garbled to characterize, so the article still rests on the Utah essay for Hastings's intent. Article adds one of our own arithmetic notes, labelled as ours |
| Virginia Reed's letter | Not found in an archive or government record; still reported only as Britannica quotes it (four words) |
| Marcy chapters | Full-text file returned 404; page-by-page reading is too costly. Read both contents pages (images 17-18): seven chapters, none described as covering finding direction by sun, stars or compass. The nav article states this as a fact about the contents list, not the book. Chapters still unread |
| NFPA 1 | Not attempted: the code is licensed text. Statements remain "NFPA's summary of the code" |
| `reference` source kind | Needs a `tools/validate.py` change, which I do not make. Britannica stays `scholarship` and NPS interpretive pages `museum` |

Verification run: see the commit message / final report for the exact results of the three commands.
