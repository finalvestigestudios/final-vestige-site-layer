# Apollo R346 — printed source-custody parity (draft, NOT LIVE)

**Issues:** [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), commercial [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) / charter #818. Base is R345 draft PR #2399 at cc372f0154068ec2b693009fee790978a060af82.

## Defect and correction

R345's three claim-led EvidencePlates print their Board findings and evidence limitations, but print CSS hides each closed custody disclosure without a paper equivalent. The generated archival PDF therefore omits each plate's original-source classification and custody, despite the visible on-screen source links. The chronology had already been repaired for this class of failure in R344.

Each R345 plate now includes a **hidden screen / printed paper** source mirror sourced from the same in-memory record. Print CSS hides the interactive disclosure and its screen source link, displays the print mirror, and retains one NASA link for each finding. The mirror explicitly labels the original NASA-hosted 1967 Board source and editorial paraphrase. It is absent from the ordinary accessibility tree and never requires JavaScript. No claim changes, images, map pins, new URLs, trackers, merchants, offers, permissions or WordPress writes.

## Reproduction / results

Requirements: PHP 7.4+, Python, Playwright, PyMuPDF, installed local Chromium.

    php -l experience2/apollo-r345/evidence-plate.php
    python experience2/apollo-r346/qa/print_source_contract.py
    python experience2/apollo-r345/qa/acceptance.py

Executed locally on 2026-11-13: 5 no-JS Chromium widths (320/390/768/1440/1920) and 5 native printed PDFs pass the source parity contract. Extended 10 Chromium contexts (including 400% root text, keyboard disclosure Enter/Space, touch, forced colors, reduced motion) and 2 additional native PDFs pass. PDFs retain 3 original-Board plate labels, 5 original Board chronology labels and 1 later NASA history label; 17+ clickable NASA PDF annotations and exactly 1 free editorial continuation. Tests are local PHP-rendered fixtures, not installed WordPress. Local screenshot and manifest receipt are packaged separately. Chromium PDF bytes can vary between runs.

The attempt to use a native loopback HTTP/CSP test was blocked by the browser's network administrator policy: net::ERR_BLOCKED_BY_ADMINISTRATOR. Accordingly **native HTTP/CSP NOT TESTED**, rather than passing by inference. Genuine axe-core, screen readers, Firefox/WebKit, installed WordPress/Assembler/CDN, real production CWV and hosted exact-HEAD CI remain **NOT VERIFIED**.

## Conversion / release gate

Controlled journey remains Grok Apollo long-form → this NASA source-led evidence experience → existing free Apollo investigation → a **separately approved and independently payable Apollo-specific educational offer**. No payable rights-cleared SKU, merchant acceptance, authenticated published Grok asset ID or 7-/30-day paid conversion/net-revenue records were established here. Purchase CTA **HOLD**; no inferred sales.

**Hard hold / no merge or deployment.** No homepage PR #49, Research Desk owner PR #158, Grok/Praxxis TASK-008 queue, live WordPress, analytics, merchant or external services altered. Founder and QD release approval remains necessary.

## R346 additional gallery finding

During native-PDF visual review, the four contextual NASA accession cards also omitted their closed provenance disclosures in print. R346 extends the same screen-hidden/print-visible mirror approach to **four gallery records**, retaining each documentary limitation and explicit image/likeness/branding rights-review warning. The gallery still links to NASA originals and embeds no photos. Its interactive source disclosure is suppressed only in print, where the static rights/limits mirror replaces it. The source-controlled print gate now additionally asserts 4/4 photographic evidence limits and 4/4 rights warnings in actual Chromium-generated PDFs at five viewport widths.
