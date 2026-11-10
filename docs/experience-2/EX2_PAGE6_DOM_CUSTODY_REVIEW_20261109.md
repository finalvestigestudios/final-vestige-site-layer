# EX2 Page 6: DOM-aware content custody — 2026-11-09

**Status: REVIEW ONLY / RELEASE HOLD.** Parent #1841; frozen #49 unchanged. This PR changes only Python admission tests and documentation. No WordPress writes, plugin install, merge, tracking, signup, content replacement, or spending.

## Reproduced false PASS in previous exact-head admission

The original regex-based `verify_homepage_preservation.py` checked matching source spans and the Jetpack string, but did not require preserved content to exist in the meaningful browser DOM. On synthetic fixture markup containing the approved 72 records, native Jetpack block, seven chapter IDs and Focus links, these transformations **incorrectly returned PASS**:

* Wrap the *entire* page fixture in `<!-- ... -->`.
* Wrap the entire fixture in `<template>...</template>`.
* Wrap the entire fixture in `<div hidden>`, `<div inert>`, `<div aria-hidden="true">`, or `style="display:none"`.

These mutations retain the original 72-record and Jetpack byte hashes. Thus an integration could satisfy the raw custody gate while making the historical archive and subscription UI unavailable to visitors.

## Change

The existing gate now runs `evaluate_dom()` as a **second, mandatory** check in the same CLI call. It parses real element starts/ends, excludes comment/template/script/style and hidden or inert ancestor subtrees, and requires:

1. 72 exposed numbered Margins records in exact order;
2. exactly one exposed native Jetpack subscriptions DOM block;
3. at least the canonical number of exposed exact Focus links;
4. exactly one exposed element for each of seven chapter anchors;
5. exactly one exposed evidence-flagship root.

It reports `dom_custody` with independent errors, and never authorizes release. Existing byte/hash checks remain mandatory. New regression tests show the original bypass rejected as HOLD, including individual inaccessible Jetpack/Margins controls and duplicate IDs; the existing 11 mutation controls remain.

## Important WordPress source-vs-rendered distinction

Read-only page ID 6 from the WordPress connector, modified `2026-11-05T12:07:24`, returns **different representations**:
- `context=edit` / raw Gutenberg content: 150,710 characters, 72 Margins spans, one `<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->` self-closing native block **comment**, and **zero rendered Jetpack DOM blocks**.
- `context=view` / rendered content: 171,183 characters, 72 Margins spans, one actual `wp-block-jetpack-subscriptions` outer div (class string occurs twice), and seven unique chapter IDs.

**Use `context=view` or an actual post-rendered isolated WordPress HTML artifact for DOM gate input.** Do not feed `context=edit` raw Gutenberg serialization and misreport a Jetpack DOM failure as an absent native block. The source integrity of the `wp:jetpack/subscriptions` block directive still needs a separately pinned canonical comparison; passing this static parser is **not** proof of a working Jetpack signup or confirmation. The previous inventory's `page_content_sha256` must be independently reconciled against the chosen rendered representation before the strict snapshot option can be treated as accepted.

## Reproducible commands from full checkout

```bash
python -I -m unittest discover -s tests/experience-2 -p 'test_homepage*preservation.py' -v
python -I -m unittest discover -s tests/experience-2 -p 'test_homepage_dom_custody.py' -v
python -I tests/experience-2/verify_homepage_preservation.py \
  --baseline tests/experience-2/page6_public_inventory_20261109.json \
  --candidate /path/to/authorized-isolated-WordPress-rendered-page6.html \
  --out /tmp/page6-custody-report.json
```

Fail closed if exact-footprint hashes drift or the DOM check fails. The standalone EX2 source alone **must** fail. Do not attempt a production overwrite.

## Limits and independent acceptance

`HTMLParser` is a conservative *static* DOM check, not a browser DOM, accessibility tree or computed-style engine. CSS selectors, overlays, JavaScript state, WordPress runtime, authentic media transfer, Jetpack delivery, Safari and WCAG/axe/Lighthouse have **not** been certified here. An isolated Playground/Assembler post-render and real browser review remain mandatory; a Playground result cannot substitute for hosted WordPress.com/JETPACK acceptance.

**Offer → step → blocker → experiment → evidence → owner:** Seven Day Focus Fieldbook → homepage to free resource/confirmed subscriber → historical material and Jetpack can be silently hidden while passing byte custody → DOM-aware admission gate → synthetic mutation suite; no measured commercial outcome → interim homepage engineering, founder retains release approval and Claude retains production integration/attribution.

No code changes to the seven-chapter experience, archives, art directions, 72 published items, Focus links or existing Jetpack block.
