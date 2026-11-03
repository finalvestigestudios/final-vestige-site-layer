# Apollo 1: media and source review (Sprint 05)

Machine-verified on 2026-10-30. A human rights and editorial review is still required. Nothing here is a clearance.

## Reuse basis

NASA Media Usage Guidelines (https://www.nasa.gov/nasa-brand-center/images-and-media/), read 2026-10-30:

- NASA content is generally not subject to copyright in the United States and may be used for educational or informational purposes, including web pages. NASA should be acknowledged as the source, and use must not imply endorsement.
- Clearances may be necessary for images that include NASA logos or NASA employees when used as cover art or in promotional content.
- Names and likenesses of deceased astronauts may be controlled by their estates for commercial use.

**Restriction recorded in the data:** editorial use only. Do not use these images in promotional, product or merchandise contexts (for example Focus Fieldbook marketing).

## Images

| Chapter | NASA ID | Date | Role | Shows the event? | Verified |
|---|---|---|---|---|---|
| 1 | S67-19766 | Jan 1967 | Context (crew near LC-34) | No | NASA record page confirms caption and credit. Identifier appears in the page markup but is **not found by the NASA Image API `nasa_id` search**; the file is served from the Final Vestige media library. **Needs human confirmation.** |
| 2 | S67-15717 | 3 Jan 1967 | Context (Spacecraft 012 in processing) | No | Image API: JSC, 1967-01-03 |
| 3 | S66-58038 | 18 Oct 1966 | Context (crew entering altitude chamber) | No | Image API: JSC, 1966-10-18 |
| 4 | KSC-20170124-PH_KLS01_0129 | 24 Jan 2017 | Museum exhibit | No | Image API: "three-part hatch that was in place on the Apollo 1 spacecraft", KSC, NASA/Kim Shiflett. Viewed. |
| 5 | S67-21294 | 28 Jan 1967 | Post-fire photograph (no people) | Yes | Image API: JSC, 1967-01-28 |
| 6 | KSC-20170124-PH_KLS01_0090 | 24 Jan 2017 | Museum exhibit | No | Image API: "redesigned hatch", KSC, NASA/Kim Shiflett. Viewed. |

**Rejected:** KSC-20170124-PH_KLS01_0164. NASA describes it as "an Apollo spacecraft mockup"; the photograph shows a white mockup capsule. The prototype captioned it as the original hatch.

`tools/verify_media.py` re-checks, against the live hosts: every image URL returns 200 with an image type and decoded dimensions equal to those declared; each record page resolves; the NASA Image API knows each NASA-hosted asset. 33 URLs passed on 2026-10-30. The record page for 0129 is the NASA Image Library detail page, because no nasa.gov `image-detail` page was found for that asset.

## Claim crosswalk against the Board report

Source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ (text read directly 2026-10-30).

| Claim in the experience | Status | Evidence |
|---|---|---|
| 16.7 psia, 100 percent oxygen test atmosphere | verified | Board: "The test was conducted with a 16.7 pounds per square inch absolute, 100-percent oxygen atmosphere." Determination: test conditions extremely hazardous. |
| First verbal fire report at 23:31:04.7 GMT | verified | Board chronology. |
| First pressure rise about 6 s after the report | verified | Board, Cabin Pressure Rise. The NASA web text prints "23:21:11 GMT", an apparent typo for 23:31:11; the interval is unaffected. Not silently corrected. |
| Pressure exceeded transducer range by 23:31:16 | verified | Board: 17 psia (cabin), 21 psia (battery compartment). |
| Rupture about 23:31:19 at at least 29 psia | verified | Board gives "about 23:31:19" and elsewhere 23:31:19.4. |
| Inner hatch could not be opened before rupture | verified | Board Finding 4. |
| Specific ignition source not found | verified | Board: "Although unsuccessful in this search...". |
| Electrical arc was the most likely initiator | **partial** | Arcing is discussed as a possible cause of transients; electrostatic discharge, spontaneous combustion, mechanical and impact heat are "eliminated as reasonable possibilities". The exact "most probable arc" sentence was not located in the extracted text. **Confirm wording.** |
| Block I hatch opened inward | **article-only** | Not found in the Board landing-page text. Source from NASA history or exhibit text. |
| NASA redesigned the hatch to open outward | partial | Exhibit text in KSC-...0090 (Block II designed to open in 5 s); direction not found in Board text. |
| Plugs-out test; unfueled Saturn IB | article-only | Not re-checked. |
| 102 ignition tests of boilerplate 1224 | article-only | Not re-checked. |

**Editorial note, not changed:** the chapter title says "Fourteen seconds"; the Board says the first stage ended "approximately 15 seconds after the verbal report" (its own stamps give 14.7 s). Wording change needs editorial approval.

**Wording changed with disclosure:** record 5's limit read "The prototype deliberately keeps this uncertainty visible"; it now reads "This experience deliberately keeps the uncertainty visible."
