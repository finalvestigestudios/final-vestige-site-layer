# Apollo R304 — claim → SourceDrawer → catalogue custody (STAGING / HARD HOLD)

Part of engineering #150 and conversion-first #820 / charter #818. **Stacks only on draft R303 PR #2155 (HEAD `1df92970829ca084bbe68ccbf19b2371b05d2546`)**. Do not change homepage PR #49 or Research Desk PR #158. No WP content/settings, live analytics, paid services, email, social publishing or merchant activation.

## What actually changed

- Existing EvidencePlate, native SourceDrawer and catalogue now share a passive, stable **FV editorial claim key** and corresponding **source key**, while repeated shortcode instances retain distinct accessible DOM IDs.
- Previously, the drawer called `nasa_mission`, `nasa_proceedings`, etc. a generic **"Record"**. That could imply an official NASA archival accession number. R304 clarifies **FV reference key (not a NASA catalogue number)** in the drawer, and exposes matching editorial identifiers in the catalogue.
- A claim's in-page source jump and catalogue return remain native, no-JS, keyboard/touch capable. No new claims, URLs, source photos, map pins, external vendors, scripts, tracking or commerce.
- The ordered historical source-digest checks remain unchanged. See `SOURCE_CUSTODY.json` for the six retrieved NASA source pages, dependency caveats and source-link-versus-image/branding rights limits. Source-page retrieval does NOT confer commercial media rights.

## Executable source-controlled QA

```sh
php -l experience2/apollo-r281/apollo-source-experience.php
python experience2/apollo-r304/qa/gate.py
python experience2/apollo-r301/qa/source_controlled_browser_gate.py
python experience2/apollo-r302/qa/source_controlled_browser_gate.py
python experience2/apollo-r303/qa/test_integrity_recovery.py
```

On exactly the tested PHP/CSS bytes, R304's source-controlled gate passed 10 real Chromium **offline fixture** contexts (320, 390, 768, 1440, 1920 × JS on/off), 60 claim/drawer/catalogue triplets and 20 deliberately corrupted catalogue-ID controls; duplicate IDs, overflow, and source-vs-editorial CTA classifications were checked. The separately packaged extended QA passed 10 contexts, 60 triplets, **80** broken-link/key controls, five CSS-absent no-JS states, actual Chromium print (13 pages/70 link annotations) and five no-JS screenshots.

Source links never count as merchant conversions. The one existing free Apollo investigation link remains `editorial-continuation`, not `merchant-confirmed-purchase`. No Apollo-specific buyable SKU and merchant order reconciliation have been verified. The owned-product/audience hypothesis is **not** an approved commercial offer.

## Release gates and ownership

**HARD HOLD:** genuine axe-core, NVDA/VoiceOver, installed WordPress/Assembler shortcode acceptance, native Chromium HTTP/CSP (localhost blocked by administrator), real field LCP/CLS/INP, exact-head hosted CI, editorial/citation/rights review, QD and founder authorization. Offline fixture screens/paint data do not prove live performance or sales.

Grok owns script/posts/distribution; Praxxis owns independent creator QA; Claude owns core website/analytics/checkout. Apollo lane owns this isolated evidence component and local QA. TASK-008 remains Grok/Praxxis source of truth. Proposed path: published Grok Apollo asset (ID/link **unverified**) → Atlas source review → free editorial Apollo investigation → **only** an independently cleared, relevant payable offer after founder approval. Realized net revenue per 1,000 qualified human sessions remains **not computable** without approved visitor, order, fee and refund records.

NASA source URLs are direct historical references, not NASA sponsorship, product licensing or agency branding. No media/insignia added. See NASA Brand Center and advertising guidance in `SOURCE_CUSTODY.json`.
