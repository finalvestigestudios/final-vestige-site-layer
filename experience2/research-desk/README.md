# Experience 2.0 / Apollo 1 Research Desk — staging-only source

This directory contains an **exact source-controlled copy** of the four core files from the ChatGPT-produced Experience 2.0 v4 Research Desk WordPress staging candidate. The file contents were verified against the original local files using Git blob IDs. Nothing in this branch is live or approved for activation on finalvestige.com.

## Files and original Git blob SHA-1

- `final-vestige-ex2-research-desk.php`: `d1879a90101b5475990132369178f42743f4b57c`
- `assets/source-ledger.css`: `b8cf00afeceba115a9e9d19044fc11dcf2890cbe`
- `assets/source-ledger.js`: `32e757cc4dc8708397ff65ac21e89dd319781d78`
- `templates/ledger.html`: `403d128c57b9bc82dac7c619651689070edef86c`

WordPress shortcode: `[fv_ex2_research_desk]`. Static HTML lists six NASA source/limitations; optional JS search activates only if the expected DOM is present. A missing template falls back to a link to the original Apollo 1 investigation. The staging plugin is deliberately independent from Site Layer PR #49.

## Verified local preparation

- Original v4 Foundation archive: `d41fdeaa62ad1d71da8a0399146189855c4208bce45cd7642443fc183d91e4ff`.
- On 2026-10-30, executed `python verify_all_v4.py` from the extracted v4 bundle: all six checks PASS, including real-browser tests where available, builder, Atlas, concept board, flagship, ledger, PHP lint.
- The committed four file Git blob hashes above match those original local files. This confirms source identity, **not** production integration or media delivery.

## Release blockers

1. No WordPress staging install, CDN/media transport test, current Assembler theme interaction QA, Jetpack scripts compatibility or caching/shortcode lifecycle smoke yet.
2. Accessibility manual tests in Safari/VoiceOver/NVDA and actual device performance are open.
3. This adapter currently loads assets only when the top-level singular post contains the shortcode. A shortcode rendered from a reusable pattern, template part or nested dynamic block may miss those assets. Staging must test this before release.
4. The core v4 Apollo 1 immersive narrative and Atlas are still in the source ZIP, **not** in this plugin branch; do not claim they are integrated.
5. Do not merge/deploy without founder visual approval, independent QD, green hosted CI and an exact release artifact.

## Follow-up

Continue on a separate branch with actual published WordPress environment tests, validate real NASA asset source and reuse conditions, determine shortcode asset-loading coverage, test CSS against Assembler, and promote only after source/QA review. Project charter: [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150).
