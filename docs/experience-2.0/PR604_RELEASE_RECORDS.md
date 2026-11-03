# PR #604 release records (kept outside the frozen PR)

PR #604's head `368399842de1bd4fc02598571c0fa29eb5ad279c` is frozen for review. These records are on a separate branch so the review stays valid. Anything here that must reach the PR itself would be a new commit and needs a fresh exact-head review.

## Status after the independent review (2026-11-02)

Reviewer: ChatGPT, comment https://github.com/finalvestigestudios/final-vestige-site-layer/pull/604#issuecomment-6588886797. Verdict **HOLD**; `FVSL-QD-PASS: NO` for head `368399842d...` and package `d73124ab...656d6b`. Source-level integrity checks passed. The reviewer ran no browser test, no authenticated WordPress.com render, no screen reader or device.

| Condition from the review | State |
|---|---|
| Exact 108,152-byte block rendered in authenticated WordPress.com draft 1902 | **Open.** Needs a signed-in browser session; the assistant does not enter credentials. |
| Named-editor NASA item-specific sign-off | **Open.** Needs a named person. |
| Independent reproduction of the browser and accessibility claims on the immutable head | **Done by a second session** and recorded in the PR at `experience2/home-flagship/release/INDEPENDENT_REPRODUCTION.md` (evidence for the reviewer, not a QD pass). Most claims reproduced; **the keyboard claim was overstated and hid a real defect** (flagship skip link obscured by the header). |
| Decide or fix the 4.58 s mobile LCP | **Decision recorded below.** No LCP code change. |
| Correct the stale 114,355-byte statement in `RELEASE_AND_ROLLBACK.md` | **Corrected in the new head** (the skip-link fix forced a new head anyway, so this no longer costs a review). |

**The head changed.** PR #604 is now `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`; the replacement block is 108,155 bytes, SHA-256 `506aa8d9d9d9c3fe7821d8e479dc8857957667f06f5f6ea5432e3f3ad0fbc7c9`, SHA-1 `8c0dd5c3adce073fd58f5001e0f90d523ffad277`. The review above applies to the **previous** head `368399842d...` only, and its HOLD stands for this one until a fresh review is recorded. Hosted `verify` is green on the new head.

## Erratum (resolved): replacement block size

At head `368399842d...` the runbook said the replacement block was 114,355 bytes; the real object was 108,152 bytes (SHA-256 `d73124ab...`), as the reviewer found. The runbook now says 108,155 for head `bdf01b4a3e...`, and states that the descriptor is authoritative if the figure ever disagrees. An operator must use the descriptor and hashes.

## Decision record: mobile LCP (P1)

**Facts (lab, from the acceptance matrix, not field data):** candidate mobile LCP 4.58 s in Lighthouse "simulate" (target 2.5 s) against the live homepage's 9.21 s in the same mode; applied-throttling ranges overlap (candidate 2.6-3.3 s, live 2.8-3.2 s); transferred bytes about 644 KB vs 1,287 KB; no LCP regression. The model-based LCP did not respond to font, preload, CSS or `will-change` changes tried; `content-visibility` on preserved sections cut blocking time.

**Decision (under the founder's 2026-11-02 authorization to make release-risk calls):** accept as a **documented P1 exception for the first release** only because the candidate is not slower than the page it replaces and sends about half the bytes, and because the only way to move the number materially is to change the candidate, which forces a new review and delays a measured improvement. **This is not accepted as the standard.** A follow-up candidate must target the actual LCP element and re-measure; the founder's directive calls 4.6-6.2 s unacceptable long-term.

**Conditions on the exception:** (1) reviewer must agree the exception is acceptable (their comment lists it as a failing criterion; this record does not override it); (2) the post-publish check records real-user LCP from Search Console / CrUX once data exists, because lab numbers here are not field data; (3) the follow-up candidate is opened as its own PR immediately after release.

## What still blocks publication

Publication needs all of: a reviewer `FVSL-QD-PASS: YES` on the exact head (or a new head and fresh review), the NASA named sign-off, the authenticated WordPress.com render of the exact block, and then the hash-locked apply with the lock tokens rechecked immediately before the write. None is waived here.
