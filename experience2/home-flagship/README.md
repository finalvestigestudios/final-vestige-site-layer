# Experience 2.0 / Homepage flagship direction study

**Status:** SOURCE-CONTROLLED DESIGN PROTOTYPE, NOT A WEBSITE UPDATE OR RELEASE. Responsive standalone HTML/CSS/JS preview containing three visual treatments of one evidence-led editorial structure. It does not change PR #49 (frozen), PR #158 (Apollo Research Desk R&D), the public WordPress homepage (page 6), theme, forms, 72 Margins records, or Jetpack.

**Founder direction:** reach the craft, immersive coherence and emotional effect of Blue Corridors' 2026 Webby-winning data visualization, without copying its UX, layout, photographs, branding or code. Make the evidence itself the experience. Preserve the independent historical research mission, existing Focus Fieldbook funnel and future ethical Mind & Perception/affiliate lane.

## Try the preview

Serve this folder with a static web server and open index.html. Use the top DESIGN STUDY / NOT LIVE controls to inspect:

1. **Black Dossier** (URL parameter: ?direction=dossier). Monumental typography, noir-black archival mood, stark gold, near-cinematic evidence chamber. This is the proposed starting direction, NOT an approved founder selection.
2. **Museum After Hours** (?direction=museum). Warmer exhibition room, paper-like original typographic object, more physical archival framing and object-centered visual treatment.
3. **Observatory** (?direction=observatory). Midnight teal, subtle measurement grid, cartographic/technical design vocabulary; no false map coordinates or speculative connection lines.

No theme button persists user state; disabled JavaScript displays the default Black Dossier markup and all three evidence exhibits in full. All historical text, original-source links and evidence boundaries are real HTML, not JS-generated prose.

## Original implementation

- **index.html:** one semantic H1 "Find what others miss.", monumental first-screen entrance, investigative deep links, three authenticated source exhibits (Apollo 1, Franklin, 1903 Malbone system map), explicit evidence limits, a method section, tightly scoped Mind & Perception bridge, direct working Focus CTA and affiliate disclosure.
- **flagship.css:** original scoped CSS (~23 KB unminified), three genuinely different visual palettes/hero geometries, responsive mobile-to-desktop intent, prominent CTA, visible keyboard focus, reduced-motion override, no body scroll lock, no new framework or external font dependency. Decorative circular patterns are original CSS art—not represented as real historical evidence.
- **flagship.js:** optional case chooser using native buttons, aria-pressed, keyboard arrows/Home/End and aria-live; optional art direction controls. HTML details disclosure works without JS. Failed images fall back to readable text/source links. All exhibits display in the absence of supported APIs or after partial initialization failure. No touch cancellation, autoplay, tracking or hidden historical content in the base HTML.
- **source-manifest.json:** three source records, exact WordPress post IDs, original-source/article URLs, evidence limits, rights status, truthful caveats.
- **tests/test_flagship.py:** source-level offline regression checks, not rendered browser/image-load certification.

## Evidence and licensing

Source metadata independently crosschecked against the published WordPress posts 434 (Apollo 1), 433 (Franklin) and 621 (Malbone) on 2026-10-30. All source records and limits are in source-manifest.json.

**NASA:** Original photo: https://www.nasa.gov/image-detail/apollo-1-crew-honored/ ; Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA media guidance does not permit implication of NASA endorsement for affiliate products; individual-photo/recognizable-astronaut and publication-context reviews remain open. We explicitly distinguish an astronaut portrait from evidence of hatch mechanics.

**Franklin:** https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg explicitly marks the historical reproduction of the 1847-48 Victory Point note public domain; source identifies the 1869 McClintock printed scan. We name the document's limits.

**NYPL:** 1903 BRT map https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0 is cited by the published Malbone investigation, but the catalog page returned 403 to our external reader this sprint. Rights metadata and live image loading remain unverified. The 1903 network map MUST NOT be presented as the plan of the 1918 temporary curve or as a literal spatial/chronological overlap with the wreck evidence.


**Image performance correction (2026-10-30):** WordPress media ID 1258 exposes the NYPL original at 5667×3831, **5,553,669 bytes**. The prototype no longer requests that full-resolution image by default: it uses WordPress-listed Jetpack 768/1024/1536 responsive variants with a sizes hint, and shows the full map by object-fit:contain rather than cropping evidence. This does NOT prove that the CDN variant bytes or load status are good; capture and record real network values before release. NASA media ID 473 original is 1041×810/78,346 bytes; Franklin ID 474 original is 960×1526/466,043 bytes. Original source links remain exposed in the evidence drawer.

## Integration path and non-regressions

The demo includes its own standalone header, studio controls and footer. It must NOT be pasted over live WordPress page 6. If a direction is approved, adapt only the selected hero and curated evidence module, preserving live WordPress Assembler navigation and canonical paths, the full 72-item Hidden in the Margins collection and enhancement, current source-driven editorial routes, 52-page Focus Fieldbook and Jetpack one-list signup, six Worlds, Apollo narrative, existing Library inspector, Public Record, and actual footer.

Preferred implementation uses source-controlled WordPress semantic HTML for real meaning; scoped CSS and optional JS delivered by the governed Site Layer plugin on a new exact release head; same-domain optimized media; individual source evidence attribution; and coordinated source ledger vocabulary with separate PR #158. Do NOT modify PR #49, falsely assume its QD/CI has passed, or deploy this preview by circumventing governance.

**Mind & affiliate coordination:** This preview links ONLY to published Puységur research and /focus/, not unpublished /mind/ or seller/affiliate pages. The future Mind hub is in Issue #171 / draft PR #172. This introduction is an evidence-relevant cultural/psychological bridge, not a claim of medical, financial, hypnotic or meditation efficacy. No commission links appear.

## Required quality gates before visitors see this

1. Execute: python -m unittest discover -s tests -v ; Node check: node --check flagship.js. Record exact commit and outcomes.
2. With LIVE WORDPRESS/NASA/NYPL IMAGE ACCESS, capture desktop/mobile shots of three themes at widths 360,390,768,1024,1440,1920. Inspect loaded images, cropping, page depth, 200% zoom, iOS Safari and Android touch. Source-only tests and screenshots from a network-blocked browser do not certify working media.
3. Test native keyboard focus, all case chooser controls, no-JS static content and details, VoiceOver/NVDA, missing Element.closest fail open, injected error fallback, mobile scrolling and reduced motion. Run axe, WCAG 2.2 AA manual contrast and focus visibility.
4. Measure Lighthouse and CWV in realistic staging: target LCP ≤2.5 s, INP ≤200 ms, CLS ≤0.1 at p75. These are targets, NOT measured results. Consider a smaller hero asset, AVIF/WebP variants with verified source rights and image optimization before release.
5. Verify rights and accurate original media captions for each, especially NYPL, with no implied NASA endorsement. Editorial sign-off mandatory.
6. Founder selects visual direction and flagship scope. Independent exact-SHA QD, hosted CI green, staging WordPress render proof, then explicit governed release approval. NOT accomplished by a source-controlled prototype.

## Source selection / R&D decision

The existing Experience 2.0 Foundation (research/experience-2-foundation-2026-10-29) recommended Black Dossier as a potential starting point; this package provides three selectable compositions and the real source-data contracts for visual review without treating founder choice as already made.

Ownership: homepage lead owns this draft branch; Apollo studio owns separate PR #158; Mind studio owns PR #172; release diagnostic lane owns frozen PR #49 CI. No ownership overlap.
