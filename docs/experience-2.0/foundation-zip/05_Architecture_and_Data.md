# Architecture & Source Data Contract

## Existing production lane — preserve it

The existing WordPress.com Atomic site uses the Assembler theme and a custom Final Vestige Site Layer plugin, deployed through a guarded GitHub Actions → verified package → WordPress Deployment Bridge sequence. PR #49 is an unmerged candidate with exact-head/hash approval rules; it must stay independent of Experience 2.0 research.

Our proposed architecture should respect the distinction:

- **WordPress content:** canonical published articles, source lists, image captions, excerpts, URL slugs, taxonomies, subscriptions, editorial policies. A no-JS reader must understand the page.
- **Progressive Site Layer:** strictly optional visual and interaction enhancements on top of semantic WordPress markup.
- **Static verified-data manifests:** versioned and editorially reviewed JSON for case narratives, artifacts, evidence relationships and location metadata. No user tracking required for v1.
- **Reusable CSS and JS:** namespaced components loaded only on pages where used, shareable across sections instead of copy/paste payload duplication.
- **Asset pipeline:** existing WP image hosting, resized sources, widths/heights, rights/credit, lazy loading below the fold. No dependence on a large paid map stack unless data/traffic prove it useful.

Do not pull in new dependencies just to achieve a visual trick. Before adding any library, produce bundle-size, cost/licensing, maintenance, offline behavior and accessibility analysis.

## Evidence graph — start with a flat verified catalog

The relationship data model supports these entities:

- **Investigation:** URL, title, summary, themes, editorial status, canonical author/review record.
- **Event:** date/range (and timezone where meaningful), precision of dating, place reference, description, cited record IDs.
- **Artifact:** source institution, archive identifier, direct original URL, type, title, date/range, reproduction/license credit, accessible text/transcription, thumbnail URL.
- **Claim:** text, support level, interpretation vs primary wording, citation anchors, last reviewed, uncertainty caveat.
- **Place:** authoritative or independently verified geographic reference; coordinate accuracy and granularity; source. Unknown coordinates remain null.
- **Relationship:** explicit named relation and its justification: `documents`, `depicts`, `occurred_at`, `mentions`, `corroborates`, `contradicts`, `interprets`, `related_editorially`. Must cite support. Never create inferred `caused_by` edges automatically.

See `record-schema.example.json`. That file deliberately includes **schema-only placeholder identifiers** and does not seed actual coordinates or sources.

## Suggested implementation split

**Phase A — Editorial front-end:** No new database. WP posts, blocks and small hand-maintained JSON manifests tracked in Git. This minimizes hosting and incident surface.

**Phase B — Authoring capability:** If catalog growth justifies it, define WordPress custom post types/taxonomy or protected fields for Artifacts / Events / Places; preserve stable old permalinks. Build read-only exports into static JSON for public interactions.

**Phase C — Geographic scale:** Only after adequate verified map coverage, add a map rendering layer. Decide between WebGL and lighter SVG/tile solutions using real mobile benchmarks. Keep list and source metadata accessible at all times.

Do not promise 'live data', personalized tracking, crowdsourced findings, or AI fact-checking as if currently implemented. Community submissions must go through an editorial approval queue.

## Required validation and invariants

- Every published claim contains at least one source anchor; primary/secondary/methodological classification clear.
- Every asset has an accessible description/transcription (where required), rights and original source link.
- Every plotted feature has geographic confidence, provenance and review date. Dataset build fails if missing.
- Every generated export has immutable version/hash and reproducible build metadata; consumers can verify its identity.
- All external links use appropriate safety attributes and no unbounded third-party request chain.
- A static HTML fallback is valid and renders the full story without any JavaScript.
- No experimental scripts load across every WP page by default: scope activation per dedicated class/shortcode/data attribute.

## Suggested directory contract for Claude to assess, not yet implement

```text
experience2/
  specs/
  fixtures/
    case-manifest.schema.json
    example-case.proposed.json
  src/
    css/
      tokens.css
      narrative.css
      components.css
    js/
      evidence-inspector.js
      chronology.js
      atlas-loader.js   # later, only after dataset verification
  tests/
    semantics/
    keyboard/
    mobile/
    source-provenance/
  docs/
    source-register.md
    design-decisions.md
```

Actual directory should be selected after reviewing existing repo boundaries and GitHub workflows; code must not be grafted into PR #49.

## MVP not-built-yet list

No WordPress pages edited. No production plugin changes. No new endpoints, geospatial APIs, or persistent databases. No new map points asserted. No actual published flagship produced. The files here are an implementation-ready planning foundation, not a feature release.
