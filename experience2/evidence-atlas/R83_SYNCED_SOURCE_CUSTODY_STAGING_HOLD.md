# Apollo R83 — nested Gutenberg source integrity (STAGING_HOLD)

**Scope:** Isolated Research Desk/Evidence Atlas browser acceptance. No images, pages, plugin installations, production WordPress changes, or media permissions are introduced. Homepage PR #49, lead branches, and original Research Desk PR #158 remain untouched.

## Previously untested

The R77 synced-pattern WordPress gate required six Atlas records, six Desk records, and 84 custody values, but did not verify that the **rendered nested pattern** kept the six original NASA destinations and six unique citation identities. A CMS integration could preserve element counts while changing an external source link. It also did not open/close a native SourceDrawer using **Enter with JavaScript disabled** in nested Gutenberg content.

## R83 correction

The real WordPress 390px/1440px, JS/no-JS cases now validate the exact six NASA URLs in approved R37 order, citation IDs 01–06, six native source disclosures, the unchanged zero-image and zero-geographic-claim constraints, explicit no-rights-clearance and provisional S67-19766 notices, and an independent **0 of 6** media-clearance statement. The first source disclosure must open and close with keyboard **Enter**, restoring its initial state before the original print, axe, interaction, and local performance checks. The negative-pattern control remains no-op.

The source checker never uploads URLs or DOM strings: outcomes contain counts and booleans; failures use allowlisted static codes in the existing R81/R82 confidential diagnostic pipeline. Twelve mutation tests cover link order, lookalike hostnames, missing/duplicate citations, lost disclosures, injected imagery, speculative coordinates, and false NASA rights/catalog assertions. Legacy 14 ordinary plus five nested browser cases remain required.

## Reproducibility

Run `python -m unittest discover -s experience2/evidence-atlas/tests -p test_wp_source_parity_r83.py -v`, plus the R81/R82 diagnostic tests; the dedicated Apollo Actions workflow must run against the exact reviewed SHA with official Assembler and real Chromium/axe, produce screenshots and native printed PDF, and preserve full fail-closed gates. Deterministic R78 archive manifest includes all changed R83 source files.

## Release HOLD

Successful local WordPress testing does **not** verify WordPress.com hosted compatibility, independent QD, NVDA/VoiceOver, physical devices, or production Core Web Vitals. Photograph-specific rights remain 0/6 cleared, catalog S67-19766 remains provisional, and the earlier intermittent synced-pattern failure's cause is not proven. The independent production homepage P0 rights issue is also unresolved; no publication, merge or WordPress write is authorized.
