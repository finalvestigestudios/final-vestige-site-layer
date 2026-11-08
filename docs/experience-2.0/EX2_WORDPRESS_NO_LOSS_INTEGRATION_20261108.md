# Final Vestige EX2 — Page 6 no-loss assembly decision (2026-11-08)

**Status: RELEASE HOLD.** This is an independently executable, read-only compatibility gate, not a WordPress update, plugin installer, image license, accessibility certification, or conversion report.

## Authenticated source, November 8

WordPress.com accessible-site inventory: **one production site**, ID `256784396`, `https://finalvestige.com`. Authenticated `pages_get(id=6,context=edit)`: published, modified `2026-11-05T12:07:24`, 150,710 characters. Source-level inventory: **72** `fv-margin-strip__item` entries, **one** seven-link `fv-hf__chapter-nav`, **seven** corresponding anchor IDs, **one** `wp:jetpack/subscriptions` block, **four** `<img>` tags, and **four** `/focus/` anchor destinations. These are SOURCE counts, not verified image network transfers or actual subscriber activity.

Protected PHP preview renderer output, separately extracted from the privately held previous-run package: **72** Margins, one chapter navigation, **zero** Jetpack subscriptions blocks, **two** image tags, five Focus destinations. This is not a complete WordPress replacement page. Its embedded 72 Margins entries are part of the renderer.

## Critical integration hazard, now demonstrated

1. **Appending** an entire duplicate experience to published Page 6 would yield at least **144** Margins entries, **two** chapter navigations, doubled chapter IDs, and potentially duplicated signup; fail.
2. **Replacing the whole Page 6 document** with only the protected PHP experience would lose the native Jetpack subscription block and current image elements; fail.
3. A source-only candidate with fewer Focus destinations, a changed Margins record, or an unreviewed image must fail before browser-stage acceptance.

The code in `experience2/review/ex2_homepage_no_loss_gate.cjs` only reads two **local** authorized editor-source files and returns a machine-readable audit. It does not write a replacement page, edit a CMS, or fetch URLs. A passing report says `STRUCTURAL_PASS_RELEASE_HOLD`, never `RELEASE_APPROVED`.

Usage (Node 22): `node experience2/review/ex2_homepage_no_loss_gate.cjs private/current-page-6.txt private/proposed-page-6.txt`. Inputs must come from an approved read-only WordPress export and remain out of the public repository. Exit code 1 means HOLD. Exit code 2 means invalid invocation. The exact native rendering, staging, accessibility, images and production release gates remain separate.

## Reproducible authenticated regression exercise

I re-fetched the **exact code committed to GitHub** and executed it against the freshly authenticated actual Page 6 editor source in a V8 isolate, without saving that complete content to GitHub:

| Case | Required decision | Observed |
| --- | --- | --- |
| Same original as proposal | Structural pass, release hold | PASS |
| Full published page appended again | HOLD: 144 Margins, 2 navs | PASS (rejected) |
| Remove Jetpack block | HOLD | PASS (rejected) |
| Remove one Margins record | HOLD | PASS (rejected) |
| Change one Margins sentence | HOLD | PASS (rejected) |
| Remove one original image | HOLD | PASS (rejected) |
| Replace Focus URLs with blog | HOLD | PASS (rejected) |
| Duplicate chapter navigation | HOLD | PASS (rejected) |
| Add one unreviewed external image | HOLD | PASS (rejected) |

**8/8 deliberate invalid cases rejected**. This demonstrates a real production-source structural blocker, not successful WordPress/Assembler integration or any conversion uplift. Existing candidate's rights-unreconciled NYPL derivative must not be silently restored, nor removed from production without independent review.

## Release architecture decision

**Do not deploy by wholesale replace or append.** In an isolated, public-content-only WordPress Playground/Assembler copy, preserve the native Gutenberg page wrapper, keep exactly one functional Jetpack subscriptions block (Jetpack may be unavailable in Playground), keep all 72 distinct Margins texts and one seven-chapter navigation. Use candidate designs as review-only component input and reconcile source and image differences explicitly; review privacy and mailing semantics independently. Keep all original media protected until licensed-source review and verified actual byte delivery. No private subscribers, users, production database, secrets, settings, or analytics data in portable test artifacts.

### Conversion gate

**Offer:** free Seven Day Focus Fieldbook, 52 pages. **Funnel:** qualified social acquisition (Grok asset_id) → relevant evidence → contextual Focus action → actually confirmed Jetpack signup → separately verified paid purchase → net realized revenue. **Blocker:** naive integration destroys or duplicates content and signup. **Change:** fail-closed no-loss gate and staged in-place assembly requirement. **Evidence:** actual source counts + 8/8 invalid integrations rejected. **Owner:** interim homepage engineering and independent Site QA; Claude remains responsible for production Jetpack/checkout/attribution; Grok/Praxxis own social acquisition. **Commercial result:** not measured; no purchase or subscriber attributed.

## Unresolved gates

No running native WordPress/Assembler instance was available in this execution environment, no actual first-party archival image bytes were downloaded (network DNS unavailable), no independent axe/WCAG 2.2 AA, no Lighthouse/CWV measurements, no genuine Jetpack signup confirmation. GitHub Actions/QD remain unqualified. WordPress.com Personal offers no native staging clone. Founder must separately approve any release; **no production edits/merges/deployments/spending**.
