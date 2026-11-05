# Apollo R130 — NASA source custody and rights HOLD (2026-11-04)

**Owner:** isolated Apollo / Research Desk evidence lane. **Base:** R129 at `7b13f90ee2144b150c6ca19444c226a0ddc564bf`. **Do not merge or publish.** This branch only changes Apollo source metadata and local custody validation; Research Desk PR #158, homepage PR #49 and all production systems remain untouched.

## Why
Existing Apollo HTML identifies six NASA photographs and warns that reproduction rights are not reviewed, but had no structured per-record rights evidence contract cross-linked to *both* the source register and the student worksheet. The new source-controlled media ledger keeps separate (a) direct official source-page metadata confirmation, (b) record attribution, (c) historical date certainty, (d) photographic purpose, (e) publicity/endorsement caveats, and (f) actual commercial reuse authorization. A NASA-hosted link is not the equivalent of a paid-product image license.

## 2026-11-04 read-only independent checks

| ID | NASA source | Metadata classification | Rights for FV republication |
|---|---|---|---|
| 01 | https://www.nasa.gov/image-detail/apollo-1-crew-honored/ | NASA date January 1967; catalog **S67-19766 remains unverified** | HOLD / likeness assessment |
| 02 | https://www.nasa.gov/image-detail/amf-s67-15717/ | NASA Jan 3, 1967; producer JSC | HOLD |
| 03 | https://www.nasa.gov/image-detail/amf-s66-58038/ | NASA Oct 18, 1966; producer JSC; identifiable crew | HOLD / likeness assessment |
| 04 | https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/ | Official URL source-cited; **NASA page metadata unavailable during this check**. Secondary Commons file cites NASA original, 2017-01-24, NASA/Kim Shiflett: https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_spacecraft_mockup.JPG | HOLD / source recheck |
| 05 | https://www.nasa.gov/image-detail/amf-s67-21294/ | NASA Jan 28, 1967; producer JSC | HOLD |
| 06 | https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/ | NASA Jan 24, 2017; NASA/Kim Shiflett, retrospective exhibit | HOLD |

NASA policy references: https://www.nasa.gov/nasa-brand-center/ ; https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ ; https://gpm.nasa.gov/image-use-policy . Official source metadata verification is **5/6**; #04 is secondary-only pending a direct NASA recheck. Individual FV photograph reuse decisions are **0/6**, **not** automatically public-domain/commercial clearance. No files are embedded, downloaded, licensed or reproduced.

## Implementation
- `r130_nasa_media_custody.json`: six-record structured and attributable NASA/media ledger with documented uncertainty and clearance HOLD.
- `r130_nasa_media_custody_gate.cjs`: read-only strict crosswalk of ledger ↔ Apollo table ↔ classroom worksheet, right status and NASA metadata fidelity; no network, data collection, or tracking.
- `test_r130_nasa_media_custody_gate.cjs`: 17 native Node tests (including negative mutations for human-visible NASA dates and credits) against the exact in-repo landing HTML; authored but not executed in exact-head CI.
- `landing-preview.html`: twelve semantic `data-fv-photo-rights="not-cleared"` bindings for record rows and handout entries, no visual, URL, layout, CTA or JS changes.
- `r127_source_role_crosswalk.cjs`: include media-custody error propagation into the existing Research Desk / creator-route fail-closed audit.

## Gates
Run `node --test experience2/apollo-creator-bridge/test_r130_nasa_media_custody_gate.cjs` and `node experience2/apollo-creator-bridge/r130_nasa_media_custody_gate.cjs`. PASS means only *source consistency*, not browser acceptance, rights clearance, merchant evidence or authorization to publish.

Required before release: official NASA source 04 recheck, per-image policy/likeness decisions, six PR158 editorial corrections, native Node CI exact-head, full-page real-navigation Chromium/axe/320–1920 screenshots/LCP/CLS, WP/Assembler QA, independent historical review and founder approval. Conversion offer remains a **hypothetical** teacher-ready casefile, not a live/verified SKU. No qualified Grok sessions, paid buyers or net revenue established. Cross-reference #820 and #818. No Google Drive TASK-008 changes or Grok posting.

OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER: Unverified educator paid casefile → paid order → no SKU/rights/merchant validation → retain no commerce → BLOCKED → Claude/Growth/founder. Grok long-form → Apollo worksheet → source/rights drift risk → R130 ledger gate → source-tested only → Apollo. Confirmed orders → net revenue → attribution/merchant statements absent → #820 governance → UNOBSERVABLE → Claude/Growth.
