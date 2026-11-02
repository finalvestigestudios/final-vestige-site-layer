# First-screen cinematic evidence composition — isolated homepage enhancement

## Creative goal

At the award-caliber benchmark, the *first screen* should make it immediately clear that Final Vestige follows authentic evidence. The existing hero contained an abstract FV orbit/monogram in its large right-hand card. This enhancement replaces it with original, explicitly non-facsimile editorial typesetting derived from the surviving **Victory Point Note** used in our published Franklin investigation.

- Correctly distinguishes 28 May 1847 original “All well” from April 1848 marginal addition about the abandoned Erebus and Terror.
- Adds an immediately available museum-record link on the first screen (Royal Museums Greenwich object HSR/C/9/1) and visible “not a facsimile” caution.
- Removes the decorative FV-only art and makes the artifact accessible to screen readers, with semantic <time>, labelled aside and actual link.
- Uses CSS-only layered original folio artwork, no new image bytes, network fonts or JavaScript. Existing three article images remain unchanged.
- Preserves the historical evidence room, seven-chapter Reading Trail, six other stages, existing Focus CTA, published Puységur bridge, and 72 Margins records on the *separate* existing WordPress homepage.

## Review & test

Python: `python -I -m unittest discover -s experience2/home-flagship/tests -p 'test_hero_arrival.py' -v` — execute on **exact** new GitHub checkout before QD. Also run all existing homepage tests and source gates. Visual QA at 320/360/390/768/1024/1440/1920, 200% zoom, no-JS, forced colors and reduced motion; preserve all variant controls. Archival text is source-grounded and does not invent a photo facsimile.

This enhancement is isolated in a new draft PR stacked on the existing exact-checkout browser QA PR #252, not deployed. It does not alter the frozen v1 PR #49, WordPress page 6, theme, plugins, site navigation, Focus list or live release governance. Independent art direction, complete WordPress staging, rights, CI, final QD and founder approval remain HOLD.