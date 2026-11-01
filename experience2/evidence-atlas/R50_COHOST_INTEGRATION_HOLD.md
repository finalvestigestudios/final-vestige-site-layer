# Apollo R50 — custody-locked WordPress Research Suite (DRAFT / RELEASE HOLD)

**Scope.** This is an isolated, staging-only WordPress adapter for co-hosting the existing, unmodified Research Desk PR #158 and Evidence Atlas R49. Place `integration/fv-ex2-apollo-suite.php` with `integration/apollo-suite.css` in a **separate staging plugin folder** with that PHP file as the plugin entry point, activate both underlying plugins first, and use `[fv_ex2_apollo_suite]` only in private staging. **No WordPress install or activation was performed by this sprint.** Do not replace the Research Desk's PR #158 source or the production homepage.

**Integrity.** Runtime refuses to render the integrated view unless the four independent original PR #158 files match exact Git *blob* IDs: plugin `d1879a90101b5475990132369178f42743f4b57c`, HTML `403d128c57b9bc82dac7c619651689070edef86c`, CSS `b8cf00afeceba115a9e9d19044fc11dcf2890cbe`, JS `32e757cc4dc8708397ff65ac21e89dd319781d78`. The independent Atlas shortcode retains its own compiled HTML hash gate. The combined wrapper requires exactly six source records in each component and exactly one component root. A missing or drifted component falls back to the original Apollo 1 article; no half-populated presentation appears. Source verifiers guard accidental drift, not hostile third-party plugins.

**Nested block asset coverage.** The original PR #158 adapter only enqueues CSS/JS when `[fv_ex2_research_desk]` appears directly inside a singular post. A wrapper can hide that original shortcode from this check. R50 directly enqueues the original, pinned Desk CSS/JS using WordPress' standard enqueue API; the unchanged Atlas shortcode enqueues its own registered assets. A pre-enqueue hook handles top-level suite shortcodes. Rendering from reusable blocks/template parts remains an **unverified late-enqueue / potential FOUC risk** requiring a genuine WordPress/Assembler test.

**No-JS/accessibility.** The suite header uses native `#fv-ex2-ledger-apollo1-title` and `#fva-title` navigation, so both six-record collections and their citations remain readable without JavaScript; the existing Atlas optional cross-links activate only after its NASA identity checks. Suite controls are 44px or taller, responsive, focus-visible and print-aware; no external images, external services, storage, fabricated geo pins, speculative source relationships or new licenses.

**Actually executed in local component sandbox:**

- `php -l integration/fv-ex2-apollo-suite.php` PASS.
- `python test_atlas.py` 11/11 PASS.
- `python -m unittest discover -s tests -p 'test_*.py' -q` 71/71 PASS (includes six new PHP suite tests).
- `node --check atlas.js` PASS.
- `python tests/browser_r50_suite.py --output <path>` Chromium 16/16 across 320, 360, 390, 428, 768, 1024, 1440, 1920px in JS-on/off modes, reduced-motion emulation and mobile touch. Tests PHP-assembled suite markup using **actual PHP-rendered Atlas** and **synthetic-contract Research Desk markup with exact PR #158 JS**. Native source-nav and reciprocal jump from filtered records, keyboard focus, all static records, no external requests or horizontal overflow verified. Screenshots at 390px and 1440px repeated byte-identically.
- Controlled, browser `set_content` LCP 84–120ms and observed CLS 0. These are **not hosted, WordPress, or field CWV measurements**.

**Still NOT EXECUTED:** original PR #158 HTML+CSS in browser; installed WordPress/Assembler rendering; genuine HTTP navigation (Chromium localhost `ERR_BLOCKED_BY_ADMINISTRATOR`); axe-core (no verified bundle available); Safari/VoiceOver/NVDA; live/hosted LCP/INP/CLS; complete six individual NASA photograph-rights decisions; exact-head hosted CI; independent QD and founder approval. Staging may show text-only NASA source links; no photograph bytes may be embedded before rights signoff.

**Next physical acceptance:** in a private, network-enabled local WordPress or WordPress Playground install, install the two exact source-pinned plugins and this suite adapter, test both top-level and reusable/template-part shortcode rendering, prove assets load once with no FOUC, and collect authentic axe/Lighthouse/browser screenshots. Keep production and homepage lead PRs untouched.
