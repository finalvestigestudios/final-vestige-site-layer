# 43-source recovery queue + 15 oversized media originals (offline reconciliation, 2026-11-09 UTC)

## Outcome, limitations, custody
New **read-only joined triage queue**, NOT new live visitor evidence. It normalizes **43 distinct stored image slots** from six existing, immutable source audits: 6 P0, 7 Florida Memory, 8 Navy, 8 Palomares, 10 Archimedes and 4 non-P0 Three Mile Island. Different from the historical **42 reportedly broken images**; **0/43** are proven broken or healthy in a guest browser. Source images have actual stored URLs and prior **external web-retriever wrapper** results; wrapper 404/403/500/400/502 are NOT origin/visitor HTTP responses.

The P0 sequence is 285:5, 285:2, 287:5, 418:1, 418:2, 407:1. Site QA **#154** owns its preexisting cold full-scroll Chrome/CDP collector; do not duplicate it. Next sample a single Florida Memory post 432 page with seven www→apex redirect wrapper anomalies **as one correlated host hypothesis**, not seven separately confirmed outages. Then Navy Pueblo/Honda image dependencies, Archimedes rights conflicts and Palomares Commons redirects.

Read-only WordPress original-size metadata additionally documents **15 originals over 1,500,000 bytes** totaling **47,096,779 stored bytes**, including **11** referenced inline originals across 8 posts (**38,480,915 stored original bytes**). Five large PNGs lack WP-generated subsizes. These original media sizes are **not visitor transfer bytes**. No valid 76%-reduction claim exists without same-cohort cold paired CDP measurements, source identity and matched slots. Read historical `docs/IMAGE-WEIGHT-WORKLIST.md` from Draft #183; absent from `main`.

## Implementation
- `qa/media-recovery/cross_ledger_43_source_15_oversize_20261109.json` — 43 exact published URLs, tool-only wrapper outcome/label, catalog URL and tier (official/Commons/third party), rights observations, conditional 960px no-upscale where known, source blob SHAs, 15 original sizes and matched inline posts, all **null** guest status/wire results.
- `qa/media-recovery/validate_cross_ledger_43_source_15_oversize_20261109.cjs` — frozen exact slot→original URL/catalog/wrapper/ledger SHA registry, constraints preventing claims of browser confirmation or rights clearance, 960px and original-byte guards.
- `qa/media-recovery/test_cross_ledger_43_source_15_oversize_20261109.cjs` — positive control and 22 synthetic forged-evidence / accidental-alteration negatives.

Source SHA pointers remain to the six **existing draft audit PRs**, not copied collector code. Source data from Archimedes is a **frozen Oct 30** snapshot, unlike live WP readbacks in other cohorts; do not silently call all 43 current live. Expanded 66-post/361-inline cohort was captured separately from historical 61-post/355 cohort; 76% must use exactly matched baseline and candidate source inventories. No rights are granted by this ledger.

## Release and fallback
Capture guest browser per slot: stored original URL, runtime `currentSrc`, cold request ID, final HTTP/MIME and redirect chain, response cache flags (disk, SW, memory), decoded width+height, actual encoded bytes, desktop+mobile screenshot. Only verified load failures become replacement candidates; use item-level primary-source catalog rights, verify exact scene/crop and label readability, document credit, and limit staging derivatives to width <=960px without upscaling. Preserve original source, WP media ID and block JSON for rollback. **Do not change Gutenberg post blocks, upload, local-cache, publish or deploy without separate explicit approval.**

No external media binaries scraped/downloaded, no WordPress production changes, no homepage design modification, no commercial spend. Native Node CI and real logged-out Chrome remain separate pending checks.
