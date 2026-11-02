# Final Vestige flagship — actual WordPress stage content custody and template precedence
**November 1, 2026 · DRAFT / RELEASE HOLD · Child of PR #530**  

## Source-grounded failure and significance

The integrated isolated Playground bootstrap in `make_integrated_playground_bridge.cjs` took the accurately assembled, SHA-256-attested seven-chapter Gutenberg content and passed it as **raw** `'post_content'=>$raw` to `wp_insert_post()`. WordPress core explicitly unslashes post data during the insertion process; unescaped backslashes in Gutenberg attributes, JS, CSS, regexes, or archival metadata can consequently be silently lost. Passing the source hash *before insertion* does **not** prove that WordPress stored the same source.

Official references:
- WordPress core `wp_insert_post()`: https://developer.wordpress.org/reference/functions/wp_insert_post/ (see slashing example and `wp_unslash($data)`).
- WordPress core REST API slashing note: https://make.wordpress.org/core/2016/04/06/rest-api-slashed-data-in-wordpress-4-4-and-4-5/
- WordPress core Trac #41579: https://core.trac.wordpress.org/ticket/41579

In addition, `stage_page_template_parity.cjs` validated that the imported `assembler//page` template **exists and resolves**, but did not test whether a more specific `front-page` template would win the routing hierarchy. WordPress documents that `front-page.html` takes priority even when a static page is configured: https://developer.wordpress.org/themes/templates/template-hierarchy/ . The *actual production* WordPress template inventory checked in this sprint contained `assembler//page` and **no** `assembler//front-page` override. A stock or future Playground theme version could differ, so local acceptance now fails closed rather than silently testing the wrong template.

## Isolation-only corrections

1. Feed `wp_slash($raw)` into local `wp_insert_post(..., true)`, leaving the untouched decoded Gutenberg source under the original SHA-256.
2. After the local WordPress insert, re-read persisted `post_content` via `get_post_field('post_content',$id,'raw')` and require byte-identical SHA-256. Any WordPress sanitization, encoding, or plugin mutation causes an explicit staging exception.
3. Before accepting the imported `assembler//page` template, reject a resolvable `assembler//front-page` template that WordPress would otherwise select ahead of the reviewed page template.
4. Add focused red/green PHP 8.4 execution tests: expected slashing preserves Gutenberg backslashes, removing `wp_slash()` fails the new gate, a simulated post-insert mutation fails the gate, and the previous unguarded bootstrap is demonstrated to accept corrupted content. Add a competing front-page template PHP rejection test.

## Actual verification and scope

Local source-matched tests performed on Node 22 and PHP 8.4: **16/16 passed** (11 template-parity / 5 post-content custody). The test harness uses faithful *stubs* of the documented WordPress slashing behavior, not a native WordPress database. No real browser screenshots, WCAG/axe pass, Lighthouse, image transfer verification, host-specific cookies, Jetpack delivery or independent QD/CI approval is claimed.

This patch is layered on PR #530 exact head `69fd86a50654e163efb732c3f466d07ea3234b5e` and does not touch frozen PR #49, current public page 6, homepage seven-chapter art, Apollo #158, Mind #171, the source rights ledger, Focus Fieldbook, or all 72 Margins records. No new subscriptions; no WordPress production/hosted staging writes; no deployment, merge, or publish.

## Required next stage acceptance

Execute the pinned generated 19-step Blueprint in a **free, isolated WordPress Playground** with the public Assembler template export, source-authenticated archival assets and source-approved rights. Verify that the real database round-trip matches the SHA-256 of the assembled WordPress candidate and that the selected runtime template is the intended `assembler//page` version; verify the actual full-width presentation at 320/390/768/1440/1920 and 200% zoom. Then run real-media Chromium screenshots, keyboard, touch, no-JS, reduced motion, axe/WCAG 2.2 AA and measured Lighthouse/CWV. Record the environment gap to WordPress.com Atomic and recheck hosted Jetpack at release without copying subscribers.

**Decision remains HOLD until those tests, founder visual approval and QD/CI signoff are real.**
