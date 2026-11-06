# Apollo Experience 2.0 — R174 Research Desk NASA media custody

**Draft / staging hold. No WordPress writes, merges, installation, image redistribution, paid offer, analytics, new creator assignment or production change.** This is an additive follow-up to R173, not a replacement for PR #158 or homepage PR #49.

## Specific new research finding (NASA pages inspected November 6, 2026)

The original Research Desk record 01 prints **S67-19766** but its linked NASA image-detail page, [Apollo 1 Crew Honored](https://www.nasa.gov/image-detail/apollo-1-crew-honored/), identifies the astronauts and a January 1967 training photograph **without displaying that catalog number**. Therefore the linked NASA page does not independently prove that ID/photo pairing. It may be correct, but is **not verified from that link**. The code adds a visible qualification; it does not silently relink or erase the original historical content.

The remaining five linked NASA pages explicitly identify the displayed catalog numbers. Importantly, **S67-21294** is a [January 28, 1967 photograph of the fire-damaged command module](https://www.nasa.gov/image-detail/amf-s67-21294/), not simply a generic background photograph, and still cannot alone identify the precise ignition source. Records 02/03 are January 3, 1967 processing / October 18, 1966 training; records 04/06 are January 24, 2017 tribute/exhibit photography. Do not associate any of these images with arbitrary timestamps within the fire.

The [1967 Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) says no single ignition source was conclusively identified. Technical findings come from written evidence, not inferred from a photograph.

[NASA image-use guidance](https://gpm.nasa.gov/image-use-policy) warns about nonendorsement, astronaut likeness/publicity, third-party rights and protected insignia. **No image is cleared for FV paid-product promotion by this work.** Historical image attribution is not a publicity release.

## Implementation

- **pinned source**: R173 PR #1303 exact Git blob `bc5e9e2618ed5bbde86b9c40c10045fb72fc66c2`; R173 original template derives from PR #158's `403d128c57b9bc82dac7c619651689070edef86c`.
- `nasa_media_custody.json`: six-source, record-specific chronology, classification, uncertainty and usage HOLD.
- `nasa_media_custody.py`: static additive overlay inserting one legible provenance aside in each original evidence record, enforcing exact SHA-1 blob, source ID, record order, original NASA photo URL, R173 source-role markup, original href order and byte-perfect original roundtrip. Drift is a hard failure. No new links, scripts, forms or data collection.
- `nasa_media_custody.css`: optional scoping, no-JS-readable, reduced-motion and forced-colors styles.
- `test_nasa_media_custody.py`: expected to run on an ordinary exact-head repo checkout against the **actual** committed R173 source, including mutation controls. CI not yet independently executed in GitHub.

Run after checkout from repository root:

```bash
python -m unittest discover -s experience2/apollo-r174 -p 'test_*.py' -v
python experience2/apollo-r174/nasa_media_custody.py \
  experience2/apollo-r173/research-desk-source-custody.html \
  /tmp/apollo-r174-staging-candidate.html
```

**Local QA evidence:** 14/14 local Python tests across R173 predecessors and the new R174 fixture suite passed. 77/77 real Chromium assertions across eight browser contexts (six widths 320/360/390/768/1440/1920, JS-off, touch/high contrast) on a **controlled R173-source-derived fixture only**. Six laboratory screenshots generated; full-page fixture screenshots are not actual WordPress. Controlled fixture measurements are not production Core Web Vitals. Screenshot test must be reproduced on exact-head WordPress staging before release. axe-core not installed; real axe, real deployed page, NASA CDN, voiceover, production LCP/CLS, official checkout and settlement were NOT tested.

## Conversion-first and ownership gates

**Audience:** history/engineering educators attracted by a Grok-owned Apollo investigation video. **One relevant first action:** Read original investigation. Do not place a sales or affiliate link in Apollo source panels. Proposed later paid educator evidence dossier must first pass product ownership/rights/checkout validation, actual educator demand and founder approval; it is not an available offer. Avoid claiming an existing FV Apollo SKU.

**Measurement:** actual Grok asset_id / UTM → qualified human landing sessions → investigation click → independently verified product-eligible lead (if any) → independently confirmed paid order → fees/refunds → realized net revenue per 1,000 qualified humans. All paid outcomes and denominator are UNKNOWN.

**Owner:** Apollo lane builds and verifies staging source; Claude owns core WordPress and analytics; Praxxis independently reviews Grok; Grok owns creator scripting/posting; founder owns production and spending approvals. Cross-reference Issue #150, commercial #820 and charter #818, TASK-008. Frozen PR #49 and existing PR #158 stay untouched.

**Release gate:** HOLD until independently checked-out exact source, genuine WP/Assembler rendering, official-source media URL delivery, axe-core/assistive tech, 320–1920 screenshots, CI exact-head, performance (LCP/CLS), source/photo ID #01 resolution, and rights/commerce approvals.
