# WordPress.com page 6 readback / rollback custody — 2026-11-02

**Status: DRAFT / HOLD. No CMS changes.** This is a release-preflight safeguard for the existing rights-safe seven-chapter flagship, stacked on PR #660 at `a258ce5c85a3d6d53e0d2514549c956ecda9b9f8`. It is not a production implementation or approval.

## Fresh read-only WordPress.com measurements

WordPress.com `pages.get(id=6,context=edit)` and `page-sections.list(id=6)` were independently queried on November 2, 2026. The responses agreed on:
- Site ID **256784396**, published homepage page ID **6**, Assembler theme, `modified=2026-10-30T09:14:14`.
- Exact raw Gutenberg content SHA-1: `7afdb933d2ec68fd993ef015c97a6eb9edfe0576`.
- Six top-level blocks, SHA-1 of each raw block **independently recomputed** against the WordPress block hashes (all six matched):
  - 0 Margins `6948a35c4e60ff43154440a7fad980dc3cae6859`
  - 1 Current Studios hero `1c97fec5cc356a02fb2f51a092f749c81efcd98c`
  - 2 Focus CTA `abc983ae1b3cf45d35589c7e5366ccc522cb0462`
  - 3 Home shell/Jetpack `f9da41225609adcca1c23f18b39079d1275c9249`
  - 4 Enter the Record `e53df6922591588603a41ce2e56dfdc418ba2d98`
  - 5 Organization JSON-LD `9454d1e44ee4932a4975796a88d2640ab9ecae8d`
- The read-only raw page contains **72 actual Margins item spans**, **one native Jetpack subscriptions block**, and **two `/focus/` links**. Nested Gutenberg blocks are not treated as top-level sections.

These are facts about the *current public WordPress document*, **not** proof that WordPress.com will preserve the unmerged flagship's inline JavaScript, CSP, or styling after a write.

## New preflight

`qa/release-candidate/page6_preflight.py` accepts fresh WordPress.com `pages.get` and `page-sections.list` JSON readbacks as local files. It never calls the CMS or a remote API. The CLI pins the exact source/WordPress chapter parity verifier before accepting a proposed replacement. The auditor:
1. Verifies both optimistic-lock tokens, published page ID, all six section indexes/types/hashes and recomputed **SHA-1 over the raw Gutenberg page and each section**. Missing or changed data means **HOLD**.
2. Independently counts the 72 Margins items, one native Jetpack subscriptions block and two Focus links. Checks the preserved named block identity.
3. Rejects malformed/nested/extra source blocks and any replacement not comprised of **exactly one core/html block** with interactive delivery.
4. Builds an in-memory before/after preview replacing only block 1. Proves indices 0,2,3,4,5 are byte-identical and that restoring the original hero produces the **exact original page bytes**. Returns only cryptographic fingerprints and safe counts; it does not emit full HTML, subscribers or credentials.
5. Returns `publication=HOLD` regardless of success. No application or rollback is performed.

### Operator usage (after independent release approval to perform preflight only)

Obtain **fresh**, minimally scoped local JSON response envelopes using the existing authenticated WordPress connector; do **not** commit or upload the raw readback files or subscriber/user records:

```bash
python experience2/home-flagship/qa/release-candidate/page6_preflight.py \
  --repo . \
  --page-json /private/path/page6-pages-get.json \
  --sections-json /private/path/page6-sections-list.json
```

The `page6-pages-get.json` input must include `id,status,modified,content.raw` from edit context. `page6-sections-list.json` must include `id,modified,content_hash,sections,classic_content`. This is an **offline, read-only** preflight, not a substitute for WordPress-hosted draft compatibility checks. If the current homepage changes, do not update lock values silently: obtain a new approval and regenerate the reviewed manifest.

## Evidence and limitations

- Twelve isolated Python adversarial tests passed locally before this PR: valid synthetic byte-identical rollback, hero drift, timestamp drift, swapped block hashes, extra root, Jetpack loss, Margins loss, Focus-link loss, double replacement, missing interactive delivery, malformed Gutenberg nesting, and unowned trailing material. GitHub hosted exact-head CI is separately required.
- We did **not** pass actual WordPress.com production readback JSON into Python or execute the proposed block in WordPress.com; the independent live WordPress hash calculation was performed in-memory during the read-only inspection. The unit tests use synthetic public-content-free fixtures.
- This does not certify hosted WordPress.com Personal-plan script retention, physical-device behavior, WCAG 2.2 AA, image rights, independent QD, or founder publication approval.
- Do not modify frozen PR #49, Apollo PR #158, Mind/affiliate lane, page 6, theme, plugins, site settings, Jetpack subscriber data, or navigation.

**Release gate: HOLD.** Continue toward a reviewed hosted compatibility plan, manual assistive-technology/real-device checks and independent QD. No Business-plan upgrade is recommended solely to obtain staging.
