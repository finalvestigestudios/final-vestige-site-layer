# Apollo Evidence Atlas R223 — traceable evidence plates (staging only)

Isolated child of [R222 draft PR #1636](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1636), within [Apollo #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), revenue governance [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). **Do not merge or deploy.** Homepage frozen PR #49 and independent Research Desk PR #158 are out of scope.

## Change and rights

The R222 native SourceDrawer now renders four **EvidencePlate** records using accessible definition lists: source type, human-readable date with machine-readable `time`, what the source **can** establish, and what it **cannot**. Each record has two meaningful paths: its exact NASA record and a native in-page link to the relevant existing finding/gallery entry. An immutable machine-readable `source-context-plates.json` crosswalk binds each source ID, date, limitation, NASA URL, and internal anchor. The PHP shortcode adapter pins its SHA-256 alongside HTML/CSS and earlier custody records; tampering falls back to the **free** original investigation. No JavaScript, imagery, maps, attribution scripts, paid offer, form, external dependency, or new CTA.

NASA verification checked **2026-11-08**: [Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) (probable electrical arc; no conclusive single ignition source); official image catalog [S66-58038](https://www.nasa.gov/image-detail/amf-s66-58038/) (18 Oct 1966), [S67-15717](https://www.nasa.gov/image-detail/amf-s67-15717/) (3 Jan 1967), [S67-21294](https://www.nasa.gov/image-detail/amf-s67-21294/) (28 Jan 1967). The exact source record dates are distinct from the Jan 27 event. [NASA advertising rules](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) forbid implying endorsement and do not confer blanket media or astronaut likeness permissions. No media embedded.

## Reproduce on pinned parent R222 staging artifact

Unzip the R222 evidence artifact and supply its exact `generated-r222-dist`. **The builder rejects a mismatched source manifest, HTML, CSS, or custody record.** Run without WordPress writes or external network:

```sh
python experience2/apollo-r223/build_r223.py --parent /path/to/generated-r222-dist --target /tmp/apollo-r223/dist
python experience2/apollo-r223/qa/evidence_plate_browser_gate.py --parent /path/to/generated-r222-dist --builder experience2/apollo-r223/build_r223.py --out /tmp/apollo-r223/qa
```

Python Playwright, PHP and /usr/bin/chromium are required. **Exact R223 output manifest SHA-256:** `60e3bcd4201715a769d1e4d819dfc4d09498eeace5e8193a535fae7350ef840e`.

Executed the **byte-identical GitHub test source** twice against PHP-rendered staging fixtures: 14/14 Chromium contexts per run at widths 320–1920, JS enabled/disabled, touch/keyboard native disclosure, in-page source-to-context navigation, 44px single free CTA, printable records, forced colors/reduced motion. 14/14 screenshot hashes matched across runs. Corrupted ledger fell back to the free original investigation; duplicate IDs, inaccessible ARIA references, broken anchors, invented geo pins, active content and horizontal overflow checked. No axe-core executed (package inaccessible offline); local HTTP navigation was blocked by browser administrator policy. These are **fixture** results, not actual WordPress acceptance or field Core Web Vitals.

## Conversion gate — next action

| Offer → step | Blocker | Change / experiment | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Educator dossier hypothesis → paid order | No verified rights-cleared sellable SKU | Validate permissions, actual checkout and delivery before promoting | **HOLD** | Commerce / Claude / Founder |
| Grok long form → Atlas | Apollo published asset ID and UTM landing unverified | Reconcile TASK-008; do not change Grok's queue | **UNVERIFIED** | Grok / Praxxis |
| Atlas → original free investigation | Source chronology/meaning may be misunderstood | Four dated EvidencePlates with native source/context paths; one existing free CTA | **LOCAL FIXTURE PASS** | Apollo |
| Confirmed orders → net revenue | No merchant-confirmed orders/refunds/fees or qualified human sessions | Reconcile privacy-safe 7/30-day cohorts; net per 1,000 qualified sessions | **NOT COMPUTABLE** | Commerce / Analytics |

**Release HOLD:** inherited R198 source-ancestry discrepancy, genuine axe-core, NVDA/VoiceOver, browser zoom, installed WordPress/Assembler, external-link click-through, hosted exact-head CI, independent QA and founder approval. Do not infer live creator posts, conversions or revenue. No social, email, affiliate, CMS or paid-service operations.
