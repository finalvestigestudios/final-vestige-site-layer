# Experience 2.0 — WordPress integration and release plan

**Status:** planning plus *locally tested* staging-only candidate; not deployed or merged. Reviewed release candidate and current live WordPress must remain distinct until a founder-approved QD change request.

## Present components and their runtime contracts

| Experience | Canonical data | HTML without JavaScript | Enhanced behavior | Proposed placement |
|---|---|---|---|---|
| Evidence Unfolds | published Apollo 1 investigation, post 434; NASA links | Six visible chapters, source photos/captions and links, full narrative | Sticky desktop evidence viewer, focus-safe source dialog, active chapter marker | Editorial investigation microsite, linked from published story |
| Research Desk / Source Ledger | `flagship-apollo1/source_manifest.json` | Six source records, real links, native `details` | Search, live count and zero-results message | Secondary source view for selected investigation; staging shortcode proof included |
| Evidence Atlas | six published WordPress posts, `atlas_seed_catalog.json` | All six linked article cards | Search and theme filters | Discovery hub **without** a geographic map until locations verified |

### Source of truth

WordPress remains canonical for published prose and live permalinks; current JSON data is a reviewed snapshot from a real published article. A production version must either source the published content through governed server code or version exact derived excerpts with a change-detection/review path. Do not auto-publish unreviewed refreshed summaries.

### Site Layer compatibility

The existing Site Layer plugin in PR #49 is responsible for the homepage's own optional animations and governs a byte-identical deployment bridge. **Do not add Experience 2.0 assets to PR #49.** The research prototypes and shortcode adapter are deliberately separate; they must not bypass that deployment contract.

### Staging plugin proof of integration

`source-ledger/wp-staging-plugin/` is an isolated candidate shortcode plugin for WordPress.com Atomic. Its shortcode `[fv_ex2_research_desk]` reads generated static HTML from a bundled file, and enqueues a small CSS/JS pair only when the direct current post content contains the shortcode. This is not yet installed and cannot be called production-ready without WordPress-staging tests.

The provided `source-ledger/wordpress-block.html` is an alternate Gutenberg Custom HTML block source. That block does not load styling or JS by itself and is **not** a full installation method. The shortcode adapter and the Gutenberg alternative are two deployment ideas—not instructions to combine them into production without review.

### Failure handling

- No JavaScript: links and native `<details>` are accessible, search absent.
- No plugin/shortcode: WordPress original posts stay unchanged; the research desk feature is absent.
- Missing trusted component template: shortcode returns a link to the original article.
- JavaScript initialization error: source ledger records never require JS and should remain readable.
- Missing media: existing exhibit provides source links and labeled fallback in an online-asset-blocked capture environment.
- Missing coordinate/provenance: Atlas card stays searchable, **no map pin is plotted**.

### Security boundaries

All source URLs for the Research Desk renderer must use HTTPS and approved source hostnames; HTML attributes and text are escaped before output. JavaScript filters existing DOM text only—no `innerHTML`, `fetch`, storage or remote third-party script. WP shortcode does not interpolate visitor-supplied attributes into the trusted template. A separate WordPress integration security review remains open. Do not represent this sandbox as a complete security assessment.

## Proposed performance budgets (pre-release targets, not current metrics)

- Initial nonmedia CSS+JS for the Source Ledger **under 20 KB uncompressed** (the current prototype is measured below 15 KB excluding HTML).
- No external script or CSS dependencies for source ledger/Atlas prototypes. Fonts use locally installed/fallback fonts in the proof.
- At most one normal image at eager load for a content experience; all other photos use lazy loading and responsive `srcset`/`sizes` where licensed and available.
- Image widths/heights specified; image priority and layout shifts to be verified against loaded assets.
- Page-level targets at 75th percentile: LCP ≤2.5s, INP ≤200ms, CLS ≤0.1 on supported devices. These remain **unmeasured**.

## Required independent quality gates before any website release

1. Founder chooses and approves one art direction; no presumption of approval from prototype progress.
2. Content editor verifies every NASA image reuse permission, original ID, caption, provenance, and six summary claims; provide a source crosswalk.
3. Integrate through separate staging site with WordPress theme/plugin stack, caching, Jetpack subscriptions, SEO schema and content preservation.
4. Independent browser QA: mobile Safari/Chrome, desktop Chromium/Firefox, 200–400% zoom, real keyboard Tab/Shift+Tab/Enter/Escape, VoiceOver/NVDA, reduced motion, high contrast and no-JS.
5. Axe-core and manual WCAG 2.2 AA review; not just DOM simulation.
6. Independent QD reviews exact code/artifact; hosted CI green, founder authorization, correct merge/release markers and rollback proof.
7. Post-deployment checks in production against actual domain and fetched NASA media. Returnable rollback and observable broken-link checks.

## Important caveat about the current prototypes

The flagship's current sticky evidence viewer is not proven with real screen readers. The offline screenshot environment cannot reach official NASA image CDN, so photographs' visual treatment and delivery/rights need validation elsewhere. The original published article must not be replaced by this truncated six-chapter exhibit without explicit editorial decision.
