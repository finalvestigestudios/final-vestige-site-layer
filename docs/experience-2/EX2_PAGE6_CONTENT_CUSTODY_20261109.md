# EX2 Page 6 content custody — fail-closed release review gate

**Status: DRAFT / RELEASE HOLD.** Companion stacked on #1834 at parent `83d7128dc5e98f04808c099aad53e7e1ce05576f`; frozen #49 untouched.

The production WordPress.com Page 6 is **already live**, including an existing seven-chapter archival presentation, 72 distinct Hidden in the Margins fragments, and an intact native Jetpack subscription block. This branch **does not modify that page**.

## Specific release hazard

The standalone Experience 2.0 `index.html` is **not** an admissible full-page replacement for WordPress Page 6. It has seven chapter anchors and Focus CTA links, but **zero** of the original 72 Margins records and **no Jetpack subscription block**. An unguarded replacement would destroy both. The source itself expressly warns not to deploy as the WordPress homepage.

The canonical read-only Page 6 inventory was captured November 9 PT / November 10 UTC, page modified timestamp `2026-11-05T12:07:24`. Its full-content SHA-256, 72-record markup SHA-256, complete 495-character Jetpack div SHA-256, and content inventory are in the adjacent public-only baseline JSON.

## Gate and reproducibility

Use Python stdlib only, no paid services or credentials. The provided CLI accepts **a public-content-only WordPress Page 6 HTML export** and checks it against the baseline fingerprints:

```bash
python -m unittest tests/experience-2/test_homepage_preservation.py -v
python tests/experience-2/verify_homepage_preservation.py \
  --baseline tests/experience-2/page6_public_inventory_20261109.json \
  --candidate /path/to/isolated-proposed-page6-public-only-content.html \
  --out /tmp/fv-page6-custody.json
```

The script exits nonzero on any removal, reordering or edit of the 72 original fragments, Jetpack block alteration/removal, Focus link reduction, or missing one of the seven expected chapter anchors. `--current-snapshot` additionally requires byte-exact production markup (use for detecting drift in the original, not a planned additive injection). The script never sends a request, installs a plugin, connects to WordPress, or edits the CMS.

**Actual run evidence (local):** 11/11 synthetic mutation regressions passed. On the independently source-pinned standalone seven-chapter `index.html` at PR #1822 (unchanged by #1834), the gate returned **HOLD** as intended: 0 Margins, no Jetpack, but 3 Focus URLs and all seven chapter anchors. This is a useful rejection, **not** an end-to-end staging acceptance.

## Integration route and unpassed gates

Prefer a separate scoped insertion into a private, public-content-only WordPress Playground/Assembler copy, retaining the original Page 6 content verbatim and showing the new experience without replacing the canonical page, user records or subscriber list. The Personal plan has no native WP.com clone. An isolated clone cannot certify WordPress.com hosting, live Jetpack behavior, customer conversion or field CWV. Obtain an actual post-integration WordPress-rendered HTML export, run this guard with that export and separately validate the real signup and first-party image bytes before considering release.

Fingerprint equality is a **necessary preservation check, not sufficient accessibility, appearance, security or subscription proof**. Some harmless CMS serialization changes may fail closed and require a separately reviewed baseline refresh. Do not use this test to bypass CI/QD, founder approval, WCAG/axe, Safari, genuine media transfers, Lighthouse, or verified net revenue. No merges/deployments/production writes or budget actions are authorized.
