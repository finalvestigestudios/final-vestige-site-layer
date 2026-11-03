# EX2 / Malbone — rights-safe fallback exact-source custody & hosted visual admission

**Status:** DRAFT / HOLD / NOT PUBLISHED. **No WordPress writes, merges, deployment, or plugin installation.** Stacked on NYPL withholding PR #780 (head `b2fb7d56dcf2d906d7b27d3ab8e44d08d0641029`). Frozen homepage PR #49 remains unchanged.

## Independently verified full published raw source readback — 2026-11-03

Authenticated read-only WordPress.com page GET (site 256784396, page 6) returned `status=publish`, `modified=2026-11-02T17:48:13`. The complete **150,958-byte** UTF-8 source was inspected **only in tool memory**; it was **never committed or exported**. A standalone SHA-256 implementation was checked against the canonical `abc` test vector.

| Exact-source invariant | Published source | Ephemeral candidate |
|---|---:|---:|
| Raw UTF-8 characters | 150,727 | 149,983 |
| 72 sequential Margin records 0..71 | 72 | 72 |
| Jetpack subscription markers | 1 | 1 |
| Textual Focus Fieldbook references | 5 | 5 |
| NYPL catalog links | 2 | 2 |
| Actual `<img data-fv-archive-img>` elements | **3** | **2** |\n| Literal `data-fv-archive-img` tokens (including JS selector) | 4 | 3 |
| NYPL binary filename references | 4 (one `img`, `src+srcset`) | **0** |
| Unverified NYPL public-domain assertions | 1 | **0** |

**Original raw SHA-256:** `c9a6cd57582cce2801620381212193d54b9e6446236b24aff1880a12ff1d3b7e`

**Independently recomputed in-memory rights-safe candidate SHA-256:** `dc2c6ff17639d114794f9c1b78b4a6ab77962ca7129473bef10a5d20a859be19`

The candidate incorporates a documented mobile-safe inline fallback width/font treatment and a shortened archival frame label after a real 320px Chromium capture exposed clipping of the original fallback text and long label. The originally hashed unpolished withholding-only candidate was `de7d7a951c780ad4d6a411438ada7d328a05965aa2fc3c3964c535e81089f3ba`; the SHA-256 above is the revised isolated art-directed candidate, not a published source.\n\nThe exact published article matched every precondition in PR #780: one Malbone article, one NYPL image with four responsive filename references, exact caption and unverified credit, one fallback, one image frame label, and linked primary source. Applying its five narrow textual/attribute substitutions in an independent JavaScript in-memory replay preserved every byte **outside** the Malbone article. All 11 preflight and 7 postflight checks passed. The original script counted four *text occurrences*, but only three are real image elements; the fourth occurs in a JavaScript selector. This branch corrects the image inventory in the parent transformer and adds a regression test. The protected count is now three actual elements before and two afterward. This **does not claim** that PR #780's Python CLI has executed against that full source in a filesystem; the remaining explicit Python source-file run must reproduce the stated candidate hash. Abort if it does not.

## Why this companion browser check exists

PR #780 only established synthetic test coverage for its offline transformer. This companion tests the **real publicly hosted WordPress/Assembler DOM**, at five widths, without any public edits. It blocks requests for the disputed NYPL image rather than transferring unverified reproduction bytes, opens the Malbone case, captures its current image frame, applies the exact reviewed copy/label/image removal **inside an ephemeral anonymous Chromium document**, and captures the resulting fallback treatment. No screenshot is a production deployment preview or an exact WordPress source rewrite.

The test is fail-closed for markup drift, article source claims, lack of catalog links, missing Focus or any of 72 Margins, image counts, clipping, overflow and missing evidence. It saves screenshot SHA-256 receipts, incomplete results and the final JSON verdict as GitHub Actions artifacts. No secrets, admin site state, subscriber information or image binaries are intentionally stored.

**Accessibility boundaries:** Automated fallback visibility and bounding-box checks are useful but not sufficient for WCAG 2.2 AA, contrast under every overlay, screen-reader semantics, zoom, no-JS or touch. A real private WordPress Playground (not the paid/unsupported WordPress.com Personal staging clone) and manual assistive-technology acceptance remain outstanding.

**Hosted infrastructure boundaries:** WordPress Playground is not WordPress.com Atomic and cannot certify host-specific Jetpack behavior, caching or field CWV. The browser check here only tests the *existing public host* with an ephemeral candidate and may not catch a WordPress/Gutenberg serialization problem.

## Run exact candidate browser admission

```bash
python -m unittest discover -v -s experience2/home-flagship/rights -p 'test_verify_hosted_nypl_fallback.py'
python -m pip install 'playwright==1.56.0'
python -m playwright install chromium
python experience2/home-flagship/rights/verify_hosted_nypl_fallback.py --output-dir nypl_visual_hold
```

No browser PASS is claimed until the new exact-head GitHub hosted job finishes. Preserve independent QD, NYPL capture-specific rights review, founder visual signoff and **separate explicit production approval**. Do not modify WordPress or frozen PR #49 from this branch.
