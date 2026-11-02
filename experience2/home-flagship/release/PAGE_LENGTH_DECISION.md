# Decision record: homepage length and preserved content (D1)

**Decision (engineering, within the founder's delegation):** ship the **six-block-preserving** design first. Only block 1 (the old Studios hero) is replaced. Nothing that is published today is removed. A shorter page through further block removal is **not** shipped in this release because it cannot yet be verified safely, and the instruction was explicit: an unproven cleanup must not jeopardise the flagship.

## Why the broader cleanup is not shipped

- Block 3 (`core/group` "fv-home-shell") holds, in one block, the latest-investigation query, the category and trail term queries, the Exchange strip, Research Desk, the sources/method group **and the native `jetpack/subscriptions` block (the Dispatch signup)**. Removing or editing any part means editing a block that contains the live newsletter form, which needs a readback and rollback plan for the Jetpack block that cannot be rehearsed without a signed-in staging render and without subscribing a real address.
- The raw page was read on 2026-11-02 for the first time (earlier sprints worked from rendered output). Blocks 1 and 2 reconstruct byte-exactly to their live hashes; block 3 has not been reconstructed or backed up as a standalone artifact.
- Texturisation differs between stored and rendered text (straight versus typographic apostrophes), so any rendered-HTML copy of block 3 would not be a faithful rollback.

## What was done instead to improve the reading experience without removing content

- The flagship ends with a concluding editorial sequence (`THE ARCHIVE DOESN'T END HERE`) leading to Investigations, The Public Record, the Research Library and the Focus Fieldbook. The Preparedness Archive is **not** linked: its public page is not approved.
- The long preserved sections after the flagship are skipped by the browser until they approach the viewport (`content-visibility:auto`), which cut mobile main-thread blocking in Lighthouse from 278 ms to 136 ms and requests from 19 to 12 in the same configuration. Content, order, links and find-in-page are unchanged.

## Destination ledger (must survive any future restructuring)

Everything below is in preserved blocks today. A later cleanup must keep a link to each or record an explicit decision.

| Preserved block | Destinations |
|---|---|
| 0 Margins strip | 72 records (indices 0-71) |
| 2 Focus CTA | `/focus/` (button and cover art) |
| 3 shell: lead + recent rail | `/blog/` posts (latest + 3 recently filed), category archives |
| 3 shell: taxonomy | six category archives |
| 3 shell: Exchange | `/community/` |
| 3 shell: more investigations | `/blog/` and six recent posts |
| 3 shell: research trails | six tag archives, `/archive/dossiers/` |
| 3 shell: research desk | `/field-notes/`, `/the-archive-trail/`, `/watch/#start-with-the-evidence`, `/field-cabinet/` |
| 3 shell: method | `/editorial-standards/`, `/about/bryan-rhodes/`, `/contact/#corrections` |
| 3 shell: Dispatch | **native Jetpack subscriptions block**, `/dispatch/`, anchor `#dispatch` (used by the site header) |
| 4 Enter the record | `/editorial-standards/`, `/the-failure-chain/`, `/free-resources/research-sources/`, `/blog/` |
| 5 JSON-LD | Organization schema |
| (removed by block 1 replacement) old hero | `/blog/`, `/accountability/`, `/collection/`, `/watch/`, `/community/`, `/labs/` (all reachable through the Assembler header) |

## Proposed phase 2 (separate approval, not part of this release)

Insert a back-up-first step: read block 3 raw, store it with its SHA-1, rehearse on a private draft page signed in, then move individual query sections one at a time with a `page-sections` readback and rollback for each, never touching the Jetpack block's markup.
