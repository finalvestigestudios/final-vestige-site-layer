# FV Experience 2.0 — LOCAL WordPress Playground CLI transport (2026-11-07)

**REVIEW ONLY / RELEASE HOLD.** Parent PR #1379 at `8fa044002e152a06ffc3a8b18a991b5fa3f0be64`. Frozen PR #49 and WordPress.com production page 6 remain untouched.

## Problem and solution
The current browser launcher embeds an approximately 157 KB source Blueprint as a ~211 KB HTML launcher with a very long Base64 URL fragment. An isolated local WordPress execution path is preferable to another static fixture or to making unpublished code publicly fetchable. WordPress Playground officially supports local ZIP Blueprint bundles in `@wp-playground/cli` using `--blueprint` and `resource: bundled`.

`local_cli_bundle.py` takes the **exact, SHA-pinned existing PR #1379 reviewer ZIP** as its only input. It relocates the two PHP MU-plugin strings into bundled files (rather than a gigantic inline URL), keeps the original six WordPress Blueprint steps and pinned Assembler commit unaltered, and verifies reconstruction of original PHP/step values in memory before writing a deterministic ZIP. This is a transport and source-custody change, not a new front-end design.

## Exact custody
- Current candidate Blueprint SHA-256: `300c79f7936d7fdf58294bb96e7b0cd1ebc0b349cdf4d2c4d13e5ec52000b23f`
- Canonical candidate Git blob: `137c74a476005684a28f5ff9a36e75c6b03268f7`
- Reviewer PHP SHA-256: `a58e144fd8e9e584681b7edceb667a4a5b0ca303e49b6902299b941d0a95a9fc`
- Assembler pinned commit: `75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f`
- Tested output ZIP: `fv-ex2-local-cli-bundle.zip`, **43,347 bytes**, SHA-256 `52fc95efcdb40473b94e6c8f3ab3903fcad0559a67f2ca245cfab5b9f83babe4`.
- ZIP contains `blueprint.json`, `SOURCE_CUSTODY.json`, `REVIEW.txt`, and two authenticated-context PHP review files. No WordPress database, production users, subscribers, secrets, merchant data or paid services.

## Local isolated developer acceptance (requires an Internet-connected machine)
Generate the existing reviewer ZIP using `make_private_browser_receipt_variant.py` against its pinned inputs, then:

```bash
python experience2/home-flagship/playground/local_cli_bundle.py --input FV_EX2_FOCUS_FIRST_SCREEN_REVIEW_ONLY.zip --output fv-ex2-local-cli-bundle.zip
FV_EX2_REVIEW_ZIP=FV_EX2_FOCUS_FIRST_SCREEN_REVIEW_ONLY.zip python -m unittest discover -s experience2/home-flagship/playground -p test_local_cli_bundle.py -v
npx @wp-playground/cli --blueprint=./fv-ex2-local-cli-bundle.zip server
```

Open the **loopback** address emitted by the CLI. Verify real Assembler rendering, all 7 chapters and 72 Margins, 5 Focus links, both historical images with **actual network response bytes**, and the local JSON viewport receipt. Repeat at 320/360/390/768/1440/1920px, 200% zoom, no-JS, reduced motion, keyboard/touch. Run independent axe WCAG and Lighthouse (measured laboratory results). Archive screenshots, actual request/response evidence, console traces and test outputs. Fail closed if any test is unavailable.

## Tests actually executed in this sprint
- Four isolated Python unit methods PASS (deterministic package, ZIP structure, deliberate Blueprint mutation rejection, deliberate theme manifest mutation rejection).
- Both extracted review PHP files pass `php -l` on PHP 8.4.
- Missing source ZIP fails instead of silently skipping.
- Local ZIP packaging preserves source content **but the WordPress CLI runtime did not start in this environment**; external hosts and npm package registry cannot be resolved.
- The submitted PR includes source and tests; the generated ZIP is supplied separately in the founder's private conversation as an artifact, not uploaded to a public repository.

## Rights, operational and conversion constraints
Only the existing NASA Apollo 1 S67-19766 (#473) and Franklin Victory Point printed reproduction (#474) image references are retained; NYPL #1258 remains excluded from the candidate pending rights review. Asset response bytes and origin parity must be measured. The free 52-page Focus Fieldbook remains the lead-capture offer. This work validates *no* subscribers, Jetpack welcome delivery, merchant acceptance, purchases, affiliate conversions, refunds or realized net revenue. It changes no campaigns, instrumentation, editor ownership or public pages.

A local WordPress/Assembler test is **not WordPress.com Atomic hosting equivalence**; Jetpack and production field Core Web Vitals require separate acceptance. No plugin installation on production, merge, deployment, affiliate activation, public upload, new subscription, or spend authorized. Independent CI/QD and founder visual/release approval remain required.

**OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:** Existing Focus Fieldbook → visitor evidence-to-action path → no actual WP-rendered QA → deterministic local CLI acceptance transport → source/packaging verification PASS, runtime BLOCKED → Interim Homepage Engineering and Site QA; Claude owns production attribution/checkout, Grok/Praxxis content/acquisition.
