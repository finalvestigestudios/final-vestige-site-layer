# Final Vestige — cold image-wire CSS/DPR integrity gate (2026-11-14)

## Why this matters
The current paired CDP comparator in draft #183 could return **LAB_PAIR_MEASURED: 76%** for a historical image that became blurry: a 1600px baseline, 960px candidate, and synthetic 1,000-to-240 encoded-byte reduction, even if the image actually rendered **500 CSS pixels on a 2× device**, needing 1000 source pixels. Existing 320px minimum-size and ALT/aspect checks did not detect this. This is an **offline QA defect**, not a real-site incident or measured savings.

## Narrow correction
The existing guest collector already reads DOM `getBoundingClientRect()` as `rectWidth`/`rectHeight` and uses explicit CDP viewport/DPR (390×844 at 2×, 1440×900 at 1×). The shared classifier now forwards positive integer `css_width_px` and `css_height_px` to each classified image slot, leaving absent, zero, and invalid boxes `null`.

The existing paired comparator requires valid CSS boxes **for every article image in both captures**, checks baseline and candidate display dimensions remain within 1 CSS pixel, and holds whenever a candidate's native width or height drops below the lesser of (a) baseline native pixels or (b) candidate displayed CSS pixels × recorded profile DPR. This preserves quality if the original was itself undersized. It remains a **density screen, not pixel-level fidelity or identity proof**.

### Example — 960px maximum is conditional
- 390 CSS px × DPR2 = 780 physical px: 960px derivative may pass the density gate.
- 500 CSS px × DPR2 = 1000 physical px: 960px derivative must HOLD relative to a 1600px baseline.
- 1024 CSS px × DPR1 = 1024 physical px: same HOLD.
- An older export without CSS metrics now fails closed. Re-run the approved collector; **do not invent measurements**.

Tests in `test_cold_wire_css_dpr_gate_20261114.cjs` use synthetic CDP fixtures, never downloaded assets. Existing comparator test fixtures were updated only with matching CSS evidence. Regression suite intentionally keeps `sitewide_76_percent_claim_permitted=false` and `visual_parity_verified=false`, even when isolated bytes pass.

## Scope and QA coordination
Changes target an **isolated draft child PR** against draft #183's comparator branch, not `main`, and do not touch Site QA #154's four files or replace its six-source logged-out-browser queue. Historic 61/355 and 42 reported failures remain unverified in real guest Chrome. The currently documented 16 originals >1.5 decimal MB total 49,107,665 **stored** bytes, not visitor downloads. See adjacent JSON for exact P0 sources, authoritative candidates and rights HOLD.

Before any WordPress staged derivative, require cold guest request IDs, true uncached status and encoded bytes, responsive screen sizes, accurate historical-scene and crop parity, item-level rehost rights, exact 960px/no-upscale fitting, documented attribution, visual map/text sharpness, editorial approval and rollback. **No production writes, third-party caching, post-block rewrites, homepage design changes, merges, deployments or spending.**
