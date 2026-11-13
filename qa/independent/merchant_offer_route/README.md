# Mini Museum affiliate landing — independent QA, no production edits

**2026-11-12 read-only observation:** FV's Collection and Mini Museum guide sponsored Awin CTA resolves to the **Mini Museum Fourth Edition** explainer page. That page presents the featured 29-specimen Large collection as **sold out**. Seller's Fourth Edition collection also advertises Small and Touch sold out, while individual fragments and the $15 Companion Guide remain listed in stock. The CTA promises broad current collection browsing, so this is a **conversion relevance / inventory friction HOLD**, not a broken link or proof that the merchant cannot sell any items.

Evidence URLs are in `evidence_2026-11-12.json`. The redirect was observed through the existing link without a purchase. Availability comes from the seller's public storefront and must be rechecked on the date of any actual release.

Run: `python -m unittest discover -s qa/independent/merchant_offer_route -p 'test_*.py' -v` and `python qa/independent/merchant_offer_route/merchant_route_gate.py qa/independent/merchant_offer_route/evidence_2026-11-12.json`. The latter intentionally exits nonzero on HOLD.

**Boundaries:** Test is pure offline Python. No WordPress, tracking, checkout, affiliate account, merchant configuration, social posting, or email writes. A route-only PASS never proves Awin commission eligibility, merchant acceptance, completed purchase, refund/fees, or revenue. Do not swap tracked links without Claude/Commerce and founder approval. The preferred next test is approved merchant deep-link to a genuinely in-stock, audience-matched page, then mobile browser/checkout-to-payment-method (no purchase) and settled order reconciliation separately.

Owner: Claude/Commerce, coordinated through issue #820. Independent Site QA only; no merge/deploy.
