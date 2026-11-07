# EX2 local WordPress instance provenance — 2026-11-07

**REVIEW ONLY / RELEASE HOLD.** New isolated child of PR #1415 at exact parent `328769ac24a0dc5964b3851aebc67fec26010ae5`. Frozen PR #49 at `10495883299d53596992c26a8987f629b2904670` not modified. No WordPress production write, bundle rewrite, merchant activation, subscription or paid service.

## Reproduced admission defect (before)

The original `run_local_wordpress_acceptance.py` accepted **any** loopback server whose root HTML contained `data-fv-home-flagship` and `wp-site-blocks`. It did not verify that the requested port was free **before** launching npm or check WordPress's REST identity. A second local server already listening on that port could therefore be misreported as the review WordPress instance while npm was still starting. Reproduction with a real local `ThreadingHTTPServer` returned:
`BEFORE_PATCH_SPOOFED_READY {'http_status': 200, 'wordpress_shell_detected': True, 'flagship_root_detected': True}`
even when the server returned only synthetic HTML and no WordPress REST response. This is **test-evidence provenance**, not a claim of compromised production.

## Isolated fix (after)

1. `refuse_occupied_port` checks `127.0.0.1:<review-port>` before npm is spawned; refuses an existing listener. Loopback-only and allowed-port contracts remain enforced.
2. `wordpress_rest_identity` makes a **read-only** request to the exact localhost site's `/wp-json/`. Requires HTTP 200, JSON MIME, `wp/v2` in the advertised namespace list, and the reported site URL exactly matching the loopback target. Redirects to production are rejected. Invalid JSON, missing keys and non-string URLs fail closed.
3. The existing complete-home browser, axe, visual, image-transfer, conversion-path and Lighthouse requirements **remain open**. REST+HTML matching is an additional admission signal, **not proof of a genuine WordPress instance or cryptographic attestation**: a deliberately crafted local fake could forge both. Run the actual WP/Assembler CLI and collect independent browser/network evidence.

## Executed local evidence

- Original runner Git blob: `efc091ecb2a48f299942fd9c4ef1c17f25037664`; updated exact tested runner Git blob: `af7886d963911c17550e44448b1f9a23d4197d1e`.
- Exact tested 12-case mock-host suite Git blob: `c4a232a5599fcd8f3e56e91b09417ad185550581`.
- **12/12 new adversarial local HTTP tests passed**: occupied/free port, marker-only fake, wrong site URL, missing wp/v2, production redirect, wrong MIME, invalid JSON, non-string URL, missing source marker, positive synthetic REST-shaped fixture, non-loopback rejection.
- **8/8 pre-existing runner regression tests passed** including the existing pinned protected bundle.
- `python -m py_compile` passed for updated runner.
- Reproduction is local and synthetic; **no actual WordPress/Assembler startup or hosted request** completed. The current shell lacks cached `@wp-playground/cli`, cannot resolve npm/GitHub hosts, and cannot meet the true integration gate.

## Editorial, source and conversion boundaries

Read-only connected WordPress inspection found one production site (256784396), Assembler active, Page 6 published. Media records: NASA Apollo 1 #473 (original metadata 78,346 bytes, S67-19766); Franklin #474 (466,043 bytes; displayed scan from an 1869 printed reproduction); NYPL map #1258 (5,553,669 bytes original, rights/source reconciliation outstanding). The image `sizes` metadata includes virtual `i0.wp.com` variants. **None of those sizes are measured browser transfer bytes.** Candidate's NYPL image remains excluded.

Historical first: seven chapters, 72 Margins and five Focus CTA destinations in unpublished candidate unchanged; public Page 6 and the 52-page Focus Fieldbook/Jetpack signup unchanged. Commercial offer remains the free Fieldbook as an audience-capture step; paid orders, affiliate reports, refunds/fees and net revenue were not checked. Owner of production attribution/checkout: Claude; Grok/Praxxis retain campaign production/QA, as agreed in Issue #820 and TASK-008. Independent Site QA retains release gate.

**OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER:** Focus Fieldbook → homepage first-screen CTA → trustworthy staging admission → localhost port + WP REST matching, no traffic/pixel changes → 20/20 local test cases passed, no WordPress acceptance → interim homepage engineering with Site QA. **Net revenue per 1,000 qualified sessions remains unmeasured**, not zero.

## Remaining gates

Actual isolated WordPress Playground CLI with pinned Assembler and public-only content; real 320/360/390/768/1440/1920 + 200% browser screenshots; axe WCAG 2.2 AA and manual keyboard/touch/reduced-motion/no-JS; original responsive media response bytes and rights; measured Lighthouse/CWV; genuine Jetpack signup/delivery evidence without unapproved test submissions; owner visual approval, CI/QD exact head, and explicit release approval. WordPress.com Personal does **not** include native one-click staging; do not suggest upgrade or confuse its default `wpcomstaging.com` alias with staging.

**No deploy / no merge / no publish / no CMS/theme/nav/settings writes / no new subscriptions.**
