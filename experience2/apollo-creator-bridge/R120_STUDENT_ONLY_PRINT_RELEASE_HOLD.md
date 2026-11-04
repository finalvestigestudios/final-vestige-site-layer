# Apollo R120 — opt-in student worksheet printing; STAGING HOLD
Date: 2026-11-04. Owner: Apollo Experience 2.0 / Issue #150; conversion coordination #820 and charter #818.

## Why it matters to qualified educators
The prior staging default Print intentionally includes the entire evidence register, chronology, photo limitations and classroom worksheet. That preserves an auditable *full source packet*, but teachers wanting to distribute a student-only worksheet would have to isolate pages manually. Worse, the full printed packet contains explanatory findings that can reveal the student's intended investigation conclusion. This is a conversion/trust usability risk for a proposed educator audience. No teacher usability testing or purchase evidence is claimed.

## Actual source change (no production)
- Added **one nonintrusive utility button** inside the existing free exercise: "Print the student worksheet only". It is hidden without JS and enables itself only when native browser printing is available. The existing **single primary classroom CTA** remains unchanged.
- Normal browser Print still includes **all four findings and the full NASA register** with the print rights warning. The separate student-only print action sets a temporary CSS mode that excludes the hero, source packet and teacher-facing solution; the student sheet keeps two direct NASA reference links, evidence prompts, and its **own visible source-custody notice** noting 0/6 file-specific photograph clearances, provisional S67-19766 association, and no NASA endorsement.
- After native print, the afterprint listener removes the temporary CSS mode. A thrown print call also resets it. No JavaScript remains fully readable and full-packet printable.
- Extended **actual-source** `qa_r113_print.py` to exercise the two print variants at 390/1440px; require no leaked teacher answer, visible standalone rights notice, working NASA links, generated student-only PDF and afterprint restoration. R120 acceptance requires all inherited full-page/axe/performance tests too.
- Added `test_r120_print_contract.cjs` with 19 static-source conditions and 11 adversarial mutations. It is a regression aid, not browser acceptance.

## Evidence actually executed
- The exact committed Apollo landing blob `c270d516bc9e4f91b4a7c780b4f38b4cfc774bce` and exact contract test blob `9f0c2559688705cd681cf67b3ab85751501a484f` were checked in V8 with Node-compatible shim: 19/19 source conditions, 11/11 mutation tests passed. **Native Node on exact checkout not executed.**
- Chromium 144: **14/14 configurations** (320, 360, 390, 768, 1024, 1440, 1920 with JS on/off) passed against a representative offline fixture carrying the R120 print-mode CSS/JS only; source-packet and student-only print modes verified, including touch, afterprint cleanup and PDF text check using `pdftotext`. **Fixture, not complete Apollo page.**
- Generated one reproducible screenshot and one fixture PDF; deterministic fixture archive SHA-256 `bfa5d4bfa73d1ee0bcd874072d4d07e2062f9bd0243b34ace12bfed7c7b92bb0`. The archive contains explicit fixture-only labeling.
- Actual complete Apollo page Chromium/Playwright acceptance **NOT EXECUTED**; axe-core **NOT EXECUTED** (approved local bundle absent); actual-page LCP/CLS **NOT MEASURED**; WordPress/Assembler **NOT TESTED**; exact-head CI not asserted green. These are release blockers.

## Offer → funnel step → blocker → change → evidence → owner
1. **Proposed paid Apollo teacher casefile → verified paid purchase:** no verified existing sellable SKU/rights/price/delivery/refunds; do not add checkout. Independent seller-origin inventory and founder approval needed. Owner: Claude/Growth + founder. **BLOCKED.**
2. **Grok-approved Apollo long-form asset → source-grounded investigation → free worksheet:** classroom printing friction; opt-in student-only print is the experiment. Evidence: staged source change, 19+11 static checks, 14 fixture browser configurations; actual-page/browser acceptance still pending. Owner: Apollo; Grok video/distribution; Praxxis external independent review. **BUILT, PARTIALLY TESTED, NOT LIVE.**
3. **Optional worksheet audience capture / educator interest:** no approved integrated Apollo-specific mechanism or user consent/merchant data. Do not add form or duplicate newsletter. Owner: Claude/Dispatch/Site QA. **NOT IMPLEMENTED.**
4. **Qualified source-attributed sessions → paid orders → refunds/fees → realized net per 1,000 human sessions:** no reconciled Apollo asset_ids, first-party sessions or merchant orders. #820 contract applies to 7/30-day cohorts; do not count pageviews, worksheet print taps or checkout clicks as sales. Owner: Claude/Growth/Praxxis. **NOT COMPUTABLE.**

## Unchanged safety and release gate
Research Desk PR #158 remains unmodified, including six R119 editorial source-role reconciliation flags requiring an independent resolution. All 6 photograph-specific reuse decisions remain incomplete; proposed S67-19766 identity provisional. No speculative geo pins, new photos, affiliate activation, analytics tags, audience data collection, Payhip links, social posts or paid services. The separately live Evidence Atlas needs a release-record reconciliation; the R120 staging file is **not** a claim of a corresponding WordPress deployment. Frozen homepage PR #49 and homepage lead branches are untouched.

**STAGING HOLD.** Full actual-page Playwright (incl. no-JS/320–1920), approved axe-core accessibility, screenshots/print PDF, actual LCP/CLS, WordPress/Assembler and historical/rights/independent review, seller validation and founder release approval are mandatory before any promotion.
