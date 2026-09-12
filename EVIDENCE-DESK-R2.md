# Evidence Desk — FVF-14 R2

## Visitor job

Keep a small working set of the exact source notes and figure captions already published in a Final Vestige investigation close at hand while continuing to read, without opening extra tabs, losing narrative position, or creating an account-level research profile.

## Interaction principle

Evidence Desk adapts the research-context pane pattern used by tools such as Zotero and Hypothesis and the companion-panel principle seen in high-quality narrative products. Final Vestige's implementation is read-only, session-only, and tied to evidence already published in the investigation. It does not create annotations, infer relationships, score evidence, or introduce a third-party service.

## Qualification / fail-closed boundary

The feature adds nothing unless the page resolves all of the following: `body.single-post`; an article content root; the trusted `h2#sources.fv-source-heading`; the trusted `.fv-source-list[data-fv-footnotes]`; Sources before the list in the same content root; at least 12 substantive narrative paragraphs and 2,800 narrative characters before Sources; at least four valid numbered source records; at least two published figures before Sources; and at least six total pin candidates.

## Source-link provenance boundary — R2

Evidence Desk inspects the literal published `href`, never browser resolution alone. `Open source` appears only for a literal HTTP(S) destination that is outside both the current origin/hostname and the controlled Final Vestige host family. The controlled family is `finalvestige.com` plus every subdomain such as `www.finalvestige.com` or `labs.finalvestige.com`. Backlinks, fragments, relative links, same-origin links, canonical Final Vestige links, aliases, and subdomains are rejected. If no qualifying external published URL exists, the source card remains usable but has no `Open source` action.

## Nondestructive story-jump contract — R2

`View in story` never permanently rewrites publisher-owned state. Scrolling occurs before any target mutation. Temporary focus state records whether `class` and `tabindex` existed and their exact prior values. Successful interaction restores those exact values; an originally absent attribute returns to absent. Repeated jumps clean the previous temporary transaction first. Scroll failure causes no publisher-node mutation. Focus failure restores state immediately and returns focus to the feature-owned control. Closing the desk during an active jump also restores the exact prior state.

## Working set and responsive behavior

A visitor can pin up to four already-published source notes or figure captions. Source cards contain published source-note text and, when provenance permits, the external destination. Figure cards use the existing caption or alt text and never clone/re-request the image. The desk uses a side panel only when measured page geometry leaves enough free margin; otherwise it uses a reachable bottom tray. Mobile forces the bottom treatment. Escape closes the desk and returns focus to the launcher.

## Accessibility, privacy, and performance

Controls have a 44 px minimum target and visible 3 px focus treatment, with forced-colors, reduced-motion, 360 px, and print handling. State is kept only in in-memory Maps for the current page load. No local/session storage, IndexedDB, cookies, analytics, history mutation, clipboard access, fetch/XHR/WebSocket/sendBeacon, iframes, or third-party scripts are used. Figure images are not cloned.

## Browser regression coverage — R2

The deterministic browser verifier covers: Final Vestige `www` alias and subdomain links appearing before a genuine external source; a source note containing only internal/Final Vestige-family links; later genuine external-source preservation; missing/reversed trusted Sources boundaries; the four-item cap; remove/replacement; no image cloning; clear/open/close/Escape behavior; absent `class`/`tabindex`; publisher-owned `class` plus nondefault `tabindex=-7`; repeated jumps; forced scroll failure; forced focus failure; close-during-active-jump cleanup; and exact state restoration.

## Delivery boundary

This R2 successor is source/build only. It must be based from then-current `production`, remain open and unmerged, pass exact-head Evidence Desk R2 CI plus repository CI, and return to independent QD. Green CI is evidence, not approval. No merge/deployment, WordPress write, navigation/indexing change, private-user processing, spending, or other separate-gate action is authorized by this package.
