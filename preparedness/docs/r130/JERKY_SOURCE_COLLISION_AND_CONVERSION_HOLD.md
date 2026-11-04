# R130 — NCHFP jerky source-ID collision | DRAFT / HOLD

**Scope:** Preparedness #136, coordination #820, charter #818. This is a read-only review dossier. Do not merge, publish, send email, change CMS/navigation/homepage/analytics/social or activate merchant CTAs. The 35-article release candidate remains draft PR #584 at ddb3528ba6494dada1fa1c3a142ce746e3a67706. R130 is stacked on R129 PR #993 at d8b9662a2d97f395f8ecb7a6426b947b44e5ab13.

## Verified new reconciliation finding

The newer historical-food contributor head 67e116e536c7410bed30f8f3b1bb8c166f3c223d replaces hist-food-nchfp-jerky with nchfp-jerky in *Pemmican and Dried Meats* and *Pioneer Travel Rations*. The frozen RC intentionally retains the original identifier under open decision S-7. Crucially, the RC Food source fragment already defines nchfp-jerky and the newer historical-food contributor fragment *also defines nchfp-jerky*.

Both records point to the same NCHFP jerky URL after normalizing only a terminal slash, but their author-specific SUPPORTS and NOTES fields differ. The Food record describes a broader reading scope; the historical-food record documents the USDA/NCHFP disagreement and limitations of that author's reading. They must not be silently coalesced just because the URL matches. An unreviewed application of the new historical-food fragment would create duplicate source-ID definitions and risk provenance loss.

Independent exact-ref inspection of 16 GitHub Git objects showed that **after CRLF-to-LF normalization the two article bodies differ only by these eight source-ID citations**: 7 in Pemmican and 1 in Pioneer. Total raw citation counts remain respectively 46 and 39. Both articles' author source_use mappings differ only by that identifier after comparing JSON objects independent of key ordering. All old/new/RC metadata safety states are pending; RC bodies and metadata exactly match the frozen older versions. The newer hist-food register retains 27 other parsed source records unchanged, retains the retargeted record's SUPPORTS and verified_on date, but changes its NOTES and URL terminal slash. This distinguishes byte/line-ending noise from content change while preserving the real cross-fragment collision.

**Evidence:** frozen contributor https://github.com/finalvestigestudios/final-vestige-site-layer/commit/2acf65ca3efa9b4b5db7976f379b9ea693be43a4 ; advanced contributor https://github.com/finalvestigestudios/final-vestige-site-layer/commit/67e116e536c7410bed30f8f3b1bb8c166f3c223d ; frozen candidate https://github.com/finalvestigestudios/final-vestige-site-layer/pull/584 . Git blob SHA values are pinned in the validator. No independent conclusion is drawn about the accuracy or safety of the temperatures, storage times, warnings or scientific source readings.

## Engineering and test evidence

New read-only gate: preparedness/tools/r130_jerky_source_collision_gate.py. It obtains 16 immutable historical objects via local Git, checks SHA identities, exact article citation replacement, word preservation excluding CRLF, metadata source-use scopes, duplicate-ID definitions, URL equivalence, unchanged safety/draft states and retained source reading descriptions. Machine output is always HOLD_HUMAN_SOURCE_ID_COLLISION, with may_publish=false, may_merge=false and independent_QD_PASS=false.

New test suite: preparedness/tests/test_r130_jerky_source_collision_gate.py. **68 of 68 synthetic/adversarial Python tests passed locally**, and both committed Python files passed bytecode compilation. Exact tested Git file blobs: tool cfe27b72a4296effc0650c9a7a2b655a02a9e3cd; test 4ff0dccf65b35127e46afe43360a8ea8b4c8f003. Actual 16 historical blobs also separately retrieved by the GitHub connector, but the *committed Python program* has not run against a trusted complete repository checkout. Full validator/build/repository tests, native WordPress draft build, GitHub CI, browser QA, mandatory integrity and independent QD remain UNVERIFIED.

Exact-checkout commands (isolated scratch checkout, no release authority):
    python -I preparedness/tools/r130_jerky_source_collision_gate.py --repository .
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

**Human decision OPEN:** choose whether to retain two author-scoped IDs, intentionally reconcile their different source interpretations before a reviewed consolidation, or reject the newer retarget; check NCHFP and USDA statements and surrounding passage context with a qualified reviewer. Keep all 32 shared-URL groups open. Never silently edit canonical citations, source register, crosswalk or human-review state.

## Independent coordination

Seven exact branch SHAs freshly checked on November 4, 2026: Start Here 2122d856; Shelter 5daeaf2d; Food f911ff7a (diverged against frozen contributor); Health d5ef5baf; historical Food 67e116e5; historical Home 7504a5f0; historical Field 4e5caf81. QA #157 remains an unresolved draft with electrical-drill and refrigerated-medication wording differences. PR #169 remains draft; separately proposed fixture fix #973 is not merged. Main home PR #49 head 1049588 and flagship PR #604 bdf01b4 remain untouched. R130 adds no change to article content or other agents' branches.

## Offer → funnel step → blocker → change/check → evidence → owner

| Offer / step | Blocker | Safe next experiment or acceptance | Evidence | Owner |
|---|---|---|---|---|
| ONE current FV-owned Preparedness pack → paid purchase/download | No authenticated rights-cleared, genuinely purchasable existing Preparedness SKU | Validate seller-side product ID, rights, current price, checkout terms, refunds/fees and actual usable delivery; NO paid CTA before approval | HOLD/UNVERIFIED | Growth, Claude, founder |
| Existing Household Emergency Plan → ungated reader | 35-article source review, 32 shared groups, #157 safety wording unresolved | Qualified safety review + actual canonical route/print/keyboard/mobile checks at 320/360/390/768/1440px | HOLD | Preparedness, QA |
| Grok high-intent family contact/reunification topic → guide | No verified matching Grok Preparedness asset_id/post URL/link surface or approved destination | TASK-008 Grok/Praxxis asset audit, then nonlive UTM test only; campaign preparedness_pilot_2026_11 and unique utm_content asset ID; TikTok bio attribution limitations | UNVERIFIED | Grok/Praxxis, Claude |
| Free guide → optional relevant product | No verified appropriate paid deliverable or merchant acceptance | Staged CTA and disclosure/accessibility/fulfillment only after product evidence; full emergency guide stays free | NOT TESTED | Claude, Site QA |
| Confirmed paid order → realized net revenue | No qualified-human session denominator, merchant order/refund/fee reconciliation | Preserve existing consent/analytics; report asset → landing → CTA → confirmed lead → merchant-confirmed paid order → fees/refunds; 7/30d cohorts, tiny sample warnings | N/A | Growth, Claude |

Draft FREE on-site CTA for review only: “Make a household contact and meeting plan you can find. Read the free Household Emergency Plan, including contacts, meeting places and a practice checklist.” Proposed route /preparedness/start-here/household-emergency-plan/ remains NOT VERIFIED LIVE/APPROVED. No fictional product, retired water freebie, payment button, signup change or sales metric.

**Release HOLD. No changes to WordPress, CMS, public pages, navigation, social content, merchant, email, analytics or core homepage.**
