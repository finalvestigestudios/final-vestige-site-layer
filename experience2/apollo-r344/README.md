# Apollo R344 — native print source-custody repair (research only)

**Status:** built on isolated branch, draft-only, **not live**. Stack on #2388/R343. Never merge, deploy, alter homepage PR #49 or edit Research Desk PR #158; founder approval still required.

## Reproduced defect

The R339 chronological evidence includes six native <details> source drawers. In the prior print CSS, their children were forced to \`display:block\` even when <details> was closed. **Chromium-generated PDF** still suppressed their textual contents: 0 "Evidence limit" rows, 0 "Record custody" rows, 0 NASA outbound-source annotations. A printout appeared to document the incident while silently losing its provenance.

## Fix

The actual PHP renderer adds a \`hidden\` print-source sibling to each of the six chronology events, reusing the same escaped documentary source, custody and uncertainty text. Native collapsed details and direct source links remain unchanged for screen and no-JavaScript use. Print CSS alone reveals the six ledgers, hides the closed interactive details, and uses legible black-on-white text instead of inherited pale-on-white paragraph text. A printed dossier now maintains independently readable source provenance without JavaScript or external services.

No image copied, invented geo pin, affiliate/campaign script, merchant CTA, user data, or WordPress setting introduced. Exactly one preexisting editorial continuation points to the free Apollo investigation.

## Reproducibility

From this PR's **exact HEAD** on an environment with PHP 7.4+, Python Playwright, Chromium and PyMuPDF:

~~~bash
php -l experience2/apollo-r339/chronology-rail.php
FV_R344_OUT=/tmp/fv-apollo-r344 python experience2/apollo-r344/qa/print_source_gate.py
php experience2/apollo-r343/qa/standalone_preflight.php
FV_R343_OUT=/tmp/fv-r343-inherited python experience2/apollo-r343/qa/browser_gate.py
~~~

The new gate checks 10 real Chromium screen contexts at 320/390/768/1440/1920px, with no-JS, 400% root text, touch, reduced motion, forced colors and native keyboard expansion, then checks three native A4 browser PDFs at varying JavaScript/viewport contexts. It verifies six source-limit/custody rows, six PDF source labels, NASA links, a single free editorial link, and absence of UTM/affiliate/merchant URLs. Two deliberate broken-renderer mutations must be rejected. The receipt, screenshot and PDF generated at \`FV_R344_OUT\` are **local fixture evidence**, not production performance results.

Genuine axe-core is NOT executed by this gate; Firefox/WebKit, independent screen-reader tests, installed WordPress/Assembler/CDN, hosted CI on HEAD and production LCP/CLS remain **NOT VERIFIED**. Re-run all those before release. Source URLs are NASA-hosted documents, not a media-rights license or a conclusive ignition identification.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

1. **Original rights-cleared Apollo educator kit → confirmed paid order:** no verified payable Apollo SKU/rights/fulfillment; no product CTA permitted. Founder and Claude commerce verify the actual merchant checkout, terms, delivery, refunds and fees before any purchase proposal.
2. **Grok film → qualified landing:** real published asset ID, allowed click destination and actual mobile route still unverified. Grok creates/distributes; Praxxis checks TASK-008 and creator claims. No invented UTM content.
3. **NASA chronology → existing free Apollo investigation:** silent print loss of six sources fixed locally. Apollo/Research Desk QA owner closes installed-WP and independent accessibility acceptance. Hypothesis: stronger provenance preserves audience trust and increases downstream qualified engagement; not yet demonstrated.
4. **Confirmed merchant orders → realized net revenue per 1,000 qualified human sessions:** 7-/30-day qualified sessions, paid orders, refunds and fees unavailable. Claude owns privacy-preserving attribution, founder owns commercial signoff. Clicks, newsletter leads and checkout starts are **not** revenue.

References: [NASA original Board investigation](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html), [NASA chronology](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/chro.html), [Apollo #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

**Governance:** HARD HOLD — no production, payments, email, social post, affiliate activation or spending changes authorized.
