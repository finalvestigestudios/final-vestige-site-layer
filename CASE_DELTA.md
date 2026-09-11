# Case Delta v1

## Visitor job

Help a returning reader answer one bounded question: **what changed on this published investigation since the snapshot I deliberately saved in this browser?**

Case Delta is not a server-side revision log, an editorial changelog, an archive, a notification service, or evidence scoring. It never claims to explain why a change occurred.

## Qualification and source-of-truth boundary

The feature fails closed unless the page has exactly one `article h2#sources.fv-source-heading`, exactly one later `[data-fv-footnotes]` list, 2–10 pre-Sources story H2 headings, 12–120 narrative paragraphs, and 4–40 source-note rows. It reads only the published DOM of that investigation.

## Snapshot contract

A snapshot is created only after the visitor activates **Save current version**. It is stored in `localStorage` under `fv_case_delta_v1`, only for the same-origin query-free pathname. The store is capped at six investigations, snapshots expire after 120 days, future/malformed/stale records are rejected, and each snapshot is capped at 90,000 serialized characters.

The snapshot contains published public material only: investigation title/path/time; story section labels, normalized section text and word counts; published source-note text and external source URLs with citation backlinks removed; and up to 20 figure captions, alt text and image URLs. No account identifier, reading history, analytics identifier, cookie, server profile, or cross-device sync is created.

## Comparison model

On a later visit, **Compare with saved version** compares the current published DOM to the last local snapshot. The dialog reports Added / Changed / Removed structural records across Story, Sources and Figures. Story changes are reported by section and word-count delta rather than presenting a line-level editorial diff. Source and figure records can expose the bounded saved/current published details. **View current** returns to a current surviving item in the story.

The interface states: “Compared with the version saved in this browser … Case Delta is not a complete editorial history and does not explain why a change was made.” It also states that nothing is sent to Final Vestige.

## Interaction, mobile and accessibility

The launcher appears before the first story H2. The comparison uses a native modal `dialog`, returns focus to its invoking control on close, has 44px minimum targets, filter buttons with pressed state, live result messaging, reduced-motion handling, forced-colors focus treatment, and a single-column mobile layout at 720px with an additional 360px pass. Print suppresses the tool. **Replace snapshot** is deliberately two-step; **Forget snapshot** removes only this page’s local snapshot.

## Performance and privacy budget

The candidate is one self-contained block with no third-party libraries, fetch/XHR/WebSocket/sendBeacon, cookies, IndexedDB, analytics calls, clipboard writes, history mutation, or background timers. Comparison runs only after explicit visitor interaction. There is no background monitoring or network request.

## Deployment guardrail

This branch is an artifact candidate only. Do not merge merely because CI passes. Independent QD must review the exact frozen PR head SHA. After the governed Site Layer bootstrap is active, executable integration must be built from then-current `production`, receive a new SHA, fresh CI and fresh QD, deploy through the approved GitHub path, and receive live desktop/mobile/accessibility/storage/destination verification before `IMPLEMENTED + VERIFIED`.
