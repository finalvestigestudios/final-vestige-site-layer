# Apollo Evidence Atlas R312 — unambiguous source-custody navigation (STAGING ONLY)

Owner lane: Experience 2.0 / Apollo 1; issues [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). This is an additive draft PR stacked on R311, **not a homepage/WordPress change**. Homepage PR #49 and Research Desk PR #158 remain separate and untouched.

## Problem and implementation

Native source disclosures were navigable without JavaScript, but four Board-authority links and three reconciliation links were not reliably distinguishable in stand-alone link lists; contextual NASA media links shared the same visible label. Repeated shortcode instances compounded ambiguity. R312 changes **link text/accessibility**, not any NASA destination, date, historical claim, claim digest, commercial attribution, photo-rights policy, media asset, geography or CTA.

- The four Board links and return links use document-action dates in screen-reader-only suffixes, keeping existing visible affordances.
- The three source-date comparison links visibly identify their respective NASA documentary authority, with no claim of independent corroboration.
- The four *link-only* contextual photo records announce their exact accession ID and Atlas instance. Images remain unembedded and commercial clearance unverified.
- The early source-catalogue jump announces the Atlas instance.
- No script, cookies, first/third-party event instrumentation, merchant links or modified campaign parameters. R311's cache-stable free investigation destination remains immutable.

## Reproduce locally

```sh
php -l experience2/apollo-r281/apollo-source-experience.php
python experience2/apollo-r312/qa/source_controlled_gate.py
# Additional extended browser / 200% text and screenshot receipt:
python experience2/apollo-r312/qa/link_purpose_gate.py
```

The source-controlled test runs actual PHP via the local fixture, then Chromium Playwright in 12 viewport/JS contexts from 320 to 1920px, checking native Chromium accessibility-tree names, disclosure keyboard operation, two separate instances, cache-stable HTML, and adversarial ambiguous-link substitutions. The extended gate generates PNG screenshots and a JSON receipt; both are standalone QA artefacts, not deployment evidence. No browser navigator contact with a deployed WordPress/CDN endpoint occurred.

## Primary-source / rights custody

- [Original Apollo 204 Review Board narrative](https://www.nasa.gov/history/Apollo204/narr.html): January 27 oral authorization and January 28 first Kennedy meeting are distinct acts.
- [Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): probable electrical arc; no conclusively identified single ignition source.
- [NASA Brand Center](https://www.nasa.gov/nasa-brand-center/) and [advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/): factual source links are permissible without suggesting endorsement. NASA names/marks and astronaut or employee likenesses have separate advertising and publicity constraints. These links **do not** establish a blanket commercial media right.

R312 adds no map pin, geographic edge, image, or NASA-branded merchandise. Four linked photos remain contextual records, not independent cause-of-fire proof.

## Commercial contract and release hold

Flagship: Apollo 1 evidence investigation for Grok's history documentary viewers. Current single next action: read the **free** Apollo 1 investigation after primary-source verification. A later paid educator/reference dossier remains a hypothesis until founder-approved SKU, rights review, checkout and merchant settlement are demonstrated. Source clicks, editorial continuations and outbound affiliate clicks **must never be counted as sales**. Grok owns video production; Praxxis reviews creator output; Claude owns analytics/caching and production engineering; founder controls commerce/release approvals.

**HARD HOLD:** independently sourced genuine axe-core, manual screen-reader QA, installed Assembler/WordPress and CDN behavior, native browser HTTP/CSP, real-user LCP/CLS/INP, exact-HEAD CI, image/editorial rights and founder release approval are not established by this local gate. Keep PR draft and unmerged.
