# Experience 2.0 — Sprint 02: Working prototype evidence

**Status:** Two front-end research prototypes created and verified locally; NO WordPress or production changes, NO edits to PR #49. Source outputs are in the conversation ZIP `Final_Vestige_Experience_2_Foundation.zip` (updated with Sprint 02 work). Request or attach that archive for code/assets; the full prototypes are **not uploaded to this planning branch**.

## Flagship prototype: Evidence Unfolds — Apollo 1

- Source: published WordPress post 434, [The Hatch Opened Inward](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/), linked NASA [Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/), six NASA image source records.
- Six complete narrative chapters rendered as semantic static HTML with source links. Desktop: progressively enhanced sticky documentary viewer + active-chapter tracking. Mobile: normal document + source figures, never scroll locked.
- Native HTML dialog shows exact archive identity, what the record supports, the evidence boundary and original source links. Escape and return focus tested.
- Accurate event-marker chart for first fire transmission/pressure rise/sensor range/rupture, expressly **not an interpolated pressure trace**. Unproven spark is explicitly identified as unproven.
- Browser QA: 360/390/768/1024/1440/1920, no horizontal overflow, six chapters, source dialog, keyboard Escape/focus restoration and anchors, JavaScript-disabled fallback, and injected JS error fallback all passed in sandbox Chromium.
- External NASA/WordPress image hosts blocked by capture environment; included offline-image fallback and official source links. **Production image delivery, rights and visual QA on loaded media remain OPEN.**
- Outputs: `flagship-apollo1/index.html`, `build_prototype.py`, `source_manifest.json`, `verify_flagship.py`, `QA_RESULTS.json`, screenshot sets, `README.md` inside the associated ZIP.

## Atlas prototype: fact-first catalog, no speculative maps

- Confirmed six existing posts with WP IDs/URLs: Apollo 1 (434), Malbone Street (621), West Loch (370), Halifax Explosion (269), Petra (37), Franklin Expedition (433).
- Six candidate place labels remain `location_review=unverified` with **null geometry**. A place mention is not a verified event coordinate. No invented relationship lines.
- `atlas-preview.html` is an original working category filter and text search, with native focusable article links, live result count, and **all six stories visible without JS**. Inactive search/filter controls remain hidden without JS.
- Browser QA: 360/390/768/1440/1920 no overflow, search, filters and static fallback PASS.
- Outputs: `atlas_seed_catalog.json`, `ATLAS_SOURCE_AUDIT.md`, `atlas-preview.html`, `verify_atlas_preview.py`, `ATLAS_QA_RESULTS.json`, screenshots in ZIP.

## Decisions and next steps

1. Black Dossier visual direction is working as a design study, but **not yet founder approved**. Continue with source-driven design options, not mass deployment.
2. Before integration: verify NASA image delivery and rights; confirm editorial wording against Board; run axe and real NVDA/VoiceOver, iOS touch and full CWV measurement.
3. Define WordPress adapters/content sourcing rather than pasting an independent static page into production.
4. Founder selection → independent QD of exact new branch/artifact → hosted CI green → governed deployment; no shortcut.
5. Add verified source evidence for each Atlas location before adding any map marker.

**Technical caution:** These files are functional prototypes, not evidence of award-winning quality, compliance certification or live deployment.
