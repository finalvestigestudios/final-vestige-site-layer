# R27 — Citation placement and malformed-token evidence gate (HOLD)

Issue #136 · Preparedness Archive · R26 parent: 99b67b370f27416b62addf9ab73bfdeb947d61a2 · Proposed changes are draft-only and not approved for publication.

## Concrete vulnerability and fix

Previously, the R26 citation-review validator counted recognized {{cite:source-id}} tokens by regular expression. That did not detect malformed starts such as {{cite: id}} when the valid token count remained unchanged, and did not prove that recognized tokens were in article text rather than hidden in HTML attributes, comments, scripts, CSS, templates, or other inert/non-prose regions.

The updated existing mandatory citation_fallback_review_gate.py now loads its fixed, local sibling citation_token_visibility_gate.py from an explicitly checked file path (works in isolated Python -I). The helper independently enumerates all cite-like starts, matches each exact recognized token to an original Unicode-codepoint location emitted from HTMLParser data, and rejects tokens in tags, attributes, comments, script/style/template/textarea/noscript/svg/math/iframe/object/pre/code regions. It never rewrites, deduplicates or translates the source prose. It is not an audit of cited claims, accessibility of links, visibility under arbitrary CSS, emergency safety, or source-reading depth.

The existing mandatory 13-stage private preflight calls this validator automatically through its established citation_fallback_human_review_queue stage, without modifying the preflight contract.

## Tests executed locally on committed-byte-identical Python inputs

- R27 new adversarial citation tests: 60/60 PASS.
- R26 previous source-identity tests: 74/74 PASS.
- R25 prior reviewer-packet tests: 63/63 PASS.
- Combined synthetic-scope tests: 197 PASS. These do not replace the full original checkout validation.
- Native exact-checkout command remains BLOCKED: original taxonomy.json is absent from the local reconstructed snapshot. The CLI exits 2 (HOLD). Full validate/build/unit-suite/13-stage preflight not demonstrated on the current private repository; GitHub Actions runner dispatch was failing before job execution in prior runs.

## Actual remote-source screening, 2026-10-31

Authenticated reads of all 35 original article bodies at the R26 head found 1,952 recognized tokens and zero malformed cite-like starts or immediately tag-contained citation tokens by preliminary raw-text screening; the original water-planner body contained seven more recognized tokens (1,959 total). This preliminary screening is narrower than the new HTML parser, has NOT run the full trusted checkout, and is NOT source claim/safety verification.

Original Claude cluster branch SHAs rechecked:
- start: 2122d856fce9f64887c16df3d52e64be9f59a55b
- shelter: 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976
- food: 4b009361277ea1d4617b368f5d45104c7318b284
- health: d2212d0ca0750817d3929865d3069835980faf20
- hist-food: 2acf65ca3efa9b4b5db7976f379b9ea693be43a4
- hist-home: f654e600f89c321a480dd8f055be4d13d0673490
- hist-field: a5ce8a62f168db05c95232e3eb385dccd0d19e7f

Independent QA PR #157: 7d1ae6b8ef93d10cfb6810987672360885e9c1aa. Examined exact patches for drill power safety, refrigerated medicine language, Red Cross source category, taxonomy gates and older tests. These are useful safety-review candidates on a separate older branch, not an automatic content overwrite or safety PASS.

Synthetic food fixture PR #169: e9cd7766dac59d47ab467d8945269b9146c2aef5. Examined exact patch; it isolates fixture upgrades in temp copies and removes stale hardcoded source-verification assumptions. The original contributor's food branch remains 4b009361277ea1d4617b368f5d45104c7318b284.

Home lead PR #49: 10495883299d53596992c26a8987f629b2904670. Flagship homepage PR #254: 8fa6fc52e034f511b96ae526f4a852e1bd76db04. No changes or merges to either.

## Unresolved — release state HOLD

Reconcile the 30 shared-URL reading-scope review groups and 43 base-source fallback relationships, verify each consequential claim across 1,959 citation occurrences, run all native scripts on an exact trusted checkout and obtain independent qualified emergency/medical review plus QD approval before any publishing. No public publishing, menu/navigation changes, WordPress/CMS writes, unreviewed medical-safety claims, or false QD PASS.
