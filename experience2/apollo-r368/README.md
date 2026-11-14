# Apollo R368: sealed chronology 400% text reflow (DRAFT / HARD HOLD)

Scope: Issue #150, conversion coordination Issue #820. Based on R367 draft PR #2517, HEAD 2bad286c2a80c28cb5b458ac5b12e98f51129c94. Isolated to experience2/apollo-r368/. Never modify homepage PR #49, Research Desk PR #158 or Grok/Praxxis TASK-008. No deployment, installation, merchant activation, posting, tracking, email or spending authorized.

## Defect fixed

In R367, Chromium at 320 CSS pixels and 64px root font gave the first evidence paragraph only 46px of inline width: inherited rem-based gutters consumed nearly the entire viewport. R368 adds scoped CSS with small pixel-capped mobile gutters, preserving the reader's font scale and the entire source-backed chronology. Actual Chromium fixture measured 254px paragraph width after the fix (+208px), no horizontal document overflow. This is not a WCAG certification or a real 400% browser-zoom test.

The opt-in [fv_apollo_chronology_r368] shortcode requires R367's four-row sealed source custody. Without R367 it displays a plain HTML notice and one free investigation link; it does not fall back to R365's unsealed renderer. The separate WordPress enqueue hook orders the R367 sequence stylesheet and new R368 reflow stylesheet after the R365 core style. This registration was tested with read-only WP API stubs, not an installed theme.

## Reproduce

At checkout root, with PHP 8.4, Python Playwright, system Chromium and PyMuPDF:

- php -l experience2/apollo-r368/reflow-adapter.php
- php experience2/apollo-r368/qa/contract.php
- python experience2/apollo-r368/qa/browser_reflow.py
- python experience2/apollo-r368/qa/build_evidence.py

92 PHP assertions passed. Eleven real local Playwright Chromium set_content fixtures passed (320 no-JS; 390 touch; 768 tablet; 1440 keyboard; 1920 wide; reduced motion; forced colors; 320/390 4× root font; tampered source and reordered sequence). Source citations are withheld on tampering; source drawers open by keyboard and touch; one free editorial CTA remains; native Chromium print retained three distinct NASA URLs across four pages. LCP/CLS where observable are synthetic local data only, not field CWV. The builder freezes source/test files and captures into a repeatable ZIP; re-capturing screenshots/PDF may change bytes.

## Source, rights, conversion, releases

Original 1967 Apollo 204 Review Board source and 2018 NASA retrospective experiments are labeled separately. Neither an exact ignition source nor photo reuse rights are claimed. No NASA images, unreviewed geographic pins, tracking, checkout or paid link. The free Apollo route remains https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . A Grok Apollo documentary asset_id, qualified traffic, an Apollo-specific rights-cleared payable kit and settled revenue remain unverified.

HARD HOLD: installed WordPress/Assembler theme lifecycle and asset URLs; real HTTP/CSP enforcement; genuine axe-core (unavailable locally; npm DNS EAI_AGAIN), screen readers, Firefox/WebKit and real browser zoom; exact-head CI, rights, checkout, founder/QD release signoff. Grok owns social production/distribution; Praxxis creator QA; Claude production site and analytics; Founder commerce/release. Never infer paid sales from clicks.