# Apollo Experience 2.0 — R201 | Editorial trust and conversion boundary

**DRAFT / STAGING HOLD.** Parent: R200 PR #1490, exact commit `0769224d8c1ba6499a4546d79c455ce90ef477ff`. This is additive work under `experience2/apollo-r201/`; it does not edit homepage PR #49, Research Desk PR #158, or production WordPress.

## Reproducible defect and change

The R200 *reader-facing* Apollo footer included internal status such as "An Apollo educator dossier is a proposed product" and "No purchase, signup or affiliate conversion is claimed here"; the gallery described itself as an "unpublished prototype." Those honest **internal QA statements** are poor editorial copy for an audience arriving from a history video. They confuse the offer and can reduce confidence precisely where a visitor is deciding whether to continue.

R201 keeps these commercial unknowns in the generated **internal** `conversion-validation.json`, while giving readers a truthful single free action: **Read original investigation**. It adds one modest original educator/researcher exercise: compare a NASA Review Board finding with a dated NASA photograph and state what each cannot establish. The NASA nonendorsement line stays visible; the gallery now describes original archive destinations rather than staging status.

No speculative map, NASA image embed, script addition, extra CTA, tracking, fake product, affiliate offer or WordPress write. The four timeline items, eight native source disclosures, gallery records, source rights and campaign-handoff code are inherited unchanged.

## Exact build and QA

```sh
python -I experience2/apollo-r201/build_r201.py
php -l experience2/apollo-r201/dist/fv-ex2-apollo-r201.php
python -I experience2/apollo-r201/qa/gate_r201.py /tmp/apollo-r201-A
python -I experience2/apollo-r201/qa/gate_r201.py /tmp/apollo-r201-B
```

Requires Python 3, BeautifulSoup, Playwright, PHP and local Chromium `/usr/bin/chromium`. Generator recursively rebuilds inherited R200 and pins template/CSS hashes in a staging-only WordPress adapter. Tests use PHP-generated shortcode output in a **mock WordPress-function shim** and actual local Chromium with 12 contexts (320–1920 px), keyboard/touch focus journeys, native details, no-JS, reduced motion, forced colors, 200% *CSS zoom simulation*, CDP accessibility tree, screenshot hashing and local PerformanceObserver LCP/CLS. Four controlled UTM passthrough cases exercise native JS in the browser using a simulated about:blank query. Eight adversarial source/commerce mutations must fail.

**Limits:** This is *not* an installed WordPress test, real 200% browser zoom, genuine axe-core, NVDA/VoiceOver, external navigation, production Core Web Vitals or hosted exact-head CI. Do not invent verification.

## Historical evidence and image rights

- [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) — the Board did not conclusively identify one ignition source.
- [NASA Apollo 1 photograph catalog](https://www.nasa.gov/gallery/apollo-1/) — dated photographs are separate from flight instrument findings and do not depict the initiating spark.
- [NASA advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) — source citation does not authorize NASA endorsements, insignia or commercial use of astronaut likenesses.

No new image use or commercial rights clearance is claimed.

## Conversion contract and gates

**Audience/offer:** Source-conscious Apollo 1 documentary viewers, especially teachers and history researchers → free investigation → *hypothetical* original educator evidence dossier. There is **no verified sellable Apollo SKU**; preserve free source access and defer any sales CTA. Grok owns video/asset ID and publishing; Praxxis owns independent creative review; Claude owns production integration; founder controls releases and commercial activation.

Record `asset_id` + allowed `utm_campaign` → qualified human sessions → landing → CTA → confirmed leads (if observable) → merchant-confirmed paid orders → refunds/fees → realized net revenue. No paid sale is inferred from any outbound click. Seven- and 30-day net revenue per 1,000 qualified human sessions remains **NOT COMPUTABLE** without orders and a valid denominator. `conversion-validation.json` intentionally uses null values, not fabricated zero sales.

**Release hold:** install and inspect in genuine staging with the current WordPress theme and CMS lifecycle; run axe-core and assistive technology; verify actual links/CDN/CSP, CI and independent QD; verify a relevant rights-cleared product, checkout, approved disclosure and merchant reports; obtain founder approval before any merge/deploy/post/email/spend.

Coordination: [Apollo issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) · [attribution issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) · [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).
