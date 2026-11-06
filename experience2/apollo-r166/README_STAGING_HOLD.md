# Apollo R166 — integrated historical-gallery decoupling + image failure recovery (STAGING HOLD)

This is an additive, isolated integration of the **exact R163** independent 1966/1967/2017 archival selector and the **exact R162** archival image-failure fallback. Their original Git blobs are copied without modification, avoiding drift and interference with original Research Desk PR #158, frozen homepage PR #49 or Claude's production branches. The static excerpt is the R162 read-only WordPress editor-derived gallery fragment, **not a current installed-page assertion**.

## Purpose and source custody

On WordPress Page 2017 the old editor-source controller coupled October 1966 crew training, January 1967 spacecraft preparation and January 2017 museum photos to arbitrary January 27 fire-second slider positions. R163's guarded transform removes that association while preserving the *technical* chronology slider and all captions, NASA citation links, alt text and original investigation CTA. R162's fallback preserves captions/sources when CDN media fails, including lazy-loaded photographs. The combined candidate is not installed on the live site.

NASA source records pinned by the builder: S66-58038 (Oct 18, 1966), S67-15717 (Jan 3, 1967), KSC-20170124-PH_KLS01_0129 (Jan 24, 2017). A NASA image record is not a grant of paid advertising/licensing or astronaut-likeness rights. Original Apollo 204 Review Board documentation supplies technical fire findings; these photographs provide historical context only. Never imply NASA endorsement.

## Exact code path and commands

- `python -m unittest -v test_integrated_bridge.py` — real Chromium against a controlled, source-derived editor excerpt; positive controls, negative source-drift gates, six widths, keyboard, reduced motion, JavaScript-disabled source access and failed images. Not installed WordPress acceptance.
- `python -m unittest -v test_smoke.py` — inherited R163 chronology checks where compatible.
- `python build_offline.py authorized_current_wordpress_editor_export.html out_preview.html` — pure file-to-file transform. Fails closed on source drift or missing/duplicate NASA citations; writes SHA-256 receipt. This does **not** post to WordPress.
- For real-browser acceptance on an approved staging host, run the existing R164 installed-page acceptance and R165 browser-selected `currentSrc` media custody. Real axe-core, CSP, CDN, device/zoom/assistive-tech, CWV, hosted CI and founder/QD gates remain HOLD.

## Business gate, funnel and release

Flagship: Apollo 1 / original investigation. Intended Grok long-form audience: educators and primary-source research viewers. One contextual next action remains **Read original investigation** (https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). An educator casefile is a *hypothetical* paid offer, NOT a verified sellable SKU. Do not add a paid CTA until actual Payhip inventory, source/licensing, merchant acceptance, fulfillment and refunds/fees have been independently proven and founder-approved. Do not put unrelated Mini Museum offers into tragedy evidence.

Attribution under #820: Grok asset_id/UTM → qualified human landing session → investigation/offer CTA → merchant-confirmed order → refunds/fees → realized net revenue (7/30-day). No asset or paid-order evidence has been supplied to this lane, hence net revenue/1,000 qualified sessions is **NOT COMPUTABLE**. Do not use click or Jetpack pageview as paid-conversion evidence.

**Release: STAGING HOLD.** No WordPress edit, deployment, mail, commercial activation, image redistribution, analytics script, social posting or spending. Cross-reference Issues #150/#820/#818, Grok/Praxxis TASK-008.
