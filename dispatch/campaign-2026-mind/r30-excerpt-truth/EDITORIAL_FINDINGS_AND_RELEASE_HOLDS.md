# Dispatch R30 — Source-aligned optional Jetpack excerpts (DRAFT, UNSENT)

**Ownership:** Dispatch [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Offer pages and merchant permissions: Mind [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Original manuscript PR #175; original excerpt fallback PR #187; initial per-issue safety PR #201; stacked draft parent PR #364. No homepage code, frozen PR #49, production WordPress, subscriber records or outgoing email is touched.

## Why this is material editorial work

The original optional custom excerpts in `delivery/wordpress_excerpt_copy.json` no longer matched all of the revised source manuscripts. **Issue 01** implied an *eighteenth-century paper trail* when the actual opening is a **1998 real-world change-blindness experiment** by Simons and Levin, linked to photographic provenance. The erroneous century could mislead readers before they reach the article. **Issue 04** previously characterized the approximately 17-second window as running from the *first indication* of the Apollo 1 fire. Its actual primary-record interpretation is **17.1 seconds between the first recorded crew report of fire and the end of the last transmission**. It is not the ignition time or the duration of the fire. **Issue 06** described a 2002 diary-compliance study; the revised excerpt accurately describes **paper diaries monitored with opening sensors**, without implying each written entry was directly time-stamped.

The corrected six excerpts are synchronized with the **current** manuscripts and existing subjects, and remain a **separately reviewable fallback** if authorized full-body delivery is not viable. The current editor-facing first blocks still show the deliberate DRAFT warning; this PR does not alter them.

## Six source-specific opening/CTA contracts

1. **01 / 1998 Simons–Levin:** Observed door-swap experiment, approximately half noticing in the first studied group, not a universal eyewitness error rate. The optional excerpt invokes photographic provenance; the sole intended primary editorial destination is published **The Missing Caption**. Primary source DOI: https://doi.org/10.3758/BF03208840 .
2. **02 / 1784 Puységur:** Historical source is Puységur's reported observation, not independently proven magnetic fluid. Distinguish the French royal commission's contemporaneous investigation from direct examination of Victor Race. Published dossier: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; Wellcome 1784 bibliographic entry: https://wellcomecollection.org/works/es4ayp6q .
3. **03 / Zen12:** The intended commercial evaluation describes the seller's tier differences, not guaranteed equivalence of twelve minutes to an hour. Beginner/Advanced six levels/24 MP3s; Premium 12 levels/48 MP3s are **seller-reported** contents. Include conditional affiliate disclosure in the excerpt itself. The guide is **unpublished/inactive** and merchant email rights and current checkout/refund terms are **NOT VERIFIED**. Merchant references: https://zen12.com/about and https://zen12.com/ .
4. **04 / Apollo 1:** Accurate distinction between recorded crew radio interval, ignition uncertainty and interacting design hazards. No exact ignition source proved. The sole primary editorial CTA is the published investigation: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ ; official investigation https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ .
5. **05 / Total Focus:** Free three-minute exercise and distinction between the seller-reported 33-minute file and unverified concentration effects. Its proposed commercial excerpt discloses possible commission without inventing a price or active affiliate link. Guide **NOT LIVE**, merchant email rights **NOT VERIFIED**, and product evidence not independent: https://hypnosislive.com/mental-skills/total-focus .
6. **06 / 2002 diary study:** Paper-diary opening sensors vs self-reported compliance; not a meditation trial or evidence of attention gains. Four-line evidence log and published free Fieldbook CTA: https://finalvestige.com/focus/ . Clinical study https://www.bmj.com/content/324/7347/1193 .

## Native Jetpack limitations remain open

As of the **authenticated October 31, 2026 23:35 UTC check**, WordPress reports newsletter enabled, `email_new_posts_by_default=false`, global `email_content_format=excerpt`, zero recent sends, existing 52-page Fieldbook welcome template **configured, not proven delivered**. Subscriber snapshot: total 2, confirmed 2, unconfirmed 2 — **not four unique recipients**, nor a verified sendable cohort. No subscriber identities were accessed or exported.

This patch creates no native WordPress post, excerpt, test email or preheader. The 350-character limit here is a **local robustness budget**, *not* proof that WordPress truncates explicitly set custom excerpts at 350 characters. WordPress.com documentation mentions 55 words for absent custom excerpts; Jetpack documentation mentions 350 characters on its variant. Both describe default fallbacks, not independently validated received messages. Jetpack also documents per-post content overrides; that feature has not been proven on Final Vestige's actual editor. A proposed manifest preheader is not automatically an email-client snippet.

**The optional excerpt route is not a substitute for the founder-approved full-length manuscript**, whose intended research and single CTA can be lost when only a teaser is delivered. It is *not* approved for substitution. The publisher must make a separate explicit delivery-mode decision after native preview and consent checks.

## Compliance, authorization and publication hold

**ALL SIX HOLD_UNSENT; #03/#05 additionally HOLD_MERCHANT.** This source-only repair does not authorize release. Required: Final Vestige valid postal address, actual rendered functional unsubscribe, genuine WordPress received MIME and safe post-title/snippet, current recipient eligibility privately verified, written product-specific Inspire3 affiliate acceptance **including permission for EMAIL**, approved earning-link/creative formats and published reviewed warm-up guides, current checkout/refund truth, and founder's final approval for exact creative/audience/date. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

The combined source audit rejects unapproved URLs, promises, bad chronology, missing commission disclosures, outdated subjects and changes to the six-issue 4:2 allocation. The audited fallback is not a marketing experiment; the list is too small for credible A/B significance. Preserve privacy and no new platform expense.

## Reproduce review from the complete repository checkout

```sh
python -m unittest discover -s dispatch/campaign-2026-mind/tests -v
node dispatch/campaign-2026-mind/r30-excerpt-truth/audit_excerpt_truth.cjs
node dispatch/campaign-2026-mind/r30-excerpt-truth/tests/test_excerpt_truth.cjs
```

The local source mirror used for preflight is not a GitHub checkout, and an offline HTML board is not a received email. Independent tests must not be called hosted CI, a legally compliant send, or proof of merchant permission.
