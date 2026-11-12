# Media Recovery — six priority source recheck and visual-parity cold-pair gate

**Pacific date:** 2026-11-11. **Ownership:** media recovery PR #1703, not homepage lead or Site QA browser collector PR #154. Historical worklist is in separate draft #183 at Git blob `2acd06a4ca4317646006eb6591face3fe76fedec`, not on main.

## New actionable engineering

The preexisting `measure_image_transfer_pair_20261111.cjs` correctly uses completed, uncached CDP Image request bytes and deduplicates shared request IDs, but a synthetic 1,000 B → 240 B result (76% **single-post** reduction) could still pass without browser-selected **physical image pixel** evidence. A 390px-wide decoded image displayed 390 CSS px on a DPR 2 device is inadequate despite unchanged DOM `naturalWidth` or an acceptable HTTP/byte measurement. Source substitution could also be accepted from row-local rights flags before a separate approval record was supplied.

The **additive read-only** `compare_cold_pair_visual_parity_20261111.cjs` wraps the existing evaluator rather than changing it or Site QA's collector. It requires decoded physical selected-source dimensions tied to exact `currentSrc`, sufficiently dense images for `painted CSS size × devicePixelRatio`, coherent aspect ratio, visible painted dimensions, and identical CSS box/object-fit/object-position across runs. A changed asset additionally needs separately supplied scene, rights, provenance and editor-review fields. A result can **never authorize production** or prove **site-wide** 76% savings.

**Implementation boundary:** this is a second-stage offline gate. Existing callers of the older comparator are *not* automatically upgraded. A capture adapter or caller must deliberately invoke the new gate and supply selected-source physical resolution. Empty/absent fields yield HOLD; do not guess pixel dimensions from `naturalWidth`. Do not infer copyright from official archive hosting; independent reviews are inputs, not authority created by the program.

## Fresh six-source status recheck

The six exact WordPress stored image origins yielded independent **web-retriever wrapper** observations on Nov 11, in priority order: `285:5=404`; `285:2=500 (redirect inaccessible)`; `287:5=404`; `418:1=403`; `418:2=403`; `407:1=400 (unsupported binary type)`. These are **not real origin GET statuses** and **not a Chrome visitor HTTP finding**. The source audit stores exact originals, official/best replacement catalogs, rights holds, verified 819×614 and 604×590 candidate sizes where known, and null guest HTTP/decoded/wire fields. Browser evidence owner remains Site QA #154.

Full machine audit: `qa/media-recovery/p0_6_recheck_visual_pair_gate_20261111.json`. Existing primary-source photos remain candidates only (Commons Three Mile Island, 1979 President's Commission, Florida Memory RC09236 different-photo alternative, USCG Pettit portrait, Coast Guard Museum Scotch Cap scene, USGS Hebgen photo). Exact scene, license, derivatives and published captions require separate verification. Do not download or cache candidate binary.

## Validation

- Exact GitHub-committed source and regression tests were independently fetched and run in an isolated V8 CommonJS-compatible harness: **17/17 pass**. This is not native Node CI or actual Chrome/CDP.
- A separate native Node local sanity run also passed 17 tests against locally reproduced parent evaluator logic. It does not certify GitHub CI.
- Site QA must produce logged-out cold full-scroll screenshots, requestId-bound completed network evidence, decoded physical resource dimensions, painted CSS geometry and DPR; no second collector has been made.
- Historical 61 posts / 355 inline / 288 offsite; expanded prior 66 / 361. The reported 42 missing images remain guest-unconfirmed. Fifteen >1.5 decimal MB WordPress originals sum to **47,096,779 stored bytes**, not transfer bytes. Proposed 76% improvement is unmeasured.

**No production WordPress changes, binary downloads, cache mirroring, homepage design changes, merge, deployment or subscription spend.** Keep PR #1703 draft.
