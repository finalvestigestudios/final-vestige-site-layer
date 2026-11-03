# Apollo R98 — seven-view source roundtrips (STAGING HOLD)

## Problem and scope

The real R97 gallery points to Source Passports, Chronology and Curated Atlas but return navigation from the six other verified Apollo views back to the gallery was incomplete. Researchers could lose the precise NASA record when switching presentations. This Apollo-only derivative changes **seven isolated static HTML preview documents**, adding **54 native, same-source route links**: 36 links from six existing views to six corresponding gallery records, plus 18 links from gallery records to the matching rights board, Research Reading Room and Evidence Review Hub. It never suggests any geographic, chronological or causal connection between different records.

The R98 generator does not modify any R85/R87/R88/R89/R93/R94/R97 source generator. Before transformation it verifies every file in the sealed R97 receipt, all 28 SHA-256 values, source URLs/catalogs/titles for each of 42 cards, unreleased rights flags, January 1967 provisional crew identity and the two January 24, 2017 retrospective dates. Untrusted, extra, symlinked or changed assets fail closed. The additive r98_crosslinks.css is scoped to navigation only. R97's original receipt remains as a historical *input* receipt; R98_ROUNDTRIP_RECEIPT.json records the 30 transformed/input files and their new hashes, with publication approval false. Deterministic ZIP creation uses fixed timestamps and normalized permissions.

## Browser acceptance

The R98-specific independent workflow builds the complete R92→R93→R94→R97→R98 chain twice, verifies byte-for-byte identical ZIPs, runs 10 adversarial source-custody tests, then uses a real HTTP server and Chromium Playwright to verify all seven documents across 320, 390, 768, 1440 and 1920px with JavaScript on/off (**70 configurations**). It exercises all six same-record native links per document at 390px, both JS settings (**84 real cross-page navigations**), keyboard activation, mobile touch-capable context, reduced-motion, forced colors, absence of unexpected external requests and horizontal scrolling. Targeted axe-core 4.14.0 scans cover gallery and Atlas; local LCP and CLS are laboratory observations, not hosted WordPress.com Core Web Vitals. Reproducible screenshot/PDF artifacts and SHA receipts are generated. The PDF preserves the six individual NASA source URLs and six photograph-reuse warnings.

**Local environment limitation:** The task execution container's Chromium blocks http://127.0.0.1 with ERR_BLOCKED_BY_ADMINISTRATOR, so local Python unit results are not browser results. Do not call browser testing a pass until exact-head GitHub Actions real Chromium finishes successfully.

## Release hold and ownership

Six photograph-specific rights assessments, S67-19766 identity review, actual hosted WordPress.com/Assembler integration, manual NVDA/VoiceOver, physical-device QA, independent editorial review and founder publication authorization remain outstanding. R98 includes **no NASA photographs, geo pins, inferred edges, WordPress content/settings writes, publishing steps, new paid services, or deployment instructions**. Frozen homepage PR #49, homepage lead branches and original Research Desk PR #158 stay untouched. Review Issue #150 before any release decision.
