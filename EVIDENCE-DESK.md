# Evidence Desk — FVF-14

## Visitor job

Keep a small working set of the exact source notes and figure captions already published in a Final Vestige investigation close at hand while continuing to read, without opening extra tabs, losing narrative position, or creating an account-level research profile.

## Interaction principle

Evidence Desk combines three useful interaction principles without copying any product's visual trade dress:

- Zotero's research-note workflow keeps source context and notes available together and supports returning from a note or annotation to the originating source context.
- Hypothesis connects a page-level sidebar of annotation cards to the exact locations they refer to in the host document.
- ArcGIS StoryMaps demonstrates why docked/stacked companion panels should preserve the primary narrative rather than obscure it, and adapts sidecar layouts on smaller screens.

Final Vestige adapts those principles into a read-only, session-only investigation working set. It does not create annotations, sync notes, infer relationships, score evidence, or introduce a third-party service.

## Final Vestige adaptation

A qualifying longform investigation receives a prominent **Evidence Desk** launcher before its first major story section. Opening the desk reveals temporary **Pin to desk** controls on the investigation's existing Final Vestige source-note records and published figures. A visitor may pin up to four items.

Pinned source cards contain the source note's exact published text plus a validated external source URL only when that URL is actually present in the published source note and passes the provenance boundary below. Pinned figure cards contain only the already-published caption (or existing alt text as a fallback); the feature deliberately does not clone or re-request figure images.

Each card provides **View in story** and **Remove**. The desk can be cleared or closed. Closing removes temporary pin controls but retains the in-memory working set while the current page remains loaded. Reloading or leaving the page destroys the state.

## Qualification / fail-closed boundary

The feature adds nothing unless all of the following resolve:

- `body.single-post`
- an article content root
- the trusted `h2#sources.fv-source-heading`
- the trusted `.fv-source-list[data-fv-footnotes]`
- the Sources heading precedes that list and both belong to the same content root
- at least 12 substantive narrative paragraphs and 2,800 narrative characters before Sources
- at least four valid numbered source-note records
- at least two published `figure.wp-block-image` figures before Sources
- at least six total pin candidates

The live compatibility reference used during this build is the published **Six Miles an Hour** investigation, which currently contains seven numbered source notes and six figures behind the same trusted Sources boundary.

## Source-link provenance boundary — R1

Evidence Desk never treats a browser-resolved link as proof that the editor published an external source URL. For each source note it inspects the raw `href` attribute and accepts an **Open source** destination only when all of these conditions hold:

- the anchor is not inside `.fv-fn-backlinks`
- the literal published `href` begins with `http://` or `https://`
- the URL parses as HTTP(S)
- the destination is not the current site's origin or hostname

Fragment links, root-relative links, other relative links, same-site absolute links and backlinks are rejected. If a source note contains no qualifying published external URL, the card remains usable for its published note text and **View in story**, but no **Open source** action is rendered.

## Desktop / mobile behavior

The desk chooses its layout from actual available page geometry, not viewport width alone. On wide screens it uses the right margin only when at least 395 px of free space exists beside the article. Otherwise it becomes a bottom research tray. The bottom layout adds a measured reachability spacer so the fixed tray cannot make the end of the article unreachable. At 700 px and below the bottom layout is forced and controls remain touch-sized.

The visitor can close the desk with its visible Close control or Escape. Close removes temporary pin controls and returns keyboard focus to the launcher. **View in story** scrolls and focuses the original published item, with reduced-motion support.

## Accessibility

- Semantic launcher section and complementary `aside`
- 44 px minimum controls
- explicit `aria-expanded` and `aria-pressed` state
- polite live pin-count status
- unambiguous 3 px keyboard focus ring
- Escape close + focus return
- visible target arrival treatment
- reduced-motion behavior
- forced-colors behavior
- 360 px mobile handling
- print cleanup

## Privacy / performance

Evidence Desk reads only the current DOM. It uses in-memory `Map` state and does not use local/session storage, IndexedDB, cookies, analytics, browser-history mutation, clipboard access, external APIs, XHR/fetch/WebSocket/sendBeacon, iframes, or third-party scripts. The only network navigation it can expose is a qualifying external URL already published in the source note after the visitor explicitly chooses **Open source**.

The feature does not clone figure image nodes, avoiding duplicate image requests. DOM work is bounded to one qualification scan, temporary pin controls while the desk is open, and a maximum of four rendered cards.

## Production artifact — R1

- Payload: `payloads/evidence-desk-wp-block-v1.txt`
- Bytes: `16047`
- SHA-256: `4ab1c7f18074caa76e5f5b0aacb08a122fd96b70fbdcc4a64e31d0c8cfbf755a`
- Static + JavaScript syntax verification: `tests/verify_evidence_desk.py`
- Browser runtime regression fixtures: generated by the verifier and executed in headless Chrome/Chromium in CI
- Workflow: `.github/workflows/evidence-desk-ci.yml`

## Browser regression coverage — R1

The deterministic verifier exercises four states through a local same-origin HTTP fixture server:

1. qualifying article where a backlink, a relative internal link and an absolute same-site link all appear **before** the true external source URL — only the true external URL may survive;
2. a qualifying article where Source 1 has backlinks/internal links but **no** external source URL — Source 1 must expose no **Open source** action while later valid source URLs remain available;
3. missing trusted Sources heading — feature must fail closed;
4. reversed Sources-heading/source-list order — feature must fail closed.

Runtime assertions also retain coverage for launcher/open state, six candidate controls, the four-item cap, remove/replacement behavior, safe external-source preservation, no internal-link leakage, no image cloning, clear, adaptive layout/spacer creation, close cleanup, Escape dismissal, and focus return.

## Delivery boundary

This PR is a frozen feature artifact based on the inert `production` baseline. It is **not** runtime integration and passing CI is **not** merge or deployment authority.

While the Site Layer bootstrap/deployment bridge remains gated, keep this artifact PR open and unmerged. After that prerequisite is active and independent QD has accepted the exact artifact identity, create the smallest executable integration from then-current `production`. That integration produces a new SHA and therefore requires fresh CI and fresh independent QD before FVS Execution Dispatch may merge/deploy it. Live destination verification remains mandatory after deployment.

No direct WordPress footer/template injection is authorized by this package.
