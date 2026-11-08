# Apollo 1 Experience Atlas — R207 source-custody capsule (staging only)

R207 adds a source custody capsule after the archival gallery and before the source-comparison exercise. Four dated NASA records identify their record type, source URL, what each establishes, and a distinct inference boundary. Native links work without JavaScript. Direct links have source-specific accessible names and aria-describedby associations with their limitations. The atlas retains its original free investigation CTA. No new paid CTA, photograph, geographic pin, collection script, vendor, form, email, or WordPress write is introduced.

NASA record identities and dates, independently checked November 7, 2026: S66-58038 (October 18, 1966); S67-15717 (January 3, 1967); Apollo 204 Review Board (accident January 27, 1967); S67-21294 (January 28, 1967). Source availability does not grant media rights. The Review Board regarded an electrical arc as the most probable initiating event but did not conclusively identify a specific ignition source. See NASA advertising guidelines: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

## Build and QA

Use the exact R206 generated dist from the accompanying evidence ZIP in the sibling folder apollo-r206/dist. Run python3 build_r207.py. The builder verifies all four R206 SHA-256 content pins and generates R207 PHP, HTML, CSS, a machine-readable custody-ledger.json and manifest.json. Run python3 qa/gate_r207.py OUTPUT_DIR with PHP, Python Playwright, BeautifulSoup and system Chromium installed. Builder and gate source blobs match independently executed local files.

Local results: PHP syntax, normal rendering, print rendering and fail-open late rendering passed; 8/8 deliberate negative mutations rejected. Chromium 144.0.7559.96 tested ten contexts in two independent runs: 320–1920px, keyboard, touch, no-JS, reduced motion, forced colors and 200% CSS zoom. There was no horizontal overflow, and 10/10 screenshots matched exactly across runs. Chromium could not navigate to localhost or an intercepted synthetic URL due to ERR_BLOCKED_BY_ADMINISTRATOR, so the browser used Playwright set_content. The QA independently verified local HTTP server response statuses through urllib. Do not claim that real WordPress staging or real URL navigation passed. Local LCP/CLS observations are not production CWV. Genuine axe-core was unavailable; NVDA and VoiceOver were not executed.

## Blocked release

Inherited R198 local builder blob 2e09257cbd0b32a93f2e7e034a84685d93ed93f5 differs from canonical GitHub blob 57ef73d5719662a1b3647536a0eace5fb65bac4a. Full GitHub ancestry rebuild, installed WordPress Assembler testing, true axe-core and screen-reader assessment, browser UI zoom, theme/CDN/CSP, hosted exact-head CI, independent QA and founder approval are outstanding. Source citation does not imply NASA endorsement or commercial photo rights.

## Business lane

Flagship audience: history educators and Apollo documentary viewers. Grok long-form video -> Apollo Atlas -> primary NASA sources -> original free investigation -> optional educator evidence dossier ONLY if a real rights-cleared and approved purchasable product is subsequently validated. No sale or lead is inferred. The KPI of verified net revenue per 1,000 qualified human sessions remains not computable until source asset IDs, merchant-confirmed orders, fees and refunds can be reconciled as required by #818/#820. No edits to frozen homepage PR #49, Research Desk PR #158, WordPress or Grok's distribution queue.