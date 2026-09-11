# FVF-16 — Case Cabinet

## Visitor job

Let a reader intentionally save a small set of Final Vestige investigations and reopen that set from elsewhere on the site without creating an account, sending a reading list to a server, or relying on an opaque recommendation feed.

## Final Vestige adaptation

**Case Cabinet** is an opt-in, browser-local reading shelf. On qualifying investigation posts it adds a compact **Save to Cabinet** / **Open Cabinet** band near the opening. Once at least one investigation is saved, non-article Final Vestige pages expose a restrained **Case Cabinet · N** launcher. The cabinet shows the exact saved title and save date, links only to a validated same-origin query-free path, allows one-item removal, and requires a two-step action before clearing the whole set.

The feature stores only three fields per entry: investigation title, same-origin page path, and save timestamp. It retains at most 12 entries and prunes entries older than 180 days. State is held in origin-scoped `localStorage`; there is no account, server write, analytics event, cookie, fingerprinting, external API request, cross-device sync, or third-party script. Storage failure makes the feature fail closed.

## Inspiration principle

- **Instapaper**: saving something for later should be available directly from the reading context, and a saved library should remain easy to manage.
- **Readwise Reader**: a reader-owned library is a durable organizational surface, not merely a transient “recent” list.
- **W3C APG modal-dialog guidance**: the cabinet uses a native modal interaction with contained focus, Escape dismissal, and focus return.
- **Web Storage / same-origin model**: the implementation deliberately confines the small saved-state record to the current browser origin.

This is not a clone of any product UI. The Final Vestige version is intentionally smaller, local-only, source-site-native, and explicit about its state boundary.

## Qualification and placement

- Save band: `single-post` pages with a trustworthy WordPress post identity and at least four narrative paragraphs.
- Global launcher: rendered only when a valid saved set exists and the current page is not already showing the save band.
- Dialog: created only when Web Storage passes a write/remove probe.
- No article/source/figure markup is rewritten.

## Accessibility / responsive behavior

- Native `<dialog>` / `showModal()` path with cancel interception and logical focus return.
- 44px minimum primary controls and 3px `:focus-visible` treatment.
- `aria-pressed` exposes current save state; `role=status` / `aria-live=polite` exposes cabinet count.
- Mobile stack at 680px and single-column controls at 360px.
- Forced-colors, reduced-motion, and print handling.
- All generated links are text links with real titles; no gesture-only behavior.

## Performance budget

- One isolated payload, under 14 KiB in this candidate.
- Zero network requests and zero third-party dependencies.
- At most 12 small records are parsed/sorted; storage writes occur only on explicit visitor actions, pruning, or cross-tab reconciliation.
- No observers, polling, image cloning, or layout-heavy continuous scroll work.

## Verification criteria

Deterministic CI locks payload bytes/hash, one-block packaging, storage boundary, cap/TTL, same-origin query-free path validation, dialog/focus behavior, responsive/accessibility rules, and absence of network/analytics/private-server APIs. Headless browser fixtures cover explicit save/remove/clear, duplicate prevention, non-post reopening, unsafe/stale-record pruning, 12-item cap, and storage-unavailable fail-closed behavior.

## Delivery boundary

Artifact review only until the governed Site Layer bootstrap is active. Do not merge or deploy this feature merely because CI passes. Any later runtime-manifest integration from then-current `production` creates a new executable SHA and requires fresh exact-head CI plus independent QD before FVS Execution Dispatch may merge/deploy.

No whole-site launch/indexing change, Scout disclosure, server-side private-user processing, billing/account/permission change, direct WordPress footer/template injection, or destructive action is authorized by this feature artifact.
