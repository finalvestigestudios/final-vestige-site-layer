# R29 — Dispatch inbox-contract and native-render credibility audit (NO SEND)

**Owner:** Issue #174; companion merchant Issue #171. **Parent:** draft PR #358 at exact \`6db066be8c479f17756406f39c429ba6c1b6dad2\`. No shared homepage, frozen PR #49, WordPress, subscriber or paid-service changes.

## Verified findings on 2026-10-31

- **Actual WordPress settings at 22:38:50–53 UTC:** newsletter enabled; automatic new-post emails OFF; global \`excerpt\`; sender name Final Vestige; reply-to no-reply; welcome template configured with 52-page Focus Fieldbook; zero recent sends. Subscriber total=2, confirmed=2, unconfirmed=2: counters are not four unique or proven eligible contacts. Subscriber addresses were never opened, exported or recorded. Welcome *receipt* unverified.
- **Exact current PR #358 first-block source reads:** every one of six Gutenberg candidates begins \`DO NOT PUBLISH OR EMAIL — DRAFT ONLY\`. This deliberate authoring guard would be a bad opening if the candidate were mistakenly published as an email. It is a **source-order risk**, not proof of any actually received snippet. Keep the guard until specifically authorized release conversion, do not publish.
- **Six subject lines:** 24, 26, 37, 45, 41, 40 characters. Accurate, evidence-based, non-sensational. Proposed preheaders: 80, 78, 75, 65, 61, 61 characters, respectively, but they are **not verified Jetpack controls**. The current authenticated newsletter settings do not expose an independent preheader field. The email client's actual preview text remains unknown.
- **Model-only excerpt results:** WordPress.com describes a 55-word default; Jetpack's 2026-10-28 guide describes a 350-character default on its variant. Neither model includes the single primary CTA in any of six present editorial bodies; for commercial #03/#05 the near-offer disclosure lies beyond both short models. A per-post full-text override is documented, but not verified on a specific unpublished post or delivered MIME.
- **Four editorial / two optional offer reviews retained.** Editorial CTAs lead to published Final Vestige material. Issues 03 and 05 have inactive warm-up-guide placeholders, not actual approved buyer guides or merchant earning URLs. Mind draft PR #361 is *not* a published product guide. Merchant acceptance, permission to promote through EMAIL, authorized SKU tracking links, current sale/refund terms and promotional-media rights are not proven.
- **Product claim truth:** Zen12 Beginner/Advanced packages (six levels/24 MP3s each) differ from Premium (twelve/48); seller's hour-in-twelve-minutes / automatic brainwave / health-wealth assertions are NOT independently supported here. Hypnosis Live Total Focus's 33-min/47-MB description is seller-reported; enhanced concentration outcome promises are not product-specific independent evidence. Do not insert evergreen price/refund figures from dynamic sales pages.
- **Editorial Standards:** firsthand evidence preferred, disputed records disclosed, AI assistance not a primary source, commercial relationships do not determine conclusions. FTC requires accurate commercial identity/subject, functional opt-out, and a valid publisher postal address; neither Final Vestige postal address nor actual Jetpack unsubscribe was verified. The merchant's own address is **not Final Vestige's mailing address**.

## Exact independent check provenance
Current 17 source/test/renderer GitHub blob hashes were independently compared to the archived baseline; **17/17 match**. Baseline Python suite executed against the reconstructed exact texts after restoring the R25 current Gutenberg #03 fixture: **134/134 PASS**. The initial run without this fixture errored (117 tests counted; not passed); corrected fixture and rerun is the valid baseline. Separate **34/34** offline Python inbox-contract regression tests executed, including 12 unsafe mutations fail-closed. Separate current GitHub source V8 checks on the new *source-controlled CJS logic* returned **40 passing checks including 17 unsafe mutations**. Distinct locally generated reviewer board passed actual offline Chromium at 320/360/390/768/1024/1440px (**6/6**); these are not WordPress/Gmail renders. Source-controlled \`REVIEW_BOARD.html\` is also a static, non-native viewer. Hosted CI remains pending/unknown until a run is inspected.

## Release requirements
Final Vestige real physical mailing address; actual received and functional Jetpack HTML/plain unsubscribe; authenticated per-post full-text control and delivered-email body, title, sender and snippet; consent/eligibility verified privately; published editorial and buyer-guide targets; partner approval and written email-promotion terms for commercial #03/#05; QA of merchant SKU price/refund/claims when relevant; final founder approval of *exact creative, audience, schedule and sending*. No email or test-email authorization exists. No posts, sends, WordPress writes or subscriber/merchant contact performed.

**ALL SIX HOLD_UNSENT; 03/05 additionally HOLD_MERCHANT.**

Official resources:
- https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ (2026-10-28)
- https://wordpress.com/support/newsletter-settings/ (reviewed 2026-10-26)
- https://jetpack.com/support/newsletter/
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- https://zen12.com/hnp ; https://zen12.com/about
- https://hypnosislive.com/mental-skills/total-focus
- https://finalvestige.com/editorial-standards/