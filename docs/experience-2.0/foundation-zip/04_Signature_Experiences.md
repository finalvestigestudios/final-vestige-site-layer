# Signature Experiences — Product and Interaction Specifications

## First flagship — THE EVIDENCE UNFOLDS (historical chronology)

**Pilot candidate:** Existing published investigation *The Hatch Opened Inward* (Apollo 1): https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/. PR #49 already contains a six-stage investigation walkthrough with real NASA images and footnoted quotations. Reuse the existing verified editorial content rather than inventing an entirely new story or constructing a false cause-and-effect graphic. The *actual body copy, source IDs, rights and chronology must be reviewed from the post before this pilot is implemented.*

### Visitor promise

'Watch the historical record come together. At each step, see what is documented, what it supports, and what cannot responsibly be concluded.'

### Proposed journey

0. **The arresting record:** One authentic photograph/document, short compelling headline and visible 'Read the story' / 'Inspect evidence' paths.
1. **Establish the record:** Event/date/context from the actual article and linked primary records.
2. **See the first source:** Full asset with descriptive transcript and catalog metadata, clearly distinguished from analysis.
3. **Reveal a critical discrepancy or question:** Only if supported by the source; show evidence basis and counterinterpretation where relevant.
4. **Build the chronology:** Step-by-step vertical rail showing what was established when. Preserve the difference between event date and document creation date.
5. **Inspect the source trail:** Expand provenance, links and notes; make missing or uncertain records explicit.
6. **Return to the interpretation:** A considered editorial conclusion and what remains unresolved.
7. **Continue the inquiry:** One genuinely related investigation, plus optional Dispatch or free resource CTA after value delivered.

### Core behavior

- On desktop, content scrolls naturally through a vertical narrative; the corresponding evidence stage advances only if the user chooses an interactive mode. No mandatory scroll lock.
- Each stage has a hash anchor and next/previous controls; clicking a source opens a drawer with title, archive, link, excerpt/transcript, rights, and explanation of how it supports the claim.
- The stage's image is never motion-animated in a way that implies a false factual transformation.
- On mobile, the asset is above text with predictable sticky chapter label only if it doesn't obscure content; drawer becomes a dialog/page with correct focus management.
- With JS disabled or motion reduced, all stages render as an ordered semantic document containing the same narrative and source links.
- Color and motion never signal 'verified' without an explicit textual legend and source record.

### Minimum acceptance

- Five to seven source-grounded content stages, every factual caption sourced and editorially reviewed.
- Keyboard navigation and source drawer focus restoration verified by real browser tests.
- Media attribution verified, image rights acknowledged; no placeholder image passes production gate.
- Content is readable in full with JS disabled.
- The page has meaningful shareable URLs/anchor links and basic metadata.

## Second flagship — THE EVIDENCE ATLAS

A map of **published, geolocatable research**. Not a generic pin map, an animated empty globe, or an algorithm guessing the location of a historical text.

### Data maturity levels

- **Level 0 (now):** Inventory published stories that identify real places; collect citations and candidate locations, no map publication.
- **Level 1:** Curated 6–12 fully verified cases, with independently checked approximate/geographic place labels, appropriate precision, and at least one evidence link per case. Publish a searchable list and accessible map together.
- **Level 2:** Optional time filters, themes, and relationship lines where there is sourced evidence; no line indicating a connection solely because two events are nearby.
- **Level 3:** Scalable data layers, source/versioned geospatial catalog, geographic clustering and optional authored guided journeys. Use MapLibre/Mapbox only after a license/performance/data comparison; cheap SVG/static maps may suffice for v1.

### Evidence Atlas sample themes (candidate queue; no geocodes asserted)

- **Space & systems:** Apollo 1 (article linked above).
- **Urban disasters:** 1918 Malbone Street wreck (published 'Six Miles an Hour').
- **Naval incidents:** West Loch 1944 (existing FV media/articles; confirm exact article).
- **Industrial/disaster history:** Halifax explosion (existing FV media/articles; confirm story).
- **Ancient infrastructure:** Petra water systems (published FV post; map evidence to confirm).
- **Exploration:** Franklin Expedition (existing Victory Point Note; location precision/archival context to verify).

These are research candidates, **not pre-approved records**. Every event needs its own reference source and a location precision rule (point, region, route, unknown); cases with ambiguous locations stay in the list but not on the map.

### Map UI states

A. **Explore by place**: map with 1–2 visible layers and textual result list, search by subject/era.
B. **Inspect event**: primary record + relationship explanation, geographic certainty, chronology.
C. **Compare**: toggle a time or classification layer with correct legend and explicit uncertainty.
D. **Open sources**: archive links and original article, no paywall behind essential evidence.

### No-JS and nonvisual parity

An HTML list with the exact same places and evidence summaries, direct story links, and source citations is the canonical content. The map is progressive enhancement. Never trap focus in map canvas. Do not rely on color alone. If the map engine fails, present list and clear offline/degraded explanation.

## Universal evidence inspector — RESEARCH DESK

A shared, source-agnostic component for documents, maps and photographs. Required fields: artifact title, institution/collection, date/range, type, stable source link, rights/credit, alt text/transcription if needed, evidence relationship. Optional: download link if licensed, digitized item ID, uncertainty and version history.

Functionality:

- True source image view with zoom/pan + keyboard zoom controls and Reset.
- Optional highlights mapped to coordinates only if a curator has verified the physical correspondence; otherwise plain annotation list.
- Source drawer with explicit separation between '**What the document says**' and '**What Final Vestige concludes**'.
- Responsive detail layout, full text fallback and no unbounded data downloads.

## Homepage narrative cut (conceptual sequence, not a directive to rewrite PR #49)

1. **Entrance:** One striking historical artifact and monumental thesis 'Find what others miss.' Direct paths to 'Enter an investigation' and 'Explore the archive'.
2. **The proof:** A 1-minute interactive source-led micro-exhibit using an existing fully supported event.
3. **The wider world:** Six existing subject pathways simplified into a purposeful editorial index rather than visually equal marketing cards.
4. **The instruments:** The Research Desk and Evidence Atlas preview. Do not fake map depth before dataset is complete.
5. **The living work:** Latest investigation, current source research, credible updates from WordPress queries.
6. **The invitation:** Existing free Focus Fieldbook and Dispatch conversion, placed where they don't interrupt the evidence journey; retain its exact Jetpack subscription mechanism.
7. **Integrity footer:** Methodology, corrections, source policy, editorial disclosures, accessible legal links.

Some sections in #49 already implement these building blocks; start by compositional reuse and art direction, not blanket replacement.
