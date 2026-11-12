# Apollo Experience 2.0 R305 — textual evidence vs photo-record custody (DRAFT / HARD HOLD)

Isolated follow-up to [R304 PR #2163](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2163), scoped to [Apollo Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) and cross-referenced to [conversion Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) / business #818. No edits to frozen homepage PR #49 or independent Research Desk PR #158.

## Concrete problem and change

The separate [Research Desk PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158) presents six image accession identifiers alongside interpretive historical summaries. An image metadata record alone is not proof of the associated causal claim and its link does not grant commercial image rights. The Apollo Evidence Atlas already uses its own linked NASA textual records, but its source catalogue did not explicitly distinguish that custody boundary from the proposed Research Desk image index.

R305 adds a visible, CSS/no-JavaScript-safe explanation to the Atlas's source catalogue. It tags each of the three existing catalogue entries as `data-fv-evidence-role="documented-textual-claim"` and the catalogue as `data-fv-gallery-status="text-only-source-custody"`. Historical words, events, URLs, dates, SHA256 integrity seals, source labels, primary claims, the existing sole free-investigation link and stylesheet are not changed. No image, speculative geography, logo, tracking script, product or form is introduced.

`RESEARCH_DESK_HANDOFF.json` lists the six photograph IDs and NASA archive URLs **transcribed from the actual PR #158 ledger blob** `403d128c57b9bc82dac7c619651689070edef86c`. This inventory is explicitly *not* independent photograph-caption authentication, a rights clearance, a source of proof for ignition, or permission to modify PR #158. Future integration must separate original text findings from contextual media and verify each record before rendering an image.

## Executable verification

Run from the repository root with PHP, Playwright Python and Chromium:

```bash
php -l experience2/apollo-r281/apollo-source-experience.php
python experience2/apollo-r305/qa/gate.py
python experience2/apollo-r305/qa/check_rd_crosswalk.py
python experience2/apollo-r304/qa/gate.py
python experience2/apollo-r301/qa/source_controlled_browser_gate.py
python experience2/apollo-r302/qa/source_controlled_browser_gate.py
```

Local Chromium `set_content` completed 10 contexts (320, 390, 768, 1440, 1920 pixels × JS on/off), two shortcode instances each, 60 source-to-claim role checks, 10 deliberate role corruptions, unique IDs, focus on native source links, no overflows and CSS-free/no-JS recovery. Six photo records passed the custody whitelist; **24 deliberate false-proof, false-rights or third-party-link mutations were rejected**. Local R304, R301 and R302 regression suites also passed. R303 extended suite did **not** finish within local execution time and is not claimed passed for R305. This is offline browser evidence, not WordPress acceptance.

## Governed integration and business contract

Proposed audience: viewers of a genuinely published Grok Apollo 1 documentary, once the actual asset ID, date, rights and destination have been independently authenticated by Grok/Praxxis through existing TASK-008. Flow: documented NASA source → accessible Atlas → original free Apollo investigation → **only after separate product, rights, checkout and founder verification** a relevant payable historical research resource. The single Atlas link remains an editorial continuation, not a confirmed lead or sale. No existing Apollo-targeted buyable SKU is authenticated by this sprint.

Success criterion for an approved future conversion experiment: 7-/30-day qualified-human sessions by published `asset_id` / `utm_campaign`, paid orders independently confirmed by merchant, refunds/fees and realized net revenue per 1,000 qualified-human sessions, with tiny-sample warnings. No attribution, checkout or commercial sales data were obtained or inferred here.

**HARD HOLD:** genuine axe-core unavailable (npm DNS failure), independent screen readers, actual WordPress/Assembler, browser native HTTP/CSP (`ERR_BLOCKED_BY_ADMINISTRATOR` even for intercepted fixture), real-user LCP/CLS/INP, photo metadata / commercial rights clearance, editorial/QD review, exact-head CI and founder release permission are not verified. No CMS, homepage, social publishing, Grok queue, email, merchant, affiliate, analytics vendor or spending changes.
