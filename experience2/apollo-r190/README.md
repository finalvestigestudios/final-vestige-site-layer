# Apollo Experience 2.0 / R190 — JS-independent evidence delivery

**STAGING ONLY — do not install, merge, publish, email, or activate commerce.** Owner lane: Issue #150; conversion contract #820 and business charter #818. Additive child of R189 PR #1404 (be63ae4f62e9463cb6e6e8af069806d2441e4227); frozen homepage PR #49 and original Research Desk PR #158 untouched.

## Demonstrated defect and fix

R189's PHP required a readable, matching-SHA optional campaign-handoff.js *before rendering historical evidence*. A missing or modified file thus replaced all four chronology records, four evidence plates, eight disclosures and the archival source gallery with a single fallback link. The prior failure is reproduced by the PHP negative control in qa/test_r190.py.

R190 generates an isolated shortcode adapter [fv_ex2_apollo_atlas] that verifies source HTML and scoped CSS as **mandatory**. If those assets are missing/modified, the clean original investigation link remains. The optional campaign JS has a **separate** SHA-256 gate: when missing or tampered, no script is enqueued and the complete historical Atlas remains visible, with a clean URL on its free investigation CTA. A valid JS file still performs R189's allowlisted browser-local UTM handoff, without cookies, beacons, visitor identity, server-side dynamic HTML, merchant events or external image embeds. A stylesheet marked done is accepted alongside enqueued to avoid a needless fallback after the head stylesheet has printed.

The generator pins every byte of four R189 assets before use, preserving chronology, NASA documentary source destinations, rights caveats and the single unpaid CTA. It builds no speculative geospatial record.

## Reproduce (from the stacked R183–R189 source checkout)

    python3 experience2/apollo-r190/build_r190.py
    python3 -m unittest discover -s experience2/apollo-r190/qa -p 'test_*.py' -v
    python3 experience2/apollo-r190/qa/chromium_gate.py /tmp/apollo-r190-qa
    php -l experience2/apollo-r190/dist/fv-ex2-apollo-r190.php
    node --check experience2/apollo-r190/dist/assets/campaign-handoff.js

The Python/PHP controlled tests locally passed **11/11**, including R189 negative control, missing/tampered JS, missing CSS/HTML, style already printed and late-render fallback. Real Chromium on a synthetic-URL DOM fixture locally passed **13 contexts / 143 assertions**, twice, with **13/13 identical screenshot hashes** across runs. Tested 320–1920px, source drawers, keyboard, touch, reduced motion and forced colors. **These are not installed WordPress tests.** The Chromium sandbox blocked direct and localhost page.goto with ERR_BLOCKED_BY_ADMINISTRATOR; navigation/CDN-caching acceptance is **NOT TESTED**. Genuine axe-core, screen reader, external-media transfer, actual LCP/CLS and exact-head CI remain open. Browser visual receipts are packaged separately; the QA script and generator are committed here.

## Sources, buyer fit and release contract

Official technical source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — no conclusive specific ignition source. NASA commercial-use caution: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — no implied NASA endorsement; astronaut likeness restrictions apply. No commercial imagery certification.

Visitor action: **Read original investigation**. Proposed buyer: history teachers/educators reached from an evidence-focused Grok long-form Apollo 1 investigation, with Praxxis reviewing TASK-008. A paid educator dossier is **not an existing verified SKU** and must remain unlinked until product rights, pricing, checkout, delivery, fees/refunds and founder approval are verified. Commercial KPI is confirmed net revenue per 1,000 qualified human sessions by asset ID and 7/30-day cohort, NOT clicks or views. Currently not computable.

**Release HOLD** until true isolated WordPress/Assembler/Gutenberg staging, stylesheet/CSP and CDN tests, genuine axe and manual accessibility, exact-head CI, independent QD and founder approval. No WordPress/site settings writes, new trackers, social posts, affiliate activation, emails, expenditure or merge.
