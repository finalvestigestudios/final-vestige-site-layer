# Apollo Experience 2.0 — R406 Research Desk identity and fragment custody

**DRAFT / HARD HOLD. This directory is NOT a WordPress installation or production release.**

## Source-anchored defect
- PR #158 ships the original six-record Apollo Research Desk. Its HTML uses fixed IDs.
- R405 draft PR #2729 server-namespaces second and later instances so no-JS works, but enqueues R404 JavaScript from PR #2728. That script **also renames every ID in the second instance**. A second-instance fragment URL published from the server no longer resolves after JS runs. The local Chromium regression proves this exact original R404 script changes the server-generated ID.
- R406 introduces a distinct `[fv_ex2_research_desk_r406]` staging shortcode which namespaces **every** instance, including the first, and a compatible optional JS that **never mutates server-rendered IDs**. It preserves native details, independent per-desk search, Escape and clear controls, nested fragment visibility/focus, missing-record fail-open, and cross-component duplicate-ID fail-open. This is not a modification of original PR #158, R404, R405 or homepage #49.

## Staging guard
`FV_EX2_R406_ENABLE=true` and a positive `FV_EX2_R406_STAGING_PAGE_ID` and `wp_get_environment_type()='staging'` must all be true on that exact singular page. Defaults OFF; no CMS or settings writes. Reject legacy R158/R405 competing assets. Before enqueue and on shortcode rendering, require four byte-exact Git-blob checks:

| bundled dependency | source PR | immutable blob |
|---|---|---|
| `templates/ledger.html` | #158 | `403d128c57b9bc82dac7c619651689070edef86c` |
| `assets/source-ledger.css` | #158 | `b8cf00afeceba115a9e9d19044fc11dcf2890cbe` |
| `assets/research-desk-resilient.css` | #2728 | `2c99fdeecd4d4245908c0f52f6a679c6f5d7718a` |
| `assets/research-desk-r406.js` | this draft | `a925ef792a4f894208f88d8edb3a7b4620b3028f` |

The standalone `qa/assemble.py` creates a deterministic, MANIFEST-pinned install *candidate* only if every original input is present and byte-exact. Do not copy synthetic test text into the actual NASA package. Failure returns only a direct link to the existing free Apollo investigation.

## Executed tests and explicit limitations
- PHP 8.4 `php -l` syntax PASS; **18/18** native PHP assertions PASS.
- Python **4/4** source-package regressions PASS including mutated and missing original inputs rejected.
- Actual local Playwright Chromium **7/7** test methods PASS, including reproduced old double-renaming bug, corrected immutable hash targets, search and Escape, fragment recovery, native details, duplicate IDs, missing-card fail-open, no JS, responsive viewports 320/390/768/1440/1920, touch, reduced motion and root-font 4x. Eight deterministic fixture screenshots; all 0px horizontal overflow in the fixture. Test HTML uses **synthetic records**, not the original NASA copy.
- Local Chromium navigation to `127.0.0.1` was `ERR_BLOCKED_BY_ADMINISTRATOR`; the runner transparently fell back to `set_content` with exact source JS and server-generated PHP fixture IDs. **No real HTTP/CSP acceptance**, no trustworthy LCP/CLS, no genuine axe-core, no screen-reader acceptance, no native browser 400% zoom, no installed WordPress/Assembler staging, no source/rights signoff, no hosted exact-HEAD CI.
- The six-record NASA source-ledger URL/claim contract and its limited primary-source status originate in unmodified PR #158, not in generated fixture claims. NASA's Apollo 204 Review Board report leaves the specific ignition origin undetermined, despite a probable electrical arc. Do not promote later fire tests into evidence of the initial ignition. No NASA image or logo is bundled in this candidate.

## Conversion decision / owners
**Grok-owned published Apollo documentary (published asset ID NOT AUTHENTICATED)** → six-record, source-backed Research Desk → **one contextual free CTA**: [Read the existing Apollo 1 investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → optional educator dossier only if founder verifies real sellable rights-cleared SKU, checkout, license, delivery and fees. No purchase or sign-up CTA has been activated.

**OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER:**
- Educator dossier → paid order → no verified saleable SKU/checkout → HOLD paid CTA → not tested → Founder/Claude.
- Grok Apollo documentary → qualified landing → no verified posted Apollo asset_id/UTM → no claimed attribution → unknown → Grok/Praxxis.
- Research Desk → free investigation → client renames server source IDs → R406 server-ID-preserving search and fragment recovery → local Chromium PASS, staging HOLD → Apollo QA/QD.
- Confirmed sales → net revenue/1,000 qualified humans → no confirmed orders, fees, refunds or 7/30-day qualified cohorts → no metric claimed → Commerce/Claude.

No social posting, creator assignment, WordPress write, live deployment, analytics installation, email, merchant activation, affiliate change, payment or spending. Founder and independent QD retain release authority. See #150, #820, charter #818; Grok/Praxxis TASK-008 remains independently owned.
