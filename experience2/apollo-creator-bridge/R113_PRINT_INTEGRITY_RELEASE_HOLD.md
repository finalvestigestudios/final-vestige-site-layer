# R113 — print-complete Apollo evidence and offline actual-source browser QA (STAGING HOLD)

**Date 2026-11-04**. Part of #150; commercial controls #820 / #818. Stacked from R112 commit 5873237fcd4cca3bfdf944cc9c9c9131b394c024. Homepage PR #49, original Research Desk PR #158, Claude's production branches and Grok TASK-008 queue untouched.

## Defect and correction

The R112 evidence filter hides two of four plates using `[hidden]{display:none!important}`. Its prior print stylesheet did not restore hidden claims: printing the “Unresolved limits” filter omitted two documented findings and produced an incomplete classroom handout. The 34rem source register table and scroll container could also clip the NASA evidence links on letter paper.

R113's print CSS restores all four findings, resets the table minimum width, allows wrapped URLs, suppresses horizontal scroll clipping, and provides a readable white-paper palette. The single free classroom exercise now tells visitors that printing includes every claim and not to distribute NASA photos without rights review. Screen interaction remains unchanged; no new product, email form, analytics script, geo pin or photograph binary.

## Reproducible verification

Exact-source contract: `python -m unittest -v test_r113_print_contract.py`.

Actual-browser candidate: `python qa_r113_print.py --chromium /usr/bin/chromium` (Python Playwright required). Optional `--axe /path/to/reviewed/axe.min.js` needs a locally approved axe bundle; this command never downloads dependencies. The real Chromium runner loads the **actual landing-preview.html bytes**, no local HTTP, and tests 320, 360, 390, 768, 1024, 1440, 1920px × JS on/off with reduced motion, keyboard activation, screen filter, all-claims print, NASA source register, screenshots, PDF SHA-256, six valid finite LCP/CLS laboratory observations and crash-safe JSON receipts. Browser lab LCP <=2500ms and CLS <=0.1; these are not hosted WordPress CWV.

Local development fixture: before fix **FAIL** (print evidence loss); after fix **PASS 14/14 real Chromium fixture modes**, 6 lab LCP/CLS trials with CLS=0, and screenshots plus PDF. Fixture is synthetic and does not certify actual R113. A reviewed axe bundle was unavailable. Exact-head source tests, full landing real Chromium and WordPress/Assembler acceptance remain to run.

## Offer / funnel / blockers

Target = high-intent secondary educator viewing a future Grok Apollo long-form investigation. Existing free exercise is the only next step. A paid teacher casefile is **not verified as a sellable SKU**; seller, rights, price, delivery, refunds, and Payhip orders unknown. A source CTA and free activity are not paid orders or confirmed subscribers. #820 owns qualified-human session → event → confirmed merchant order → fees/refunds/net revenue and 7/30-day per-1000 analysis. No Grok video asset or campaign is confirmed.

All six NASA photograph-specific reuse assessments and the provisional S67-19766 identification remain open. The separate published WordPress Evidence Atlas page #2017 requires release-approval provenance; R113 is not installed there. STAGING HOLD: independent historical/media rights review, screen-reader/touch device, actual/WordPress browser and hosted performance QA, exact-head CI and founder release approval. No merge, production settings/content writes, emails or spending.
