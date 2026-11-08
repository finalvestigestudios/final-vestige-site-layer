# EX2 — Published homepage versus protected preview: exact-source drift gate

**November 7, 2026 PT | Release HOLD.** Parent PR #1515 (SHA e2f8e6ddbf7fe8e455c7b1a7d629f61e6d96a4f0); frozen PR #49 unchanged.

## Verified materially important live-site finding

Fresh authenticated read-only WordPress **Page 6** (modified **2026-11-05T12:07:24**) confirms the seven-chapter homepage **and Franklin editorial folio are already PUBLISHED** at finalvestige.com. The separate reviewed Playground package is still unpublished/uninstalled. Do not mistake those two states.

| Inventory | Public WordPress Page 6 | Exact protected Playground candidate |
|---|---:|---:|
| Chapters | 7 | 7 |
| Hidden in the Margins | 72 | 72 |
| HTML Focus Fieldbook links | 4 | 5 |
| Archival image elements | **3** | **2** |
| NYPL map 5003296 | **Rendered in public page** | Excluded / reference-only |
| Franklin folio | Present | Present |

Live Page 6 content UTF-8 SHA256: `685911178ae68ca9dfbd8f47f5903ef57f76ac4b52e886d8287416304c98794b`.
Private candidate ZIP SHA256: `8db20aac81deba544d057abfe28fe3baaf71639f74f421a210676fbb0b36e56b`.
Candidate PHP homepage HTML SHA256: `baf26bcaddbf1b86b90f0065e1d68fbd856be03027ecd9d14ebc0ada60a21b1d`.

### New release blocker

Page 6 publicly includes the **NYPL 1903 Brooklyn Rapid Transit map** in an archival image element (WP media #1258). The protected candidate intentionally excludes its binary reproduction pending rights reconciliation. That is a **real live-versus-candidate delta**, not proof of infringement or permission. WordPress caption wording is not independent rights verification. An unreviewed replacement would also change Focus CTA inventory.

### Code and reproduction

`experience2/qa/verify_live_page6_release_delta.py` is a no-network, read-only source-delta verifier. It SHA-pins the separately supplied private #1515 candidate ZIP and PHP custody, extracts the actual plugin homepage HTML, normalizes CDN/HTML query strings to image filenames, and always returns release HOLD. No public full HTML, subscribers, private emails, cookies, credentials, or analytics data are committed.

Run inside a directory containing the separately supplied protected ZIP:

```sh
python experience2/qa/verify_live_page6_release_delta.py --live experience2/qa/live_page6_inventory_20261107.json --candidate /private/fv-ex2-official-playground-web-review.zip --out /tmp/fv-ex2-live-delta.json
```

Run the 12 adversarial methods after placing the protected ZIP at the test's documented local path, or adjust that test-only path. The test data is a **point-in-time** inventory; refresh the WordPress Page 6 read and SHA-256 immediately before considering any later release. This source comparison is not WordPress Core/Assembler acceptance, media byte proof, accessibility certification, Lighthouse/CWV, Jetpack delivery, or commercial attribution.

### Conversion-first decision and owners

**Offer:** free 52-page Focus Fieldbook. **Step:** historical homepage -> usable Focus route -> confirmed opt-in -> independent paid order. **Blocker:** 4 versus 5 CTA paths and 3 versus 2 archival images plus rights uncertainty, separate Jetpack/merchant verification pending. **Change:** fail-closed, source-controlled drift review; no unauthorized live edits. **Evidence:** exact WordPress source inventory and deterministic protected candidate check. **Owner:** homepage engineering + independent Site QA; Claude owns Jetpack/commerce attribution; Grok/Praxxis own asset IDs/social traffic. Net revenue per 1,000 qualified human sessions remains NOT COMPUTABLE.

Before any release: reconcile published Page 6 with candidate, document NYPL exact file rights, run isolated WordPress/Assembler and actual media transfer, keyboard/touch/no-JS/axe WCAG 2.2 AA, Lighthouse/CWV, QD/CI at exact SHA, founder visual and production authorization. The WordPress.com Personal plan does not furnish native staging. Do not merge, overwrite Page 6, install on public site, activate affiliate or send email.

Read-only sources: WordPress pages-get Page 6; WordPress media-get IDs 473/474/1258; current public homepage; GitHub Issue #150, #820; private #1515 exact-source bundle.
