# R424 — Exact-source Research Desk acceptance (staging only)

**STATUS: SOURCE-CONTROLLED QA TOOLING, PRODUCTION HARD HOLD.** This is an isolated improvement to R423 draft PR #2834 and source-ledger PR #158. It does not change the homepage PR #49, Grok/Praxxis TASK-008, WordPress content/settings, production services or existing measurement tags.

## Problem and change

R423 used shape-compatible synthetic browser fixtures. Those are useful unit tests but cannot establish that the **actual PR #158 six-card HTML** integrates safely with the **actual R423 WordPress shortcode**. The new read-only acceptance harness makes that distinction executable instead of presenting a synthetic PASS as real staging acceptance.

It verifies exact reviewed Git blob SHA-1 identities for three PR158 template/CSS/JS source files and the R423 adapter PHP, rejecting missing sources, altered bytes and symlinks outside the trusted source tree. It then uses PHP with in-memory staging-only WordPress stubs to render the real adapter twice, validates unique IDs, 12 source cards, 12 photograph custody annotations, exactly one existing free-investigation link per instance, and absence of injected media/forms. Playwright Chromium loads the real PHP-generated HTML, original stylesheet and original progressive-search JavaScript, exercising widths 320/360/390/768/1024/1440/1920, search scope isolation, keyboard-native disclosures, no-JS, reduced motion, forced colors, overflow and screenshots.

The harness does not download sources and has no synthetic fallback. It produces a machine-readable HOLD if the reviewed exact-source checkout is missing. It does not deploy or authorize any page.

## Run and evidence boundaries

In experience2/apollo-r424:

    python qa/test_runner.py
    python qa/real_research_desk_acceptance.py --repo /path/to/read-only/PR158-checkout --bridge-dir /path/to/reviewed/R423-folder --output QA/real-template

The expected GitHub sources are PR #158 at commit 250d7f05a4de037e73826dcf0cfaef0ec4c29383, and R423 at 93dda51158453fbc8e2fcc353ef535490eac0d73. Confirm checkout object identities before treating any test result as evidence. Five local adversarial unit tests passed on the reviewed R424 Python source; the actual PR158+R423 integration could NOT run because the exact reviewed PR158 tree was not available in the local container. The runner correctly emitted HOLD with exit code 2. Browser navigation to localhost was independently attempted and returned ERR_BLOCKED_BY_ADMINISTRATOR. Do NOT claim navigated LCP/CLS, genuine axe-core, installed WordPress staging, field Core Web Vitals, screen-reader acceptance, exact-head CI or QD release approval.

NASA source provenance: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ supports the Board's inconclusive ignition-source determination. A photograph showing the crew, training, preparation or a later museum display does not independently prove all historical claims presented alongside it. This sprint reproduces no NASA imagery, logos or speculative map pins.

## Conversion-first release contract

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Original Apollo educator evidence kit | Verified paid purchase | No authenticated rights-cleared, purchasable SKU, fulfillment or merchant confirmation | Withhold paid CTA until verified by owner | HOLD | Founder / Claude |
| Grok Apollo video | Qualified human landing | Published matching asset_id, actual post URL, UTMs unavailable | Existing TASK-008 handoff only; no content takeover | UNVERIFIED | Grok / Praxxis |
| NASA Research Desk | Free source investigation | Previous R423 tests used synthetic ledger | Require exact-source PHP + browser checks | 5/5 unit PASS, integration BLOCKED | Apollo / QD |
| Confirmed orders | Realized net revenue per 1,000 qualified human sessions | No verified orders/fees/refunds or 7/30-day human-session cohorts | Later owner-approved measurement, no duplicates | NOT COMPUTABLE | Claude / Commerce |

Controlled visitor journey: approved published Grok Apollo film → source-authenticated Research Desk → free Apollo investigation at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ → separately approved original educator product after commercial verification. No paid offer is inserted into the historical narrative.

Upstream R417's four-file discrepancy remains quarantined. Production release requires source reconciliation, actual staging, axe/LCP/CLS where possible, independent QD, exact-head CI and explicit founder authorization. Cross-reference #150, #820 and business charter #818. No release, publication, email, purchase or paid service.
