# R176 — Research Desk catalog notice: semantic fallback + direct acceptance harness

Staging-only; **not installed or approved for release**. Part of issues #150, #818, #820. It does not touch homepage PR #49, Research Desk PR #158, WordPress, analytics, social distribution, or merchant checkout.

## Defect and exact correction

R175 correctly qualified an unconfirmed photo ID, but its no-CSS DOM joins "photograph" directly to "Reported": the span has no intervening text delimiter. Readers whose custom CSS is missing, blocked or disabled can encounter a concatenated catalog label. This R176 follow-up uses a native paragraph and deliberate punctuation, retains NASA's **uncertainty** without claiming the catalog ID is false, and avoids a hidden or JS-only explanation. The catalog note is *not* an advertisement or an assertion of commercial media rights.

Run from checkout (branch with R174 and R175 siblings):

    python experience2/apollo-r176/catalog_semantics.py experience2/apollo-r174/research-desk-provenance-candidate-UNPUBLISHED.html /tmp/fv-apollo-r176-UNPUBLISHED.html
    python -m unittest discover -s experience2/apollo-r176 -p 'test_*.py' -v
    python experience2/apollo-r176/browser_acceptance.py --fixture /tmp/fv-apollo-r176-UNPUBLISHED.html --out /tmp/fv-r176-browser

The transform first calls R175 from the pinned actual R174 Git blob b23879150024b3b667679ff4dd7faae1e37cfc07. It asserts exactly six provenance entries, fourteen original links, reversibility, and zero script, form, media, or commercial changes. Any drift is a hard hold. It only rewrites the existing R175 notice; the rest of the story is identical.

Browser acceptance works on the source-derived **offline fixture or generated source candidate**, not an installed WordPress theme. The resulting JSON distinguishes the two. It records six viewport screenshots, focus/keyboard/activation tests, no-JS and no-CSS text, forced-colors, reduced-motion, page CLS and LCP observations. axe-core runs only if a supplied local JS bundle is authentic (--axe path); absent that bundle the receipt explicitly marks axe=NOT_RUN and release remains held. No CDN or network dependencies. Compare screenshot SHA-256 on repeat runs; do not claim on-site performance from file fixtures.

## Governed release gates

Installed WordPress staging acceptance remains outstanding, including native shortcode/Gutenberg compatibility, CSP, real NASA image delivery, screen-reader sampling, genuine axe-core, actual LCP/CLS and external links. No unrelated commerce is inserted. Existing visitor CTA **Read original investigation** remains unchanged. Any later educator casefile CTA requires a real rights-cleared SKU, confirmed checkout and founder approval; paid conversions must be merchant-reported with fees/refunds accounted for. Grok retains YouTube/Shorts ownership; Praxxis handles external content QA.
