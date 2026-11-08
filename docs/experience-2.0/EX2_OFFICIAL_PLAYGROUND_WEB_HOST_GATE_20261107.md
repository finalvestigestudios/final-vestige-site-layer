# EX2 official WordPress Playground **web** host admission — 2026-11-07

**Status: DRAFT / OFFLINE REGRESSION TESTED / WORDPRESS-CORE NOT TESTED / RELEASE HOLD.**
Parent: draft PR #1509, exact head `2da94e7091b00fa530c1a0397c2b44936415fbd7`. Frozen PR #49 is untouched.

## Release-blocking integration finding

The pinned private Playground review ZIP imported by #1509 checks `home_url()` against only localhost, 127.0.0.1, ::1 or `*.localhost` in **three separate locations**: the very first Blueprint runPHP preflight and both standalone MU-plugin entrypoints. WordPress Playground's official browser build does **not** necessarily use a loopback WordPress site host. Its source file `packages/playground/remote/src/lib/config.ts` documents the separately hosted WordPress origin: `wpsandbox.wordpress.net`, while `playground.wordpress.net` hosts the Playground UI. The remote worker derives `WP_HOME`/`WP_SITEURL` from that configured WordPress origin.

Upstream source: [WordPress Playground remote config at pinned commit 2659f16](https://github.com/WordPress/wordpress-playground/blob/2659f16b3bf6e17479031a05cd28f9ac5e943f39/packages/playground/remote/src/lib/config.ts), [worker endpoint](https://github.com/WordPress/wordpress-playground/blob/2659f16b3bf6e17479031a05cd28f9ac5e943f39/packages/playground/remote/src/lib/playground-worker-endpoint.ts). Hosting implementations can change; re-check current origin before importing.

**Reproduced with PHP 8.4.24 (NOT WordPress core):** old pinned preflight rejects `https://wpsandbox.wordpress.net/scope:private/` before theme installation, and both old MU plugins decline registration even if the local marker exists. This may explain why the official-browser integration path has stalled, but it is not a measured Playground import failure.

## Change

SHA-pin the exact #1509 derived ZIP (`dbc305c6047756665a2fd54ffb88ab4822b7b43dad370c575423a627fd4ce061`) and exact plugin and Blueprint hashes. Deterministically alter **only** (1) the Blueprint's first preflight to allow exact `wpsandbox.wordpress.net` in addition to existing loopback hosts, and (2) both MU-plugin entrypoint guards to use that same exact-host alternative. Preserve the required local-review option marker, reject explicit `WP_ENVIRONMENT_TYPE=production`, and reject live `finalvestige.com`, WordPress.com alias, parent Playground UI and spoofed lookalike hosts. No server writes, deployment, analytics, billing or affiliate changes.

The 7-chapter HTML/CSS/JS, 72 public Margins records, five Focus links, two archival-image elements, Assembler pinned commit `75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f`, and all subsequent Blueprint import/validation steps remain unchanged.

## Exact offline evidence

- `test_playground_web_admission.py`: **10/10 passing methods** including actual PHP execution of original and corrected preflight and both MU guard files. Negative controls reject prod, similar-looking hostnames, explicit production environment, and missing marker. Local loopback remains permitted. Derivation deterministic; source-tampering rejected.
- An extended independent 14-method PHP variant was also tested locally; 14/14 PASS.
- Protected source HTML SHA-256 `baf26bcaddbf1b86b90f0065e1d68fbd856be03027ecd9d14ebc0ada60a21b1d`; CSS `152bfd327325997bee65191028501467292c70bc8573a39b439a5e6d49bc8afb`; JS `67230d93773a46fb2942368d5e13fb127788bf4504bb8ff106c317fd4af5b6ee`, unchanged in locally executed PHP.
- Derived compact candidate ZIP SHA-256 `ab239980f6d29bcd519bd56b854d1db610dd22542ab235bdd948f0e3878a945a`.
- The regression suite requires the **private parent ZIP to be provided separately**; do not commit unpublished review payload to public git. Reproduction: `python playground_web_admission.py parent_PR1509_review.zip --out fv-ex2-web-host-review.zip` then `python -m unittest -v test_playground_web_admission.py` in the same folder.
- No browser-WordPress, Assembler theme, Jetpack, archive-image byte or Lighthouse result is claimed by these tests.

## Rights, conversion and owner boundaries

No new media or claims. Apollo crew photograph WP #473 (NASA credited; metadata 78,346 bytes) and Franklin Victory Point reproduction WP #474 (1869 printed reproduction; metadata 466,043 bytes) remain attributed. Rights-pending NYPL #1258 remains excluded. No authentic network image-response bytes have been admitted.

**Offer → step → blocker → proposed change → evidence → owner:** free 52-page Focus Fieldbook → historic homepage to `/focus/` → official-browser WordPress integration cannot begin if safety preflight rejects its real host → admit exact sandbox hostname while retaining non-production boundary → PHP before/after 10/10 PASS; actual Playground import UNKNOWN → interim homepage engineer and independent Site QA. Claude owns Jetpack and paid-conversion attribution; Grok/Praxxis own acquisition. No incremental revenue claimed.

## Next external acceptance (do not silently waive)

Import the **private candidate ZIP** into disposable official Playground browser using its ZIP/Blueprint workflow, read host and environment via WordPress PHP, verify Assembler active and shortcode registered, render 7 chapters and all 72 Margins records; then execute real first-party archival-media request/byte capture, axe/WCAG 2.2 AA, reduced-motion/keyboard/no-JS/touch checks and Lighthouse at 320/360/390/768/1440/1920. Run 200% zoom. Verify Jetpack separately against actual hosted behavior. Playground is not WordPress.com Atomic production. Founder visual approval, exact SHA CI/QD PASS and separate release authorization remain mandatory.

**No public WordPress changes, no installation, no merge, no deployment.**
