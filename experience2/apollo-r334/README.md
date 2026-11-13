# Apollo R334 — independent Research Desk custody bridge (staging only)

Issue #150 · cross-reference #820/#818 · Research Desk PR #158 · parent Apollo draft PR #2331 (R333) at `1144b5c624c46e021ac4c4f543f834d050fd9fc2`. Frozen homepage PR #49 is out of scope.

## Actual implementation

Standalone WordPress-only shortcode `[fv_apollo_custody_review]`, with no WordPress content or settings writes. `fv-apollo-custody-bridge.php` and `assets/fv-apollo-custody.css` implement a six-record, **source-first** link-only comparison of PR #158's original `templates/ledger.html` Git blob `403d128c57b9bc82dac7c619651689070edef86c` (PR #158 commit `250d7f05a4de037e73826dcf0cfaef0ec4c29383`). Documentary NASA text is deliberately presented ahead of each related photograph catalogue link. Each photograph sits in a native `<details>` disclosure with explicit unverified reuse rights. No NASA photos or external images are loaded, no map or speculative pin is rendered, and no additional trackers, scripts, purchases or signup forms exist.

### Source-precedence review requiring Research Desk owner approval

| Desk record | Current label in PR #158 | First link in PR #158 | Source-precedence concern |
|---|---|---|---|
| 02 | Primary Review Board Record | NASA S67-15717 spacecraft photo | Photo cannot independently support oxygen/pressure Board findings |
| 03 | Instrument Chronology | NASA S66-58038 training photo | Photo cannot establish recorded instrument times |
| 04 | Hardware and Design Finding | NASA KSC-20170124-PH_KLS01_0164, 2017 tribute photo | Retrospective exhibition is not contemporaneous hatch proof |
| 06 | Engineering Response | NASA KSC-20170124-PH_KLS01_0090, 2017 tribute photo | Exhibition cannot independently establish redesign timing or implementation |

Records 01 and 05 retain contextual status but also present documentary support first in the staging bridge. These are **source-link precedence and editorial labels for review**, not findings that any historical claim in PR #158 is false. NASA's Board report states that an electrical arc was the most probable initiator but no *single ignition source* was conclusively identified. The image-detail pages are link-only, not reuse-licence evidence. PR #158 must be corrected by its own owner; this bridge does not alter its files.

## Browser acceptance and reproducibility

Run from repository root with PHP, Python 3, PyMuPDF (`fitz`), Playwright Python and Chromium installed:

```bash
python experience2/apollo-r334/qa/commit_gate.py
```

The committed test invokes **actual R334 PHP through `qa/wp_stub.php`**, injects the exact scoped CSS into offline Chromium and tests widths 320, 360, 390, 768, 1024, 1440 and 1920px, JS enabled and disabled, with extra 400% root text at 320px: **16 responsive browser contexts pass**. It also tests duplicate shortcode IDs, keyboard Enter disclosure operation and CSS+JS-disabled semantic access (3 more acceptance contexts), 19 named interactive controls per instance, unique source URLs, on-screen target geometry, no horizontal overflow, touch emulation, forced colors and reduced motion. Six unsafe input mutations are detected: unauthorized merchant, false photo rights, invented geo pin, photo falsely substituted for document, invalid CTA, erased review flag. One real Chromium print PDF: 4 pages, 13 URI links including six media records, no UTM or paid links. Four browser screenshot artifacts and a JSON receipt are produced under `QA/`.

This is **offline browser testing of a PHP WordPress stub**, *not* an installed WordPress/Assembler/CDN test, native site HTTP/CSP test, independent screen-reader test, Firefox/Safari acceptance or production Core Web Vitals. `axe-core` is not installed and **was not executed**; its independent gate remains blocked. No live audience sessions, confirmed orders, net revenue, affiliate payouts or actual Grok asset attribution are known from this sprint. CI must pass on the exact PR head before release consideration.

## Conversion/release contract

**One controlled proposed journey:** Grok's approved Apollo long-form/Shorts asset (asset ID and destination unverified) → NASA source-aware Atlas/Research Desk → the **one existing free investigation link** → an **independently authenticated, payable, rights-cleared Apollo-appropriate product**, only after Founder/Claude approval. The draft bridge contains no paid offer or paid CTA. Proposed test hypothesis: making source relationships explicit preserves trust and reduces false-premise drop-offs before continuing to the investigation; success requires verified qualified human sessions and ultimately source-confirmed paid orders, refunds/fees and realized net revenue per 1,000 qualified sessions, not presumed click-to-sale conversion.

**HARD HOLD:** no standalone production deployment, no WordPress writes, no edits to Research Desk PR #158/homepage PR #49, no social posting/creator queue changes, no new tracking, merchant, affiliate, email, spending or fabricated geographic relationships. Requires editorial approval, image rights review, hosted CI, real WordPress and independent accessibility acceptance, Grok campaign identification, confirmed payable SKU/checkout and Founder/QD release authorization.
