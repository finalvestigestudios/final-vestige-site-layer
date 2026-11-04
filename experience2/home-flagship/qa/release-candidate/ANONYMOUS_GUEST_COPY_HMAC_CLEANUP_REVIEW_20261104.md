# Seven-chapter flagship — anonymous Playground copy custody and cleanup (2026-11-04)

**Release decision: HOLD. Source-controlled offline correction, NOT WordPress-certified.**

## Branch custody

- Parent: draft PR #985 at exact commit `1f500d0ae16218574c288a23e337af571b521332`; its branch is `chatgpt/ex2-playground-private-fixtures-safe-cleanup-20261104`.
- This companion change is confined to `isolated_guest_render_gate.mjs` and the new offline test `test_guest_copy_ownership_and_cleanup.mjs`.
- PR #49 (`10495883299d53596992c26a8987f629b2904670`) remains frozen. No homepage HTML, CSS, imagery, WordPress production, Focus landing, theme or tracking source modified.
- Only production WordPress site `256784396` is present in `wpcom_user_sites(environment='all')` (2026-11-04 check). WordPress.com Personal has no native second staging site; do not use its included wpcomstaging.com host as one.

## Source-traced blocker

The prior anonymous render gate generated PHP that called `wp_insert_post(...post_status=publish...)` without selecting the isolated Playground editor's `unfiltered_html` capability. A PHP/WordPress write performed without that capability can strip script/style elements, producing a source checksum mismatch and preventing real anonymous browser qualification. **This is a risk established by source inspection, not a demonstrated WordPress runtime failure.**

The original PHP also accepted a draft by matching its title/status/content, not by checking the original editor HMAC; deleted its guest copy by ID and title prefix alone, with no ownership HMAC; and captured the new guest-copy ID solely from the returned PHP JSON. A malformed, lost or corrupted receipt could bypass deletion of a page already published in isolated Playground.

## Narrow correction

1. Check the existing private synthetic-only marker and one-time 64-character fixture token; refuse when another guest copy is already tracked.
2. Require the original draft's `_fv_ex2_editor_qa_owner` HMAC, verify public-Margins/synthetic-Jetpack markers, and use ONLY the disposable local admin with `unfiltered_html` to preserve Gutenberg-saved bytes. `wp_slash` source content before insertion.
3. Establish a separate guest-copy ownership HMAC in post metadata and write its ID to the non-public `/tmp/fv-ex2-guest-copy-id` BEFORE returning a create receipt.
4. Arm cleanup before invoking PHP creation. If the response is missing or damaged, cleanup recovers the ID from the private tracker. Reject supplied/tracked ID mismatches and any wrong HMAC, type, title, source marker, host, site mode or environment.
5. Require verified page absence AND removal of the private tracking file. Never delete pages without an exact HMAC match. Failure to prove deletion or tracker removal closes the release gate.
6. No new subscription, navigation changes, published WP.com content, external URLs, pixels, analytics, affiliate links or design chapters.

## Executed evidence

- V8 evaluation of functions extracted from actual committed GitHub `isolated_guest_render_gate.mjs` and test bodies from `test_guest_copy_ownership_and_cleanup.mjs`, with mocked file IO/module imports: 7/7 test bodies passed (the PHP-lint test's subprocess was stubbed in V8; do not count it as actual PHP execution).
- Actual system PHP 8.4 lint of the two generated PHP scripts, reconstructed from the emitted exact-source function output: both PASS, zero syntax errors. The comparison with complete checkout source is not established.
- Test negative controls remove HMAC draft binding, guest tracking, admin HTML permission or deletion HMAC and confirm assertions fail.
- Committed full Node `node --test` file is **NOT YET RUN in a complete checkout**. No verified `@wp-playground/cli` runtime or pinned Assembler installation was present. No localhost WordPress, real media transfer, axe or Lighthouse was executed.
- The remaining original candidate/WordPress CLI/render acceptance must be run from this exact head and not inferred from the isolated tests.

## Reproduction from exact checkout

```sh
node --test experience2/home-flagship/qa/release-candidate/test_guest_copy_ownership_and_cleanup.mjs
node experience2/home-flagship/qa/release-candidate/playground_gutenberg_editor_gate.mjs --self-test
node experience2/home-flagship/qa/release-candidate/playground_assembler_render_gate.mjs --self-test
# Then run the existing candidate builder and official free Playground + Assembler admission harness;
# retain negative controls and complete anonymous screen/axe/image receipts.
```

## Conversion-first release decision

| Offer | Funnel step | Blocker | Change | Pass / fail evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Existing free **52-page Seven Day Focus Fieldbook** | Social evidence story → homepage → contextual Focus button → signup | The **anonymous visitor** staging path could fail to preserve markup or leave a published local test copy after a lost reply | Isolated capability-bound copy, HMAC custody and guaranteed tracked cleanup | Offline V8 7/7 and local PHP 2/2 lint; real WP/Assembler anonymous browser **NOT TESTED** | Homepage engineering, independent Site QA; Claude owns attribution/checkout |
| Existing rights-cleared owned digital product (TBD by commerce audit) | Confirmed lead → relevant paid offer | No confirmed mapped offer or independently attributed order | No new claims/links/instrumentation; request commerce acceptance via issue #820 | Revenue, orders, fees, refunds and net per 1,000 qualified sessions **NOT VERIFIED** | Claude and founder |

Preserve Grok's TASK-008 social asset IDs/campaign URLs, independent investigations, public 72 Margins, Jetpack confirmation/welcome, and archive provenance. This sprint has **no measurable commercial uplift claim**.

## Next release gate

Run actual anonymous WordPress/Assembler Playground with **five viewports** and browser image decode/network receipts; complete axe whole-document and manual WCAG, keyboard/no-JS/physical 200% zoom and Lighthouse. Hosted WordPress.com Atomic differences (Jetpack, URL redirects, cookies, CWV) remain separate acceptance limits. Independent QD/CI and founder visual/release approval are still required. No merge, live install or publication is authorized.
