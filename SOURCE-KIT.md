# FVF-5 — Source Kit

Source Kit is an evidence-portability feature for evidence-rich Final Vestige pages. When a page contains a recognizable Sources/References section with at least two list items, the payload inserts a restrained utility card immediately after the source heading.

Visitor actions:

- **Copy source list** — copies the source text plus the primary source URL where needed.
- **Copy Markdown** — preserves links as Markdown without inventing citation metadata or a bibliography style.
- **Download .md** — creates the same source trail locally in the browser with no network request.

The payload does not alter the published source list, score source quality, infer missing bibliographic fields, store visitor data, or call third-party services. It remains inert when the page does not qualify.

## Delivery state

This branch is intentionally based on the current `production` branch and does **not** duplicate or modify the frozen `FVSL-BOOTSTRAP-001` PR #1 runtime. It contains the exact visitor-facing payload and deterministic CI only. Runtime manifest integration must wait until the bootstrap PR lands; that later integration requires a fresh exact-SHA QD review before merge/deployment.

## Exact artifact identity

- Path: `payloads/source-kit-wp-block-v1.txt`
- Bytes: `11199`
- SHA-256: `6fa06fe80e6b2a17cca3b9453b02ab174d404367847909fee2ef98c6fac09659`
