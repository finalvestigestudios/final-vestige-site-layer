# R271 — Complete wrapped privacy-warning PDF receipt and 9pt alternative (HARD HOLD)

**Preparedness Integration only · Issue #136 / commercial coordination #820 · 2026-11-10 PT**

**DRAFT / HARD HOLD.** No approved card, no independent QD PASS, no medically certified content, no CMS/navigation/site change, no commercial CTA, no creator publishing. This is a separate review-only source experiment, not a change to the held original Tool #104 or the 35 articles.

## Root defect and bounded change

R270's PDF witness checked that a single privacy **prefix** and status badge appeared in each card face, but did **not** establish that *all continuation lines* of the longer printed warning survived clipping and cutout. Its authentic 8pt finding remains pinned and **negative**, not erased or recharacterized.

R271 adds a parallel CSS-only candidate with exactly **two** substitutions from source R269: `font-size:8pt` -> `font-size:9pt`. The candidate is authenticated as Git blob `a898d45f5cf050e941ce9f771f0d684084735570`; its parent R269 remains `4fbe028e0460dc81478825f501d76b03596faeaf`. All household guidance, warnings, five blank fields, printed card layout, source references and canonical URLs remain byte-identical apart from the two CSS font declarations.

In offline Chromium **144.0.7559.96** on US Letter, JavaScript disabled and enabled each yielded one printed PDF page; both cutout faces retained the complete normalized warnings, face-local **UNAPPROVED - DO NOT USE** notice, and all five blank fields. Font extraction measured about **9pt** in both modes. Front warning wraps to four PDF text lines; back to two; all lines and five fields lie inside the tested face text bounds, without detected field overlap. The strict verifier reconstructs **the entire privacy paragraph**, not just the prefix, and rejects omitted/altered continuation, box overflow and missing/false release-state fields. Report is **bounded PDF text/geometry evidence**, *not* physical print legibility or safety approval. A 9pt font is an internal review target, **not a legal standard or verified accessibility threshold**.

The reader-visible sheet-level note remains separate, but the *UNAPPROVED - DO NOT USE* stamp is inside both detachable faces. No actual paper cutting, folding, handling, children, caregivers, screen readers or human legibility studies have been performed.

## Frozen execution ledger

- Python: **98/98** genuinely executed isolated `unittest` cases, with adversarial receipt/schema/approval/identity/continuation/overflow tests, plus `py_compile` on the new gate, test and reproducer (local authenticated matching Git object bytes).
- Manual script: executed offline Chromium + Playwright + PyMuPDF with JavaScript ON and OFF, new PDF witness regenerated; independently generated JSON matches the frozen R271 receipt exactly.
- Responsive smoke: **10/10** Chromium screen cases at 320/360/390/768/1440px with JS enabled/disabled, no horizontal overflow in tested configurations; **not** full accessibility/400% zoom.
- Original 35 articles, six tools, 2,000 citation occurrences, canonical routes, crosswalk, source assets and publishing states **not edited**.
- Frozen seven Claude branches rechecked via GitHub compare: all **identical** (0 ahead/behind): start 2122d856, food f911ff7a, health d5ef5baf, shelter 5daeaf2d, hist-field 4e5caf81, hist-food 67e116e5, hist-home 7504a5f0.
- Independent QA PR #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; fixture PR #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5`; homepage lead PR #1689 at `f55c36b6598eec558dd8bb24e4c8988becc51be0`. Inspected metadata and scopes; none modified.
- New evidence/validator modules source-pinned in the R220 pre-/post-export custody chain. **Full native Python validation, build, inherited suite and authentic 41 WordPress drafts NOT EXECUTED**: local `github.com` DNS prevents complete checkout. Do not mislabel isolated tests as native pipeline tests.

## Source/citation and safety HOLD

All **32 shared-URL groups** and **15 duplicate source-ID groups** remain unresolved; original Article #7 two CDC citations and Article #20 one Ready.gov citation remain disputed, and Article #7 chemical-contamination advice needs qualified review. Article #15/Tool #104 child-information privacy and accessible communication require independent signoff. No citation/source or original wording modified by R271; no QD PASS or release authorization.

## Conversion-first decision

**ONE audience:** households planning emergency contacts and reunification. The **existing public free Preparedness Archive** is the only admissible free destination pending an authentic source-backed published creator asset and verified native mobile click path (Grok/Praxxis TASK-008). Do **not** promote any held card/article prototype.

**ONE provisional commercial candidate:** existing Legacy Triage PDF listing, **not yet an approved Preparedness upsell**. Before any on-site CTA, the founder/commerce owner must audit its complete rights-cleared PDF, sensitive information/credential handling, suitability, actual checkout/delivery, fees/refunds and explicit approval. No new product or retired water freebie. No paid conversion, merchant sale or affiliate sale has been verified; net realized revenue per 1,000 qualified human sessions **not computable**, not zero.

Funnel contract: authenticated Grok `asset_id` + `utm_campaign` → qualified human landing session → relevant free guide/tool view → optional approved CTA click → verified merchant paid order → fees/refunds → net revenue. Keep unconfirmed leads, clicks, checkout starts and actual settled orders separate, with 7/30-day cohorts and tiny-sample warnings. No new tracking script, social post, email, merchant activation, spend or CMS changes authorized.

**Before any release:** independent source/citation adjudication, print/cut/fold and human legibility testing, disability/child-information privacy review, real mobile/assistive-tech QA, checkout/fulfillment and founder signoff, plus native 35-article build and 41 draft-export validation.
