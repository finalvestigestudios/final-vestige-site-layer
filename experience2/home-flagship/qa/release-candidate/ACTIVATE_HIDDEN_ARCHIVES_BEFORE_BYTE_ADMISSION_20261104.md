# Homepage P0: Exercise the actual three-case interface before lazy-image admission

Parent **draft PR #1022** exact head `cf906f5270a55d96cfa07142525774ce2f0fbc33`. This is a **separate stacked draft**; frozen PR #49, Apollo lane #158, live WordPress and commercial instrumentation are untouched.

## Fresh primary-source witness — read-only WordPress Page 6, November 4, 2026

The live published Page 6 (WP last-modified `2026-11-04T14:39:24`) actually contains three `article[data-fv-case]` exhibits and `button[data-fv-case-button]` controls for `apollo`, `franklin`, `malbone`. Its progressive enhancement explicitly sets `panel.hidden = panel.dataset.fvCase !== active` and updates button `aria-pressed`. Only Apollo is displayed initially in enhanced mode. All three archival `img[data-fv-archive-img]` are `loading="lazy"` with sourceful captions and evidence boundaries. The controls are hidden when no-JS so that all articles remain readable.

The previous `readImages` attempted `scrollIntoViewIfNeeded` on all three images without selecting their case. Hidden images cannot be scrolled into view and may never load; the old test could report a false **HOLD** even on a functioning homepage, or record a misleading transferred-image result. This is a deterministic **test fixture/execution-path defect**, not proof of a live production failure.

## Exact change

- Add allowlisted `activateArchiveCase(page,caseId)`, which *clicks the real archive button* rather than directly mutating `hidden`. Require unique button and panel, only the requested panel unhidden, and correct `aria-pressed=true`; reject unknown IDs, missing/duplicate controls and ineffective clicks.
- In `readImages`, activate each archive case *before* scrolling/loading its associated lazy exhibit. Require all three to have been exercised; retain the previously committed image URL SHA-256 matching, HTTP-200/positive-byte, alt and decoded-dimensions requirements.
- Preserve the already-existing no-JS check, 72 Margins, seven chapters, full-document axe, seven responsive widths and header Focus CTA test. This QA harness performs anonymous GET and local archive-button clicks only—no forms or commerce actions.

## Evidence — distinguish what was actually executed

**Local real Chromium:** A representative, isolated HTML reproduction of the exact published button/hidden-panel/lazy-img behavior was executed using Python Playwright and native Chromium. At seven widths (320, 390, 768, 1279, 1280, 1440, 1920), hidden Franklin images **could not be scrolled before activation** (negative control), while the three archive cases each became selectable, images decoded, and keyboard activation worked. Screenshots and JSON stored locally in /mnt/data/fv_archive_case_browser_evidence; these are reproducible offline fixture evidence, **not** screenshots of live WordPress or the exact source checkout. A newly committed Node/Playwright browser test exercises the exported source-level helper, across the same seven widths, with unknown-case, missing-control and ineffective-click negative controls. The author-side equivalent of that browser test ran locally via Node 22 + system Chromium: **2/2 TAP tests PASS**. Source is committed; complete exact-checkout execution in a network-enabled runner remains a separate gate.

**Still NOT verified:** production WordPress/Assembler Chromium render, actual first-party image body transfers, full-document axe/WCAG 2.2 AA, 200% zoom, Safari, Lighthouse/field CWV, linked media legal clearance, CI/QD at exact SHA, real mobile CTA engagement or paid revenue. A WordPress.com Personal plan cannot use native WP.com staging; isolate WordPress Playground instead. Do not characterize this fixture as exact WordPress staging.

## Rights and editorial integrity

No new artwork or imagery. The three existing exhibits remain Apollo 1 NASA S67-19766 (WP media #473), Franklin Victory Point note Commons reproduction (#474), and NYPL map image 5003296 (#1258). Their image captions, source boundaries, rights ledger and attribution still require final independent release review; this PR neither adds licenses nor asserts blanket commercial rights. No Blue Corridors visuals copied. All 72 Margins and the 52-page Focus/Jetpack workflow remain unchanged.

## Offer → funnel step → blocker → experiment → evidence → owner

**Offer:** Seven Day Focus Fieldbook (free lead capture; not a paid order). **Step:** historical archival interaction → contextual Focus CTA. **Blocker:** QA tried to verify hidden lazy images without selecting the archive, invalidating the trust/visual test. **Change:** real archive-button activation and verification before inspecting the images. **Evidence:** real isolated Chromium fixture passes at seven widths; exact source and committed browser harness; live bytes unverified. **Owner:** homepage QA; Claude handles real attribution/merchant integration; Grok and Praxxis retain social acquisition. No confirmed subscribers, paid orders, affiliate sales, refunds/fees or net-revenue improvement measured.

**Release status: HOLD.** No live WordPress writes, publishing, branch merging, affiliate activation, campaign posting, email, analytics deployment or spend.
