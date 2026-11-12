# Apollo Evidence Atlas R319 — CDP accessibility-name release QA

**Staging-only / independent QA / NOT LIVE / HARD HOLD.** Child of [R318 draft PR #2246](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2246), engineering [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). No homepage PR #49, Research Desk PR #158, Grok TASK-008 or production changes. This sprint adds test coverage only: **it does not change the Apollo component, tracking or paid offer**.

## Exact source and reproducible command

Execute from the repository root with PHP, Node, Python + Playwright, and /usr/bin/chromium:

```sh
python experience2/apollo-r319/qa/ax_tree_gate.py
```

The gate fails closed on mismatched underlying tested R317 source Git blob IDs:
- PHP `9ff32d45b7e957e1d25724ab5fc55c467aaa55e2`
- JS `a3c858b51005495ebebb326086badc155c1b7e5a`

R319 actually executes **15/15 offline Chromium configurations**: widths 320, 390, 768, 1440 and 1920; JavaScript on/off and forced colors; reduced-motion and touch emulation on narrow widths. The source-controlled test reads genuine Chromium **DevTools Protocol Accessibility.getFullAXTree**, checking non-empty accessible names for links, native disclosure summaries and controls in both closed and expanded states, 14 accessible disclosure summaries across two Atlas instances, two uniquely named regions, and discoverable source links. It verifies visible, keyboard-focused fragment navigation into an originally collapsed Board authority record, no cross-instance CTA mutation, first-party campaign continuity with JS and stable fallback without JS. Cache query-variant PHP body equivalence, PHP syntax and JS syntax are also checked.

An **intentional destructive mutation** removes the CTA accessible name; the CDP audit detects it, and the CTA text is restored before screenshots. This guards against a test that always passes irrespective of bad markup. Browser screenshots and JSON receipts are produced under `experience2/apollo-r319/QA` by the local runner.

## Limits and safety

This is **not genuine axe-core** and is not independent NVDA, VoiceOver or WCAG certification. Chromium in this environment blocks native `file://` and HTTP(S) navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`, so the executable uses real Chromium `about:blank` + `set_content` and audited source-controlled PHP/CSS/JS. It does **not** prove WordPress/Assembler shortcode asset enqueue, Jetpack/CSP, CDN/cache behavior, destination navigation, production LCP/INP/CLS or a merchant purchase.

R318's offline LCP/CLS observations remain non-production and are not reused as R319 measurements. No image was embedded: NASA links and three documentary plus four contextual media records are preserved from pinned PHP. NASA's Board record does not conclusively establish the exact ignition source (https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). NASA's advertising rules prohibit implied endorsement and regulate astronaut likenesses (https://www.nasa.gov/nasa-brand-center/advertising-guidelines/); linked material is not a product media-rights grant.

## Business decision and release gates

Hypothesis only: **Grok Apollo long-form → source-linked Evidence Atlas → original NASA proof → free Apollo investigation → separately founder-approved, rights-cleared paid educational dossier**. The last sale step is deliberately NOT rendered, linked or instrumented. A payable Apollo-relevant SKU, real published Grok `asset_id`/link, first-party qualified human sessions, merchant-confirmed orders, commissions, fees and refunds are **unverified**. Net realized revenue per 1,000 qualified human sessions is **not computable**.

Remaining hard gates: genuine axe-core, independent screen-reader acceptance, browser HTTP/CSP and real new-tab navigation, installed WordPress/Assembler/Jetpack/CDN, p75 field LCP/CLS/INP, source/media rights and editorial/QD review, authenticated merchant offer, hosted CI on exact HEAD, founder production release authorization. No social posting, payment, email, WordPress or tracking writes authorized.
