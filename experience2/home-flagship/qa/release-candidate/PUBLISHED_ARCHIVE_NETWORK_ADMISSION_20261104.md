# 2026-11-04 — Published seven-chapter archive network integrity admission (DRAFT / HOLD)

**Source of truth:** Experience #150, Conversion #820, parent QA PR #1011 `1825fd864834f88e121f4ffee1a6cfa66c8ffbd4`. **Scope:** existing live anonymous-browser harness ONLY; no WordPress edits, new media, new chapters, releases, or analytics.

## Exact read-only production witness

WordPress.com site 256784396, Page 6 (`publish`, modified `2026-11-04T14:39:24` as reported by WordPress) contains **four image elements**: three archival image exhibits and the existing Focus cover. All three exhibit elements use `data-fv-archive-img`, responsive `srcset`, lazy loading and descriptive alt text. Canonical first-party source paths and WordPress media IDs:

| Evidence | Media ID | Public source filename | Served responsive derivatives |
|---|---:|---|---|
| Apollo 1 crew, NASA identifier S67-19766 | 473 | `s67-19766.webp` | `i0.wp.com` |
| Franklin expedition Victory Point note | 474 | `Franklinexpeditionnote.jpg` | `i0.wp.com` |
| NYPL 1903 rapid-transit map | 1258 | `edit-017-v02-nypl-5003296-original.jpg` | `i0.wp.com` |

The fourth image is the existing `focus_complete_cover.webp`. Do not make this a substitute for a missing historical exhibit.

**Source versus rights:** Verified that published WordPress source refers to these media records; metadata is NOT proof of rights, source-credit completeness, unmodified historical accuracy, CDN transfer bytes, or anonymous-user delivery. Maintain independent NASA identification/nonendorsement, Franklin photographic provenance and NYPL reuse/credit checks.

## The actual preexisting false-pass

In parent #1011, `readImages()` passed if `main img` returned zero rows: an empty loop never failed. The image-response event collected `bytes` asynchronously but no check asserted that any required exhibit transferred a nonzero response body. A missing Apollo, Franklin or NYPL exhibit could therefore leave the browser gate green if no other criterion failed. That is a release-admission defect, not evidence that production images are broken.

## Proposed change on this isolated branch

- Pin the three already-published archival asset filenames, **not** synthetic artwork or new image sources.
- Require each exhibit in DOM with completed positive bitmap dimensions.
- Require an actual HTTP 200 image response with **nonzero body bytes**, after waiting for image response-body promises.
- Admit only first-party `/wp-content/uploads/` and the explicit WordPress `i0.wp.com/finalvestige.com/wp-content/uploads/` derivative path; no URLs, secrets or image query strings in public receipts.
- Preserve the actual `/focus/` click contract and require the intended Fieldbook offer text in addition to Jetpack markup.
- Fail closed on missing DOM images, zero-byte responses, blocked/failed HTTP, untrusted host, missing decode.

## Verification and release limitations

**BUILT:** isolated source + six new node:test negative/positive checks; parent browser fixture preserved. **TESTED:** six pure-helper adversarial V8 preflight checks on transformed source (with a minimal URL shim; NOT full Node or Chromium). **NOT YET VERIFIED:** complete exact-checkout Node suite, live Chromium transfer bytes, anonymous browser screenshots, whole-document axe, physical 200% zoom, Lighthouse/field CWV, image rights and independent QD/CI.

The current runtime cannot resolve public domains and its Chromium network navigation reports `ERR_BLOCKED_BY_ADMINISTRATOR`, including localhost; no live-browser PASS is claimed. A read-only live regression should run on a suitably network-enabled trusted runner with allowed egress. **Do not change production infrastructure or turn off browser security restrictions to make this test pass.**

## Conversion-first decision

**Offer:** existing free 52-page Focus Fieldbook. **Step:** social visit → evidence → unobstructed header Focus CTA → `/focus/` → confirmed direct-audience signup → independently verified paid sale. **Blocker:** browser gate could ignore missing archival trust evidence. **Change:** fail closed on all three real exhibits and measured transferred bytes. **Evidence:** source-grounded media/markup inventory; six isolated helper controls. **Owners:** homepage engineering browser QA; Claude attribution/commerce; Praxxis creator QA; Grok content/distribution. **Revenue/lead outcome:** not independently verified.

Release remains HOLD pending live browser/Assembler staging, QA and founder approval. No production CMS writes, merge, publish, email, subscriptions, affiliate activation or spend.
