# Final Vestige conversion-first read-only source QA (DRAFT)

Local/offline checker for **already-authorized, sanitized** HTML snapshots. No WordPress network requests, subscriber actions, Awin/Payhip clicks, checkout, or production writes.

Usage:

- From qa/site/conversion_first run: python -m unittest -v test_audit
- From the same folder run: python audit.py /path/to/sanitized-rendered-collection.html --proposed-utm 'https://finalvestige.com/collection/?utm_source=youtube&utm_medium=organic_social&utm_campaign=nav_pilot_2026_11&utm_content=example_asset_001'

**Strict evidence boundary:** Source order is not rendered viewport, accessibility certification, merchant acceptance, paid conversion, or net revenue. All tests use synthetic fixtures, not live subscribers. The "affiliate before inline disclosure" diagnostic is a source-order review flag, not a definitive FTC compliance finding. Real 360/390/768/1440 browser screenshots and keyboard acceptance, merchant checkout/return, double-opt-in welcome/download, and reconciled Payhip/partner orders + refunds remain HOLD. Never treat arbitrary subscribe query parameters or gift reveal as confirmed_signup (#129 and earlier #198 already cover the separate preexisting issue).

**Source observation (Nov 3, 2026):** Published /collection/ WordPress page 78 contains two Awin/Suunto affiliate anchors with rel=sponsored (product image and textual CTA); their nearest .fv-affiliate-note occurs **after** both in source order. Page 78 includes a free Focus Fieldbook CTA but no Payhip link in the CMS-rendered body. The other inspected bodies /, /focus/, /dispatch/, /free-resources/ have no Payhip buy link either; **this is a bounded entry-page review, not proof a Payhip shop or product is unavailable**. Source verification did not access the public page in a real browser because the QA environment's DNS resolver could not resolve finalvestige.com. No real Awin redirect, Payhip checkout, purchase, or payout was requested or verified.

**Governance:** Issue #820 owns conversion measurement; Claude owns production code/analytics, Grok owns distribution/TASK-008, Praxxis verifies creator evidence, founder owns approval. Do not change frozen homepage PR #49, WordPress CMS, tracking scripts or payment/affiliate settings. Re-fetch current source, obtain approved merchant/product eligibility, and coordinate the narrowly scoped disclosure/content test before any production edits.
