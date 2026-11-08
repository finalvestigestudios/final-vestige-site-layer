# Apollo Evidence Atlas R209 — source-comparison classroom bridge (DRAFT / STAGING HOLD)

The R209 builder produces a deliberately isolated, verifiable extension of the R208 evidence atlas. The **source-controlled** `lesson.html` and `lesson.css` introduce an original no-JavaScript, print-friendly comparative reading between the NASA Apollo 204 Review Board report (completed April 1967, discussing January 27 fire) and dated NASA image S67-21294 (January 28 aftermath). The report did not conclusively identify a specific ignition source. The photograph cannot show the spark. Native `<details>` provides an optional answer rubric with keyboard/touch/no-JS support.

**Reproduce:** obtain the exact R208 `dist/` from the prior evidence package and set `FV_APOLLO_R208_DIST` to its absolute directory. The builder hard-fails on absent/changed R208 manifest or assets. Run:

```sh
FV_APOLLO_R208_DIST=/path/to/r208/dist python3 experience2/apollo-r209/build_r209.py
php -l experience2/apollo-r209/dist/fv-ex2-apollo-r209.php
python3 experience2/apollo-r209/qa/gate_r209.py /tmp/apollo-r209-QA
```

No WordPress installation, merge, live deployment, photo download, geo pin, external tracker, affiliate activation, paid SKU, invented order or newsletter change occurs. Existing Apollo source navigation, native disclosures, rights boundaries, UTM-preserving optional JS, and the single **free original investigation** CTA remain.

**Release barriers:** This is based on a SHA-256-pinned R208 **staging output snapshot**, NOT canonical upstream reconstructed ancestry. The R198 GitHub/source-archive mismatch remains. Chromium fixture is real browser but `set_content` rather than installed WP. Genuine axe-core (unavailable here), screen-reader/actual zoom, theme/CDN/CSP, hosted exact-head CI, independent QA and founder approval are not satisfied.

**Commercial hypothesis:** a free source-analysis sample may help qualified Apollo viewers and educators trust the free original investigation and validate demand for an original rights-cleared educator dossier. No Apollo paid product, confirmed merchant purchase, lead or realized revenue is verified; commercial metrics are **not computable**. Grok owns creator content/links/asset IDs, Praxxis owns external creator QA, Claude owns website production engineering; this repo lane only stages evidence UI and browser QA. See #150, #820, charter #818 and TASK-008. No changes to homepage PR #49 or Research Desk PR #158.
