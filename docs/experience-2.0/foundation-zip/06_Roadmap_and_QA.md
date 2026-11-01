# Roadmap, Build Packages, and Release Gates

**Rule:** PR #49 must finish its own release/CI/QD work without scope contamination. Experience 2.0 starts on a separate planning branch or issue; visual selection first; production is untouched until approved.

## Work package 0 — baseline + design evidence (research lane)

- Record **current production** (WordPress page ID 6) and **unmerged candidate** (PR #49) as separate snapshots, at 360/390/768/1024/1440/1920 pixels.
- Capture both light/dark system settings as appropriate, keyboard focus sequences, reduced motion, 200%/400% zoom, image loading/failures, and actual font behavior. Never judge appearance from HTML alone.
- Run mobile/desktop Lighthouse and WebPageTest (if available) for baseline, save reports with timestamps/environment. Measure field Core Web Vitals if real user data exists.
- Compile an authorized media register: asset URL, provenance, license and correct editorial context.
- Present **exactly three** annotated visual directions and record founder's selected design.

**Gate:** selected visual target, source-safe asset kit, baseline evidence, verified content scope.

## Work package 1 — design system + section chassis

- Build a namespaced Experience 2.0 CSS token layer and lint/test it against existing WordPress Assembler and Site Layer styles.
- Establish typography, spacing and caption conventions; real responsive heading behavior.
- Implement a testable component shell (ExhibitHero, EvidencePlate, SourceDrawer, StoryChapter) in **an isolated branch or preview**, never directly in production.
- Add graceful no-JS and no-motion baseline first, then enhancement. Instrument user action errors without collecting sensitive visitor content.

**Gate:** visual screenshot QA for target breakpoints, keyboard and semantic tests, component contracts, no broken old blocks.

## Work package 2 — first flagship: Evidence Unfolds

- Choose a single approved published investigation, provisionally the Apollo 1 article already used by PR #49.
- Build a short, genuinely compelling 5–7-station evidence chronology using records that are explicitly sourced and have rights clearance.
- Implement EvidencePlate and SourceDrawer plus an indexed narrative with deep links.
- Verify quote/date/asset consistency against original article; do not introduce new scientific/historical claims in UI without separate editorial sourcing.
- Compare source-derived page with actual rendered page, including no-JS text parity.

**Gate:** independent editorial source review + accessibility review + desktop/mobile visual review + genuine user task success.

## Work package 3 — homepage choreography integration

- Adapt the selected Experience 2.0 art direction to the existing site and PR #49 assets, without deleting verified work simply because it's already implemented.
- Preserve: latest content queries, World pathways, Public Record, free Focus Fieldbook, working Jetpack Dispatch subscription, editorial policy links, all existing canonical URLs.
- Source-led animation: small number of intentional transitions between sections; build with visibility and reduced-motion contracts.
- Ensure mobile landing is fast and primary CTAs visible without waiting for animation.

**Gate:** complete viewport screenshots, navigation & conversion regression, measured performance, QD, exact artifact identity.

## Work package 4 — verified Atlas seed (separate lane)

- Inventory existing posts for geolocatable subjects. Validate precision, date, source and rights individually.
- Produce 6–12 fully reviewed entries (not necessarily 6–12 distinct map pins; some may remain region-level or unplottable).
- Ship accessible text catalogue first; decide map renderer only after performance/licensing evaluation.
- Add filters/time/relationships only where evidence supports them; beware an overly sparse globe.

**Gate:** 100% of visible map points have verified coordinate source and uncertainty/precision metadata; nonvisual result parity.

## Performance targets (not measured current values)

- Google's 'good' 75th percentile field CWV thresholds: **LCP ≤2.5s, INP ≤200ms, CLS ≤0.1**, assessed independently for mobile/desktop. Source: https://web.dev/articles/defining-core-web-vitals-thresholds.
- Suggested additional internal budgets (proposal): initial critical-path JS under ~150KB gzip where feasible; first hero image optimized/responsive; no more than one major animated experience eagerly initialized on first view; all other interactions lazily activated.
- No render-blocking third-party tracker required to read the page. Avoid automatic video playback downloading full resolution on cellular; honor Save-Data and prefers-reduced-motion.
- Do not label a build 'fast' without measured data; aim for 90+ mobile Lighthouse performance but do not treat synthetic score as the only acceptance proof.

## WCAG and resilience targets

- WCAG 2.2 AA as minimum target; visible focus, alt/transcript, input modality parity, no keyboard traps, 200%/400% zoom, appropriate semantics and screen reader output.
- Test Chrome, Firefox, Safari/WebKit as available; real Chromium alone does not prove iOS behavior.
- Test mouse, touch, keyboard, voiceover/NVDA where practical; no-JS, unsupported browser features, slow images, partial init failure, offline media, slow connection, reduced motion, contrast adjustments, long localized text.
- For sliders and map controls, asserted ARIA min/max must match actual reachable values. Touch-action disabled only while an actually working control owns the gesture; fail-open back to browser scroll otherwise.
- Simulated DOM unit tests + real browser tests; **SKIP is never PASS**.

## Release and governance

1. Visual design selection by founder.
2. Implementation PR with exact files, scope, source register and deterministic artifact.
3. Independent QD at exact head; only QD may issue the marker, never the implementing agent.
4. Hosted CI green on exact head; diagnose failures with logs/annotations, not speculative billing explanations.
5. Authorized governed merge/deploy into correct WP destination; manual Page 6 content changes only if covered by a snapshot, reversible diff and explicit approval.
6. Post-deploy byte/hash verification plus production screenshots, interaction tests and conversion smoke test.
7. Rollback plan to previous content + plugin. No release considered complete until independently verified.

## Metrics to measure only after launch

- Users who start and finish a flagship investigation; sources opened; mobile completion; return-to-archive rate.
- Source quality: percentage with original archive link, attribution, evidence type and verified location (where plotted).
- Acquisition quality: engaged visitors from social content and movement to relevant investigation / free resource / Dispatch.
- Perf and reliability by device, not purely engagement vanity metrics.

Metrics are proposed instrumentation goals, not current measured results.
