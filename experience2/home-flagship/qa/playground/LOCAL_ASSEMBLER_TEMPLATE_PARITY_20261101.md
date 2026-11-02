# Final Vestige — custom Assembler template parity in isolated WordPress
**November 1, 2026. DRAFT / RELEASE HOLD. No WordPress.com writes.**

## Source-grounded integration defect

The authenticated *live* WordPress page template `assembler//page` is a **custom block template**, not the stock Assembler page template. Read-only `templates.get` showed a `core/post-content` with `className:"fv-post-content"` and constrained `contentSize:"760px"`, `wideSize:"1440px"`, plus this explicitly page-6-scoped layout override:

```css
.page-id-6 .fv-post-content>*{max-width:none!important}
```

The existing free WordPress Playground staging Blueprint installs a **stock** `assembler.zip`, and creates a *new* local front page with an unrelated page ID. The seven-chapter flagship `.fv-hf {width:100%}` does not cancel an outer WordPress-constrained post-content width. Therefore stock-theme previews could wrongly appear to validate the homepage's full-bleed composition while failing to reproduce the public site's customized rendering rules. This is a **verified source-level staging-parity gap**, not an observed rendered regression.

## Implementation in this isolated child PR

Added `stage_page_template_parity.cjs`, wired into the existing `make_integrated_playground_bridge.cjs` **private CLI**. It requires a read-only export of the **PUBLIC** `assembler//page` Gutenberg template and an independently computed SHA-256; verifies the current production template's exact structural contract and one full-bleed CSS override; rejects changed templates, scripts/forms/subscriber blocks and missing local authorization. The temporary local-only template copy changes *only* the page-specific CSS selector into:

```css
body.home .fv-post-content>*{max-width:none!important}
```

The local Blueprint's **existing `runPHP` step** registers the copied template as the local `assembler//page` `wp_template`, binds it to `wp_theme=assembler`, and refuses to proceed unless `wp_get_block_template()` resolves the expected full-width rule. It adds **zero** Blueprint steps or files; exact 19-step structure, 15 write-file steps, source hashes and original Gutenberg source remain under their existing acceptance gate. The raw template is **not committed** or embedded in a public GitHub artifact.

The integrated CLI requires two new arguments: `--public-template /private/assembler-page-template.blocks.html` and `--template-sha256 <independent SHA256>`. It continues to require the existing `--public-page`, `--page-sha256`, `--output`, `--receipt`, and any rights-approved private media manifest. No subscription upgrade.

## Evidence and limits

- **10/10** new Node 22 + PHP 8.4 tests passed using a synthetic *public-template* fixture. Positive PHP code execution and deliberate theme-binding failure were both exercised.
- **8/8** inherited local Jetpack render-hook tests also passed, with two minimal local `require()` stubs *only* for the unchanged bridge dependencies; therefore this does **not** constitute a full exact Git checkout or native WordPress test. The modified bridge's Git blob and both new source/test Git blobs were independently compared with tested local files.
- No genuine WordPress Playground runtime was available during this run. Exact `wp_template` storage/resolution, actual 320/390/768/1440/1920/200%-zoom rendering, image network fetch, axe/WCAG, Lighthouse, Safari, hosted Jetpack, CI/QD, rights and founder approval **remain unverified**.

## Exact-source baseline and governance

Parent is draft PR #522 head `8c105ced651beffcfc5e95bff5d792bdd2208987`, not frozen PR #49 `10495883299d53596992c26a8987f629b2904670`. This changes **only** local Playground engineering code, tests and this memo; no homepage seven-chapter content, Apollo 1 #158, Mind #171, live WordPress page 6, Jetpack, Focus Fieldbook or 72 Margins records were modified. No production merge, install, preview publishing, theme/navigation/settings mutation or billing change.

## Next acceptance

In a private free WordPress Playground/local WordPress environment: independently hash the real PUBLIC template export and rights-verified Apollo/Franklin/NYPL source bytes, run the integrated Blueprint, verify actual `assembler//page` template resolution + full width at all target screen widths, and execute genuine image/axe/keyboard/no-JS/performance tests. Record actual screenshots with the custom production template comparison. WordPress.com host-specific and hosted Jetpack checks remain separate. **Release HOLD.**
