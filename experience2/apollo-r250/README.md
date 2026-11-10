# Apollo Experience 2.0 — R250 original-source acceptance (STAGING HOLD)

This independent browser gate targets the **actual, hash-sealed Apollo 1 R238 Atlas**, not the Research Desk's six-record synthetic fixture. It is deliberately additive, isolated from homepage PR #49 and Research Desk PR #158. No WordPress, media, commerce, analytics or creator changes.

## Exact immutable input

The previously published R242 QA archive `Apollo_R242_Computed_Contrast_Print_Custody_STAGING_HOLD.zip` contains `sealed-r238/`. The nested `sealed-r238/manifest.json` SHA-256 must equal:

`f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`

The script refuses altered manifest/files, invokes `wp-render-shim-r224.php` against the R224 adapter, and checks the generated fragment matches the exact source file.

## Reproduce

```bash
python3 -m pip install playwright beautifulsoup4
# PHP CLI and local Chromium are required. No network is contacted by the browser.
unzip -q Apollo_R242_Computed_Contrast_Print_Custody_STAGING_HOLD.zip 'sealed-r238/*' -d /tmp/apollo-source
python3 experience2/apollo-r250/qa/r250_real_atlas_gate.py --atlas /tmp/apollo-source/sealed-r238 --out /tmp/apollo-r250-acceptance
```

Set `PLAYWRIGHT_CHROMIUM_EXECUTABLE` if Chromium is not installed as `/usr/bin/chromium`. The output directory must not exist. The script runs widths 320, 390, 768, 1440, and 1920px with JavaScript on/off, native keyboard and touch opening, skip link, reduced-motion, explicit NASA action names from Chromium accessibility tree, CSS 200% zoom **approximation**, print-visible NASA URL index, closed/expanded disclosures, and offline screenshots. It rejects seven deliberate custody mutations: source identity, invented geographic location, unapproved checkout, duplicate CTA, missing print bibliography, injected script, and falsified chronology.

## Last local acceptance (2026-11-09 PT)

A local independently authored equivalent test against the same sealed R238 source and PHP shim passed **2 × 10 Chromium 144 contexts**, rejected all seven mutations, and produced 10/10 byte-identical screenshot pairs and matching deterministic receipt SHA-256 `921ab4f83c22a662dea4421353a1b7df3af7012b8f532487ff365388b9eb6d81`. The **committed runner is a separately composed equivalent**, not claimed byte-identical to that executed local test; hosted CI/commit-source acceptance still needed. Local browser LCP observer returned 96–108ms with no layout-shift entries, but these are not field Core Web Vitals. Screenshot evidence remains in the attached local artifact.

## Provenance, editorial safeguards and conversion

Original primary technical evidence: NASA Apollo 204 Review Board; separate NASA photographs S66-58038 (pre-fire), S67-15717 (pre-fire) and S67-21294 (aftermath). A probable electrical arc is not a conclusively identified ignition source; source citation is not promotional rights clearance. No invented pins, implied NASA endorsement, or simulated fire.

One existing next action: **free original Apollo 1 investigation**. Potential educator dossier and space-history affiliate offer are *hypotheses*, not paid CTAs. Follow `#820` and `#818`: require actual Grok asset ID and verified merchant approval; distinguish qualified visits, clicks, leads, confirmed orders, fees/refunds and realized net revenue. No revenue figures can be inferred from this browser run.

## Release gate

**NOT LIVE.** Still blocked on: executed committed-source check, genuine axe-core, independent screen reader, browser-interface zoom, installed WordPress/Assembler with exact CSP, hosted CI, independent site QA, field LCP/CLS, R198 ancestry reconciliation, commercial media-rights/merchant approval, founder production authorization. No production release, affiliate activation, social posting, emails or spending permitted by this PR.
