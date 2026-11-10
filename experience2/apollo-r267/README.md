# Apollo R267 — post-article CTA large-text reflow (DRAFT / HARD HOLD)

**Scope:** additive, screen-only CSS for the **CLI-only R266 after-article review fixture**. This is not a WordPress plugin; it registers no hooks, does not activate commerce, and does not modify or load on public pages. Stack solely on Apollo R266 PR #1930 (base commit `cc2d62649101290274ac1477e4f38fbd7d2c8773`). Do not touch homepage PR #49 or independent Research Desk PR #158.

## Reproduced problem / exact behavior

With Chromium 144, original R224 Apollo HTML, R262 overlays and R266 preview, resizing the document **root font size** to 200% or 400% at narrow widths caused the existing `inline-flex` CTA to become unusually tall. At **320 CSS px**, 200% produced a **453.09 px** link and 400% **2644.94 px**, even though horizontal overflow was absent. At **390 CSS px**, 400% also produced **2644.94 px**. This is a *root-text-size stress test*, not proof of actual browser UI zoom or an installed WordPress defect.

`assets/postscript-reflow.css` is a narrow 480px-and-below screen-only override. It removes the decorative arrow when space is scarce, makes the action a full-width block, and uses fixed, bounded margins and padding while **preserving the user's enlarged text**. On the same fixture, measured heights become **151.56 px** (320/200%), **626.75 px** (320/400%) and **453.97 px** (390/400%). Do not cap font-size to make the screenshot look good. Desktop/tablet and original R266 print visibility are unchanged.

## Reproduction

A separately stored, source-sealed Apollo R238 fixture is required; it is not licensed or shipped as part of this code PR. With `fixture/sealed-r238` in place and Playwright Python + Chromium available, from repository root run:

```bash
python experience2/apollo-r267/qa/committed_smoke.py fixture/sealed-r238 experience2/apollo-r262 experience2/apollo-r266 experience2/apollo-r263/qa/wp-real-source-sequence.php experience2/apollo-r267/assets/postscript-reflow.css
```

Extended standalone QA and PNG screenshots are in the independently packaged evidence archive and should not be confused with the committed smoke. Both QA executions passed 33 cases each: 30 combinations (320/390/768/1440/1920 px × 100/200/400% root text size × JS on/off), forced-colors focus, print visibility and a negative control that removes the fix. Six cropped card screenshots matched across both runs. The 30-case committed smoke also passed. Tests check 55 original NASA links, 31 original fragments, one unchanged original investigation CTA, one optional distinct FV buying-guide CTA, no unexpected requests and no observed horizontal overflow. The additional CTA remains **unpublished review content**; passing tests is not merchant permission.

## Editorial, revenue and release boundaries

The editorial action is always **Apollo documentary → source-verified Atlas → free original Apollo investigation**. A **separate, optional, after-article** Mini Museum guide can be considered only after publisher eligibility, adjacent disclosure, merchant acceptance, rights, actual checkout and founder production approval. Specimens are **not Apollo mission artifacts**, nor is NASA the offer's sponsor. No NASA image/logo is copied into the commercial component; NASA advertising and brand guidelines still require separate rights review for future materials: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ and https://www.nasa.gov/nasa-brand-center/ . Grok retains content/distribution, Praxxis creator QA, Claude core site/analytics, founder release/commerce approval.

**Release gate: HARD HOLD.** Genuine provenance-verified axe-core NOT EXECUTED (unavailable in offline runtime); no independent screen-reader acceptance, actual browser UI zoom, WordPress/Assembler installation, public HTTP/CSP tests, real LCP/CLS, trusted qualified-human campaign sessions, verified order/fees/refunds, rights/merchant eligibility, independent QD or hosted CI. These are not inferred from screenshot or computed-style passes. Never merge/deploy or modify production WordPress without founder authorization. Issue #150 engineering record and #820 conversion priorities govern this draft.
