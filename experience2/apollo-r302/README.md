# Apollo R302 — NASA source egress is never a purchase (STAGING / HARD HOLD)

Independent Experience 2.0 Apollo work for Issue #150 and commercial priority #820 / charter #818. This PR stacks exclusively on draft Apollo R301 PR #2145. It does not edit homepage PR #49 or Research Desk PR #158, and authorizes no merge, deployment, WordPress write, analytics activation, social posting, email or spending.

## Implementation

The existing PHP Evidence Atlas attaches inert attributes to all official NASA outbound source links: `data-fv-link-purpose="official-evidence-source"` and `data-fv-conversion-kind="noncommercial-source-reference"`. The fail-closed NASA fallback receives the same attributes. The sole free investigation CTA retains `editorial-continuation`. Nothing emits a network request, cookie, analytics event, attributed session, checkout, lead or paid order. Existing source links, CTA position, historical claims, CSS, imagery, geography and UTM behavior are unchanged.

## Verified historical boundary

NASA's Apollo 204 Review Board narrative dates oral authority January 27 and convening January 28, 1967; the proceedings record receipt January 31 of a January 28 memorandum, and the original narrative records February 3 written confirmation. These are distinct actions in related NASA institutional records, not independent eyewitness confirmation. The NASA archive memorandum webpage's date heading does not independently establish its signing time.

- Original narrative: https://www.nasa.gov/history/Apollo204/narr.html
- Original proceedings: https://www.nasa.gov/history/Apollo204/proceed.html
- Archival memorandum: https://www.nasa.gov/history/Apollo204/15.html
- Rights/endorsement: https://www.nasa.gov/nasa-brand-center/

No NASA insignia, photographs, product endorsements, location pins or paid-use permissions are introduced.

## Reproduce

From a repository checkout or extracted evidence ZIP with Python Playwright, PHP, Chromium at /usr/bin/chromium (PyMuPDF additionally validates PDF contents):

```sh
php -l experience2/apollo-r281/apollo-source-experience.php
python experience2/apollo-r301/qa/source_controlled_browser_gate.py
python experience2/apollo-r302/qa/source_controlled_browser_gate.py
python experience2/apollo-r302/qa/verify_source_egress.py
python experience2/apollo-r302/build_archive.py
```

R302's source-controlled Chromium gate checks 10 JS-on/off contexts at 320–1920px, 260 source classifications, 20 source corruption controls, and the 10 existing false-paid-order controls. The independent extended suite exercises 60 malformed-source tests, provenance links and native keyboard disclosures, 200% font, five PNGs, a 13-page PDF, 70 print links. Both use actual PHP output in offline Chromium; neither is an installed WordPress or native HTTP browser test.

## Conversion and release decision

Flagship candidate: Grok documentary -> Apollo Evidence Atlas -> original NASA source inspection -> existing free Apollo investigation -> only after independent rights, merchant and founder approval, a relevant Apollo educator dossier (future B2B product hypothesis, NOT a sellable SKU). Paid revenue and net revenue per 1,000 qualified human sessions require confirmed orders, fees/refunds and 7/30-day qualified cohorts. Published Grok asset_id, approved Apollo offer and merchant sales records remain unverified; outcomes are NOT COMPUTABLE, not zero.

HARD HOLD: genuine axe-core, independent screen readers, installed WordPress/Assembler, browser HTTP/CSP, exact-head CI, field LCP/CLS/INP, independent editorial and QD review, verified commercial offer and explicit founder release approval. Grok owns social publishing, Praxxis creator QA, Claude production analytics/checkout, founder release and spending decisions.
