# Apollo R247 — protected Research Desk assets (STAGING HOLD)

2026-11-09 PT. Scope **only** `experience2/research-desk/`, stacked on R246 draft PR #1801 at `9d28657c0ba88a24e53545abcfd72d992ea411c1`. Canonical Experience Issue #150; commercial Issue #820 / charter #818. Original Research Desk PR #158 and frozen homepage PR #49 remain unchanged.

## Functional improvement

R246 protected the exact six-record NASA HTML template. However, a corrupted or unauthorized **CSS or JavaScript asset** could still be enqueued by WordPress. R247 now checks the bundled stylesheet and optional search JS *separately*, using pinned Git blob identities **before enqueue**, and requires the same CSS check before late inline fallback. If either asset is absent, changed or corrupt, only that asset is skipped; trusted evidence remains visible even without JavaScript or styling. The HTML seal continues to fall back to the existing free original Apollo 1 investigation if the **HTML** itself is changed. This is a check against accidental/unreviewed source drift, not protection if executable PHP or the repository itself is maliciously changed.

Protected **Git blob identities**, pinned against actual repository files:

| File | Git blob |
| --- | --- |
| `templates/ledger.html` | `403d128c57b9bc82dac7c619651689070edef86c` |
| `assets/source-ledger.css` | `db531213e6f8dbaa44fba2885eefdd016dab93e3` |
| `assets/source-ledger.js` | `32e757cc4dc8708397ff65ac21e89dd319781d78` |

No historical source URLs, source finding, rights claim, timeline entry, image, CTA, analytics snippet, storefront, homepage file or WordPress setting changes.

## Reproducible tests

From repo checkout:

```bash
php -l experience2/research-desk/final-vestige-ex2-research-desk.php
python experience2/research-desk/qa/r247_asset_integrity.py
python experience2/research-desk/qa/r246_seal_smoke.py --source experience2/research-desk
```

The first exact-source R247 test **is committed but not executed on this full GitHub checkout** during this run; the runner has only a synthetic local test fixture. The existing R246 smoke offers an exact NASA mode but that exact mode remains unexecuted here. Two local independent synthetic PHP→Chromium runs were executed at widths 320, 390, 768, 1440, 1920 with JS on/off (10 contexts/run), keyboard details interaction, mobile touch, reduced motion, static no-JS evidence and network/overflow checks. Both screenshot sets and browser receipts matched; **NOT** installed WordPress or exact original HTML browser validation. Additional local synthetic asset-custody PHP regression passed 8 conditions. This is **not** an axe-core or full WCAG claim. Browser proof remains a synthetic scope.

## Conversion-first release decision

One controlled high-intent editorial journey: verified Grok Apollo documentary (only when an actual published asset ID/URL exists) → Apollo research landing/SourceDrawer → NASA review-board context → **single free original investigation CTA**. A relevant optional space-history artifact offer (Mini Museum) must remain **disabled** until FV-specific merchant authorization, appropriate commercial rights, approved disclosure, checked destination/checkout, and source-confirmed purchases exist. No NASA-endorsement claim.

- **OFFER → FUNNEL → BLOCKER → CHANGE/TEST → EVIDENCE → OWNER**
- Mini Museum artifact → paid purchase → approval/checkout/settlement unverified → keep conditional commercial destination disabled until reviewed → **HOLD** → Founder / Commerce / Claude.
- Grok Apollo video → source-based landing → published creator `asset_id`, URL and attribution unverified → reconcile existing TASK-008, without creator-queue edits → **UNVERIFIED** → Grok / Praxxis.
- Research Desk → original investigation → CSS/JS drift could corrupt trust and visitor use → independently sealed assets R247 → **LOCAL SYNTHETIC PASS, EXACT INSTALL HOLD** → Apollo.
- Verified order → net revenue per 1,000 qualified-human sessions → no authenticated checkout/merchant sales/refund/fee cohort → reconcile first-party and merchant records for 7/30-day cohorts → **NOT COMPUTABLE** → Commerce / Analytics.

## Unmet release gates

Exact NASA source browser run; actual isolated WordPress/Assembler shortcode lifecycle; genuine axe-core and screen readers; Safari/Firefox; browser UI zoom and keyboard/touch devices; live/candidate LCP, INP and CLS; hosted CI and independent QD; R198 source ancestry; commercial rights clearance and founder sign-off. No approval to merge, deploy, publish, send emails, post videos or spend. Production must not be modified.