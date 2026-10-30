# Gutenberg heading-outline audit (read-only QA)

This tool inspects **saved WordPress Gutenberg page markup**; it makes no network calls, does not change content, and never asserts that a source observation is a live rendered browser defect.

## New source-level observation — October 29, 2026

Among 12 inspected, high-impact published pages, **10** began their saved content with an H1. The other **two** place a Puységur featured source card containing an H2 before the page title H1:

- `/explore/` (WordPress page **525**): featured H2 `Puységur’s Animal Magnetism Files` precedes H1 `Search and browse Final Vestige`.
- `/free-resources/` (WordPress page **77**): same featured H2 precedes H1 `The Library`.

This is a semantic heading-order **review finding**, not a demonstrated WCAG violation, visible layout failure, or SEO ranking penalty. The featured cards use `section[aria-labelledby]`, so a tag-only change could degrade labeling. Coordinate a DOM/screen-reader review with Claude before any edit. Consider placing the page H1 before the featured card in document order while preserving its visual design and accessible section name.

## Running the checker

```sh
node qa/accessibility/heading_order_audit.cjs sanitized-pages.json
node --test qa/accessibility/test_heading_order_audit.cjs
```

Input is a sanitized JSON array of published page snapshots `{id, status, url, content}` obtained read-only from `pages.get` with `context=edit`. No private identifiers or credentials are needed.

The report marks items `PASS_SOURCE_ONLY` or `REVIEW_SOURCE_ONLY` and excludes drafts. Source markup can differ from the live DOM after theme rendering or dynamic blocks; a logged-out browser and keyboard/screen-reader check remain required.

**Production safety:** no WordPress writes; no plugin, template, navigation, style, brand or subscription modifications. Do not merge or deploy this draft without QD. This does not overlap active homepage/Preparedness Archive work, Focus funnel QA #129/#141–#144, or Field Cabinet security draft #147.
