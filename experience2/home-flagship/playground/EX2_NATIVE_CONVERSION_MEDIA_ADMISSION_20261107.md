# EX2 — Integrate conversion and archival-image gates into real WordPress admission
**2026-11-07 · DRAFT ONLY · RELEASE HOLD · no CMS writes or deployment**

Parent: draft PR #1399, pinned parent commit `a1e31b8bae722b3a5d83c7829a09bece2b21577f`. Frozen PR #49 remains untouched. This branch changes only the existing **read-only** native WordPress admission test and adds regression controls; it does not change the seven-chapter candidate, theme, plugins, tracking, production Page 6 or merchant funnels.

## Actual gap repaired

Previously `verify_integrated_playground.py` could pass its semantic checks with five Focus URLs even if an overlay occluded every first-screen signup CTA. It also decoded a received archival image and reported bytes without binding the browser-selected URL to specific authorized WordPress media IDs, expected responsive dimensions, HTTP 200, and media MIME type. Separate earlier reviewer/provenance code existed but was not part of the **same native WordPress release-admission path** invoked by #1399.

## New unified gate

1. `read_semantics` records geometry and a `document.elementFromPoint` hit test for each Focus link. It requires at least one visibly unobstructed first-screen Focus destination (24x24 px minimum technical target). The gate runs on all seven widths and both JavaScript modes, so a popup, invisible link, clipped mobile layout, or pointer-obstructing overlay blocks acceptance.
2. Native `run` now imports the previously-reviewed `verify_archival_provenance.py`, calls `classify_source` for each selected original/CDN derivative, decodes *actual response.body()* using the existing Pillow decoder, then verifies selected dimensions, status, Content-Type and SHA-256 transfer receipt. CDN responses are explicitly `first_party: false`; no assumption that a WordPress CDN derivative was fetched from the Final Vestige origin.
3. Negative-control tests cover covered/offscreen/no-geometry Focus buttons; swapped archival URLs; wrong HTTP status/type/dimensions; and missing historical chapter/Margins counts. These are unit tests, **not staging tests**.

## Independently executed offline evidence

- Actual pinned private PHP source from #1393 bundle `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d` provided the HTML/CSS for isolated Chromium testing. No WordPress renderer was involved.
- 12 source-rendered static Chromium states: 320, 360, 390, 768, 1440, 1920px, each JS enabled/disabled. All observed 5 Focus links, **2 unobstructed first-screen targets**, zero horizontal overflow; no sources or marketing scripts changed.
- A simulated full-page fixed overlay at 390px obscured **both** first-screen Focus CTAs as expected. A narrower overlay blocked only one first-screen CTA. These are negative controls.
- A synthetic V8 test evaluated the **exact committed source JavaScript expression** under clear, overlaid, hidden, offscreen and 320px controls: 5/5 intended outcomes.
- The archival source verifier has offline negative tests for malformed CDN URL, wrong MIME, wrong dimensions and missing bytes; this is **source-format evidence only**, not confirmation of transferred WordPress media.
- 200% CSS zoom static fixture check at 320/390/768/1440/1920: no horizontal overflow. This is not browser-native zoom, genuine WordPress, axe or Lighthouse.
- Artifact screenshots and JSON are in the private founder review evidence package; not published to a public production host.

## Asset rights and historical custody

- Apollo crew photo: existing site WordPress media #473 / `s67-19766.webp`; source attribution NASA, with non-endorsement/editorial use considerations. NASA Apollo 1 source: https://www.nasa.gov/mission/apollo-1/ .
- Franklin note: site media #474 / `Franklinexpeditionnote.jpg`, described in its site metadata as a **published 1869 reproduction**. The hero's separately designed parchment is labeled editorial typesetting, **not facsimile**; original dated 28 May 1847 and 26 April 1848 marginal addition corroborated by RMG record HSR/C/9/1: https://www.rmg.co.uk/collections/objects/rmgc-object-504898 .
- NYPL #1258 is **excluded from the unpublished candidate**, with no new rights claim. No image transfer was obtained in this environment.

## Business/QA contract

**OFFER → STEP → BLOCKER → CHANGE → PASS/FAIL EVIDENCE → OWNER**: free 52-page Focus Fieldbook → evidence-informed homepage visitor sees reachable contextual CTA → semantic-only test could miss obstructed CTA and unverifiable archival provenance → integrated first-screen hit test and authentic selected-image response receipt → source/fixture positive and negative controls pass; WordPress execution remains BLOCKED by npm/remote theme DNS → interim homepage engineering + independent QA. Claude owns analytics, Jetpack conversion confirmation and checkout; Grok/Praxxis own creator-to-site attribution.

**Hard release gates remain:** successful isolated WordPress/Assembler startup; real image bytes, browser/axe WCAG 2.2 AA, keyboard/no-JS/touch/200% zoom; measured Lighthouse/CWV; confirmed Jetpack signup only with authorization; founder visual approval; exact-SHA QD and CI. WordPress.com Personal does not offer a separate native clone. An isolated developer site does not certify WordPress.com-hosted redirects, Jetpack, cookies, or field CWV. No subscription, conversion, purchase or net-revenue claim is made.

**Release decision: HOLD.** No merge, deploy, publish, production settings change, affiliate activation, subscriber data write, or spending.
