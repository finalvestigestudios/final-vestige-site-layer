# Apollo R462: preserve full source custody when optional assets disappear

**Scope:** [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Isolated draft stacked on [R461 #3037](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3037). No homepage PR #49, Research Desk PR #158, Claude engineering, or Grok/Praxxis TASK-008 modifications.

## Reproduced failure and minimal fix

R461's gallery renderer dropped **all six NASA source-custody cards and the printable source references** when *either* optional CSS or JavaScript file was missing. This is not acceptable progressive enhancement: a missing enhancement should not erase the historical record.

R462 now distinguishes **unavailable** optional assets from **present but altered** assets:
- JS absent: all source cards, citations, evidence limitations, right-to-use holds, printable references and one free investigation CTA remain readable with pinned CSS; controls remain hidden.
- CSS absent: the full native, keyboard-operable HTML is emitted **without JavaScript**; the optional filtering controls remain hidden and links stay actionable.
- Both absent: full semantic HTML remains.
- An asset that exists but fails the pinned SHA-256 verification still triggers the existing fail-closed safe investigation link.
- WordPress shortcode registration remains gated to the explicitly configured staging environment and a single staging page ID.

## Reproduction and evidence

Source-controlled commands from this directory:

    php -l apollo_rights_gallery.php
    python qa/test_contract.py
    python qa/r462_asset_fallback_contract.py
    python qa/browser_qa.py
    python qa/r459_print_qa.py
    python qa/r460_print_custody_qa.py
    python qa/r461_pdf_link_custody_qa.py

An additional extended Playwright/PyMuPDF regression, including independent CSS-absent and JS-absent scenarios, 320–1920px, 20 reproducible screenshots and local test receipts, is included in the accompanying R462 QA ZIP. This is an **offline PHP-rendered local browser fixture**, not actual hosted WordPress navigation. Hosted axe-core, navigated LCP/CLS, screen-reader acceptance and field CWV remain HOLD_NOT_RUN. Do not represent local performance evidence as production performance.

## Editorial and commercial release gates

The six entries are **source index cards, not image grants**. NASA's [Apollo 204 review board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) did not conclusively establish one ignition source. [NASA advertising guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) prohibits implied agency endorsement and adds restrictions around identifiers and astronaut likenesses.

**Unresolved**: source-to-ID mapping S67-19766 and independently unconfirmed NASA Images catalogue link KSC-20170124-PH_KLS01_0129. Do not treat either as accepted archive or merchandise rights. No NASA imagery or invented Atlas pins are embedded.

**One intent-aligned visitor path:** Grok's independently verified Apollo documentary (asset_id not yet confirmed) → existing Apollo Evidence Atlas → printed source-custody sheet → [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → only after independent review and founder authorization, a rights-cleared, genuinely sellable original educator resource. No paid CTA at present.

**Commercial gate:** SKU, price, checkout acceptance, fulfillment, asset_id/UTM campaign, qualified-human sessions, paid orders, refunds, fees and realized net revenue are **not verified**. Do not equate source downloads, clicks or leads with sales. Net revenue per 1,000 qualified-human sessions and 7/30-day cohorts cannot be computed.

**Release HARD HOLD:** independent staging/assistive-tech/axe/LCP/CLS QA, media/source acceptance, exact-head CI/QD and founder approval. No merge, deployment, WP write, social publication, analytics installation, affiliate/merchant activation, signup, email or spending.
