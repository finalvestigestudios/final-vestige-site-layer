# R172 — reviewed Apollo caption integration (STAGING HOLD)

**Scope:** isolated additive Apollo Experience 2.0 PR based on R171 `dab14381ffc3ab8cf7de6df2bd628838badaa625`. No homepage PR #49, Research Desk PR #158, WordPress, merchant, analytics, social platform, or paid service changes.

## The defect and the specific fix

R171 independently proved that the three original NASA archive captions on WordPress Page 2017 concatenate their title, prose and source credit in source markup. R169/R170 source custody must remain in force. R172 integrates only the exactly reviewed R171 caption transform and one hash-pinned CSS block, inside the existing final Gutenberg Custom HTML block, **after** unchanged R170 verification. It independently checks the resulting byte-exact preview and historical/link/executable integrity. No changes to the chronology, photographs, NASA anchors, CTA, link destinations, forms, or tracking.

Original editor-source witness used by R168: Page 2017 modified **2026-11-05 18:19:45**, 96,302 bytes, SHA-256 `6948f3d62d91d08c27a3a4b71122fef6ef37bdd333c31f81c27db4ad95ce5e4c`. **This run did not re-fetch or re-attest WordPress editor content.** Any revision change must cause HOLD pending a fresh read-only review.

R171 module SHA-256 pinned `c7b88c83b92a4842a7d202847e775a9cbe8be7e709826815b66142df7d6c6e1a`; scoped CSS SHA-256 pinned `11b810d6398bdd09c3878124a1d846776cef6ac481cccfe409b6681f7de242e0`.

## Reproduce on a clean checkout

With Python 3.11+, Playwright installed and Chromium available, from repository root:

```sh
PYTHONPATH=experience2/apollo-r172 python -m unittest -v experience2/apollo-r172/test_apollo_reviewed_caption_bridge.py
```

Only for an independently re-witnessed, exact raw WordPress editor export (NOT for public HTML):

```sh
python experience2/apollo-r172/apollo_reviewed_caption_bridge.py ./private-wp-page-2017-editor.txt ./preview-staging-hold.html
```

The CLI cannot override the pinned witness. Do not commit the raw private/editor export or promote its HTML without an approved, separate release.

## QA evidence (2026-11-06, controlled fixture)

- **3/3 Python unittest methods passed in each of three runs**; **13 deliberate unauthorized mutations rejected**.
- Real Chromium: **13 contexts**, **255 checks**, six widths **320, 360, 390, 768, 1440, 1920px**; JavaScript on/off, touch emulation, keyboard Home/End, chronology independence, reduced motion, forced colors, source links, CTA and caption geometry; no recorded page errors or horizontal overflow.
- Six screenshots reproducible across two consecutive captures: SHA-256 checksums in `artifacts/r172-browser.json` inside separate evidence ZIP.
- Offline laboratory observed LCP **68–92ms** and CLS **0**; *not* installed WordPress measurements, field CWV, or Lighthouse results. Images were network-blocked in fixture; these are not NASA CDN proofs.
- **NOT EXECUTED:** genuine axe-core (library unavailable), manual screen reader, installed WordPress/Gutenberg rendering, true CSP/CDN/media delivery, production LCP/CLS and CI on the exact PR head. Release remains **STAGING HOLD**.

## Source / rights / geographic integrity

Apollo is the single recommended evidence-rich history flagship for Grok's independently controlled long-form + Shorts, with the Atlas as relevant source-led landing. Its three gallery records are dated separately (NASA S66-58038: Oct 18, 1966; NASA S67-15717: spacecraft processing Jan 1967; NASA KSC-20170124: 2017 exhibit). They are **not** images of the fire itself. No map pins or geographic edges are introduced.

NASA historical collection: https://www.nasa.gov/gallery/apollo-1/

NASA advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

Editorial attribution is not blanket clearance for paid-product marketing, recognizable astronaut likenesses, NASA identifiers, or any implied endorsement. **Commercial imagery rights not certified.**

## Offer → funnel → blocker → experiment → evidence → owner

| Offer / funnel step | Blocker | Proposed change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Prospective Apollo teacher-ready casefile → paid order | **No authenticated sellable SKU, rights clearance, verified checkout or delivery** | Inventory and rights attestation *before* a product CTA; test educator purchase flow separately | BLOCKED; zero sales claimed | Claude/Commerce + founder |
| Grok Apollo YouTube asset → Atlas | No verified published Apollo asset ID, destination or qualified sessions | Reconcile TASK-008 asset inventory and allowed UTMs; creator owns script/distribution | UNKNOWN | Grok/Praxxis |
| Atlas provenance → original investigation | Misjoined NASA captions undermined trust | R172 exact caption integration, single contextual **Read original investigation** CTA | BUILT; OFFLINE CHROMIUM TESTED | Apollo QA |
| Investigation → relevant future offer | No verified matching paid Apollo offer | Keep commercial CTA absent; review only once actual product exists | COMMERCIAL HOLD | Founder/Claude |
| Verified paid order → net revenue/1,000 qualified visits | No reconciled order, refunds, fees, campaign attribution | Issue #820 7/30-day cohort measurement, distinguish outbound clicks from confirmed sales | NOT COMPUTABLE | Analytics |

Hypothesis: clearer photo/date/source provenance reduces trust friction and improves qualified continuation to investigation. **Not measured; no conversion or revenue uplift claimed.** One visitor action only: **Read original investigation**; no unrelated Mini Museum/Cold Case affiliate placement inside historical copy.

## Release governance

Keep draft. Next step: install only into independently approved WP **staging**, verify the current editor witness and Gutenberg serialization, then genuine axe-core and manual assistive-tech, CSP, real responsive CDN/image delivery and production-like LCP/CLS, independent review, green exact-head CI, explicit founder approval. **No WordPress or production writes authorized by this document.** Coordinate through Issue #150, cross-reference #820 and #818. Grok TASK-008 remains Grok/Praxxis-owned.
