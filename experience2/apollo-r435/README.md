# Apollo R435 — photo provenance correction and source-only catalog gallery

**Status:** DRAFT / STAGING-ONLY / HARD HOLD. New files isolated to `experience2/apollo-r435/`. Base proposed: R434 PR #2892 at `a7d7aa2d2e54cd56d9c6416b6fb1209843ea203a`. Do not edit or merge homepage PR #49, Research Desk PR #158, any homepage lead branch, or Grok/Praxxis TASK-008. Source of truth: #150; conversion charter: #820 / #818. No production, WP writes, photo downloads, merchant/affiliate activation, tracking scripts, email, spending or social posts.

## Why this matters

Direct read of PR #158 found six *real* NASA catalog URLs, but some images can misleadingly be interpreted as direct evidence of adjacent claims. NASA lists S66-58038 as **October 18, 1966 altitude-chamber training**, not January 1967 fire telemetry; NASA lists S67-15717 as **January 3, 1967 spacecraft movement**, not cabin oxygen-pressure measurements. The two KSC-20170124 photographs are **January 24, 2017 retrospective museum-exhibit photographs**, not pictures taken during the Apollo 1 accident. S67-21294 is **January 28, 1967 post-fire damage**, not conclusive proof of a unique ignition mechanism. See `source_catalog.json` and its six NASA URLs. These mismatches were established against the actual NASA image-detail captions on November 17, 2026; historical claims still refer separately to the 1967 Apollo 204 Review Board.

This sprint adds a **clearly dated, source-only gallery index with six source drawers**, preserving the *one* high-positioned free-investigation CTA in R434. It shows every photograph's archival subject, credit, original NASA catalog URL, and what it cannot establish, with chronological order and explicit rights status. It downloads/hotlinks **zero** image bytes, never claims NASA endorsement, and blocks resale of unreviewed images. The gallery is a nonintrusive native disclosure, not a substitute for the primary Board.

## Code and activation

- `[fv_apollo_photo_custody_r435]` only renders on a single confirmed WP staging page when `FV_R435_ENABLED=true` and integer `FV_R435_STAGING_PAGE_ID` matches `get_queried_object_id()` and WP environment is `staging`.
- Parent R434 PHP/CSS are verified at exact Git blob SHAs. The local JSON catalog has a SHA-256 pin. R434 then independently verifies the R433/R432/R431/R430/R429 chain. Unknown preloaded parent implementations, changed template assumptions or source mutation cause a safe plain-link fallback. NO dynamic remote HTML is trusted.
- All core source meaning and the free investigation link survive no JavaScript. Gallery and per-record drawers use native details/summary, accessible visible focus and reduced-motion/forced-colors CSS. No geo map is published; source records do not constitute verified geography.
- Photo rights are **NOT REVIEWED for product reproduction**. Source existence and caption credit are not per-image commercial permission. Founder/QD must approve a separately reviewed rights manifest before any actual images appear or paid educator pack is listed.

## Reproduce independent local QA

From `experience2/apollo-r435` with upstream R429–R434 source present:

```
php -l staging-photo-custody.php
python qa/test_contract.py
python qa/browser_qa.py
python qa/staging_acceptance.py  # EXPECTED HOLD exit=2 unless approved HTTPS and reviewed axe-core supplied
python qa/package_evidence.py
```

`qa/test_contract.py` runs source and negative-tamper tests against actual upstream dependency files. `qa/browser_qa.py` uses real Chromium on **actual PHP-generated markup**, but `page.goto` is blocked by administrator policy: it uses `set_content`, so its assertions/screenshots are **offline**, not navigated staging, and it never reports LCP/CLS or genuine axe. `qa/staging_acceptance.py` requires founder-approved nonproduction HTTPS URL, pinned axe-core bundle SHA and success of real page.goto + axe + PerformanceObserver before a real acceptance receipt can exist. CI at exact Git head and screen-reader/WordPress cache/theme acceptance still need independent QD.

## Conversion experiment / hard gate

High-intent target: grades 6–9 history educators from a *verified published* Grok Apollo documentary. Journey: approved Grok asset_id + approved UTM landing → R434 primary verified free article CTA → full free Apollo investigation → **future** optional original teacher dossier, only if an actual rights-cleared payable SKU and checkout/fulfillment are authenticated. R435 adds an optional provenance gallery *after* the primary CTA, not another monetization point. Hypothesis: clearer distinction between photo evidence and event claims reduces trust friction; no experiment or revenue measurement has occurred. No authenticated FV Apollo SKU, verified buyer, settlement, refund or qualified human-session denominator is currently known. Net revenue / 1,000 qualified human sessions is **NOT COMPUTABLE**, not zero.

**Release gates:** R417 archive mismatch, actual installed staging and real axe/LCP/CLS, QD accessibility, original photo right-by-right review, verified commerce and founder release. No changes may be considered LIVE by virtue of this branch or screenshots.
