# Apollo Experience R309 — curated NASA media-custody index (staging only)

**Draft only, not installed or live.** This is an isolated Apollo change stacked on R308, not homepage PR #49 or Research Desk PR #158. Existing claim chronology, NASA documentary sources and one free editorial continuation remain unchanged.

## Why this exists

PR #158 indexes six candidate NASA photographs; earlier Apollo R305 blocked all of them from the Atlas to avoid treating imagery as evidence of the precise fire cause or as unrestricted commercial imagery. R309 independently inspected the NASA record pages and adds **four confirmed contextual source-page links** in one optional `<details>` disclosure *below* the existing three-record documentary catalogue. No actual image is embedded, fetched, licensed, or presented as claim proof. Two ambiguous/unresolved records stay excluded. `SOURCE_CUSTODY.json` identifies exact source URLs, dates, limits and rights status. This is a **link-only record index, not an image gallery** until the rights/editorial release gate is satisfied.

NASA links to third-party sites do not imply endorsement. NASA's current [Brand Center](https://www.nasa.gov/nasa-brand-center/) allows factual linking while warning about commercial endorsement, marks, identifiable individuals and third-party material. The historic [Apollo 204 Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) identified a probable electrical initiator but no single conclusive ignition source. An archival photo cannot fill that evidentiary gap.

## Test/rollout contract

From the repo root with PHP, Python Playwright and installed Chromium:

```bash
python experience2/apollo-r309/qa/source_controlled_gate.py
python experience2/apollo-r304/qa/gate.py
python experience2/apollo-r305/qa/gate.py
python experience2/apollo-r305/qa/check_rd_crosswalk.py
python experience2/apollo-r308/qa/source_controlled_gate.py
```

A reviewed digest and pinned source URLs fail closed on contextual-media edits; *only* the media index is withheld if invalid, while the original documentary claims, source links and free-investigation CTA remain readable. The media index is keyboard/touch/no-JS operable; four links are properly labeled as `noncommercial-media-reference`. Every record carries `data-fv-claim-proof="no"` and `data-fv-image-rights="not-cleared-for-reuse"`. Responsive styles are scoped to the index with 320–1920px and print/forced-colors support. The historical source selectors in R304/R305 QA are narrowed to the canonical documentary list so the two custody categories cannot be confused.

## Commercial and release boundaries

**One journey:** future approved Grok Apollo long-form → Atlas → NASA documented sources → free Apollo investigation → separately approved, audience-relevant paid offer. The extra photograph links are **not conversion events** and remain opt-in below the existing free continuation. There is no authenticated published Grok asset, payable Apollo SKU, merchant settlement or 7/30-day qualified human cohort yet. Net revenue per 1,000 qualified sessions remains unavailable.

**Release: HARD HOLD.** No WordPress/Assembler installation, genuine axe-core, VoiceOver/NVDA, native browser HTTP/CSP, field LCP/CLS/INP, merchant checkout acceptance, product/affiliate rights review, exact-head hosted CI or founder authorization in this run. Offline Playwright does not satisfy those gates. No NASA promotional marks, invented geolocation, analytics, new product CTA, paid services, social posts or live changes.
