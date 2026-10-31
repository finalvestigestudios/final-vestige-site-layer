# Final Vestige Experience 2.0 — consolidated seven-chapter review surface

**Status: DRAFT / RELEASE HOLD.** This is an **independent review branch**, not a production deployment, WordPress installation, staging acceptance, or permission to merge. Source of truth: Issue #150. Frozen v1 PR #49 must remain unchanged. Review alongside separate Apollo #158 and Mind/Perception #171 lanes; do not merge their work into the home candidate.

## Why this review branch exists

The full homepage, design folio, source-led chapters, no-JS presentation, CSP QA, WordPress private-preview design, Assembler parity importer, and source/media custody checks were spread across sequential draft PRs. Reviewers can inspect the **combined proposed tree** in one draft PR targeting `main` without merging or modifying any of those source branches. The compare immediately before this handoff showed **84 commits and 94 changed files ahead of main, zero behind**. These counts are a scope warning, not an endorsement or quality score. The branch is a *composite review surface*, **not a substitute for its exact-parent staging tests**.

Canonical upstream terminal parent before this review: PR #329 SHA `8da9b520604b24429622b9a5a32898a925faf734`. Current review branch is a descendant; use `git rev-parse HEAD` and GitHub PR head SHA for all executions. Do not reuse PR #254 SHA `8fa6fc52e034f511b96ae526f4a852e1bd76db04` as the SHA for this combined checkout.

## Actual cumulative experience

The seven source-native chapter anchors are `fv-hf-title`, `fv-hf-chronicle`, `fv-hf-evidence`, `fv-hf-inquiry`, `fv-hf-method-title`, `fv-hf-observer`, `fv-hf-mind-title`. The revised hero uses an explicitly labelled, editorial **not-a-facsimile** Victory Point note folio distinguishing 1847 and 1848; the same sheet's dated entries remain readable when scripts fail. The three evidence-case images retain source references and limitations. The observer comparison is an original studio exercise, not a medical/attention assessment. Black Dossier, Museum After Hours and Observatory remain available as review variants until the founder selects one.

The published WordPress page is separate: page ID 6, site ID 256784396. A read-only `pages.get` returned 47,021 characters with 72 distinct `--i:0` through `--i:71` Margins fragments, Focus Fieldbook references and Jetpack subscriptions. **No CMS write has been performed.** Recheck immediately before any separate governed production release.

## Demonstrated source-level defect closed here

The optional Observer Lab's *aria-live* status originally stated `Compare the lower-right corner` on first render and every switch. This **disclosed where the missing FV seal was before the reader opened the native answer disclosure**, compromising the editorial exercise. An isolated code change makes announcements answer-neutral (`Frame A displayed.` / `Frame B displayed.`) and adds ArrowLeft/ArrowRight/Home/End switching while keeping Tab, Enter and Space native.

A dependency-free Node `node:test` / `vm` regression suite executes the **actual committed JS** against an explicit synthetic DOM contract. Exact before/after blob witness: original `9b69d69dc61909d3e802365e47ab5287108efa4e` failed 3/7 checks; updated `f70567529114aa07ae5fb01a8a5b146dadb78804` passed 7/7. The test source Git blob is `a11d28ea4e13114ecd3ed40cfdf37c42a193e92a`.

Run from the repository root:

```bash
node --check experience2/home-flagship/observer-lab.js
node --test experience2/home-flagship/tests/test_observer_interactions.cjs
python -I experience2/home-flagship/qa/release-candidate/verify_csp_exact_browser.py \
  --root experience2/home-flagship --expected-head "$(git rev-parse HEAD)" \
  --output /tmp/fv-ex2-current-csp
```

The Node contract tests **do not** certify Chromium, accessibility, WordPress markup or mobile styling. The last exact-head Chromium command above is an **unrun admission instruction** in this environment; record its real result rather than promoting the Node result to full UI QA.

## Next decisive gate — single integrated, non-production review

WordPress.com production is on the **Personal** plan; no native staging clone. Do **not** interpret the included wpcomstaging.com address as a clone. Run the existing PR #322 `run_local_staging_admission.py` against the **complete exact checkout**, with an independently verified official Assembler 0.0.126 archive/hash and a free isolated WordPress Playground / PHP instance; import only sanitized public presentation, never production databases, users, subscribers, tokens or analytics.

The sealed private preview must only accept an authenticated local editor. Verify real seven-chapter rendering, script-disabled meaning, functional four interactions and three negative controls at seven widths (including 320/390/768/1440/1920), 200% zoom, keyboard/touch, reduced motion, forced colors, browser CSP, and first-party archival media network responses/decoded bytes. Run real axe-core **WCAG 2.2 AA** and Lighthouse laboratory checks, recording raw results and screenshots. If a tool or entitlement is absent, report **NOT TESTED**, never PASS. WordPress Playground is not WordPress.com Atomic host parity, and Lighthouse lab data are not field p75 CWV.

Archive release rights remain open until the *exact shipped media bytes* (WP Apollo #473, Franklin #474, NYPL #1258 and responsive derivatives) are reconciled with verifiable NASA/Commons/NYPL record-specific permissions. Do not infer image rights merely from a linked catalogue page. Keep independent QD and exact-head CI as hard gates. The founder must approve a chosen art direction and a separate exact release plan before production publication.

## Ownership and safety

No new standalone chapters, merchant pitches, affiliate links, subscriptions, hosted infrastructure, CMS writes, theme changes, plugins, merges, or deployments are introduced by this review. Focus Fieldbook (52 pages), Jetpack signup and the 72 existing Margins entries remain production-preservation requirements. Issue #150 owns homepage direction; Apollo #158 and Mind #171 remain separate lanes. **Decision: HOLD.**
