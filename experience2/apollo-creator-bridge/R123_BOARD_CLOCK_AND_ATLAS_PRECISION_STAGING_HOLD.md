# Apollo R123 — Board clock certainty + Atlas R80 photographic-date parity

**2026-11-04 · DRAFT / STAGING HOLD.** Additive Apollo owner lane under [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), commercial governance [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) / [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Parent branch: R122 `ea8a828477d21346376edc8542e280e8c531191c`. No homepage PR #49, Research Desk PR #158, Grok/Praxxis queue, WordPress, analytics, Payhip or production changes.

## Primary-source chronology and precision

The existing three-point chronology collapsed important distinctions between an electrical interruption, first spoken warning, intense fire, pressure-vessel rupture and last transmissions. This increased the risk that “14 seconds” could be mistaken for a measured ignition-to-death interval. R123 renders five static, no-JavaScript Board-derived milestones with ISO 8601 UTC labels and explicit evidence classifications:

| NASA Board clock (GMT Jan 27, 1967) | Evidence label | Editorial limit |
| --- | --- | --- |
| 23:30:55 | Observed electrical event | Power interruption might be associated with initiation but is **not** a proven unique ignition source. |
| 23:31:04.7 | First recorded verbal fire report | Not proven ignition time. |
| About 23:31:12 | Approximate fire-intensity point | No invented telemetry interpolation. |
| About 23:31:19 | Approximate pressure-vessel rupture | Not an exact onset timestamp. |
| By 23:31:22.4 | Bounded cessation of voice/data transmissions | Not certified death time. |

Difference between the displayed report and approximate rupture is **about 14.3 seconds**, while the Board's summary describes the initial fire stage as **approximately 15 seconds**. These approximate descriptions must not be presented as conflicting measurements. **Neither is an ignition-to-death clock.** Historical primary source: [NASA, Report of the Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). Independent historical editorial review is required; source references do not themselves certify our paraphrases.

## Atlas R80 cross-component custody repair

The previous Apollo photo rail ordered the month-only January 1967 crew portrait between day-known photos, insinuating narrower precision than supported. R123 synchronizes with the existing [Atlas R80 chronology custody rule](../evidence-atlas/R80_CHRONOLOGY_CERTAINTY_STAGING_HOLD.md): only **four day-known photographic checkpoints** are ordered (1966-10-18 record 03, 1967-01-03 record 02, 1967-01-28 record 05, 2017-01-24 records 04 and 06 grouped together). Record 01 is in a separate month-known / day-unknown note with `<time datetime="1967-01">`. All six original NASA URLs remain linked, with no new photograph binary, geo pin, relationship edge, rights claim, remote asset, product, analytics or signup mechanism. This source reference rail is **not** the instrument-based fire chronology.

Proposed crew-portrait catalog number **S67-19766 is provisional**: cited NASA page does not itself establish that identifier. Individual NASA photograph-use assessments **0/6 complete**. [NASA imagery/branding rules](https://www.nasa.gov/nasa-brand-center/) are general policy, not six photo-specific commercial permissions. The Research Desk [PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158) still requires independent source-role reconciliation and was not modified.

## Source-controlled implementation and reproduced validation

- `landing-preview.html`: five machine-readable Board clock records, uncertainty callout, four exact-day photo checkpoints, 2017 grouping and segregated month-only photo.
- `qa_r113_print.py`: **existing** actual-source full-page browser runner augmented with 320–1920px JS-on/off checks enforcing time order, precision labels, source URL, image chronology, one relevant free CTA and no-JS custody. It still fails acceptance without exact tracked Git HEAD and an approved local axe bundle. We did **not** create a parallel metrics or measurement script.
- `test_r123_board_clock.cjs`: **22 executable dependency-free Node `node:test` regression cases**. These were invoked against the exact connected GitHub branch `landing-preview.html` in a V8 **Node-compatible harness**: **22/22 PASS**. This is not native Node CI, full-page Chromium/Playwright, axe-core, performance, actual WordPress or field Core Web Vitals evidence.
- To reproduce locally from this branch: `node --test experience2/apollo-creator-bridge/test_r123_board_clock.cjs`, then `python experience2/apollo-creator-bridge/qa_r113_print.py --html experience2/apollo-creator-bridge/landing-preview.html --axe /path/to/approved/axe.min.js --out /tmp/apollo-r123-browser`, with a working installed Playwright Chromium and exact Git HEAD. Both commands remain **unexecuted on a native host for R123**. No R123 screenshots, PDF, LCP/CLS or axe receipts are claimed.

## Conversion-first plan (one relevant educator pathway only)

| Priority | OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| P0 | Proposed paid Apollo educator casefile → merchant-confirmed purchase | No independently verified currently sellable, rights-cleared Apollo SKU, terms, delivery, price or refunds | Claude/Growth to inspect current merchant inventory and verify a matching offer **before** adding any commercial button | **BLOCKED; no paid sale or revenue verified** | Claude/Growth + founder |
| P1 | Grok Apollo history long-form → investigation → free worksheet | Exact time and photo-date ambiguity undermine trust and classroom utility | R123 uncertainty custody + Atlas R80 precision parity; keep no-JS/free worksheet as sole CTA | **BUILT; V8 22/22 source tests; actual-page browser pending** | Apollo; Grok owns production/distribution, Praxxis external review |
| P2 | Worksheet → optional paid casefile | Not yet verified or approved | One quiet contextual CTA **only after** relevant merchant SKU and separate founder approval | **NOT ACTIVATED** | Founder/Claude |
| P3 | Creator `asset_id/utm_content` → qualified human sessions → confirmed order → fees/refunds → net revenue | No observed Apollo-qualified sessions or merchant orders; no reconciled cohort denominator | Reuse #820 privacy-reviewed tracking, never duplicate scripts; 7/30-day cohorts and tiny-sample flags | **NOT COMPUTABLE** | Claude/Growth/Praxxis |

**Release gate is STAGING HOLD:** genuine exact-head full-page Chromium matrix, keyboard/touch/no-JS, axe scans, screenshots/PDF, measured lab LCP/CLS, historicist/QD review, Research Desk #158 source-role reconciliation, six photo-specific rights decisions, WordPress/Assembler staging QA, published Atlas approval-record reconciliation, hosted CI and explicit founder approval. Source-controlled ≠ browser-qualified ≠ live ≠ merchant-verified. Nothing merged, deployed or published.
