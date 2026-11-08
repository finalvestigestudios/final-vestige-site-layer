# EX2: Isolated Focus journey preview (2026-11-08)

**DRAFT / RELEASE HOLD. WordPress.com production Page 6 and Focus Page 1579 are not modified.** Stack on PR #1613; frozen PR #49 is untouched.

## Commercial blocker closed for the prepared staging bundle

The seven-chapter review renderer exposes five contextual Focus Fieldbook anchors pointing to production. Those anchors would exit the disposable staging site, preventing isolated destination QA and potentially contaminating production traffic. Separately PR #1613 documents a `?subscribe=anything` false success claim on the published Focus page. This PR does NOT repair Jetpack or claim a confirmed subscription.

The new MU-plugin, `fv-ex2-focus-local-route.php`, rewrites **only those five anchors in the rendered preview shortcode**, **only** on an exact loopback or official WordPress Playground host with the existing local-review option marker; an explicit production environment is rejected. It throws on changed shortcode markup or a changed link count. In production, it never registers. It has no email form, tracking, affiliate URL or purchase claims.

The accompanying private staging ZIP (distributed in the engineering evidence artifact, **not in this public repository**) deterministically builds on the PR #1607 protected package (SHA-256 `7416678c39d4d08914e19182b980df5e2d3fdec43208a01a983d2b57edc42bed`). It adds this MU-plugin and a clearly marked, **non-submitting** local Focus page, and makes the existing WordPress admission check fail if any of the five Focus links still exit to production. No production database, subscribers or secrets are exported.

## Verified offline

- PHP 8.4 syntax PASS for the exact guard source.
- 65/65 PHP-function-stub + Chromium checks PASS; 320×568, 390×667, 768×1024, 1440×900 with JS on/off; seven chapters, 72 Margins and two private review images retained.
- Production host, lookalike host, missing marker, explicit production environment rejected; mutated Focus href count throws.
- Two independent six-member ZIP builds are byte-identical: SHA-256 `e3a7f7ef73e7db6f7705b01fd3a0aa52452626dd1a1291f66c11248e7712e9dc`.
- Browser runtime blocks **both HTTP loopback and file navigation**. Browser checks anchor destinations and focused controls and renders an explicitly simulated Focus page separately; **it does not prove native cross-page navigation**. No claim of WordPress Core, Assembler, Jetpack, axe, Lighthouse, hosted CWV, media transfers, confirmed leads or paid revenue.

## Conversion contract

**Offer:** existing 52-page free Focus Fieldbook. **Step:** homepage contextual action -> Focus page -> verified Jetpack subscriber -> independently confirmed purchase. **Blocker:** private preview links escape to live production. **Change:** isolated local route, with no fake success or form. **Evidence:** 65 offline checks and real PHP output; **WordPress navigation untested**. **Owner:** interim homepage engineering, with Jetpack and live attribution reserved for Claude. Grok/Praxxis retain acquisition.

### Source and rights

No new artwork or historical narrative. WordPress records still describe NASA Apollo #473, Franklin #474, and NYPL #1258, but attachment file sizes are not actual image-download receipts. NYPL derivative rights and actual transferred bytes remain a release HOLD. No purchase or payout assumption for Inspire3 or any merchant.

### Next native stage

Import the prepared ZIP ONLY into a disposable free WordPress Playground with Assembler and network permissions, verify the new local page is registered and five contextual anchors navigate inside that site, then run WCAG 2.2 AA checks, independent axe/manual audit, real media byte tests, actual zoom and Lighthouse. Separately verify live Jetpack consent/confirmation without creating unauthorized subscribers. Frozen PR #49 and live Page 6 remain unchanged. Exact CI/QD and founder release approval still required; **do not merge or publish**.

For offline reproduction, the downloadable engineering artifact includes `build_focus_local_route.py`, `verify_focus_local_route.py`, the protected input/output ZIPs, full JSON receipt and screenshots. Those helper scripts and ZIPs were executed locally and are **not claimed to be in this GitHub commit**.
