# Apollo Experience 2.0 — R405 isolated no-JS Research Desk adapter

**DRAFT / HARD HOLD. No production or staging installation is authorized.** Branch stacks only on R404 PR #2728. Homepage PR #49, original Research Desk PR #158 and Grok/Praxxis TASK-008 are unchanged.

## Problem and correction

PR #158 renders the same fixed IDs when `[fv_ex2_research_desk]` is used multiple times; R404's optional client script repairs the second instance only when JavaScript runs. With JS disabled, both desks retain duplicate IDs. The R158 asset hook also discovers only a top-level shortcode in post content and may miss nested/reusable shortcode placement, after `wp_head` has already printed styles.

The proposed **distinct staging-only shortcode** `[fv_ex2_research_desk_r405]` server-namespaces all IDs/labels/ARIA references in successive instances, including when JavaScript is off. On a specifically approved staging page it enqueues one reviewed core CSS, one R404 corrective CSS and the R404 optional script *before* shortcode rendering, avoiding nested-block detection. It refuses to load alongside a previously enqueued original R158 script/style. It is **not** intended to be co-installed as a live second source desk.

`FV_EX2_R405_ENABLE` must be defined `true`; `FV_EX2_R405_STAGING_PAGE_ID` must be a positive numeric staging page ID; `wp_get_environment_type()` must equal `staging`; and the requested page must exactly match. Defaults reject all pages. The standalone source is not installed by this PR. All four dependency blobs are checked as Git objects against exact PR #158/R404 source, both at enqueue and render time. Missing/mutated sources produce only a link to the existing free investigation, never fabricated NASA content.

## Verified input Git blobs

| Package file | Exact source | Expected blob |
|---|---|---|
| `templates/ledger.html` | #158 six-record NASA ledger | `403d128c57b9bc82dac7c619651689070edef86c` |
| `assets/source-ledger.css` | #158 original CSS | `b8cf00afeceba115a9e9d19044fc11dcf2890cbe` |
| `assets/research-desk-resilient.js` | R404 replacement JS | `4f2d41dc1dc3d5e321b36a422cefd06a0ecd6760` |
| `assets/research-desk-resilient.css` | R404 CSS | `2c99fdeecd4d4245908c0f52f6a679c6f5d7718a` |

**Offline assembly** (needs source files from exact PR #158 and R404 checkouts):

```sh
python experience2/apollo-r405/qa/assemble.py --research-desk-dir /path/to/research-desk --r404-dir experience2/apollo-r404 --output /tmp/fv-apollo-r405-STAGING.zip
```

This code refuses to bundle unverified bytes; it builds fixed-timestamp, sorted, SHA-256-manifested ZIP. Building is not installation or deployment.

**Local executed tests:** `php qa/test_adapter.php` (18 native assertions), `python qa/test_browser.py` (5 genuine Chromium methods, seven screenshot contexts). Browser fixture HTML is output by **actual PHP** namespacing code but contains synthetic placeholder records, **not** the actual PR #158 HTML. Fixture confirms duplicate ID repair in no-JS, search, keyboard, touch and fail-open. It does not certify NASA claim correctness, the exact PR #158 template, installed WordPress, actual third-party rights, axe-core, real HTTP/CSP, independent screen readers, native browser 400% zoom or LCP/CLS.

## Release gates

1. Independent exact-commit hosted CI on both R405 and dependency refs; verify original PR #158 source checkout plus byte-complete dependency archive.
2. Explicit founder-approved staging page and plugin assembly; separate QD code review and permission to install only to staging.
3. Native WordPress/Assembler nested/reusable block rendering; detect old/new asset collision; verify source link/limitation custody, both no-JS and enhanced, at 320–1920px. Genuine axe-core, independent NVDA/VoiceOver, keyboard/touch, reduced motion, 400% native zoom, actual network, Core Web Vitals and CSP evidence.
4. Commercial pathway stays one nonintrusive **free investigation** link. Any educator dossier requires separately verified SKU, rights, checkout and merchant settlement; Grok owns videos, Praxxis owns creator QA, Claude owns production analytics. Do not infer paid orders from CTA clicks.
5. Founder and independent QD release approvals still mandatory. No WP content/settings, affiliate activation, social posts, emails, spending or production deploy authorized.
