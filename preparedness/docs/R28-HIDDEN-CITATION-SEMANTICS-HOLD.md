# R28 — semantic/inline-hidden citation evidence HOLD (Issue #136)

**Scope:** Preparedness Archive source/citation integrity only. No articles, tool content, metadata, crosswalk, homepage, WordPress, public navigation or publication state changed.

## Gap and bounded repair

R27's raw HTMLParser token placement gate correctly rejected citations in comments, tag attributes and inert elements, but accepted syntactically valid `{{cite:id}}` placeholders in `hidden`, `inert`, `aria-hidden="true"`, and inline CSS concealed elements. This could produce structurally correct citation totals while evidence appeared only in hidden HTML.

R28 extends the same mandatory citation-context audit (no stage bypass) to exclude those locations, including nested ancestors, inline `display:none`, `visibility:hidden|collapse`, `content-visibility:hidden`, and zero opacity. It also excludes document `head/title` and form/control `select/option/optgroup/datalist/button` regions from article-prose evidence. Boolean `hidden="false"` is correctly treated as hidden.

**Limit:** This is a static HTML semantic/inline-style check, **not** computed browser styling. External stylesheets, CSS classes, scripts, dynamic DOM changes and assistive-technology behavior require separate browser/human QA. It does **not** establish factual adequacy, source accuracy, advice safety or QD approval.

## Verification scope

- Added 63 deterministic R28 adversarial/positive Python tests; 63/63 passed against the local corresponding implementation.
- Relevant locally reconstructed R25–R28 suite: **320/320 passed**, no skips or failures. This is not full-repository CI. Python compile check passed.
- Authenticated GitHub lexical scan of **35 unchanged article bodies** and **one water-planner body** at parent commit `be6b5189524394d9e3cee5996a2c7becb4e75dcf`: 1,952 article citation placeholders + 7 tool placeholders = **1,959**; no transport errors. Limited scan saw no obvious hidden-attribute or inline-hidden patterns. It is **not** equivalent to executing the new Python gate against the entire checkout.
- The complete native validator/build/full 13-stage preflight remains unexecuted because local GitHub DNS resolution fails. Hosted Actions execution is not established.
- All seven frozen original Claude branch heads were rechecked on October 31, 2026: food `4b009361277ea1d4617b368f5d45104c7318b284`; health `d2212d0ca0750817d3929865d3069835980faf20`; historic-field `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`; historic-food `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`; historic-home `f654e600f89c321a480dd8f055be4d13d0673490`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; start `2122d856fce9f64887c16df3d52e64be9f59a55b`.
- Safety QA PR #157 (head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`) and fixture QA PR #169 (head `e9cd7766dac59d47ab467d8945269b9146c2aef5`) inspected; both separate draft bases. The integrated article already avoids main-power-off drills and contains stronger refrigerated-medication prescriber/pharmacist warning, while the integrated test already uses an isolated temporary fixture; **do not blindly merge either older patch**.
- Homepage PR #49 head `10495883299d53596992c26a8987f629b2904670` and #254 head `8fa6fc52e034f511b96ae526f4a852e1bd76db04`: read only, untouched.

## Release and evidence custody

**HOLD — may_publish=false; qualified_safety_clearance=false; independent_QD_approval=false.** Original 81-file frozen corpus, seven source inventories, 35-article slate, 30 shared-source review groups, 43 base fallbacks and 1,959 citation occurrences must remain intact. Human source reading-scope/citation-claim reviews and qualified emergency/medical safety assessment are still pending. No public or CMS writes are authorized. This draft is engineering-only.

No false PASS should be inferred from passing synthetic tests or unchanged source counts.
