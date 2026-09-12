# FVF-16 — Case Cabinet R1

## Visitor job

Let a reader intentionally save a small set of Final Vestige investigations and reopen that set from elsewhere on the site without creating an account, sending a reading list to a server, or relying on an opaque recommendation feed.

## Final Vestige adaptation

**Case Cabinet** is an opt-in, browser-local reading shelf. On qualifying investigation posts it adds a compact **Save to Cabinet** / **Open Cabinet** band near the opening. Once at least one investigation is saved, non-article Final Vestige pages expose a restrained **Case Cabinet · N** launcher. The cabinet shows the exact saved title and save date, links only to a validated same-origin query-free path, allows one-item removal, and requires a two-step action before clearing the whole set.

The feature stores only three fields per entry: investigation title, same-origin page path, and save timestamp. It retains at most 12 entries and prunes entries older than 180 days. State is held in origin-scoped `localStorage`; there is no account, server write, analytics event, cookie, fingerprinting, external API request, cross-device sync, or third-party script.

## R1 state-integrity repair

A successful Web Storage probe is not treated as proof that later persistence will succeed. R1 makes the cabinet transactional:

- startup reads and canonicalizes the stored set, then persists that canonical set **before any cabinet UI is created**; if that write fails, the feature aborts cleanly;
- save, remove, and clear construct a proposed next state without mutating the committed in-memory state;
- each mutation writes the proposed state first and updates in-memory/UI/ARIA state only after persistence succeeds;
- a post-probe `setItem()`/`QuotaExceededError` failure leaves the prior durable record set, count, cards, `aria-pressed` state, and button labels unchanged;
- failed destructive clear also disarms its confirmation state and tells the reader that nothing changed.

This closes the QD finding in the original v1 candidate where UI/in-memory state could diverge from durable storage after a later write failure.

## Inspiration principle

- **Instapaper**: save-for-later belongs directly in the reading context.
- **Readwise Reader**: a reader-owned library is a durable organizational surface rather than a transient recent list.
- **W3C APG modal-dialog guidance**: the cabinet uses a native modal interaction with Escape dismissal and focus return.
- **Web Storage / same-origin model**: the saved-state record remains confined to the current browser origin.

This is not a clone of any product UI. The Final Vestige version is intentionally smaller, local-only, source-site-native, and explicit about its state boundary.

## Qualification and placement

- Save band: `single-post` pages with a trustworthy WordPress post identity and at least four narrative paragraphs.
- Global launcher: rendered only when a valid saved set exists and the current page is not already showing the save band.
- Dialog/UI: created only after Web Storage passes the probe **and** the canonical stored set can be persisted successfully.
- No article/source/figure markup is rewritten.

## Accessibility / responsive behavior

- Native `<dialog>` / `showModal()` path with cancel interception and logical focus return.
- 44px minimum primary controls and 3px `:focus-visible` treatment.
- `aria-pressed` exposes current save state; `role=status` / `aria-live=polite` exposes cabinet count and mutation failures.
- Mobile stack at 680px and single-column controls at 360px.
- Forced-colors, reduced-motion, and print handling.
- All generated links are text links with real titles; no gesture-only behavior.

## Performance and privacy budget

- One isolated payload under 14 KiB.
- Zero network requests and zero third-party dependencies.
- At most 12 small records are parsed/sorted.
- Writes occur on startup canonicalization, explicit visitor save/remove/clear, or cross-tab reconciliation reads.
- No account, cookie, server-side reading history, analytics event, fingerprint, external API request, iframe, or third-party script.

## Verification criteria

Deterministic CI locks payload bytes/hash, one-block packaging, storage boundary, cap/TTL, same-origin query-free path validation, dialog/focus behavior, responsive/accessibility rules, and absence of network/analytics/private-server APIs. Browser fixtures cover:

- ordinary save/remove/clear and duplicate prevention;
- non-post reopening;
- unsafe/stale-record pruning and the 12-item cap;
- total storage unavailability;
- successful probe followed by canonical startup write failure;
- successful probe followed by save failure;
- successful probe followed by remove failure;
- successful probe followed by clear failure.

The failure fixtures assert both durable storage and rendered/ARIA state remain on the prior committed value.

## Delivery boundary

Source/build artifact only. Do not merge or deploy because tests pass. Fresh exact-head feature and repository CI plus independent QD are required before any governed FVS Execution Dispatch merge/deployment. Any code change after the final freeze invalidates the reviewed identity.

No whole-site launch/indexing change, Scout disclosure, server-side private-user processing, billing/account/permission change, direct WordPress footer/template injection, or destructive action is authorized by this repair.
