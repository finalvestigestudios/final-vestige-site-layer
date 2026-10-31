# Apollo Experience 2.0 — R14 source concordance (PRIVATE STAGING / HOLD)

Parent: R13 draft PR #262, commit `f5423c6058f2f9b677634dfd1ca4a6334ece0f3d`. Canonical Apollo casefile remains the **12-blob-verified** PR #215 commit `74375657f2cdaac0710f94c6de6c24534ee06858`. Research Desk draft PR #158 and frozen homepage PR #49 were not touched.

## Implemented

A six-card photograph-to-claim **Source Concordance** is generated offline from the original pinned `apollo-casefile/records.json`, inserted in private PHP staging review between the hero and chronology, and served only to permitted WordPress staging editors with a valid nonce. It distinguishes 1966 rehearsal photos, 1967 preparatory/aftermath photographs and 2017 tribute exhibits from the historical claims they are used to contextualize. Each card has a native anchor to the pre-existing claim, the exact original NASA catalog URL and a no-JS `<details>` disclosure giving the image's limits. No new imagery, inferred location pins, third-party scripts or network calls are used. Source rights remain **HOLD_PER_ITEM_REVIEW**, with no NASA endorsement implied.

The 7 original canonical assets retain their PR #215 integrity pins. Two additional **derived** assets (`source-concordance.html`, `.css`) are compressed into the authenticated single-file staging PHP plugin and independently SHA-256 checked before delivery. The HTTP response exposes a concordance SHA-256 header. The separate, read-only staging admission probe checks that header, the six rendered records, exact original fragment/exports, role restrictions and nonce denials. If any required asset fails its hash or its record count, PHP responds with HTTP 503 rather than partial content. No static public plugin assets are created.

## Executed checks (local exact authored source bytes)

- `PYTHONPATH="$PWD/qa:$PWD" python -m unittest discover -s qa -p 'test_*.py' -q`: **56/56 PASS**. Includes source-date and host mutation denials, permission/nonce tests, a repaired HTTP fixture alias, staging admission SHA tampering, original custody gate and NASA editorial metadata gate.
- `PYTHONPATH="$PWD/qa:$PWD" python qa/browser_exact.py`: **7/7 Chromium/Playwright widths PASS**: 320, 360, 390, 768, 1024, 1440 and 1920 pixels; responsive reflow, six-card navigation, 44px route/disclosure targets, keyboard Enter toggles, touch, no-JS native disclosure and synthetic 200% zoom.
- `python build_sealed.py --out /tmp/apollo-a.zip` twice with distinct output paths: **byte-identical**, SHA-256 `4f57acab377142c0d665209e896087645078b28389b4cc09c2aea5824263db2a`.
- `php -l fv-ex2-apollo-sealed-template.php`: **PASS**.
- R14 browser run synthetic LCP observations: **304ms (320), 132ms (360), unavailable (390), 140ms (768), 140ms (1024), unavailable (1440), 176ms (1920)**. Synthetic CLS: **0 at all 7 widths**. These are offline Chromium observations; never call them hosted CWV.
- Screenshot SHA-256: desktop `6256cd06921a8f225cd942b0369234b03b3607cca2a76a98695fa88ab6a37e03`; mobile `76f1d29ad2447984c1eb02905a612bcbb82da4a7f4ce7bbca80ca884e1ee541e`.

## Hard release blockers

**HOLD**: no authorized WordPress instance was installed or modified; the locally available test harness implements PHP HTTP transport with a **synthetic** WordPress stub. Actual Chromium HTTP-origin navigation was attempted but blocked by environment policy (`net::ERR_BLOCKED_BY_ADMINISTRATOR`) and is NOT a PASS. Verified axe-core bundle remains unavailable, so WCAG automated certification is NOT RUN and `--require-axe` must fail closed. Safari/VoiceOver/NVDA, current Assembler/Jetpack integration, item-level NASA media rights, public-domain/likeness analysis, hosted LCP/CLS/INP, hosted CI, independent QD and founder visual approval remain pending. Zero production/main/WordPress writes, activation, deployment, paid-service use or invented geographic relationships.

## Reproduction

From `experience2/apollo-wp-bridge/sealed` on the exact R14 branch with Python, PHP and system Chromium/Playwright installed:

```sh
PYTHONPATH="$PWD/qa:$PWD" python -m unittest discover -s qa -p 'test_*.py' -q
PYTHONPATH="$PWD/qa:$PWD" python qa/browser_exact.py
PYTHONPATH="$PWD/qa:$PWD" python build_sealed.py --out /tmp/apollo-r14-first.zip
PYTHONPATH="$PWD/qa:$PWD" python build_sealed.py --out /tmp/apollo-r14-second.zip
sha256sum /tmp/apollo-r14-{first,second}.zip
php -l fv-ex2-apollo-sealed-template.php
# A release gate MUST fail until a verified axe bundle is provided:
PYTHONPATH="$PWD/qa:$PWD" python qa/browser_exact.py --require-axe
```

The six NASA catalog references were previously checked on **October 30, 2026**; the offline R14 builder checks data consistency, not live URL freshness, license grants or NASA approval. See `qa/NASA_R13_SOURCE_AUDIT.md` and NASA's [Images and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/).
