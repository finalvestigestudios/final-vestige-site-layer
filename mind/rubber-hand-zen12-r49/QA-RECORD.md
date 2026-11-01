# Final Vestige Mind & Affiliate R49 — source-controlled isolated QA record

**Date:** 2026-11-01. **Status:** DRAFT ONLY / HARD HOLD. **Exact branch:** `feature/mind-rubber-hand-zen12-verified-r49-20261101`. **Repository base:** `main`. **QA record parent commit:** `fde7a1a9d57c54e84ca4b598f5733f26574fcaea`. Final QA commit HEAD will be recorded in Issue #171, after this file is committed.

## Deliverables actually built

1. **Original independent 1,893-word scientific investigation:** *The Hand That Wasn't Yours*. 1998 original rubber-hand experiment and later experimental distinction between self-ownership and proprioceptive drift; an honest methodological comparison to the existing Puységur historical archive; free safe hand-position observation. `investigation.md` and responsive `investigation.blocks.html`. Absolutely no product/affiliate recommendation inside the investigative article.
2. **Original ~1,949-word Zen12 independent guide** based on exact official seller tier offer and checkout. Reports **seller-described**, NOT independently delivered/tested: Beginner first six levels/24 MP3s, Premium all 12/48 MP3s, Advanced last six/24 MP3s; guided/music/nature/white-noise styles, 12-minute sessions. **Never adopts 12-minutes-equals-an-hour, automatic brain entrainment, treatment or wealth promises.** Free twelve-minute listening format experiment, alternatives, buyer/privacy objections, seller-claimed warranty explicitly untested. Numeric price and payouts omitted.
3. **Two complete WordPress-ready unpublished presell candidates**. A is text-only; B has exactly the SAME 14,232-character substantive HTML article core plus original static poster, full transcript, optional-video context. No autoplay, media streaming, fake play button, merchant href, iframe, form, script, tracking, or separate email list. Near disabled future CTA a prospective clear FTC earning disclosure; truly disabled HTML button. Both keep the existing `/focus/` route.
4. **Noncanonical alternate `/mind/` hub** with source/evidence editorial position, four archive rooms, links ONLY to already existing first-party pages, no premature links to unpublished drafts. Canonical Mind hub PR #172 completely untouched.
5. **50-source/claim/affiliate-permission row CSV**, editor source register, SEO/TikTok/internal-navigation plan, privacy-hard-off synthetic aggregated attribution with allowlisted categories/min 20 group suppression, rigorous source and privacy tests.
6. **ACTUAL original 40-second film rendered OFFLINE**: *Twelve Minutes Is Time. Not Proof.*, six illustrated scenes, no third-party footage/audio. H.264 540×960, 12 fps, 480 frames, actual ffprobe duration **40.000 s**, **253,040 bytes**, video SHA-256 `e1302c4f80df368564e1446b21d310326cbc5c80134d3adb9b7d504ac7dd80f6`. Six stills visual contact-sheet inspected for legibility/clipping. Source-controlled exact executed renderer file `render_r49.py` **Git blob SHA `e3157213c66c6633538171d0e087fdc80d2f68ff` matches `git hash-object` of the local executed 5,275-byte Python source**; note JavaScript code-point string length differs from UTF-8 byte length. Committed `captions.vtt` spans 00–40 seconds and `film-transcript.txt` provides accessible text. Local reviewer MP4, PNG poster, caption file, contact sheet, and ZIP are outside Git; NOTHING hosted in WordPress. B stays an honest static concept; hosted VTT sync remains UNVERIFIED.

## Test evidence — actually executed

Read back **16/16 initial committed source files** from authenticated GitHub API; after renderer+QA additions, compare and further readback should be recorded in Issue #171. Loaded the exact committed `source-tests.mjs`, `privacy-tests.mjs`, and `privacy-synthetic.mjs` bodies in an isolated JavaScript V8 harness with `node:test` and assertion imports adapted to a compatible shim. **58/58 assertions PASSED**, including **8/8 unsafe mutation cases caught** (premature merchant link, enabled button, missing near-offer disclosure, form, script, iframe, autoplay, injected tracking) and privacy hard-off/PII rejection/n=19 suppressed versus n=20 allowed. An initial 56/58 run exposed two mutation false negatives due to false reliance on `aria-disabled` and a separate disclosure in the guide; these tests were FIXED, and all 58 retested successfully. This is **not** a native Node test run; native repository checkout, host CI, and browsers remain unverified.

Programmatic check against the exact committed A/B found **byte-identical 14,232-character article core**, one H1 each, no merchant checkout hrefs or active offer. Editor-only source citations include merchant URL; reader HTML omits direct seller URLs to prevent bypassing a disabled CTA. Original SVG poster has text alternatives.

## Research and merchant references used
- Botvinick and Cohen (1998): https://doi.org/10.1038/35784
- Rohde et al (2011): https://doi.org/10.1371/journal.pone.0021659
- Holle et al (2011): https://pubmed.ncbi.nlm.nih.gov/24168532/
- Golaszewski et al (2021): https://doi.org/10.1002/brb3.2124
- Existing Puységur live source archive: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ (WordPress id 1377, authenticated read-only)
- Existing Focus Fieldbook: https://finalvestige.com/focus/ (WordPress id 1579, authenticated read-only)
- Official vendor catalog: https://inspire3.com/
- Actual Zen12 offer: https://zen12.com/hnp ; About https://zen12.com/about ; Research https://zen12.com/research ; checkout https://zen12.com/getstarted (no payment attempted)
- 2023 binaural beat EEG review (14 studies; NOT a Zen12 trial): https://pubmed.ncbi.nlm.nih.gov/37205669/
- NCCIH general meditation: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety (NOT Zen12 study)
- FTC endorsements: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC health claims: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Public Inspire3 Limitless Labs creatives https://inspire3.com/ll/ are **not permission** for Zen12. Targeted personal Gmail read-only search showed consumer sales promotions only, NOT Final Vestige-specific affiliate acceptance.

## Strict release hold and unverified items

Written Final Vestige-specific partner acceptance, exact product/tier earning URL, web/TikTok/email/creative permissions, current price and customer refund execution, independent substantiation of efficacy or removal, verification of actual merchant privacy terms, editorial legal review, WordPress staging sanitization, native Node tests/CI, true browser keyboard/touch/zoom/360/390/768/1440/1920 a11y, first-party video hosting and synchronized captions, Lighthouse/CWV and privacy approved instrumented A/B, actual conversion evidence, QD/art/Site QA and explicit founder release approval.

**Zero** WordPress CMS/menu/settings/production writes, zero changes to homepage PR #49 or agent #150, no change to canonical Mind PR #172, zero Jetpack/Focus list duplication, zero Dispatch #174 newsletter changes, zero merchant or affiliate activation, zero real-event collection, zero deploy/merge.
