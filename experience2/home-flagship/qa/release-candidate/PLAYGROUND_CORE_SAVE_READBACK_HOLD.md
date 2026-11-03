# EX2 / Page 6 — disposable WordPress core persistence gate

**Draft / RELEASE HOLD / no production writes.** Builds on PR #793 exact
`0ef30cffea2d20c21f5d78ee1fff3b5edcb29a69`. This is the first
**WordPress-core database save-and-raw-readback harness** for the existing
combined NYPL rights-safe + Margins contrast candidate, not another homepage
design. It uses only the existing upstream synthetic fixture, never a live
page export. It can execute in the isolated free WordPress Playground CLI
using PHP/WASM and SQLite, without Docker, a WordPress.com upgrade, or
subscriptions. It will not operate on finalvestige.com.

## Exact source and safety

- The generator imports the already-tested `source_fixture()`,
  `build_candidate()` and contrast CSS from the existing release-candidate
  source. The generated input carries the same rights-safe correction,
  72 records, native Jetpack Gutenberg block comment, and Focus Fieldbook
  reference as the synthetic tests; it does **not** use or expose a copy
  of page ID 6. SHA-256 is checked by the Node harness before starting PHP.
- The PHP probe refuses a nonloopback site URL or a missing synthetic marker.
  It inserts **one draft page inside the ephemeral Playground WordPress
  database**, reads `post_content` back through WordPress core, calls
  `parse_blocks()`, checks invariants and deletes the draft. The
  Node runner closes the isolated site and rejects any non-PASS result.
- The GitHub workflow uses `contents: read`, no WordPress credentials,
  no production API endpoint, no export of users/subscribers, and no
  uploading the candidate or the Playground database as CI artifacts.
- It pins the free `@wp-playground/cli@3.1.56`, Node 22,
  WordPress 6.8 and PHP 8.3. The snapshot is **not** WordPress.com
  Atomic, the live Jetpack plugin suite, or the Assembler theme.

## Reproduction in an authorized developer checkout

Run in a clean temporary directory and ensure no private content is present:

```bash
python -I -m unittest discover -s experience2/home-flagship/qa/release-candidate \
  -p test_build_combined_page6_offline.py -v
python -I experience2/home-flagship/qa/release-candidate/write_synthetic_playground_candidate.py \
  --output /tmp/fv-ex2-synthetic-candidate.html \
  --manifest /tmp/fv-ex2-synthetic-manifest.json
npm install --no-save --no-package-lock --no-audit --no-fund @wp-playground/cli@3.1.56
node experience2/home-flagship/qa/release-candidate/playground_core_save_readback.mjs \
  --candidate /tmp/fv-ex2-synthetic-candidate.html \
  --manifest /tmp/fv-ex2-synthetic-manifest.json
rm -f /tmp/fv-ex2-synthetic-candidate.html /tmp/fv-ex2-synthetic-manifest.json
```

## Acceptance and unsupported claims

PASS requires actual WordPress-core draft insertion, SHA-exact raw readback,
balanced top-level Gutenberg HTML blocks, 72 Margin records, Jetpack
subscription block comment, Focus Fieldbook, the chapter-nav marker and
integrated accessible-contrast marker. It records WordPress/PHP versions,
before/after SHA-256, block counts and boolean verdicts, **not** page text.

**This is not a Gutenberg browser-editor Save action** or a production
Assembler/Jetpack rendering test. WordPress core persistence does not prove
that Gutenberg's editor will accept these custom HTML blocks, that Jetpack
signup renders or sends subscriptions, that all scripts survive the editor,
or that hosted CSP, browsers, reduced motion, keyboard, screen readers,
Safari, Lighthouse and p75 field CWV qualify. The next development gate is
a private *editor* save/readback with the free Assembler theme (download
from its official WordPress.com theme page if source/terms allow), followed
by exact-source protected staging replay without credentials in artifacts,
then independent QD/manual WCAG 2.2 AA and founder release approval.

The actual live page was read only on 2026-11-03, status `publish`,
modified `2026-11-02T17:48:13`, with 72 Margins and one Jetpack block.
Production site ID 256784396 has **no separate staging** on the currently
confirmed Personal plan; its `wpcomstaging.com` address is not a clone.
We have not requested an upgrade. The disputed NYPL digital-capture rights
remain unverified and the existing source links must be preserved.
Frozen PR #49 is unchanged; PR #158 Apollo and Issue #171 Mind remain separate.
No merge/deployment/WordPress publication is authorized.

**Evidence policy:** CI PASS must be checked on the final Git commit SHA.
Source syntax pass, unit tests, Playground boot, core save/readback and
Gutenberg editor render are separate gates; never conflate them.
