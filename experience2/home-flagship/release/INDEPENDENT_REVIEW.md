# Independent automated review of the polish round (not QD acceptance)

**What this is:** a fresh-context reviewer (a separate model session with no prior context, read-only) examined commit `71f1f23b9346e40f164bc7bf21ee998ebba2fcb5` against `5f87f1b0a48ed2f17ecca49a60c44a482ca530de` on 2026-11-02.
**What this is not:** the independent **QD** acceptance the authorization requires. That needs a named human reviewer on the exact final SHA and has **not** happened.

## Result and disposition

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | `.fv-hf details > summary{display:inline-flex}` (my 44 px rule) overrode the grid layout of the inquiry and Observer accordion headers; column widths collapsed (e.g. 101/957/65 -> 26/960/65 px at 1440) | **P1, real regression I introduced** | **Fixed.** Rule now `details:not([class]) > summary{display:list-item;...}`; verified: classed accordions compute `grid` again, plain disclosures keep their marker (`list-item`, 44 px). |
| 2 | `<noscript>` image twins redundant and double-stack opacity when scripting is off: current Chrome fetches the lazy image itself; my earlier "photos not fetched" FAIL came from a too-short wait | P2 | **Confirmed by test and fixed:** with the twins stripped, JS-off still loads 3/3 photos (3 requests); with twins 6 images/4 requests. Twins and the test/contract changes that tolerated them are **removed**. The earlier A14/A21 "FAIL" was a harness artifact and is withdrawn. |
| 3 | No test of fragment navigation into `content-visibility`-skipped sections (`#dispatch`) | P2 | **Added** to `run_wp_qa.py`; result: target in view, Jetpack form visible. |
| 4 | Rollback procedure covered operation 1 only | P2 | **Fixed** (`RELEASE_AND_ROLLBACK.md`: reverse order, `content_hash` equality only after both are reverted). |
| 5 | JSON still said "NOT TESTED" for inline survival; dry-run conclusion stronger than a 957-byte probe supports | P2 | **Fixed**: wording now "probe-level only; exact block not yet stored". |
| 6 | Matrix referenced a missing `INDEPENDENT_REVIEW.md` | P2 | This file. |
| 7 | `contrast_audit.py` did not reveal inactive case panels | P2 | **Fixed**; audit now reveals all three cases and covers the page in a head pass and a tail pass (Chrome blanks full-page captures beyond 16,384 px). Result: 0 failures. |
| 8 | Lighthouse accessibility 96 vs 100 unexplained | P2 | Explained: the same two preserved-content items on the live page (Focus button label, fixed by optional operation 2; frame-dependent contrast on the rotating Margins strip). |
| 9 | "Lower blocking time" only holds in simulate mode | P2 | **Narrowed** in the matrix: simulate mode only; applied-throttling runs overlap the live page. |
| 10 | Shipped block exposes internal authoring comments | P2 | **Fixed**: CSS `/* */` and HTML `<!-- -->` comments are stripped from the inline block. |
| 11 | No EOL protection for the production block files | P2 | **Added** `.gitattributes` marking `release/production-change/*` as `-text`. |

Categories the reviewer reported as **no findings:** hashes and apply/rollback parameters (all recomputed and matching), breakout sequences in the block (4 `<script>`/4 `</script`, no `<!--`/`-->` inside), duplicate IDs against the preserved page, CSS scope, no overstated QD/WordPress.com/field-CWV claims, source tests (only the 6 expected environment errors) and the 21/21 contract check.

## Still not done by anyone

Human QD acceptance; authenticated WordPress.com render of the exact block; NASA item-specific sign-off.
