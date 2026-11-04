# EX2 native WordPress navigation semantics — isolated diagnostic and repair (2026-11-03)

**DRAFT / RELEASE HOLD.** Stacks exactly on PR #856 head `a55fb0602fe24c0a7bc9eb6b6cfe377280eaaa66`. Frozen PR #49 and live WordPress page 6 are strictly untouched.

## Known actual-browser baseline

[Hosted Assembler run 41736939617](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41736939617) failed the **whole-document** axe `list` rule against `.wp-block-navigation__container` (serious) at **768, 1440 and 1920**. The flagship-only axe had zero findings; narrow scope hid the theme defect. Previous work verified saved Gutenberg full-width composition (320/390/768/1440/1920), 7 chapter targets, 4 source scripts, and Apollo/Franklin decoded image response bodies. Its default navigation appears to use WordPress's page-list fallback; the exact direct-child list shape must be measured in browser rather than assumed.

## New isolated experiment

- Inspect and log exact **unmodified** Assembler nav topology (tag names, direct child types, link counts, no user text or URLs), together with actual axe `list` and `listitem` results at 768. Save baseline screenshot before any changes.
- Only if a direct nested list and matching axe issue are **both proven**, run a guarded PHP command *inside the disposable WordPress Playground server*. It refuses non-loopback home URLs, multisite, or any active theme other than Assembler.
- Use WordPress **native** `wp_navigation` and `wp_template_part` posts to provide an explicit Home link via `core/navigation-link`, replacing exactly one navigation block in a local header template part. Record original/override SHA-256 and post IDs for custody.
- Re-render and re-run real axe; require a functioning link, no direct nested UL/OL and **zero** list/listitem violations. Save after screenshot. The subsequent complete 5-width/full-document axe and no-JS gates still run **without disabling any axe rule**.
- Strict failure at any unexpected header block structure or mismatch. No DOM patching, no browser CSS injection, no changes to vendor ZIP, and no reusable production payload.

This represents **a custom-configured local Assembler template part**, not the untouched vendor default. Even if browser CI passes, it **cannot** qualify production Assembler navigation without an independently reviewed actual-site native menu/template decision and explicit release permission. The vendor default remains a documented failing baseline.

## Static verification and evidence levels

- Eight local Node adversarial tests exercised the baseline gate, loopback restrictions, mocked native WordPress before/after, and failure modes; test code is committed on this branch and in CI.
- Standalone PHP source syntax was checked with PHP `-l` and passed *before* committing; this does not prove runtime behavior.
- **Pending real browser CI:** First actual WordPress render may reveal a different header block structure or broken menu override. It must be reported RED, not 'green by intention'. Actual GitHub workflow tests and screenshot artifact are required for verified success.
- Keep mobile wrapping, 200% **physical** zoom, keyboard/touch interactions, manual WCAG 2.2 AA, Lighthouse/CWV, archival rights, real Jetpack/72 historic records, WordPress.com-hosted parity, QD and founder approval under HOLD.
- No edits or access beyond read-only to live production. No merged PR, deployment, purchases or subscriptions.

External corroboration of the **general** WordPress nested page-list failure (not proof of this particular theme): [WordPress support report](https://wordpress.org/support/topic/page-list-block-used-as-navigation-menu-is-not-accessible/). The exact issue here is determined solely by reproducible local axe + DOM inspection.
