# QA log

## 2026-10-29: sprint 1

**Automated (offline), all passing:** `validate.py` 0 errors / 0 warnings; 18 unit tests OK.

**Rendered (Playwright, Edge channel, local file preview, not the live theme):**

| Page | 360 | 390 | 768 | 1440 | Console errors |
|---|---|---|---|---|---|
| landing | no h-overflow | no h-overflow | no h-overflow | no h-overflow | 0 |
| making-water-safer | no h-overflow; tables scroll in labelled, focusable wrappers | same | same | same, 2-column with sticky TOC | 0 |
| salt-beef-salt-pork-age-of-sail | checked at the same four widths | | | | 0 |

Also checked: landing filter (search, topic) works and announces counts; print stylesheet switches to white background and hides the TOC; PDF render of the water guide produced. Screenshots were reviewed by eye for header, action box, bleach table, safety verdict, Then/Now.

**axe-core 4.9.1** (wcag2a, wcag2aa, wcag21a/aa, wcag22aa and best-practice rules; landing, both articles, 390 and 1440 px): **0 violations** after two fixes (landing had no `<main>`; labelled `div`s needed roles). Articles now emit no `<main>` of their own because the WordPress theme template supplies it; only the preview wrapper adds one. axe reported `color-contrast` as *incomplete* (it cannot resolve the paper texture background), so contrast rests on the token-pair check below plus a human spot check.

**Contrast:** all 16 foreground/background token pairs meet 4.5:1 (enforced by the validator).

**NOT done (do not read this log as a pass for these):**

* Rendering inside the live WordPress theme. Local previews use only our CSS. Whether the theme adds a second H1 for the page title, constrains `core/html` width, or strips the inline `<script>`/`<style>` is unverified until a draft is previewed by an authenticated user.
* Screen-reader and keyboard walkthrough by a human (only the first Tab stop, the skip link, was checked). axe's incomplete `color-contrast` items on the paper-textured boxes.
* Link click-through by a human; Lighthouse/CWV; real-device mobile.
* Independent verification of any claim in the safety checklist.

## WordPress draft probe (2026-10-29)

* Created **draft** page ID 1868 "The Preparedness Archive" (slug `preparedness`, parent none, status draft) from `build/wp/landing.html`. No `_content_warnings` were returned, and `page-sections.list` shows one `core/html` block holding the `<style>`.
* **Not verified:** how the live Assembler theme renders it (duplicate page-title H1, content-width clamp, whether `<script>` survives front-end output). That needs an authenticated preview of `https://finalvestige.com/?page_id=1868&preview=true`.
* Not touched: navigation ID 5 (read only), homepage page 6, Focus page 1579, retired Water Resilience Field Manual draft (page 85), PR #49.
