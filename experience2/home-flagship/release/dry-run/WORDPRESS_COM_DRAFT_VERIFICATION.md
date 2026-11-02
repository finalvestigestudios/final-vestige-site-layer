# WordPress.com private-draft verification (authorized 2026-11-02)

**Scope used:** one private draft page, **ID 1902**, titled "FV flagship dry run (PRIVATE DRAFT - delete after verification)" on site 256784396. Created with `pages.create` status `draft`, comments closed. It has never been published. Page 6, navigation, theme, plugins and subscriber settings were not touched (page 6's six block hashes, `modified` and `content_hash` were re-read before and after and are unchanged).

## Verified on WordPress.com

| # | Question | Result | How |
|---|---|---|---|
| 1 | Does the editor keep an inline `<style>`? | **YES** | Raw (`context=edit`) and rendered (`context=view`) content both returned the `<style>` unchanged, no `_content_warnings`. |
| 2 | Does it keep an inline `<script>`? | **YES** | Same. A JSON-LD script already lives in page 6 block 5; an executable inline IIFE with arrow functions and template literals also survived. |
| 3 | Does it keep `<noscript>` with an `<img>`? | **YES** | Same (no longer used by the candidate: the no-JS photographs load without it). |
| 4 | Does sanitisation alter hazard characters? | **NO** | Probe 2 contained `>`, `~`, `+`, `::before`, `:where`, `:is`, a `data:` URL, `@media`, `&&`, `\|\|`, `<`, `>`, a regex literal, a template literal with `${}`, and `&amp;`. The draft's `block_hash` from `page-sections.list` equals my local SHA-1 of the same bytes (`8346f10143988d7793c1021c061752edb7834939`): stored byte-for-byte (`dry-run/probe2-block.html`). |
| 5 | Is the draft exposed publicly? | **NO** | Signed-out request to `https://finalvestige.com/?page_id=1902&preview=true` returned the theme's "Page not found". |
| 6 | Could the draft subscribe anyone or post a form? | **NO** | The probes contain no form. The full candidate does not contain the Jetpack block; the Jetpack subscription lives only in page 6 block 3, which the dry run does not include. |
| 7 | Was page 6 changed? | **NO** | `page-sections.list` on page 6 before and after: same six `block_hash` values, `modified` `2026-10-30T09:14:14`, `content_hash` `7afdb933d2ec68fd993ef015c97a6eb9edfe0576`. |

Conclusion: on **probe-level** evidence the inline-block route is not stripped or altered by WordPress.com. The draft currently holds only a 957-byte probe; the exact 108 KB candidate block has **not** been stored there yet (that is the next step below), so this is necessary but not sufficient evidence. The fallback (a Site Layer plugin delivery) is not indicated on current evidence.

## Not yet verified (BLOCKED on a signed-in browser)

The in-app browser is not signed in to WordPress.com and credentials were not entered by the assistant. Therefore these were **not** done against the real WordPress.com render:

- Assembler header/footer/layout of the candidate on the live theme and its custom templates.
- The seven chapters loading, mouse/keyboard/touch interactions, screenshots "from the WordPress.com draft".
- A Lighthouse run of the draft (it cannot be fetched without authentication).

Those checks were run, with the same scripts, on the local WordPress + Assembler stage (see `ACCEPTANCE_MATRIX.md`); that is a proxy, not a substitute.

## To finish (needs one action from you)

Sign in to WordPress.com in the in-app browser pane (or tell me to use your signed-in Chrome). Then: insert the exact replacement block (`production-change/replacement-block-index1.html`; size and hashes in `PROPOSED_PRODUCTION_CHANGE.json`) into draft 1902, confirm its `block_hash` equals the SHA-1 in `PROPOSED_PRODUCTION_CHANGE.json`, run `qa/run_wp_qa.py` against the preview URL (its POST blocker stays on), capture desktop and mobile screenshots, then trash the draft only after the evidence and rollback copies are verified.

## Retention

Draft 1902 currently holds the 957-byte probe, not the candidate. It stays until the evidence above is captured, then it should be trashed (`pages.delete` moves it to trash; permanent removal is wp-admin only).
