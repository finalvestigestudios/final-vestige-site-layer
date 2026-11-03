# Critical-CSS-first saved Gutenberg experiment — 2026-11-02

**Status: DRAFT / NO RELEASE / PERFORMANCE UNVERIFIED UNTIL EXACT-HEAD CI.** Source change is solely the parse order of one existing, scoped 60,549-character inline stylesheet in the already reviewed seven-chapter Gutenberg fixture. No chapter, art-direction asset, archive image, evidence text, external link, interaction script, subscriber record, or paid service is added or removed.

## Evidence and attribution

- Parent: PR #699 exact commit `a12da977ff4d0fe6a92dae100b0057eb3abde27b`.
- Real saved-page baseline from the user-provided PR #699 CI ZIP, file `GUTENBERG_SAVED_NATIVE_CDP_LAB.json`, `source_sha=a12da977ff4d0fe6a92dae100b0057eb3abde27b`: cold-cache 390px mobile LCP **3,804 ms** and **3,872 ms** under 4x CPU, 150ms RTT and 1.6Mbps; desktop 1,044ms; CLS 0. Both mobile trials FAIL the 2.5s laboratory diagnostic budget. LCP is a text `p` element, not a photo.
- Before: the first 36,550 characters of the proposed WordPress HTML preceded a single 60,549-character scoped `<style>` block; the stylesheet was at the bottom of the seven-chapter editorial HTML and before the scripts.
- Experiment: move that same stylesheet, byte-for-byte, immediately after `<!-- wp:html -->` and before the opening hero element. No additional CSS or preload asset. The rest of the candidate's text and scripts remain in their original order. This is a testable **hypothesis** about parse/render timing, not an established root cause or performance gain.
- The separate design-study HTML is *not* modified; strict source-vs-release chapter content parity is preserved by bounding the editorial fragment at the first trailing `<script>` instead of assuming stylesheet placement. The release fixture git blob pin must match its new exact content.
- Regression controls: enforce one stylesheet before hero; compare exact editorial interior/rights notices against independent study source; guard malicious missing opening, case/source and no-JS preservation through existing adversarial checks.
- All remaining media are the already reviewed Apollo and Franklin files. The NYPL map capture remains **not reproduced**; its catalog citation alone is retained. No new rights determinations or source claims.

## How to evaluate the CI result

Run the two exact-head GitHub workflows for the new draft branch; neither a green workflow nor a visually pleasing screenshot certifies the performance budget. Read **`GUTENBERG_SAVED_NATIVE_CDP_LAB.json`** and report both mobile 390px trial LCP values, text LCP element attribution, FCP and document responseEnd; compare against the above baseline. `native_lab_budget_gate` must be PASS_LAB_ONLY on BOTH mobile trials at <=2,500ms (and CLS <=0.1), with valid instrumentation, before recommending the CSS-order change for the release candidate. This experiment is not powered by a full randomized A/B test, and environment/run variance is expected; ideally repeat both variants within the same CI job if the result is near threshold.

Review actual 320, 390, 768, 1440 and 1920px saved-page screenshots; axe WCAG-tagged checks, no-JS historical images, 200% equivalent reflow/keyboard/touch, CMS raw-save byte identity, and image-network safeguards must remain green. Do not mistake the **private iframe's** Lighthouse score for this saved Gutenberg page.

## Governance

Free isolated local WordPress/Assembler is the test target; **WordPress.com Personal has no native staging clone.** This is not hosted WordPress.com infrastructure, nor field Core Web Vitals. Publication remains **HOLD** for independent QD, actual browser zoom, manual assistive-technology/physical device validation, legal rights sign-off, hosted compatibility, and founder publication approval. No updates to live page 6, site settings, theme, navigation, PR #49 or Apollo/Mind workstreams. No deploy/merge without exact release instruction.
