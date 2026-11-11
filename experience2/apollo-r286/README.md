# Apollo R286 — bounded WordPress synced-pattern preflight

**Staging only · HARD HOLD · Parent:** R285 draft PR #2047 at f40ef90ac7961248542626b7c09914327c0a6369. Scope: isolated Apollo Evidence Atlas shortcode. No homepage PR #49, Research Desk PR #158, live WordPress, analytics, social or commercial changes.

## Reproduced defect and implementation

R285 limited each synced-block list to 128 siblings and each body to 250,000 bytes, but not total work across nested branches. A 10-group/100-reference offline fixture located the shortcode after **80 get_post reads** and incorrectly approved pre-head work. Another fixture could scan several individually valid near-250KB block bodies. These are reproduced code-path risks, not observed production failures.

R286 shares one traversal budget across all branches: **maximum 32 block database reads, 256 parsed nodes, and 500,000 cumulative bytes**. Existing 8-level, 128-sibling, 128-unique-ref and 250KB-per-body checks remain. Budget exhaustion stops optional pre-head asset discovery; the original post-render stylesheet fallback and full source-linked evidence markup remain. Valid two-hop and within-budget 20th-reference fixtures still work. No NASA historical statements, official links, source hashes, commercial CTAs or styles change.

## Reproduction

From the extracted repository-style root, execute:

- php experience2/apollo-r285/verify_preflight.php
- php experience2/apollo-r286/verify_bounded_preflight.php
- python experience2/apollo-r281/qa/committed_gate.py QA/Browser
- python experience2/apollo-r285/verify_print_export.py QA/Print
- python experience2/apollo-r286/build_archive.py QA bundle.zip

Results: inherited R285 PHP simulation 14/14; R286 bounded-fanout/aggregate-byte/node/fallback simulation 6/6; R285 original code fails the new negative control, with 80 reads. Chromium offline actual-component suite 10/10 JS/no-JS contexts at 320–1920px, source round-trip keyboard checks, touch/reduced-motion, forced-colors, zoom-like font scaling, overflow and print assertions. Actual Chromium PDFs 2/2, NASA and free-investigation destination annotations/text 8/8. Two deterministic archives plus fresh extraction and independent rebuild must yield identical checksums. These are local tests, not production acceptance.

Browser file:// navigation was refused with net::ERR_BLOCKED_BY_ADMINISTRATOR. Genuine axe-core dependency unavailable. Installed WordPress/Assembler, navigated HTTP/CSP, independent screen readers, true browser-interface zoom and field LCP/CLS/INP remain unverified; do not label offline fixture results as field CWV or accessibility certification.

## Sources and commercialization

Primary official report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA media/endorsement restrictions: https://www.nasa.gov/nasa-brand-center/ . The Board did not conclusively identify a single ignition source. No new NASA photos, badges, astronaut likenesses, geographic pins, or commercial representations.

Controlled path: **verified Grok Apollo asset (not authenticated) → Evidence Atlas NASA source custody → free investigation → optional separately disclosed product guide (not activated) → independently verified settled purchase less fees/refunds.** Existing investigation: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . Mini Museum merchant eligibility and buyer fit remain unverified. Net realized revenue per 1,000 qualified human sessions is not computable. Grok owns scripts/social; Praxxis creator QA; Claude website/analytics; founder approves production and spend.

No deployment, paid service, WordPress write, merchant activation, emails or social posting. CI, WordPress, genuine axe, rights/editorial review, browser HTTP/CSP, authenticated merchant and founder release gates: **HARD HOLD**.
