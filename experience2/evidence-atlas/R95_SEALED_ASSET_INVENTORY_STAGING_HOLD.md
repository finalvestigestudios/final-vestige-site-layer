# Apollo Evidence Atlas R95 — sealed input inventory and exported source custody

**RELEASE HOLD · review-only code · no WordPress or homepage write.**

## Actual defect

R94 already authenticated NASA record identities against R93/R92 and rejected unreviewed binary formats. However, its copying loop accepted **any additional** input with a `.html`, `.css`, `.js`, `.json`, or `.txt` extension. A stray unreviewed script or HTML page could enter the review archive, even though it did not appear in the inherited source custody receipts. Its R94 receipt hashed only its three newly generated files rather than the full exported review package. This is a staging artifact-custody gap, **not evidence that production was compromised**.

## R95 correction

- Pin the exact 15 inherited R92 assets/receipts plus six R93 source-passport outputs/receipt. Reject missing and additional files/directories, symlinks, and nonregular entries **before creating the output directory**.
- Verify the nine original browser assets against the inherited R91 asset-boundary receipt; enforce staging-only status, 24 verified source bindings, zero approved photograph rights, zero external asset dependencies, and deployment disabled.
- Hash all **24 exported files** in `R94_ATLAS_RECEIPT.json`: 21 inherited source files + R94 HTML/CSS/JS. The generated receipt is outside its own hash manifest, avoiding a circular hash. Existing genuine Chromium acceptance checks every receipt hash.
- Add 12 adversarial regressions covering unreviewed JS, HTML, JSON, directories, symlinks, missing passport scripts, altered inherited JavaScript, falsified asset-boundary status, source-root symlinks, and complete archive custody. Existing R94 regressions and historical source checks remain required.
- Independent R95 CI on the exact PR head includes pinned Playwright/axe/Chromium, 320/390/768/1440/1920px JS/no-JS checks, keyboard and touch, reduced-motion and forced-colors coverage, local LCP/CLS observation, reproducible screenshots, actual PDF, and deterministic twice-identical ZIP archives. These outcomes must **not** be claimed until the relevant jobs execute successfully.

## Reproduction from repository root

```bash
python -m unittest discover -s experience2/evidence-atlas/tests -p test_asset_inventory_r95.py -v
python -m unittest discover -s experience2/evidence-atlas/tests -p test_curated_atlas_r94.py -v
python experience2/evidence-atlas/tools/build_reciprocal_routes_r92.py /tmp/apollo-r92
python experience2/evidence-atlas/tools/build_source_passports_r93.py --src /tmp/apollo-r92 --out /tmp/apollo-r93
python experience2/evidence-atlas/tools/build_curated_atlas_r94.py --src /tmp/apollo-r93 --out /tmp/apollo-r95-a --archive /tmp/apollo-r95-a.zip
python experience2/evidence-atlas/tools/build_curated_atlas_r94.py --src /tmp/apollo-r93 --out /tmp/apollo-r95-b --archive /tmp/apollo-r95-b.zip
cmp /tmp/apollo-r95-a.zip /tmp/apollo-r95-b.zip
```

Use separate, empty output directories for reruns. CI requires the exact GitHub SHA and archive hashing.

## Historical and publication boundaries

Six NASA source links remain directly associated with their individual evidence records, with photographic dates not substituted for accident chronology. The crew portrait's proposed `S67-19766` association is provisional and its day is unknown; two January 24, 2017 commemorative images are not ordered within that day. No NASA photos are embedded; no geography, map pins, or causal edges are inferred; all six image-use assessments are pending.

**Do not merge or publish without** a successful exact-head source and real-browser QA run, source/editorial review, authorized hosted WordPress.com compatibility test, manual NVDA/VoiceOver and physical-device acceptance, rights decisions, and founder approval. Frozen homepage PR #49, homepage branches, and original Research Desk PR #158 are out of scope.
