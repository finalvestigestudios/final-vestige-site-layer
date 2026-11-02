# R80 — Private, accessible full-evidence reading room (DRAFT; HARD HOLD)

**Owner:** Preparedness Archive source/citation safety-gates lane, Issue #136.
**Stacked parent:** R79 consequential-context PR #689 at immutable SHA `f83f1af253aac8a4069ec60df2d55fcee451edc0`.
**Separate immutable release candidate:** PR #584 / `ddb3528ba6494dada1fa1c3a142ce746e3a67706`, untouched.
**Alternative parallel R79:** PR #686 / `1be8e64420a40102d974d9704bbdc3b0ca920bd4`, separately unmerged; R80 makes no claim to combine those two siblings.

## New engineering deliverable

R80 converts the *fully reconstructed and sealed* R79/R78/R77 source-review evidence into **one self-contained, offline, accessible, printable HTML reading room** for independent fact-checking. This is NOT WordPress content and MUST NOT be pasted into the public CMS. The HTML deliberately has no active outbound source links, network fetches, external CSS, scripts, forms, images, publication API, approval importer or data telemetry.

The reading room makes every original source context accessible without summarization or losing reading depth:

- **35 article and six tool dossiers**, with **4,070 complete original DOM text blocks in original document order**.
- **2,173 actual local citation occurrences**, linked to **2,359 distinct origin-scoped source-variant edges**. No shared source ID or exact URL may collapse multiple research origins.
- **244 individually displayed, complete candidate and historical source research records**, including uncited readings and unaltered source metadata, without truncation.
- **347 original R79 uncited consequential-language review work orders**, placed beside their exact text blocks and carrying full adjacent context, neighboring cited passages and source identities. They are lexical screening tasks, **not 347 substantiated source errors or unsafe procedures**.
- Existing **32 shared-URL** and **15 repeated-ID** human review groups remain unresolved, not auto-fixed.

Rendering invokes the R79 **full independent evidence reconstruction** and validates the downstream mapping again. All source URLs render as **inert escaped text**; source records are completely rendered as escaped JSON. Local hash-based navigation links identify document, block and distinct source origin without WordPress URL rewrites. A Content Security Policy disables network/resources and form submission. No user-provided markup or source field becomes executable HTML. Duplicate anchors, broken navigation, active content, missing citations, missing sources and missing HOLD banners fail closed. Print CSS retains warnings, context and complete text.

This output is an editorial evidence-review *aid*, not independent confirmation of a government source link, exact source applicability, current guidance or a qualified emergency safety judgment. Neighboring citations are context only. It does not establish that medical, food-preservation, water-treatment, generator, CO, infant, medication or evacuation instructions are safe.

## Private reproduction (trusted exact checkout only)

```sh
python -I preparedness/tools/r80_offline_evidence_reading_room.py
python -I preparedness/tools/r80_offline_evidence_reading_room.py --private-html-stdout > /tmp/fv-preparedness-r80-private-review-only.html
python -I -m unittest discover -s preparedness/tests -p test_r80_offline_evidence_reading_room.py -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The first command prints only an evidence census, output bytes and SHA-256; the second prints complete **unpublishable** private HTML to stdout. Neither action writes to the repository, production, WordPress or any CMS. Only redirect to a **private** temporary directory; do not commit generated HTML to the repo or upload it to an artifact/CDN. Tool output is not approved emergency advice.

The isolated R80 test module defines **121 individual Python checks** (41 distinct document cases, 40 corpus custody/security checks, 40 injection/negative checks). They must actually execute in hosted CI before any successful-test count is asserted. Existing R79 separate private diagnostics were verified successful on exact parent head at [Actions #41542360363](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41542360363), while the **separate mandatory private machine integrity check FAILED CLOSED** at [Actions #41542360400](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41542360400).

## Immutable coordination snapshots (verified 2026-11-02)

| Workstream | Exact Git SHA |
| --- | --- |
| Start Here Claude | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter Claude | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food Claude | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health Claude | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical food Claude | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical home Claude | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Historical field Claude | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Independent safety QA PR #157 | `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (draft, unmerged) |
| Synthetic-fixture PR #169 | `e9cd7766dac59d47ab467d8945269b9146c2aef5` (draft, unmerged) |
| Homepage lead PR #49 | `10495883299d53596992c26a8987f629b2904670` (untouched) |
| Flagship PR #604 | `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` (untouched) |

PR #169's remaining shared-working-tree `_dup_test.json` fixture concern has been referred to that owner and is **not** altered in R80.

## Release integrity is NOT passed

Five current Claude branch heads have diverged from frozen historical R14 baselines. The separate 13-stage `seven_cluster_git_parity` publication gate still FAILS CLOSED and MUST NOT be waived or silently rebaselined to get publication through. Outstanding items include human inspection of candidate/original source links, source URL reuse/claim-scope and fallbacks, 15 safety exceptions, 22 editorial decisions, qualified reviews of consequential emergency guidance, real WordPress/browser/mobile/print/assistive QA, independent QD and founder authorization.

**Release status: HARD HOLD.** Zero human source/claim/safety/QD approvals. No article edits, source edits, publishing, CMS writes, navigation changes, homepage changes, Git merge or unsupported safety claims. The new HTML is for offline private review ONLY.
