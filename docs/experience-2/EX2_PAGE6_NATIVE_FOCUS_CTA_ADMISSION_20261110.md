# EX2 Page 6 — native Focus action admission correction (2026-11-10)

**DRAFT / RELEASE HOLD / no WordPress writes.** Isolated stack on PR #1866 at parent `2daa46608bdcf42c8043fb57c33dda75e80ede83`. Frozen PR #49 is untouched. This corrects integration logic; it is **not** a new visual chapter or campaign.

## Reproduced real-page blocker

A fresh read-only `wpcom_mcp_pages_get(id=6, context=edit)` returned the published Gutenberg source (modified `2026-11-05T12:07:24`). It contains 150,710 source characters, five Custom HTML blocks, the old seven-chapter flagship in **the second** HTML block, **72 original Margins records**, and **one serialized Jetpack subscription block** outside that flagship. Its native Focus CTA is:

`<a class="fv-focus-cta__button" href="/focus/" ...>`

The #1860 composer previously required `https://finalvestige.com/focus/` **outside** the replaceable flagship. This is FALSE for the actual Page 6 source (which uses a root-relative link) even though the action is valid. The absolute link happens to occur **inside** the replaceable candidate; it cannot prove preservation of the external WordPress-native CTA. Consequently the existing builder would refuse the exact real-page input despite earlier synthetic tests passing. This is a reproducible **integration blocker**, not a claim of production malfunction.

## Isolated changes

- `tools/experience-2/compose_page6_flagship.py`: select exactly one original, external `fv-focus-cta` section and one `fv-focus-cta__button` link; admit only `/focus/` and canonical `https://finalvestige.com/focus/`, with no query/fragment, non-HTTPS scheme, off-domain host, protocol-relative URL or userinfo. Record preserved target in offline receipt. Do not infer success from a matching URL elsewhere.
- `tools/experience-2/build_page6_playground_bundle.py`: emitted PHP now checks the **native section/button link** (including real production root-relative spelling) as part of independent local WordPress parsing; no longer scans for an unrelated absolute URL anywhere.
- Update existing scoped-composer and Blueprint fixture tests to represent actual Page 6 link semantics; include approved absolute alternative and negative cases for redirects, duplicate CTA, unrelated absolute link and PHP redirect substitution even when the attacker-controlled payload digest matches.

## Evidence and limits

- Live read-only Page 6 structural check: old external-link gate **FAIL**; corrected native action gate **PASS**; 72 Margins and one Jetpack block outside exactly one flagship confirmed. 42,732 chars outside the target block remain in scope for byte-preserving composer validation.
- **Local source-equivalent** Python regression suites: 19/19 scoped-composer controls and 14/14 Playground-builder/PHP-mock controls passed, including `php -l` and a negative test proving redirected Focus fails even with a matching content SHA. Local fixture uses the GitHub-pinned eleven source blobs, but a **separate synthetic Git commit**, not the new PR's exact SHA. This is **not** exact-checkout CI or actual WordPress.
- WordPress.com connected tooling still lists only production site `256784396`. The site's Personal plan has no native staging clone. Isolated Playground is the no-subscription path, but its CLI cannot be launched from the current runtime because `registry.npmjs.org` DNS resolution fails. A genuine private WordPress/Assembler render, Jetpack functional signup, network image-transfer bytes, axe/WCAG, Lighthouse and hosted browser/security acceptance remain **NOT TESTED**.
- Current media attribution metadata read-only verified: Apollo image 473 (NASA S67-19766), Franklin 474 (Victory Point note, archival reproduction), NYPL 1258 (1903 BRT map). Metadata and reported file sizes do not certify licensing or completed media transfers.

## Conversion acceptance / release gate

**OFFER** — existing free 52-page Focus Fieldbook. **FUNNEL** — evidence → *original* WordPress Focus CTA → independently confirmed subscriber → verified paid conversion. **BLOCKER** — invalid admission mistakenly rejected legitimate Page 6 while potentially confusing candidate links with preserved native CTA. **CHANGE** — bounded, approved URL verification in composer and PHP plus adversarial tests. **PASS** — local equivalent source tests and live read-only source shape. **NOT PASS** — exact-HEAD CI/QD; genuine WordPress/Jetpack/Lighthouse/WCAG; confirmed subscribers or paid orders. **OWNER** — interim homepage engineering; Claude owns production/attribution when available; founder owns release approval.

No source art, history, rights, Mind/Affiliate offers, campaign links, tracking, Jetpack records, or production content changed. No merge, deployment, local WordPress installation, affiliate activation, email or spend. **RELEASE HOLD.**
