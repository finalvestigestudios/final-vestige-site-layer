# R381 · Curated Apollo Evidence Atlas — staging only

This independent Experience 2.0 component is stacked on R380, not on homepage PR #49 or Research Desk PR #158. **No activation, merge, deployment, CMS writes or commerce authorization.** It depends at runtime on R377's exact SHA-256-sealed six-record NASA source custody (`custody.json`). All source claims, limits, citations and image-catalog distinctions come from that reviewed model; there are no geography pins or unreviewed evidence edges.

## Delivered

- Three explicitly differentiated documentary phases: the January 27, 1967 ground test (four records), 1967 Review Board assessment (one), and December 1967–February 1968 deliberate engineering testing (one). These phase groupings are editorial navigation, **not invented timestamps for every sub-event**.
- Six `EvidencePlate`-style records, native `SourceDrawer` details with evidence role and limitations, a three-link `ChronologyRail`, optional accessible role filter/reset and clear `aria-live` result status.
- All evidence readable without JavaScript, no extra libraries, no external media, no geographic canvas and no automated visitor measurements. Filtering changes visibility only; printing restores all six citations even when filtered.
- Staging-only shortcode `[fv_apollo_curated_atlas_r381]`; only the explicitly approved R377 staging environment may register. Top-level singular-post stylesheet/script enqueue is restricted to pages with this exact shortcode and SHA-256-sealed CSS/JS files. Dynamic/reusable/template-part shortcode placement is **not certified** for this new component: do not install without dedicated installed WordPress/Assembler acceptance.
- Unverifiable source content fails closed to a plain free Apollo investigation link. Asset/enqueue failure retains source HTML and the editorial link (no-JS fail-open for meaning).

## Reproduce

From repository root, after installing PHP 7.4+ and `playwright` Python package with local Chromium and `pdftotext`:

```sh
php -l experience2/apollo-r381/atlas.php
php experience2/apollo-r381/qa/php_contract.php
python3 experience2/apollo-r381/qa/browser.py
python3 experience2/apollo-r381/qa/package.py
sha256sum experience2/apollo-r381/QA/Apollo_R381_Evidence.zip
```

The checked-in **test scripts**, not screenshots, constitute committed QA source. Generated screenshots, JSON results and PDF stay local in the deterministic evidence ZIP. Re-running `package.py` on unchanged bytes must produce the same SHA-256. Screenshots and lab metrics can differ across browsers and machines. The browser test uses Chromium `set_content` with PHP-rendered fixtures: **NOT actual HTTP/HTTPS or installed WordPress staging**. Axe-core, independent screen readers, production LCP/CLS/INP, native 400% zoom, staging HTTP/CSP and exact-HEAD hosted CI remain unverified.

## Source and media rights

- [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) — primary investigation; no conclusive identification of a single ignition spark.
- [NASA February 14, 2018 flammability account](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) — reports 102 **later intentional Command Module** ignitions, not the fatal January 1967 accident.
- Context records and their limits are preserved in the R377 sealed JSON. Research links do **not** grant rights to resell photographs or claim NASA affiliation. No NASA photographs, insignia or maps are reproduced.

## Single conversion hypothesis and gate

**High-intent audience:** history/social-studies educators drawn by an approved Grok Apollo documentary. **Pathway:** Grok source-linked long-form/Shorts (content, platform posts and approvals remain Grok/Praxxis-owned) → Atlas source proof → [free full investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → *only after verification*, an original rights-cleared educator dossier with independently approved merchant checkout. The Atlas has one contextual, nonintrusive free continuation CTA; no unapproved merchant link, lead form or email.

**Hypothesis:** visible distinctions between evidence and inference might increase qualified educator trust and onward purchase intent. **Not tested commercially.** No verified payable SKU, fulfilled checkout, attributable qualified-human session, confirmed lead, paid order, refund or net revenue. The KPI, net revenue per 1,000 qualified-human sessions across 7/30-day cohorts, is **not computable**. No interpretation of a CTA click or affiliate outbound as a paid sale.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Educator dossier, unverified | Purchase | No rights-cleared payable SKU/fulfillment | Withhold paid CTA | HOLD; no merchant proof | Founder / Claude |
| Grok Apollo documentary | Qualified landing | No published asset_id/approved UTM verified | Candidate source-first landing only | NOT MEASURED | Grok / Praxxis |
| Free Apollo investigation | Reader continuation | Evidence-role ambiguity | R381 curated Atlas + one CTA | 34/34 PHP, 175/175 Chromium fixture checks | Apollo QA |
| Paid orders | Realized net revenue | No settlement/refunds/fees or consented cohort data | Existing approved measurement only | NOT COMPUTABLE | Claude / Commerce |

**Release:** HARD HOLD pending approved staging, true axe-core, screen readers, HTTP/CSP, hosted CI, editorial rights + founder/QD approval. Cross-reference Issues #150, #820, charter #818. No modification to frozen homepage PR #49 or PR #158.
