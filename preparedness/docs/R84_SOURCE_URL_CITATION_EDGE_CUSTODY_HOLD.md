# R84 — Four-stage literal source-URL/citation-edge custody (PRIVATE DRAFT; HARD HOLD)

**Scope:** Final Vestige Preparedness Archive, Issue #136. Additive review-only engineering stacked on immutable R83 `783c5b8edd1bfd855b8b2d21fde3eb659818e36d`. This change must never authorize production deployment, content publication, WordPress writes or medical emergency advice.

## Research custody and independent review problem

R83 records unabridged citation context across the frozen, integrated, current-Claude and separate candidate snapshots, but citations can still point to distinct original records sharing a raw ID, to different URLs with similar appearance, or to URLs containing credentials, ambiguous authorities, local addresses or misleading escapes. A visually well-formed citation is **not** evidence that its URL was opened, that its source supports the adjacent claim, or that its advice is safe.

R84 reconstructs **all seven Claude-origin source fragments across all four snapshot stages** using the exact existing R82/R83 sealed histories. It connects each R83 citation occurrence to all matching stage+origin+literal-ID+reading-digest research identities. It preserves complete original source-reading objects and exact literal URLs without stripping queries/fragments, changing case, decoding percent escapes, rewriting metadata or resolving two different identities into a single source. Any citation outside the seven-fragment scope remains explicitly outside scope; R80 is the independent **complete** 35-article/six-tool archive census.

## Deterministic invariants and review outputs

- R82 and R83 source/context reports must independently verify and remain `HOLD`. Every candidate source reading must independently match its SHA-256 and literal raw ID.
- All four stages keep **every complete source record**, every citation occurrence, each distinct origin-scoped variant, and the full R83 citation context's immutable SHA-256 pointer. Original unabridged text remains reconstructible in R83; original complete source evidence resides in the R84 catalog.
- Duplicate URLs are grouped **only by exact literal equality within a stage** and are never merged. Case variants and alternative encodings remain distinct, even if a browser might treat them as equivalent.
- URL observations flag non-literal HTTPS, embedded credentials, port ambiguities, escapes in authorities, malformed percentages, IP/local hosts, fragments, queries, control characters, backslashes, non-ASCII, path dot segments and parser failures. These are **human-review cues, not proof of malicious or invalid links**; **there is no network request or live link validation**.
- Downstream citation crosswalk fails closed when a claimed source variant has no matching original stage+origin+ID+reading digest, when a candidate has the wrong ID, or when a multi-origin ambiguity is falsely represented as one verified source.
- Private one-way reviewer CSV uses inherited formula-safe encoding, includes only review candidates, is kept in temporary Actions storage and deleted. Never upload private ledgers as public artifacts or inject them into the website.
- All approval counters are zero, all source and claim assessments `NOT_REVIEWED`, `medical_safety_approved=false`, `may_publish=false`. A cryptographic hash verifies **custody only**, not truth, relevance, medical safety, URL accessibility or publication readiness.

## Exact-head acceptance process

The isolated draft PR workflow requires the fixed R83 parent, an exact four-file ADD-only diff, Python 3.12 compilation, adversarial source/URL tests (including synthetic no-write fixtures), real historical Git source reconstruction, rebuilt four-stage citation edges, existing Python validator, private WordPress-ready offline build, and the entire Preparedness Python regression suite. CI success means **diagnostics only**; an independent mandatory release-integrity workflow remains binding and is never bypassed.

## External dependencies and unsatisfied release gates

Read-only independent coordination pins: safety QA draft #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; food synthetic fixture draft #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5`, which still contains an original shared-working-tree temporary duplicate fixture; homepage #49 at `10495883299d53596992c26a8987f629b2904670`; flagship #604 at `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`; separate Preparedness RC #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706`. None are modified or merged.

**Unresolved:** historical five-contributor frozen baseline parity; human source/URL and exact claim-support verification; unresolved source identity/URL and fallback decisions; 15 safety exceptions; 22 RC editorial decisions; qualified high-consequence water/food/medicine/generator/CO review; WordPress browser, responsive and assistive-technology QA; independent QD signoff and explicit founder publication approval. Do not report QD PASS or assert historical food/medical instructions are safe.

**Publication decision: HARD HOLD.** No new published pages, public navigation or CMS writes. All output remains private draft engineering.
