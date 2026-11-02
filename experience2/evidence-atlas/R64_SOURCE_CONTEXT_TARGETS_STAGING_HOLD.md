# Apollo R64 — NASA context-link accessibility and complete private-staging triplet (HOLD)

Scope: Issue #150 / original R38 Research Desk + source-built Evidence Atlas. The original Research Desk PR #158, frozen homepage PR #49 and lead homepage branches have not been edited. All files in this PR are restricted to experience2/evidence-atlas/.

## Reproduced defect

In real Chromium, the NASA technical context link and NASA media-rights guidance link measured approximately **22px and 18px tall** on desktop. This fails the team's 44px target for important source-navigation touch controls. The earlier R63 semantics pass had not audited both source-reference hitboxes.

## Source-controlled correction

The cohost-only CSS now makes those two real NASA links at least **44px** tall, underlines them in all normal/forced-colors modes, gives keyboard focus a visible outline, and appends original href URLs to paper output. Responsive links wrap without horizontal overflow. The cohost stylesheet cache version is now **0.0.64-staging**. No NASA image binaries, photo identity, dates, geographic claims, original R38 source, Atlas runtime CSS/JS, or catalogue rights assertions changed.

The complete WordPress **distribution triplet** builder now packages and SHA-256 indexes the exact R38 Research Desk plugin (five Git-blob-pinned files), compiled Atlas plugin, and suite adapter/CSS, with a fail-closed STAGING_HOLD manifest. The builder never performs WordPress writes, installation or activation.

## Reproduction

Run the repository's Python unittest discovery under experience2/evidence-atlas/tests, the original test_atlas.py, browser_r64_source_target_acceptance.py with --output, and build_full_staging_r64.py with --output. The R64 bundle builder accepts --qa and --output; run twice and compare byte-for-byte. PHP lint and Node syntax tests are separately required.

R64 Chromium: **32 cases** across 320,360,390,428,768,1024,1440,1920px, JS on/off, normal/forced colors. Tests verify source URLs, noopener, keyboard focus, ≥44px hitboxes, print URLs, source integrity, no external requests, no-JS content and complete print custody. The existing R63 runner is a separate 32-case regression. The four original PHP cohost profiles are retested against copied distribution bytes.

Observed local LCP/CLS are **fragment-lab** only, not p75 hosted Web Vitals. The single skipped unit test is an R38/PR158 fixture limitation.

## Release gate: HOLD

Actual WordPress/Assembler installation and asset loading, checksum-verified axe-core execution, NVDA/VoiceOver, independent QD, hosted Core Web Vitals, and exact-head CI remain outstanding. Image-rights reviews remain **0/6** and the S67-19766 catalogue-to-photo association is provisional. No merger, deployment, WordPress change, paid services or unreviewed geographical pins are authorized.
