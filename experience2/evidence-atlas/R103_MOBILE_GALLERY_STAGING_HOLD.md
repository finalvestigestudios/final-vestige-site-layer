# Apollo R103 — responsive source comparison (STAGING HOLD)

This is an **isolated, derived source package**, not a change to the frozen homepage PR #49, the lead homepage lane, or Research Desk PR #158. Base: R102 draft #853. It reuses the actual sealed R99 seven-view WordPress staging package, retaining all original NASA records, reference links, photograph-date limits, all six uncleared photographic rights, and the `edit_others_posts` editorial permission boundary.

## Meaningful R103 improvements
- On phones, the comparison table retains **native semantic table markup** inside a visible, keyboard-focusable horizontal-scroll region with a label and explicit swipe/arrow-key instructions; it no longer relies on cramped three-column cells.
- Each source card provides a **native View comparison link only after exactly two records are selected**. The link uses the document fragment and needs no custom navigation. A rejected third source does not create a false third comparison, and Clear comparison hides the links again.
- No-JavaScript mode leaves all six NASA source records and source links visible, with enhancement controls hidden. Reduced motion, forced colors, and 320–1920px viewports are tested.
- Only the R97 gallery HTML/CSS/JS and **their three exact compiled PHP SHA-256 pins** are changed in the derived, independently packaged preview. Seven view records and NASA source URLs stay intact. Original R99 receipt remains as an *input-only historical artifact*; the new R103 manifest is the authoritative output hash inventory.

## How to reproduce
From an **unchanged R99 build** produced by the current R92→R93→R94→R97→R98→R99 tools:

```sh
APOLLO_R103_R99=/path/to/r99 python -m unittest discover -s experience2/evidence-atlas/tests -p test_mobile_gallery_r103.py -v
python experience2/evidence-atlas/tools/build_mobile_gallery_r103.py --src /path/to/r99 --out /tmp/r103 --archive /tmp/r103.zip
python experience2/evidence-atlas/tests/browser_mobile_gallery_r103.py --package /tmp/r103 --out /tmp/r103-browser --axe /path/to/axe.min.js
```

The dedicated GitHub Actions workflow builds the entire source chain, tests SHA sealing against eight adversarial conditions, generates and byte-compares two deterministic ZIPs, PHP-lints the sealed preview, and executes 10 actual Chromium JS/no-JS viewport configurations with mobile taps, keyboard scrolling, native comparison links, forced colors, reduced motion, overflow checks, axe scans and hash-receipted screenshots. The browser harness uses **local `set_content` with trusted CSS/JS inlined**, not a WordPress route or hosted CMS, so CSP, authenticated routing, and WordPress compatibility require separate R103-specific testing. Do not report LCP/CLS or hosted CWV from this harness; the earlier R102 WordPress/Assembler LCP variability (2540ms failure vs 560ms retry) remains unresolved.

## Release restrictions
**NOT APPROVED:** six NASA photo-specific rights clearances remain **0/6**; S67-19766 crew portrait identification/day are provisional; no inferred map pins or edges; source-editorial, rights, WordPress.com/Assembler, physical device, NVDA/VoiceOver, field CWV, QD review and founder approval remain pending. No WordPress content/settings/plugin writes, homepage branch touches, production deployment or paid services.