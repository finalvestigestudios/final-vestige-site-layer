# Apollo R262 — staging overlay bridge / SOURCE ONLY / DRAFT HOLD

Tracks #150 and conversion #820/#818. Parent is R261 draft PR #1895; frozen homepage #49, Research Desk #158 and Claude's homepage lane are untouched.

R253–R261 added source-controlled tested CSS/JS but no WordPress enqueue path. This separate optional preview-only plugin provides one deterministic CSS bundle and exact R261 JS helper. Original R224 source-sealed plugin must already have passed verification and queued its base CSS at priority 20. The bridge runs at priority 25, checks both bundled asset SHA-256s and queues the overlay CSS with the original base CSS dependency plus footer JS. No original NASA records, page HTML, map pins, checkout, settings, WP content, analytics, merchant links or social queue are altered. When the source or assets are absent the overlay does nothing, leaving the original evidence/fallback intact.

CSS concatenates original Git blobs in strict R253/R254/R255/R256/R257/R260 order; each original hash and both generated asset SHA-256s appear in integrity.json. JS is byte-identical to R261. Local QA: original sealed R238 PHP adapter through a function mock, Chromium Playwright 320–1920 JS on/off + forced-colors/reduced-motion, native no-JS disclosure, focus, 55 NASA URLs, 31 fragments and exactly one free original investigation CTA. PHP hook exclusion and intentionally corrupted asset/source guards were independently exercised locally. Screenshots and receipts reproducible. Test command:

```sh
python3 experience2/apollo-r262/qa/integration_acceptance.py --fixture fixture/sealed-r238 --source experience2/apollo-r262 --out dist/apollo-r262
```

The fixture is included in the preceding R261 evidence archive, not copied into this PR. **Offline PHP MOCK and Playwright set_content do not prove installed WordPress/Assembler or real HTTP/CSP.** Genuine axe-core, independent screen readers, browser UI 200% zoom and production LCP/CLS remain NOT TESTED. CI exact-head, QD, source/media rights, inherited R198 discrepancy and founder release authorization remain HOLD.

Commercial hypothesis: previously published Grok Apollo documentary (URL + immutable asset_id + rights/UTMs to be verified by Grok/Praxxis) → NASA evidence Atlas → one FREE original investigation https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ → separately verified/approved ORIGINAL educator source kit. No existing Apollo SKU, checkout, merchant/affiliate acceptance, confirmed paid order or net revenue is established; no commerce CTA. Measure qualified human sessions/asset_id, landing, free CTA, consented confirmed lead if separately approved, merchant-confirmed paid order, refunds/fees and net revenue per 1,000 qualified sessions in 7/30-day cohorts. Do not confuse clicks or leads with sales. No posting, email, merchant, WP or analytics changes.
