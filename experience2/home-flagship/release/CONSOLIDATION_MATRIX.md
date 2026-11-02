# Consolidation matrix - Flagship release candidate (2026-11-02)

**Canonical branch:** `release/homepage-flagship-candidate-20261102` (cut from PR #565's head, which contains PR #550's head; production-rooted).
**Not merged, not deployed, no CMS writes.** PR #49 is untouched. `main` and `production` histories were not merged.

Heads below were re-read from the GitHub API on 2026-11-02 and are not carried over from earlier reports.

| Source | Exact head | Check state when read | Decision | Why |
|---|---|---|---|---|
| PR #49 (frozen homepage v1) | `10495883299d53596992c26a8987f629b2904670` | `verify` **failure**, `deploy` skipped | **EXCLUDED - frozen** | Directive. Not touched, not rebased, not stacked on. |
| PR #550 (production-rooted flagship port) | `6ef459ec76208fc84022328b938d79bf556ac774`, base `production` `3f7841a7c671f9e8e955b417480d853ad0a0a948` | `verify` success, `deploy` skipped, mergeable clean (draft) | **INCLUDED - canonical base** | 99 added files, 0 deletions, nothing in `production` touched. |
| PR #565 (corrected exact-source Chromium gates) | `91ca7a7d0e9e1b22374ea354775a0ae9d985e502`, base = #550 head | `verify` success, `chromium` success | **INCLUDED (fast-forward)** | Retires the studio-picker assertions, locks art-direction identity. This branch starts exactly here. |
| PR #573 chain (WordPress/Assembler staging, ~30 commits) head `96e29738f162b971af61f95b80d41a9234065b97` | stacked on #565 | Actions run for that head still pending when read | **PORTED selectively** (lessons + two blobs) | See next rows. Its iframe private-preview plugin, ZIP-custody tooling and mutation harnesses were **not** imported. |
| PR #580 (HTTP readiness diagnostics) | `2142c7ceb36c499eb5c6dd5437bfb0abc5796275`, base `20db505b4186...` | `ephemeral-wordpress` **failure**, `exact-source-php` success, `verify` success | **PORTED: two files** | `parity/assembler-public-safe.json` (git blob `b2edb0832f572826b56bdfe0d48054e9eeaa29d6`) and `parity/apply_local_parity.php` (`8bcfd5a15e12ec5f4f9f6b596f58ec7b141372a5`): the public-safe Assembler header/footer/page template and site CSS. Everything else in the chain **excluded**. |
| PR #375 / #368 (duplicate header/footer fix) | `63a25bb7...` / `96923217...` | not re-read | **SUPERSEDED** | `wp-candidate/build_candidate.py` drops the standalone banner, masthead and footer and turns the nested `<main>` into a `<div>`, so the Assembler chrome is the only chrome. |
| Focus Popup draft (`feat/fv-focus-popup-affiliate-warmup-20261031`) | `ae67e98d...` | n/a | **NOT INTEGRATED** | Source read (fail-closed JS). Production has v0.1.1 installed with the shortcode on no page. Not placed on the homepage. |
| Apollo Research Desk #158 and R-series (#568, #575, #582) | independent | n/a | **EXCLUDED - independent lane** | No shared files. |
| Mind & Perception #171 / #172 / #367 / #374 / #570 / #578 / #583 | independent | n/a | **EXCLUDED - independent lane** | The flagship only links the two already-published targets (Puysegur files, /focus/). No `/mind/` link, no commerce. |
| Preparedness Archive | independent | n/a | **EXCLUDED** | Unpublished separate workstream. |

## What this branch adds on top of #565

| Path (under `experience2/home-flagship/`) | Purpose |
|---|---|
| `wp-candidate/build_candidate.py`, `run_stage.py`, `wp-integration.css` | Builds the composed page and launches free WordPress Playground with the official Assembler 0.0.126. `--delivery inline` puts the flagship CSS/JS inside the page block (no plugin upload). |
| `wp-candidate/snapshot/` | Byte-exact public snapshot of live page 6 (sha256 in `.meta.json`) and the public per-block layout CSS the page depends on. |
| `wp-candidate/parity/` | The two ported blobs above. |
| `wp-candidate/qa/` | `run_wp_qa.py`, `measure_images.py`, `verify_preservation.py`, `make_production_change.py`, `cache_proxy.py`. |
| `index.html` (small edits) | Two nested `aside` landmarks became `role="group"` (axe `landmark-complementary-is-top-level`); explicit credit/rights lines in the three source drawers; a visitor-facing sentence replaced "A future /mind/ hub is in draft review ... in this study". |
| `tests/test_hero_arrival.py` | Follows the `aside` -> `div` change. |
| `release/` | This package, measured evidence, and the proposed production change. |

## Composition rule (what the homepage becomes)

Live page 6 has six top-level blocks. Only **block 1** (the old "Studios hero" and its `<style>`) is replaced by the seven-chapter flagship. Blocks 0, 2, 3, 4, 5 (72 Margins strip, Focus CTA, the home shell with the Jetpack Dispatch block, Enter-the-record, Organization JSON-LD) stay byte-for-byte. The hero's six links (`/blog/`, `/accountability/`, `/collection/`, `/watch/`, `/community/`, `/labs/`) remain reachable through the Assembler header.

## Outstanding (not decided here)

- **D1 (founder):** the existing "latest / trails / research desk" sections still follow the flagship, so the page is long (about 19,000 px at 1440). Trimming them is a separate content decision; nothing was removed.
- Focus Popup placement (needs its own verification).
- Packaging into the governed Site Layer lane if the plugin route is preferred over the inline block.
