# Apollo R154 — exact PR #158 Research Desk template browser acceptance (STAGING HOLD)

Scope: [Experience 2.0 #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter #818. Independent additive review; **nothing added to or changed on PR #158's original branch**, frozen homepage #49, production WordPress, analytics, Grok/Praxxis, email, or commerce.

## Meaningful difference from R152/R153

R153 tested a hand-authored *mark-up-shape synthetic fixture*, not the actual Research Desk. **R154 tested the exact complete six-record `ledger.html` from PR #158** (Git blob `403d128c57b9bc82dac7c619651689070edef86c`), **and the exact PR #158 stylesheet** (Git blob `b8cf00afeceba115a9e9d19044fc11dcf2890cbe`). Local copies were reconstructed independently and verified byte-identical with Git blob SHA-1. This new runner loads those files in Chromium's offline HTML shell with the previously staged R153 replacement JS (`3610ec8f68fc0332db04bcfa5c368574818e9866`) and supplemental scoped CSS. The original PR #158 JS remains unchanged and must **not** be loaded alongside R153 candidate JS.

The runner rejects mismatched source files, refuses to overwrite evidence, and produces screenshots with SHA-256. It makes no HTTP requests or WordPress changes. Testing is **not** full WordPress/Assembler/Jetpack integration; layout may change under the real theme.

## Local reproduction with an R154 branch checkout

```bash
python -m py_compile experience2/apollo-r154/r154_exact_template_browser_qa.py
node --check experience2/apollo-r154/r153_source_ledger_compat.js
python experience2/apollo-r154/r154_exact_template_browser_qa.py \
  --template experience2/research-desk/templates/ledger.html \
  --css experience2/research-desk/assets/source-ledger.css \
  --js experience2/apollo-r154/r153_source_ledger_compat.js \
  --extra-css experience2/apollo-r154/r153_source_ledger_compat.css \
  --out /tmp/apollo-r154-first
# For accessible-browser audit add --axe /path/to/reviewed/axe.min.js
# Use a NEW output directory for a second run and compare SHA256SUMS.
```

Chromium 144.0.7559.96 native Playwright run against **exact full PR #158 template and CSS**: **132/132 checks passed**, twice, at 320/360/390/768/1440/1920. Test coverage: six actual source records, 12 NASA links, six evidence limitations, existing investigation link, static no-JS six-card reading and native details, JS optional search, zero-results status, generated Clear button, minimum 44px target, external hash navigation restoring a hidden record and focus, Escape, touch tap at 390px, reduced-motion, and absence of overflow and page errors. Six full-page PNG screenshots per run had **identical SHA-256 hashes across consecutive runs**. The committed Python Git blob and locally executed file match; source and style blobs verified.

**Not executed:** actual WordPress staging/theme/shortcode lifecycle, actual published-page Playwright, actual-page axe-core (not installed; do not call this a WCAG pass), screen reader/device tests, merchant checkout, and LCP/CLS of a loaded production page. Hosted CI exact head unavailable until workflow dispatch is restored. Source links were retained from PR #158, but no new photo-specific commercial rights clearance or individual external retrieval assertion is made. **No merge or deployment authorized.**

## Conversion priority: one contextual path, no off-topic monetization

High-intent audience: secondary educators using original Apollo 1 investigation materials. Existing editorial action: Grok-sourced long-form (asset_id/UTM **NOT VERIFIED**) → Apollo Evidence Atlas → **Read the full investigation** → optional future educator casefile only if a real seller SKU, rights, delivery, refund terms, accessible checkout, and founder release approval are independently authenticated. Do **not** put Mini Museum or other unrelated affiliate offers into a tragedy investigation. No casefile purchase action was activated or implied live.

Hypothesis: accessible source custody and reliable evidence navigation improve trust and qualify readers for a later verified educator offer. This is **not** a demonstrated increase in purchases. Measurement chain (existing #820 only; no new analytics script): asset_id + utm_campaign → qualified human landing sessions → editorial CTA → confirmed lead if applicable → seller-confirmed paid order → refunds/fees → realized net revenue/1,000 qualified sessions (7/30-day cohorts, tiny-sample flags). No attributed Apollo paid customer or realized revenue is verified.

## Gate and owner

- Apollo: obtain approved offline axe-core and run WCAG audit; inspect full-template screenshots; browser + physical device check. Confirm NASA individual media use boundaries.
- Claude/site lead: validate proposed JS as *replacement* in isolated WP staging including Assembler/Jetpack caching and shortcode render variants; measure staging LCP/CLS/INP, source delivery.
- Grok/Praxxis: independently establish actual published asset_ids and landing URLs through existing TASK-008; no queue takeover.
- Growth/founder: verify rights-cleared paid SKU and merchant acceptance; approve any future commercial UI.
- QD/founder: independent review, exact-head green CI, explicit release authorization. **STAGING HOLD.**

R154 is an **exact-template offline acceptance milestone**, not a production acceptance or an attribution result.
