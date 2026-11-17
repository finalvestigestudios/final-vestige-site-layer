# R434 — Whole-document safety and canonical identity gate

**Issue #136 | Commercial priority #820 / charter #818 | 2026-11-17 PT | DRAFT / HARD HOLD.**

Additive, read-only review on R433 #2857. No changes to original articles, citations, source registry, slugs, state, producer branches, WordPress, commerce or analytics. The CLI always returns exit 2, even after passing structural review. The new digest is not a source-truth or release credential.

## Reproducible coverage gap

The R433 prior gate checks readable main-body content and its links/citations, but ignores parts of the document outside the main element. Synthetic preview exports with corrected matching byte locks can receive (a) an unreviewed script outside main, (b) an unauthorized Payhip link outside main, or (c) an offsite rel=canonical URL, **yet R433 reports no structural errors**. Three new regression cases first demonstrate that result using the actual inherited R433 module, then show R434 detects the issue. This is a **synthetic coverage defect**, not evidence of an actual live attack.

## New checks

1. Entire WordPress/preview document head, template chrome and outside-main markup, including script, iframe, object/embed, form, inline event handlers, embedded srcdoc, base URL and meta refresh.
2. Require one canonical for each of the 35 intended article routes, cross-check OpenGraph/Twitter URL host, path and query, and detect canonical drift between WordPress and private preview.
3. Detect unapproved commercial destinations (including Payhip, Stripe, PayPal, Gumroad), obfuscated and percent-encoded hostnames, mixed case, subdomains, relative protocol links, unsafe schemes, userinfo and unexpected ports in common link/form/redirect attributes.
4. Flag CSS external/executable references, possibly concealed safety text, srcset, noscript and template HTML for human inspection. **Normal WordPress theme scripts/forms/images may trigger conservative holds**. Authorized template behavior requires a separately approved allowlist, never blanket suppression.
5. Preserve the inherited R433 ordered passage/citation/link/byte-lock checks, all 35 original identities and five source conflicts/nine unselected forks. No source merges, manuscript selection, or QD overrides.

## Exact local execution

**92/92 new synthetic and adversarial tests PASS. Combined R430–R434 342/342 PASS in one local run.** R434 Python compilation PASS. Source and test Git blob hashes are recorded with issue receipt. Missing-authentic-evidence CLI exits 2 HARD HOLD. No full original 35-article native validate/build, no 70 authentic paired exports, no qualified source/medical/food/emergency/child-privacy QD, and no full GitHub CI success are claimed.

## Conversion-first prioritized plan

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| One authentic FV-owned, rights-cleared Preparedness digital pack, conditional only | Free guide to checkout to paid delivered order | Genuine sellable SKU, merchant ownership, rights, delivery and refunds unverified | Independently verify existing product, seller, checkout, usable download and refund evidence before any paid CTA | **HOLD**, no authenticated payable Preparedness SKU | Founder/Commerce |
| Free official-resource Archive | One already-published family-communication Grok asset to free /preparedness/ | Real immutable asset ID, post URL/date, accurate hook, rights, mobile route unverified | Praxxis checks TASK-008 independently; Grok controls posts, creator queue and social IDs | **UNMATCHED**; free CTA proposal only, unpublished | Grok/Praxxis |
| Original Article #15 with optional Tool #104 | Free guide to practical printable | Emergency applicability, child privacy and accessible print/offline safety unapproved | Qualified source and QD review; keep Tool #102 separate, no retired water offers | **HARD HOLD**; no public tool or safety claim | Preparedness/QD |
| Verified commercial revenue | Qualified humans to landing, relevant CTA, confirmed lead, independently reported paid order, fees and refunds | Merchant receipts, refunds/fees and 7/30-day session attribution missing | Reconcile approved consent-aware first-party events; no duplicate scripts or false paid-event inference | **NOT COMPUTABLE**, not zero | Claude/Commerce |

**Release blockers:** authentic full Git checkout, source/claim and 5+9 variant adjudication, native 35-article build, 35 true WordPress and 35 preview exports, source/health/food/privacy/accessibility/browser/print QD and founder release clearance. Independent QA #157 and synthetic fixture PR #169 remain separate; dependent fix #2205 and homepage #1689 belong to their owners.

**NO merge, public release, CMS/navigation changes, Grok queue/content/social posts, email, merchant or affiliate activation, duplicate analytics, spending or false QD PASS.** Cross-reference issues #136, #820, #818 and Grok/Praxxis TASK-008.
