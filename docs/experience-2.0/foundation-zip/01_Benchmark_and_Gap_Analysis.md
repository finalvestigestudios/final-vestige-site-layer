# Benchmark and Site Assessment

**Method note:** Source-driven review of Blue Corridors' public website HTML, Ode's full published case study and implementation article, official Webby result, connected WordPress site metadata/content, and exact-source PR #49. **No authenticated browser crawl of Blue Corridors' rendered pages, no Lighthouse run, and no full side-by-side production screenshot review occurred in this sprint.** Any claims about measured performance or mobile quality are targets, not independently observed facts.

## Why Blue Corridors is the right comparator

The project received the 2026 Webby for Websites & Mobile Sites / Best Data Visualization. The Webby criterion is its ability to represent complex datasets innovatively, appealingly and comprehensibly. It is not evidence that every page meets every possible performance or accessibility threshold.

Ode reports integrating large multi-institutional tracking sets into differentiated lines (tracks), polygons (corridors), and base rasters (ranges), with consistent colors per species, readable layer controls, downloadable/shareable views, source attribution, and scalable data ingestion. Video footage first establishes emotional connection; the tool then makes invisible patterns visible. See primary sources in README.

## Transferable principles versus things to reject

| Principle | Blue Corridors example | Final Vestige translation | Do NOT copy |
|---|---|---|---|
| One hero idea | Large whale footage + memorable headline | One compelling historical artifact and what it reveals | Whale scenes / borrowed imagery |
| Meaningful layers | Routes, corridors, ranges, threats | Document, claim, date, place, actor, relationship, uncertainty | A globe when content lacks locations |
| Active exploration | Map controls, time, toggles | Read narrative / inspect evidence / follow sources / compare records | Overwhelming default controls |
| Transparent sourcing | Researcher credits and citations | Source cards, original URLs, evidence quality, reconstruction labels | Unattributed AI syntheses |
| Shared visual grammar | Palette & species-specific layers | Gold indicates verified annotation; neutrals for records; clear styles for uncertainty | Copying the blue/bright map UI |
| Story to tool | Homepage → map → solutions | Hero → flagship case → primary records → related inquiry → subscribe | Unrelated microinteractions |
| Extendable datasets | Many years of structured data | WordPress-backed source and location relationships progressively added | Speculative auto-generated geocodes |

## Final Vestige's actual architectural/experience position

**Strengths already present:** Black/gold brand character; clear headline 'Find what others miss'; genuine artifacts in the PR #49 hero (Franklin Victory Point note, NYPL BRT map, navy Forrestal photo, FV evidence-boundary illustration); real Apollo 1 stages; NYPL source-based library loupe; six directions into the site; free Focus Fieldbook and Dispatch mechanism; an explicit release-integrity and QD process. Existing text emphasizes checking sources rather than accepting an unsupported claim.

**Structural gaps we can address:**

1. **A sequence of sections is not yet a single authored journey.** The hero, Worlds, Library, and comparison can feel like independent demonstrations. Define a narrative arc: claim → evidence → discrepancy → interpretation → next inquiry.
2. **Evidence remains largely page-specific.** The 1903 map, Apollo 1 records and other evidence need a common schema and reusable inspector; avoid rebuilding one-off JS for each article.
3. **No verified, consistent geographic dataset yet.** An Atlas is a future feature, not a first-launch promise. Create a validation queue and start with a small curated set before publishing geographic claims.
4. **Theme tokens and section CSS are not unified.** Site presets currently have generic grayscale + Inter, while PR #49 uses custom exact colors and Fraunces. A namespaced design system could prevent drift while preserving WordPress compatibility.
5. **The current PR is still a held release candidate.** Experience 2.0 cannot inherit claims that unmerged code has already shipped or that tests pass in production.
6. **Touch, keyboard, and reduced-motion behaviors need explicit interaction contracts.** Every animation must disclose how it degrades, not just its ideal desktop display.
7. **Conversion needs a coherent role.** Preserve the genuine Focus and Dispatch pathways, but position them at the point of demonstrated value; do not put ads over primary-source evidence.

## Editorial interaction quality test

Every proposed interactive feature must answer four questions: (1) What factual relationship does it reveal? (2) Which source supports it? (3) How do you reach the same understanding without the interaction? (4) How do we prove it operates correctly on keyboard, mobile, reduced motion and no-JS?

If a feature has no satisfactory answer, it is decoration, not a priority.

## Known unknowns / follow-up checks

- Actual Blue Corridors WebGL implementation, full DOM/asset payload, real screen-reader usability and field Core Web Vitals **not independently measured**. Do not attribute specific proprietary technologies to them beyond Ode's disclosed description of Mapbox proof-of-concept tests.
- Sitewide Final Vestige production screenshots and Lighthouse baseline **not captured**. Capture before selecting designs or asserting visual defects.
- Image rights for each visual treatment must be reviewed individually; existing publication is not proof every source image can be repurposed without constraints.
- Exact homepage layout after possible future PR #49 merge is unknown; confirm branch/head before any work.
