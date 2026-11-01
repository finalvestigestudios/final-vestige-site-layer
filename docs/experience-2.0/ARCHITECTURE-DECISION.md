# Experience 2.0: where the code lives

**Decision (recommended, not yet approved):** ship Experience 2.0 as its own small plugin, `final-vestige-experience-2`, separate from the Final Vestige Site Layer plugin. Keep WordPress as the canonical home of posts and URLs. Do not build a separate platform.

## Why a separate plugin, not Site Layer

| Concern | Site Layer | Separate Experience 2.0 plugin |
|---|---|---|
| Release gate | Deployed through a governed bridge that requires a byte-identical artifact, independent QD and green CI for the homepage release (PR #49) | Its own version, its own gate. A defect in one cannot block the other. |
| Current state | PR #49 is open and its `verify` check was failing at last read | Independent of that blocker |
| Blast radius | Homepage, Margins Wire, Focus Fieldbook path, Dispatch | Only pages that contain an Experience 2.0 shortcode |
| Asset cost on other pages | Always-on enhancement code | Zero: assets register early but enqueue only where used |
| Maintenance | One large governed surface | A small surface: 4 PHP files, no admin UI, no storage |
| Rollback | Tied to the homepage deploy | Deactivate the plugin; posts keep their original content |

A plugin does not fork the design language. Tokens are namespaced (`--fvx-*`), so Site Layer can adopt them later through the same governed path without a collision.

## What is not decided here

- Whether the flagship becomes a WordPress page with its own template, or a section of the published article. The directive forbids replacing the complete investigation with the shorter experience without editorial approval, so it is built as a companion.
- Whether the Atlas needs a map library. That waits for verified geography.

## Boundaries the plugin keeps

- Stores nothing, registers no options, REST routes or admin screens, and makes no remote requests (enforced by a test that scans the PHP for those calls).
- Ignores shortcode attributes entirely.
- Verifies each bundled template against the build manifest before output; a missing or altered file falls back to a link to the original article.
- Static output only, so it is safe behind page caching.
- Content stays in semantic HTML; JavaScript only reveals optional controls.

## Preserved and untouched

Public Record and Accountability pages, Investigations and Library, Labs and digital products, existing URLs, Query blocks, the Focus Fieldbook path, Jetpack Dispatch, analytics and SEO metadata. This work edits none of them and does not touch the live homepage.

## Source of truth and freshness

WordPress remains canonical. `atlas/tools/ingest_wp.py` reads the public REST API (GET only) and records a content hash per post; `--check` reports changed, missing or moved posts so they are re-reviewed before any derived text is refreshed. Nothing auto-publishes.
