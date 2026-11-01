# Experience 2.0 — Sprint 02: working prototypes

**Current status:** two isolated, functioning front-end study pages; no WordPress/production deployment. The founder has not yet selected a final art direction or approved a flagship for live integration.

## Completed in this sprint

1. Built **Evidence Unfolds: Apollo 1**, a six-chapter source-backed cinematic investigation page using Final Vestige post 434 and six linked official NASA photograph records. The site uses a desktop sticky research plate, native source dialog, original annotated event markers, accessible anchors, intact no-JS narrative, and error fallback. The entire experience runs without third-party JavaScript or external data API calls.
2. Created `flagship-apollo1/source_manifest.json` and a deterministic page generator. The 1967 fire source-uncertainty distinctions are explicitly preserved.
3. Tested the actual local HTML in Chromium at 360/390/768/1024/1440/1920; source dialog, Escape and focus return; no-JS content; and deliberate JS exception. No horizontal overflow at tested widths.
4. Created **Evidence Atlas source-review queue** of 6 published, WordPress-verified investigation URLs/IDs with place candidates, *no* invented coordinates or relationship edges. Built `atlas-preview.html`: a working filter/search with six linked cards, accessible live-result count, and readable/no-JS list. Browser-tested at 360/390/768/1440/1920.
5. Recorded that the screenshot environment cannot load external NASA/WordPress media: test images use an explicitly labeled source-unavailable fallback, so screenshots do not certify final archival media presentation.

## Screenshots and demonstration

- Apollo 1: `flagship-apollo1/flagship-1440-top.png` and `flagship-apollo1/flagship-390-top.png` for first viewport; full page screenshots at 390/1440.
- Atlas: `atlas-preview-1440.png` and `atlas-preview-390.png`.
- Open `flagship-apollo1/index.html` and `atlas-preview.html` in browser for working controls; prefer http-server to preserve browser security policies if file URLs are restricted.

## Design decision — not preapproved

**Black Dossier** currently supports the strongest portfolio-worthy, content-first presentation. `Museum After Hours` is appropriate for individual Research Desk exhibits, and `Observatory` can inform future verified-data geography layers. Founder selection is still required before production-grade implementation. Do not copy the reference site's layout or assets.

## Next engineering sprint

1. Verify the six NASA image URLs in an unrestricted browser and audit rights/attribution, download dimensions, responsive crops and alternate text; replace unreachable WordPress CDN links with approved local/optimized assets only when rights verified.
2. Run axe, NVDA or VoiceOver and real touch scroll and focus regression. Improve image-loading and first-contentful-paint performance under measured conditions.
3. Replace brittle hand-authored HTML generation with an explicit component interface and WordPress integration adapter. All content must remain in semantic WordPress fields; source data should be cached or statically compiled, not fetched on every interaction.
4. Compare live homepage and unmerged PR #49 at 360/390/768/1024/1440/1920 to the selected Experience 2.0 art direction. Preserve existing lead-gen and dynamic site blocks.
5. Vet six Atlas records for exact event-vs-artifact coordinate distinctions, precision and original-source references; publish no pins until cleared.
6. Ship separate, governed feature PR(s) only after founder concept selection, QD exact-sha review, and hosted CI recovery. PR #49 remains untouched.

## Quality caveat

A polished prototype does **not** establish production performance, media rights, screen-reader parity, or a Webby-level outcome. Independent review and real measurements are still necessary.
