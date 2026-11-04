# EX2 exact-browser Margins parity repair — release HOLD (2026-11-03)

## Confirmed upstream contract mismatch (not a hypothetical)
Parent draft PR #882 @ `d0db8bb8a868ff21a6fe44116b0feabdc8c14fed` changed the **saved Gutenberg** Margins window label to `72 published historical fragments in isolated review` and populated all 72 spans from **public** WordPress page ID 6 (last modified 2026-11-02T17:48:13). However, its existing `playground_assembler_render_gate.mjs` still asserted `label:'72 synthetic historical fragments'` in `checkView` at every tested viewport. This is a deterministic false browser failure before whole-page axe even runs, regardless of whether the saved WordPress page renders correctly. The old receipt also falsely continued describing the Margins text as synthetic.

## Independent source-grounded evidence
- Live published WordPress page 6 read-only (`context=edit`) and exact PR #882 JSON fixture independently compared: all **72** item texts match in order, and all indices 0..71 are present.
- Prior saved Assembler 320/390/768/1440/1920 screenshot matrix at Actions run `41736939617` shows the *earlier* invented placeholder Margins; these screenshots do NOT certify the new text copy or revised browser harness.
- The new branch does not touch the seven chapters, Franklin folio, site imagery, flags, affiliate terms, Focus/Jetpack content, frozen PR #49 or live CMS.
- Source rights remain **unqualified**: Apollo/Franklin media body decoding was previously demonstrated, but this change adds no rights grant and does not reproduce the NYPL capture.

## Corrective implementation
1. The browser's saved-layout assertion now expects the **public-text** ARIA label actually serialized by the current builder.
2. Its real 320/390/768/1440/1920 Playwright views compare the *entire ordered 72-node textContent* against source-custodied published JSON, failing at the first inconsistent index instead of merely asserting node count. The exact sensitive-free failure receipt contains only the index, not text.
3. JavaScript-disabled 390px rendering checks all 72 texts identically; scroll/opacity/readability assertions and screenshot preservation remain enabled.
4. The fixture validator requires page 6, site 256784396, canonical domain, isolated-only marker, 72 ordered unique nonempty items. 
5. Real browser receipt classification and limitations distinguish **publicly published text** from synthetic Jetpack, synthetic header and missing live rotator/hosted parity.
6. Eight built-in Node regression tests enforce provenance, saved-markup/QA label agreement, missing/extra/reordered/altered text and malformed fixtures. Existing Assembler Actions workflow invokes the test **before** installing the theme or saving the candidate.

## Verifiable status and nonclaims
- Independently executed **20/20** source/helper contract assertions against the **GitHub-fetched updated harness** and published JSON, including all 72 exact WordPress source strings. This is local code-contract execution, **not** GitHub Actions, Node module import, WordPress rendering, Chromium, axe or Lighthouse.
- No fresh after-change rendered screenshots, complete-document WCAG pass, keyboard/touch audit, 200% physical zoom, Safari or field CWV are claimed. The known Assembler whole-document desktop navigation-list violation remains a release blocker.
- As of the preceding revision, GitHub Actions jobs failed before running any steps; this exact branch requires fresh execution evidence. Do not mark CI PASS without actual steps.
- Isolated WordPress Playground is **not** WordPress.com Atomic/Jetpack parity. WordPress.com Personal does not provide a native one-click staging clone.

## Required next sequence
Run the updated exact-head Node contract test; then full isolated Gutenberg Save + real saved Assembler browser screenshots at 320/390/768/1440/1920, 200% zoom/reflow, keyboard/touch, whole-document axe, true no-JS, media bytes/decode and lab Lighthouse. Confirm genuine native WordPress navigation remediation is functioning; fail closed on any serious axe findings. Independently reconcile archival image rights, review the full mobile/desktop art direction and retain founder/QD/production publication gates. No merge, production edit, publication or subscription upgrade authorized.
