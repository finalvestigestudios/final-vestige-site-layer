# Apollo 1 Evidence Atlas — R43 photographic ChronologyRail — STAGING / HOLD

Issue: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150  
Parent staging draft: PR #455 / `2ff0e1269a269a22d51d27915e7c43e31f5af43b`  
Scope: exclusively `experience2/evidence-atlas/`; no merge, WordPress install, CMS writes, images, paid services, or homepage edits.

## Implementation

1. **Evidence chronology, not accident reconstruction:** source-custody-driven 1966/1967/2017 ChronologyRail in both standalone Atlas and WordPress shortcode, with six native `<time datetime>` references and six native anchor targets. One 1967 record is month-only (`1967-01`) and **is never assigned a fictitious day or position within January**. Within-year entries retain custody ledger order, not asserted event sequence. Captions explicitly distinguish 2017 museum photographs from 1967 accident evidence.
2. **Meaningful interactions:** original source index and new chronology link to the same six NASA records; optional JS restores cards hidden by filtering before keyboard focus lands, preserves native fragment URLs, and restores hidden evidence on fragment navigation. No-JS still provides all dates, original-source links and six expanded-readability native disclosures.
3. **Tamper/failure response:** validation now requires exactly one ChronologyRail reference per custody ID, matching year cohorts and exact anchors. If a timeline destination or year is altered at runtime, JS enhancement stays hidden and all six records remain accessible.
4. **Integrity:** generated WordPress fragment SHA-256 pinned in PHP, `1a18e882c09a5437fd97dd10a2e464728c1f4c89ca5dc1ca95cd9ca3848ce22a`. The six-entry R37 custody crosswalk stays untouched (Git blob `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea`). No NASA binaries, invented geo pins, map edges, analytics or external network calls.

## Executed local checks (2026-11-01)

- `cd experience2/evidence-atlas && python -m unittest discover -s tests -p 'test*.py' -q`: **23/23 PASS** (includes eight new source/semantic/date-precision tests).
- `python -m unittest test_atlas.py -q`: **11/11 PASS**.
- `node --check atlas.js`: **PASS**; `php -l final-vestige-ex2-evidence-atlas.php`: **PASS**.
- `python tests/browser_regression_r42.py --output <dir>`: inherited prior Chromium **14/14 PASS**.
- `python tests/browser_regression_r43.py --output <dir>`: current Chromium **14/14 PASS**, 320, 360, 390, 768, 1024, 1440, 1920 widths × JS on/off; source jumps, filter recovery, fragment changes, keyboard disclosure, touch, reduced motion, no horizontal overflow, **3** tamper/print checks.
- Repeated Chromium screenshots at 390/1440 (JS/no-JS): **4/4 byte-identical**; QA JSON likewise identical. Fixed-timestamp deterministic ZIP builder included in this PR.

**Critical qualification:** Browser test input is the actual PHP-rendered shortcode built from the pinned R37 NASA source dataset, but Playwright uses `page.set_content`, **not an HTTP navigation or a running WordPress instance**. Explicit `page.goto` loopback tests in Chromium returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`, including no-proxy and resolver-rule attempts. These tests **do not** verify script loading, CSP, caching, hosted LCP/CLS/INP or WordPress/Assembler layout. No tested axe-core bundle is available locally; no axe certification is claimed. Manual screen-reader/Safari checks, rights clearances, independent QA, passing GitHub CI and founder visual signoff remain open.

## Reproduction

From a complete checkout containing the pinned custody crosswalk:

```sh
cd experience2/evidence-atlas
python -m unittest discover -s tests -p 'test*.py' -q
python -m unittest test_atlas.py -q
node --check atlas.js
php -l final-vestige-ex2-evidence-atlas.php
python tests/browser_regression_r42.py --output /tmp/apollo-r42-regression
python tests/browser_regression_r43.py --output /tmp/apollo-r43-qa
python tests/build_r43_review.py --qa /tmp/apollo-r43-qa --out /tmp/apollo-r43.zip
```

**Release gate: HOLD.** Do not merge or deploy. No changes to frozen homepage PR #49, homepage lead branches, or original Research Desk PR #158. Coordinate final assembly review only after an authentic isolated WordPress/Assembler environment and independent QA exist.
